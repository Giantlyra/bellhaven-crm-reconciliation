"""Controlled execution queue for explicitly approved, low-risk field corrections.

This module adds NO new write path. Every write still goes through executor.execute, so all existing safeguards
apply to every item (approval bound to the proposal fingerprint, fresh live preview + plan token, SOP/policy
re-check, per-op audit, CRM read-back, CRM_WRITES_ENABLED). What the queue adds:

  * an ELIGIBILITY GATE: only single-account `phone`/`name` updates with an exact address+ZIP identity match,
    high confidence, no competing CRM candidates, an account that is already under Bellhaven, and (for renames)
    a name that is recognisably the same. Everything else (ownership, parent, status, duplicates, CHOW, billing
    address, uncertain matches, material renames) is "manual review only" and cannot be queued.
  * AUTOMATIC PRE-WRITE VALIDATION per item, immediately before its write: eligibility, approval, drift/policy
    preview, exact request equals the approved operation, and a live re-fetch of the website page confirming the
    proposed values are still published.
  * an independent PROTECTED-FIELD DIFF after the read-back: every field except the written ones (and the CRM's
    own updated_at) must equal the pre-write record, and the account's contacts must be unchanged.
  * STOP-ON-ERROR: the first item that is not verified (or violates the diff) halts the queue; later items are
    reported as not run and nothing else is written.
  * RECEIPTS: ledger audit events (queue_started / queue_item / queue_finished) plus a JSON receipt file.

Nothing here approves a proposal. A proposal is queueable only after a human approved it in the app.
"""
from __future__ import annotations

import difflib
import json
import re
from datetime import datetime, timezone

from . import config
from . import executor as X
from . import ledger as L
from .evidence import BELLHAVEN_PARENT
from .normalize import norm_phone

ALLOWED_FIELDS = {"phone", "name"}
MIN_NAME_SIMILARITY = 0.80          # below this a rename could be an ownership/brand change: manual review
ALLOWED_RISK = {"low", "medium"}
LINK_FIELDS = ("chow_current_account", "duplicate_of_account")
BELLHAVEN_PARENT_IDS = {BELLHAVEN_PARENT}   # the Bellhaven Senior Living parent account in this CRM


def queue_phrase(n: int) -> str:
    return f"APPLY QUEUE OF {n}"


def _norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("&", " and "))


def name_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm_name(a), _norm_name(b)).ratio()


def eligibility(p: dict) -> list:
    """Reasons this proposal must stay in manual review. An empty list means it may be queued (once approved)."""
    pl = p["payload"]
    why = []
    if p["kind"] != "FIELD_UPDATE":
        return [f"{p['kind']} proposals are always manual review"]
    ops = pl.get("ops") or []
    if len(ops) != 1 or ops[0].get("type") != "update":
        return ["not a single-account update"]
    op = ops[0]
    fields = op.get("fields") or {}
    outside = sorted(set(fields) - ALLOWED_FIELDS)
    if not fields or outside:
        why.append(f"changes {outside or 'nothing'}: the queue only handles phone and name")
    if (p.get("risk") or pl.get("risk")) not in ALLOWED_RISK:
        why.append(f"engine risk is {p.get('risk') or pl.get('risk')}")
    if (p.get("confidence") or pl.get("confidence")) != "high":
        why.append("match confidence is not high")
    ev = pl.get("evidence") or {}
    if not str(ev.get("basis", "")).startswith("address+ZIP match"):
        why.append("identity is not an exact address+ZIP match")
    if ev.get("duplicates") or ev.get("alternatives"):
        why.append("other CRM account(s) compete for this facility")
    if pl.get("warnings"):
        why.append("the proposal carries warnings: " + "; ".join(pl["warnings"]))
    base = (pl.get("baseline") or {}).get(op.get("account_id"), {})
    if base.get("parent_id") not in BELLHAVEN_PARENT_IDS:
        why.append("account is not already under Bellhaven (an ownership question)")
    if any(base.get(k) for k in LINK_FIELDS) or base.get("status") != "Active":
        why.append("account has an ownership/duplicate link or is not Active")
    if "name" in fields:
        sim = name_similarity(base.get("name", ""), fields["name"])
        if sim < MIN_NAME_SIMILARITY:
            why.append(f"material rename ({base.get('name')!r} → {fields['name']!r}, similarity {sim:.2f}): "
                       "could be a brand or ownership change")
    return why


def default_fetch_site(url: str) -> dict:
    import httpx
    from .scrape import parse_detail
    if not url.startswith(config.SITE_BASE):
        raise ValueError(f"refusing to fetch a URL outside the Bellhaven site: {url}")
    r = httpx.get(url, timeout=30, follow_redirects=True)
    r.raise_for_status()
    return parse_detail(r.text, url)


def _site_problems(p: dict, fetch_site) -> list:
    """The proposed values must still be what the Bellhaven website publishes, at the same address."""
    pl = p["payload"]
    web = (pl.get("evidence") or {}).get("website") or {}
    fields = pl["ops"][0]["fields"]
    try:
        page = fetch_site(web["source_url"])
    except Exception as e:  # noqa: BLE001  fail closed
        return [f"could not re-fetch the website page: {type(e).__name__}: {e}"]
    out = []
    for k in ("street", "zip"):
        if page.get(k) != web.get(k):
            out.append(f"website {k} changed since the proposal: {web.get(k)!r} → {page.get(k)!r}")
    if "phone" in fields and norm_phone(page.get("phone")) != norm_phone(fields["phone"]):
        out.append(f"website phone is now {page.get('phone')!r}, not the proposed {fields['phone']!r}")
    if "name" in fields and page.get("name") != fields["name"]:
        out.append(f"website name is now {page.get('name')!r}, not the proposed {fields['name']!r}")
    return out


def validate_item(crm, ledger, pid: int, fetch_site=None) -> dict:
    """READ-ONLY pre-write validation of one queue item. Returns {pid, ok, problems, pv, p}."""
    fetch_site = fetch_site or default_fetch_site
    p = ledger.get_proposal(pid)
    out = {"pid": pid, "ok": False, "problems": [], "pv": None, "p": p}
    if p is None:
        out["problems"].append("no such proposal")
        return out
    out["problems"] += [f"manual review only: {r}" for r in eligibility(p)]
    if p["status"] != L.APPROVED:
        out["problems"].append(f"status is '{p['status']}': it must be approved by a human in the app first")
    else:
        appr = ledger.last_decision(pid, "approved")
        if not appr or appr.get("fingerprint") != p["fingerprint"]:
            out["problems"].append("no approval recorded for this exact proposal version")
    if out["problems"]:
        return out
    try:
        pv = X.preview(crm, ledger, pid)
    except Exception as e:  # noqa: BLE001
        out["problems"].append(f"preview failed: {type(e).__name__}: {e}")
        return out
    out["pv"] = pv
    out["problems"] += pv["problems"]
    op = p["payload"]["ops"][0]
    reqs = pv["requests"]
    if not (len(reqs) == 1 and reqs[0]["method"] == "PATCH" and reqs[0]["path"] == f"/accounts/{op['account_id']}"
            and reqs[0]["body"] == op["fields"]):
        out["problems"].append("the live request does not equal the approved operation")
    if pv["noop"]:
        out["problems"].append("the CRM already holds the target value: nothing to write")
    out["problems"] += _site_problems(p, fetch_site)
    out["ok"] = not out["problems"]
    return out


def preview_queue(crm, ledger, pids: list, fetch_site=None) -> list:
    """Validate every selected item (read-only). Items that write an account another item touches are deferred."""
    items, included = [], []
    for pid in pids:
        clash = X.batch_overlaps(ledger, included + [pid])
        if clash:
            items.append({"pid": pid, "ok": False, "p": ledger.get_proposal(pid), "pv": None,
                          "problems": [f"deferred to a later queue: {clash[0]}"]})
            continue
        v = validate_item(crm, ledger, pid, fetch_site)
        items.append(v)
        if v["ok"]:
            included.append(pid)
    return items


def _contacts_by_account(crm, ids: set):
    fn = getattr(crm, "list_contacts", None)
    if fn is None:
        return None
    out = {i: [] for i in ids}
    for c in fn():
        if c.get("account_id") in out:
            out[c["account_id"]].append((c.get("contact_id"), c.get("name"), c.get("title"), c.get("phone"),
                                         c.get("email"), c.get("is_active"), c.get("updated_at")))
    return {k: sorted(v, key=str) for k, v in out.items()}


def run_queue(crm, ledger, items: list, *, confirmation: str, writes_enabled=None, fetch_site=None,
              actor: str = "local-reviewer") -> dict:
    """items: [(pid, plan_token), ...] exactly as shown in the queue preview the operator reviewed."""
    pids = [pid for pid, _ in items]
    if X.normalize_phrase(confirmation) != queue_phrase(len(items)):
        raise X.ExecutionError(X.phrase_mismatch(queue_phrase(len(items)), confirmation, "Queue confirmation"))
    if not items:
        raise X.ExecutionError("The queue is empty")
    if len(set(pids)) != len(pids):
        raise X.ExecutionError("A proposal appears twice in the queue")
    enabled = config.WRITES_ENABLED if writes_enabled is None else writes_enabled
    if not enabled:
        ledger.log("queue_refused", None, pids=pids, reason="dry-run", actor=actor)
        raise X.WritesDisabled("Live CRM writes are disabled (dry-run mode). Restart the server with "
                               "CRM_WRITES_ENABLED=1 to run the queue.")
    overlap = X.batch_overlaps(ledger, pids)
    if overlap:
        raise X.ExecutionError("Queue refused: " + "; ".join(overlap))
    for pid in pids:                      # whole-queue gate before ANY write
        p = ledger.get_proposal(pid)
        why = eligibility(p) if p else ["no such proposal"]
        if p and p["status"] != L.APPROVED:
            ledger.log("queue_refused", pid, reason=f"status {p['status']}: not approved", actor=actor)
            raise X.ExecutionError(f"#{pid} is '{p['status']}': only proposals a human approved can be queued")
        if why:
            ledger.log("queue_refused", pid, reason="; ".join(why), actor=actor)
            raise X.ExecutionError(f"#{pid} is manual review only: {'; '.join(why)}")

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ledger.log("queue_started", None, pids=pids, actor=actor)
    acct_ids = {ledger.get_proposal(pid)["payload"]["ops"][0]["account_id"] for pid in pids}
    contacts_before = _contacts_by_account(crm, acct_ids)
    results, stopped = [], False
    for n, (pid, token) in enumerate(items):
        if stopped:
            results.append({"pid": pid, "status": "not_run", "note": "an earlier item did not verify"})
            continue
        v = validate_item(crm, ledger, pid, fetch_site)      # automatic pre-write validation, per item
        if not v["ok"]:
            r = {"pid": pid, "status": "blocked", "problems": v["problems"]}
            ledger.log("queue_item", pid, **r)
            results.append(r)
            stopped = True
            continue
        p = v["p"]
        op = p["payload"]["ops"][0]
        aid, fields = op["account_id"], op["fields"]
        before = v["pv"]["fresh"][aid]
        try:
            res = X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=token,
                            writes_enabled=True, actor=actor)
        except X.ExecutionError as e:
            res = {"status": "refused", "error": str(e)}
        r = {"pid": pid, "account_id": aid, "status": res["status"], "token": token,
             "wrote": dict(fields), "before": {k: before.get(k) for k in fields}}
        if res["status"] == L.VERIFIED:
            after = crm.get_account(aid)
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            illegal = [k for k in changed if k not in fields and k != "updated_at"]
            contacts_ok = True
            if contacts_before is not None:
                contacts_ok = _contacts_by_account(crm, {aid})[aid] == contacts_before[aid]
            r.update(after={k: after.get(k) for k in fields}, changed_fields=changed,
                     protected_ok=not illegal and contacts_ok, contacts_checked=contacts_before is not None)
            if illegal or not contacts_ok:
                r["status"] = "verified_but_protected_field_changed"
                r["problems"] = ([f"unexpected change to {illegal}"] if illegal else []) + \
                                ([] if contacts_ok else ["the account's contacts changed"])
        else:
            r["problems"] = res.get("problems") or ([res["error"]] if res.get("error") else [])
        ledger.log("queue_item", pid, **{k: v2 for k, v2 in r.items() if k != "pid"})
        results.append(r)
        if r["status"] not in (L.VERIFIED, L.RESOLVED):
            stopped = True
    ledger.log("queue_finished", None, results=[{"pid": r["pid"], "status": r["status"]} for r in results],
               stopped=stopped)
    receipt = {"started": started, "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "actor": actor, "stopped_early": stopped, "results": results}
    path = None
    try:
        d = config.DATA_DIR / "queue_receipts"
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"queue-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        path.write_text(json.dumps(receipt, indent=1, default=str))
    except OSError:
        path = None
    return {**receipt, "receipt_file": str(path) if path else None}
