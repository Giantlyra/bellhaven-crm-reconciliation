"""Evidence comparison for the proposal review page (Review & Monitoring Interface).

Read-only: builds a side-by-side view from data that already exists (the proposal payload captured at scan time, the
run/source records in the ledger, and the run's saved snapshot). It makes no network calls and writes nothing. The
matching logic is not changed here; this module only explains what the Reconciliation Engine already decided.

Comparison results per field:
  "match"          both sources have a value and they agree after normalization
  "differs"        both sources have a value and they disagree
  "not available"  one source does not carry this field; this is never treated as a mismatch
"""
from __future__ import annotations

import glob
import json
import os
from typing import Optional

from . import normalize as N

NA = "Not available"
BELLHAVEN_PARENT = "0015QAPLGS3FVYEEEM"

# (label, website key, CRM key, how to compare, is an identity field)
FIELDS = [
    ("Name", "name", "name", "name", True),
    ("Street", "street", "billing_street", "street", True),
    ("City", "city", "billing_city", "text", True),
    ("State", "state", "billing_state", "text", True),
    ("ZIP", "zip", "billing_zip", "zip", True),
    ("Phone", "phone", "phone", "phone", False),
    ("Care type", "_care", "care_type", "text", False),
    ("Parent / owner", "_parent", "parent_name", "parent", False),
    ("Account status", None, "status", None, False),
    ("Administrator", "administrator", None, None, False),
    ("Lifetime revenue", None, "lifetime_revenue", None, False),
    ("Outstanding AR", None, "outstanding_ar", None, False),
]

KIND_SUMMARY = {
    "FIELD_UPDATE": "Correct CRM field values to match the Bellhaven website.",
    "WRONG_PARENT": "Move the account under the Bellhaven parent (direct re-parent; the billing SOP allows it).",
    "CHOW": "Change of ownership: keep the old account as the financial record and link it to a Bellhaven account.",
    "DUPLICATE": "Mark a duplicate account Inactive and point it at the surviving account. Nothing is merged or deleted.",
    "WEBSITE_ONLY": "Create a CRM account for a community the website lists but the CRM does not have.",
    "CRM_ONLY": "Flag a CRM account that the website does not list.",
    "HOLD": "No change. Identity or ownership must be resolved by a person first.",
}


def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _same(how: str, a, b) -> bool:
    if how == "name":
        return N.norm_name(a) == N.norm_name(b)
    if how == "street":
        return N.norm_street(a) == N.norm_street(b)
    if how == "zip":
        return N.norm_zip(a) == N.norm_zip(b)
    if how == "phone":
        return N.norm_phone(a) == N.norm_phone(b)
    if how == "parent":
        return "bellhaven" in str(b).lower()
    return str(a).strip().lower() == str(b).strip().lower()


def _website_value(web: dict, key: Optional[str]):
    if not web or key is None:
        return None
    if key == "_care":
        offers = web.get("care_offerings") or []
        return N.website_care_type(offers) or None
    if key == "_parent":
        return "Bellhaven (listed on the Bellhaven website)"
    return web.get(key)


def _money(v):
    if isinstance(v, (int, float)):
        return f"${v:,.0f}"
    return v


def compare(web: Optional[dict], crm: Optional[dict], proposed: Optional[dict] = None) -> list:
    """One row per field: website value, CRM value, result, and the proposed value if this proposal changes it."""
    proposed = proposed or {}
    rows = []
    for label, wk, ck, how, identity in FIELDS:
        wv = _website_value(web, wk) if web else None
        cv = crm.get(ck) if (crm and ck) else None
        if ck in ("lifetime_revenue", "outstanding_ar") and crm is not None:
            cv = _money(cv)
        w_na = web is None or wk is None or _blank(wv)
        c_na = crm is None or ck is None or _blank(cv)
        if w_na or c_na:
            result = "not available"
        else:
            result = "match" if _same(how, wv, cv) else "differs"
        note = ""
        if wk == "_care" and web:
            note = "website lists: " + (", ".join(web.get("care_offerings") or []) or "nothing")
        if wk == "_parent" and crm and not c_na and crm.get("parent_id"):
            note = f"CRM parent_id {crm.get('parent_id')}"
        rows.append({
            "label": label, "identity": identity,
            "website": NA if w_na else wv, "crm": NA if c_na else cv,
            "result": result, "note": note,
            "changes": ck in proposed, "proposed": proposed.get(ck) if ck in proposed else None,
            "crm_key": ck,
        })
    return rows


def _snapshot_accounts(run_id: Optional[int], data_dir: str) -> dict:
    """Account records from the run's saved snapshot (read-only), for naming competing candidates."""
    if not run_id:
        return {}
    files = sorted(glob.glob(os.path.join(data_dir, "snapshots", f"run-{int(run_id):04d}-*.json")))
    if not files:
        return {}
    snap = _load_snapshot(files[-1])
    return {a.get("account_id"): a for a in snap.get("accounts", [])}


def _load_snapshot(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


WEB_KEYS = ("name", "street", "city", "state", "zip", "phone", "care_offerings", "administrator")
CRM_KEYS = ("name", "billing_street", "billing_city", "billing_state", "billing_zip", "phone", "care_type", "parent_id",
            "status", "lifetime_revenue", "outstanding_ar", "chow_current_account", "duplicate_of_account")


def record_freshness(ev: dict, run_id: Optional[int], data_dir: str) -> dict:
    """Compare this proposal's own website and CRM records with the latest saved scan (read-only)."""
    if not run_id:
        return {"run": None, "website": None, "crm": None}
    files = sorted(glob.glob(os.path.join(data_dir, "snapshots", f"run-{int(run_id):04d}-*.json")))
    snap = _load_snapshot(files[-1]) if files else {}
    if not snap:
        return {"run": run_id, "website": None, "crm": None}
    out = {"run": run_id, "website": None, "crm": None}
    web = ev.get("website")
    if web:
        cur = next((f for f in snap.get("facilities", []) if f.get("source_url") == web.get("source_url")), None)
        out["website"] = (["community no longer listed"] if cur is None else
                          [k for k in WEB_KEYS if (cur.get(k) or None) != (web.get(k) or None)])
        out["website_retrieved_at"] = cur.get("retrieved_at") if cur else None
    crm = ev.get("crm")
    if crm:
        accts = {a.get("account_id"): a for a in snap.get("accounts", [])}
        cur = accts.get(crm.get("account_id"))
        out["crm"] = (["account not found"] if cur is None else
                      [k for k in CRM_KEYS if (cur.get(k) if cur.get(k) not in ("", None) else None)
                       != (crm.get(k) if crm.get(k) not in ("", None) else None)])
    return out


def source_status(led, p: dict) -> dict:
    """Timestamps and completeness for the run that produced the evidence, and for the latest scan."""
    def describe(run):
        if not run:
            return None
        srcs = {s["source"]: s for s in led.sources(run["id"])}
        errs = run.get("errors")
        try:
            errs = json.loads(errs) if isinstance(errs, str) else (errs or [])
        except ValueError:
            errs = []
        return {"id": run["id"], "status": run["status"], "finished_at": run.get("finished_at"),
                "website_facilities": run.get("website_facilities"), "crm_accounts": run.get("crm_accounts"),
                "website": srcs.get("website"), "crm": srcs.get("crm"),
                "notes": [e.get("info") or e.get("error") or str(e) for e in errs if isinstance(e, dict)]}

    ev_run = led.db.execute("SELECT * FROM runs WHERE id=?", (p.get("run_id"),)).fetchone()
    ev_run = dict(ev_run) if ev_run else None
    latest = led.latest_run()
    latest = dict(latest) if latest else None
    a, b = describe(ev_run), describe(latest)
    unchanged = None
    if a and b and a.get("website") and b.get("website") and a.get("crm") and b.get("crm"):
        unchanged = (a["website"]["fingerprint"] == b["website"]["fingerprint"]
                     and a["crm"]["fingerprint"] == b["crm"]["fingerprint"])
    return {"evidence_run": a, "latest_run": b, "unchanged_since_evidence": unchanged}


def candidates(pl: dict, accounts: dict) -> list:
    """Every other CRM account the engine considered for this facility, with its role."""
    ev = pl.get("evidence") or {}
    out, seen = [], set()
    main_id = (ev.get("crm") or {}).get("account_id")
    # Candidates are checked against the website record, or against the CRM account when there is no website record.
    if ev.get("website"):
        ref, ref_keys = ev["website"], ("name", "street", "city", "state", "zip")
        ref_name = "website"
    else:
        ref, ref_keys = ev.get("crm"), ("name", "billing_street", "billing_city", "billing_state", "billing_zip")
        ref_name = "this CRM account"
    if main_id:
        seen.add(main_id)

    def add(role, a):
        aid = a.get("account_id") if isinstance(a, dict) else a
        if not aid or aid in seen:
            return
        seen.add(aid)
        rec = a if isinstance(a, dict) else accounts.get(aid, {"account_id": aid})
        ident = []
        if ref and "billing_street" in rec:
            for label, rk, ck, how in (("Name", ref_keys[0], "name", "name"), ("Street", ref_keys[1], "billing_street",
                                       "street"), ("City", ref_keys[2], "billing_city", "text"),
                                      ("State", ref_keys[3], "billing_state", "text"),
                                      ("ZIP", ref_keys[4], "billing_zip", "zip")):
                rv, cv = ref.get(rk), rec.get(ck)
                ident.append((label, "not available" if _blank(rv) or _blank(cv) else
                              ("match" if _same(how, rv, cv) else "differs")))
        out.append({"role": role, "account_id": aid, "name": rec.get("name", NA), "identity": ident,
                    "address": " ".join(str(rec.get(k) or "") for k in ("billing_street", "billing_city",
                                                                         "billing_state", "billing_zip")).strip() or NA,
                    "parent": rec.get("parent_name") or rec.get("parent_id") or "none",
                    "phone": rec.get("phone") or NA,
                    "revenue": _money(rec.get("lifetime_revenue")) if "lifetime_revenue" in rec else NA,
                    "ar": _money(rec.get("outstanding_ar")) if "outstanding_ar" in rec else NA,
                    "status": rec.get("status") or NA})

    out_ref = ref_name
    if ev.get("survivor"):
        add("Surviving account (kept)", ev["survivor"])
    if ev.get("current_owner_account"):
        add("Current-owner account (link target)", ev["current_owner_account"])
    for d in ev.get("duplicates") or []:
        add("Same address, handled by a separate duplicate proposal", d)
    for aid in pl.get("account_ids") or []:
        add("Candidate at this address", aid)
    for a in ev.get("alternatives") or []:
        add("Considered, not used (address does not match)", a)
    for c in out:
        c["identity_ref"] = out_ref
    return out


def _describe_ops(pl: dict) -> list:
    cur = pl.get("current") or {}
    lines = []
    for op in pl.get("ops") or []:
        if op.get("type") == "create":
            f = op.get("fields", {})
            lines.append(f"POST /accounts: create '{f.get('name')}' at {f.get('billing_street')}, "
                         f"{f.get('billing_city')} {f.get('billing_state')} {f.get('billing_zip')}, phone "
                         f"{f.get('phone')}, care type {f.get('care_type')}, parent {f.get('parent_id')}, "
                         f"status {f.get('status')}.")
        else:
            parts = []
            for k, v in op.get("fields", {}).items():
                new = "the id returned by the create step" if isinstance(v, str) and v.startswith("$ref:") else repr(v)
                old = cur.get(k) if k in cur else None
                parts.append(f"{k}: {old!r} → {new}" if old is not None else f"{k} → {new}")
            lines.append(f"PATCH /accounts/{op.get('account_id')}: " + "; ".join(parts) + ".")
    if lines:
        lines.append("No other field is sent. lifetime_revenue and outstanding_ar are never written.")
    else:
        lines.append("Nothing. This item has no CRM operation and cannot be approved.")
    return lines


def explain(p: dict, pl: dict, rows: list, cands: list) -> dict:
    ev = pl.get("evidence") or {}
    web, crm = ev.get("website"), ev.get("crm")
    kind = p.get("kind")
    ident = [r for r in rows if r["identity"]]
    matched = [r["label"] for r in ident if r["result"] == "match"]
    differ = [r["label"] for r in ident if r["result"] == "differs"]
    unavailable = [r["label"] for r in ident if r["result"] == "not available"]

    # Why the same facility
    same = []
    if web and crm:
        same.append(f"Engine match basis: {ev.get('basis') or 'not recorded'}.")
        if matched:
            same.append("Identity fields that agree: " + ", ".join(matched) + ".")
        if differ:
            same.append("Identity fields that differ: " + ", ".join(differ)
                        + ". Names are never used alone to decide identity; the address decides.")
        if "Street" in matched and "ZIP" in matched:
            same.append("Street and ZIP agree exactly (after normalizing abbreviations), which is the strongest "
                        "identity evidence available.")
    elif web and not crm:
        same.append("No CRM account was matched. " + (ev.get("basis") or ""))
    elif crm and not web:
        same.append("No website community was matched to this CRM account. " + (ev.get("basis") or ""))
    if kind == "HOLD":
        same.append("Identity is NOT established: " + (pl.get("hold_reason") or ""))

    # Which source supports each change
    support = []
    proposed = pl.get("proposed") or {}
    for r in rows:
        if r["changes"]:
            if r["website"] != NA and _same({"Phone": "phone", "ZIP": "zip", "Street": "street",
                                              "Name": "name"}.get(r["label"], "text"),
                                             r["website"], r["proposed"]):
                support.append(f"{r['label']}: the website page lists {r['website']!s}.")
            else:
                support.append(f"{r['label']}: set to {r['proposed']!r} by the engine's rule for {kind}, "
                               "not copied from a website field.")
    web_for = {"name": "name", "billing_street": "street", "billing_city": "city", "billing_state": "state",
               "billing_zip": "zip", "phone": "phone"}
    for op in pl.get("ops") or []:
        if op.get("type") != "create":
            continue
        from_web, derived = [], []
        for k, v in op.get("fields", {}).items():
            wk = web_for.get(k)
            if web and wk and not _blank(web.get(wk)) and _same({"phone": "phone", "billing_zip": "zip",
                                                                  "billing_street": "street", "name": "name"}
                                                                 .get(k, "text"), web.get(wk), v):
                from_web.append(f"{k} = {v}")
            elif k == "care_type" and web and v and v in N.website_care_types(web.get("care_offerings") or []):
                from_web.append(f"care_type = {v} (website: {', '.join(web.get('care_offerings') or [])})")
            elif k == "parent_id" and v == BELLHAVEN_PARENT:
                derived.append(f"parent_id = {v} (the Bellhaven parent; the website lists this community)")
            elif k == "note":
                derived.append("note = an explanatory text naming the source page")
            else:
                derived.append(f"{k} = {v}")
        if from_web:
            support.append("New account fields copied from the website: " + "; ".join(from_web) + ".")
        if derived:
            support.append("New account fields set by rule (not website fields): " + "; ".join(derived) + ".")
    create_keys = {k for op in pl.get("ops") or [] if op.get("type") == "create" for k in op.get("fields", {})}
    for k, v in proposed.items():
        if k in {r["crm_key"] for r in rows} or isinstance(v, dict) or k == "new_account" or k in create_keys:
            continue
        shown = "the new account's id" if (isinstance(v, str) and (v.startswith("<") or v.startswith("$ref:"))) \
            else repr(v)
        support.append(f"{k}: set to {shown} by the engine's rule for {kind} (derived, not a website field).")
    if web and web.get("source_url"):
        support.append(f"Source page: {web['source_url']} (retrieved {web.get('retrieved_at') or NA}).")
    if not support:
        support.append("No change is proposed.")

    # What is still missing
    missing = []
    if web and not crm:
        missing.append("No CRM account matched this community, so its fields cannot be compared with a CRM record. "
                       + ("Check the competing candidates below." if cands else
                          "No other CRM account was found at this address or ZIP and street."))
    elif crm and not web:
        missing.append("No website community matched this CRM account, so nothing on the website supports or "
                       "contradicts its values.")
    elif unavailable:
        missing.append("Identity fields not available from one source: " + ", ".join(unavailable) + ".")
    missing.append("The website does not publish account status, revenue, AR or CRM parent IDs; those come "
                   "from the CRM only and are re-read live before any write.")
    if crm:
        missing.append("The CRM account record has no administrator field; the website administrator was not "
                       "cross-checked against CRM contacts.")
    if any(r["label"] == "Phone" and r["changes"] for r in rows):
        missing.append("The phone number is supported by one source (the website). No call or second source "
                       "confirms which number is in use.")
    if cands:
        missing.append(f"{len(cands)} other CRM account(s) relate to this facility (see Competing candidates).")
    if kind in ("CRM_ONLY",):
        missing.append("Absence from the website is the only evidence; nothing confirms the facility closed or "
                       "changed owner.")
    if kind == "CHOW" and len(pl.get("ops") or []) == 1:
        missing.append("No website or About-page statement confirms the change of ownership.")
    for w in pl.get("warnings") or []:
        missing.append(w)

    return {"summary": KIND_SUMMARY.get(kind, ""), "same": same, "support": support, "missing": missing,
            "changes": _describe_ops(pl)}


def build(led, p: dict, data_dir: str) -> dict:
    pl = p["payload"]
    ev = pl.get("evidence") or {}
    rows = compare(ev.get("website"), ev.get("crm"), pl.get("proposed") if p.get("kind") != "WEBSITE_ONLY" else None)
    cands = candidates(pl, _snapshot_accounts(p.get("run_id"), data_dir))
    for c in cands:  # link each candidate to the open proposal that handles it, if any (read-only lookup)
        row = led.db.execute("SELECT id, kind, status FROM proposals WHERE subject_key IN (?, ?) AND status NOT IN "
                             "('superseded', 'resolved') ORDER BY id DESC LIMIT 1",
                             (f"dup:{c['account_id']}", f"acct:{c['account_id']}:fields")).fetchone()
        c["proposal"] = dict(row) if row else None
    latest = led.latest_run()
    fresh = record_freshness(ev, latest["id"] if latest else None, data_dir)
    return {"rows": rows, "candidates": cands, "sources": source_status(led, p), "fresh": fresh,
            "explain": explain(p, pl, rows, cands), "website": ev.get("website"), "crm": ev.get("crm")}
