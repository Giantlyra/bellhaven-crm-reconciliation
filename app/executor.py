"""The ONLY code path that writes to the CRM. Kept separate from policy so the write path is auditable.

Decision and execution are separate steps:

  approve()  records a human decision. It never writes.
  preview()  READ-ONLY. Re-reads every touched account, checks drift since the proposal, re-runs the risk
             policy on the fresh data, checks for an existing CHOW successor, detects already-applied
             state, and returns the exact HTTP requests plus a plan token bound to that fresh state.
  execute()  writes, only if ALL of these hold:
               - live writes are enabled for this process (CRM_WRITES_ENABLED=1; default is dry-run)
               - status is approved (or failed -> resume), and the approval was for this exact fingerprint
               - the operator typed the confirmation phrase "APPLY <id>"
               - a fresh preview produces the same plan token the operator reviewed (nothing changed since)
             Each op's outcome is persisted before the next; creates are never blindly retried; every
             touched account is read back and compared before the proposal is marked verified.
"""
from __future__ import annotations

import hashlib
import json
import threading

from . import config
from . import ledger as L
from .policy import check_ops, successor_conflicts


class ExecutionError(Exception):
    pass


# One execution at a time in this process. A proposal found in 'applying' while this lock is free was interrupted
# (server killed mid-write) and may be resumed through a fresh preview + typed confirmation; it is never resumed while
# another execution is running.
_EXEC_LOCK = threading.Lock()


class WritesDisabled(ExecutionError):
    pass


def confirmation_phrase(pid: int) -> str:
    return f"APPLY {pid}"


def batch_phrase(n: int) -> str:
    return f"APPLY BATCH OF {n}"


def normalize_phrase(text) -> str:
    """Collapse any run of whitespace (incl. non-breaking/Unicode spaces) to one space and trim. Words and case must
    still match exactly; this only stops invisible spacing differences from failing a deliberate confirmation."""
    return " ".join((text or "").split())


def phrase_mismatch(expected: str, got, what: str = "Confirmation phrase") -> str:
    return f"{what} mismatch: type exactly '{expected}' (received {(got or '')!r})"


def _resolve(fields: dict, refs: dict) -> dict:
    out = {}
    for k, v in fields.items():
        if isinstance(v, str) and v.startswith("$ref:"):
            ref = v[5:]
            if ref not in refs:
                raise ExecutionError(f"Unresolved reference {v}")
            v = refs[ref]
        out[k] = v
    return out


def _find_existing_create(crm, fields: dict):
    """Uncertain-create recovery: an account this candidate already created for the same facility."""
    try:
        hits = crm.list_accounts(q=fields.get("name", ""), zip=fields.get("billing_zip", ""))
    except Exception:  # noqa: BLE001
        return None
    found = [h["account_id"] for h in hits if h.get("created_by_candidate") and h.get("name") == fields.get("name")
             and h.get("parent_id") == fields.get("parent_id")]
    return found[0] if len(found) == 1 else None


def _done_ops(ledger, pid: int, n: int) -> dict:
    out = {}
    for i in range(n):
        rec = ledger.op(pid, i)
        if rec and rec["status"] in ("succeeded", "verified"):
            out[i] = rec
    return out


# ------------------------------------------------------------------ decisions (no writes)

def approve(ledger, pid: int, note: str = "", actor: str = "local-reviewer"):
    p = ledger.get_proposal(pid)
    if p is None:
        raise ExecutionError("No such proposal")
    if not p["actionable"]:
        raise ExecutionError("HOLD items have no executable operations and cannot be approved")
    if p["status"] != L.PENDING:
        raise ExecutionError(f"Only pending proposals can be approved (this one is '{p['status']}')")
    ledger.decide(pid, "approved", note, actor)
    ledger.set_status(pid, L.APPROVED)


def reject(ledger, pid: int, note: str = "", actor: str = "local-reviewer"):
    p = ledger.get_proposal(pid)
    if p is None or p["status"] not in (L.PENDING, L.HOLD, L.APPROVED, L.CONFLICT):
        raise ExecutionError("Only pending / hold / approved / conflict proposals can be rejected")
    ledger.decide(pid, "rejected", note, actor)
    ledger.set_status(pid, L.REJECTED)


def hold(ledger, pid: int, note: str = "", actor: str = "local-reviewer"):
    p = ledger.get_proposal(pid)
    if p is None or p["status"] not in (L.PENDING, L.APPROVED):
        raise ExecutionError("Only pending / approved proposals can be put on hold")
    ledger.decide(pid, "hold", note, actor)
    ledger.set_status(pid, L.HOLD)


def release(ledger, pid: int, note: str = "", actor: str = "local-reviewer"):
    p = ledger.get_proposal(pid)
    if p is None or p["status"] != L.HOLD:
        raise ExecutionError("Only held proposals can be released")
    if not p["actionable"]:
        raise ExecutionError("This HOLD has no executable operations; resolve identity and re-scan instead")
    ledger.decide(pid, "released", note, actor)
    ledger.set_status(pid, L.PENDING)


def annotate(ledger, pid: int, note: str, actor: str = "local-reviewer"):
    if not ledger.get_proposal(pid):
        raise ExecutionError("No such proposal")
    ledger.decide(pid, "note", note, actor)


# ------------------------------------------------------------------ preview (read-only)

def preview(crm, ledger, pid: int) -> dict:
    p = ledger.get_proposal(pid)
    if p is None:
        raise ExecutionError("No such proposal")
    pl = p["payload"]
    ops = pl["ops"]
    done = _done_ops(ledger, pid, len(ops))
    out = {"pid": pid, "fingerprint": p["fingerprint"], "problems": [], "notes": [], "requests": [],
           "fresh": {}, "noop": False, "recovered": {}, "done": sorted(done)}
    if not ops:
        out["problems"].append("No executable operations (HOLD item)")
        out["token"] = ""
        return out

    # ---- fresh reads of every account in the baseline or touched by an op
    ids = list(pl.get("baseline", {}))
    ids += [op["account_id"] for op in ops if op["type"] == "update" and op["account_id"] not in ids]
    for aid in ids:
        try:
            out["fresh"][aid] = crm.get_account(aid)
        except Exception as e:  # noqa: BLE001
            out["problems"].append(f"Could not re-read {aid}: {type(e).__name__}: {e}")
    if out["problems"]:
        out["token"] = ""
        return out
    fresh = out["fresh"]

    # ---- drift since proposal (fields we already wrote in a partial attempt are expected to differ)
    written = {(op["account_id"], k) for i, op in enumerate(ops) if i in done and op["type"] == "update"
               for k in op["fields"]}
    targets = {(op["account_id"], k): v for i, op in enumerate(ops) if i not in done and op["type"] == "update"
               for k, v in op["fields"].items()}
    for aid, base in pl.get("baseline", {}).items():
        ours = None
        for k, v in base.items():
            if (aid, k) in written or fresh[aid].get(k) == v:
                continue
            if (aid, k) in targets and fresh[aid].get(k) == targets[(aid, k)]:
                out["notes"].append(f"{aid}.{k} already equals the target value (changed outside this proposal).")
                continue
            # A sibling proposal on the same account (e.g. Lima parent vs Lima phone) that THIS engine wrote and
            # read back is explained drift, not unexplained drift. Policy is still re-run on the fresh values below.
            ours = ours if ours is not None else ledger.verified_writes(aid, exclude_pid=pid)
            if k in ours and fresh[aid].get(k) == ours[k][0]:
                out["notes"].append(f"{aid}.{k} changed since proposal by verified proposal #{ours[k][1]} "
                                    f"({v!r} → {fresh[aid].get(k)!r}); policy re-checked on the new value.")
                continue
            out["problems"].append(f"Drift: {aid}.{k} was {v!r} at proposal time, now {fresh[aid].get(k)!r}")

    # ---- policy on fresh data
    pending_ops = [op for i, op in enumerate(ops) if i not in done]
    out["problems"] += check_ops(pending_ops, fresh)

    # ---- creates: uncertain-create recovery, then duplicate-successor protection
    refs = {ops[i]["ref"]: rec["returned_id"] for i, rec in done.items() if ops[i]["type"] == "create"}
    for i, op in enumerate(ops):
        if op["type"] != "create" or i in done:
            continue
        prev = ledger.op(pid, i)
        if prev and prev["status"] in ("uncertain", "failed", "started"):
            rid = _find_existing_create(crm, op["fields"])
            if rid:
                out["recovered"][i] = rid
                refs[op["ref"]] = rid
                out["notes"].append(f"Op {i}: earlier create outcome was uncertain; found account {rid} created by "
                                    "this candidate — it will be adopted, not re-created.")
            else:
                out["problems"].append(f"Op {i}: earlier create outcome uncertain and no matching account found; "
                                       "inspect the CRM manually before retrying.")
                continue
        try:
            cands = crm.list_accounts(zip=op["fields"].get("billing_zip", ""),
                                      parent_id=op["fields"].get("parent_id", ""))
        except Exception as e:  # noqa: BLE001
            out["problems"].append(f"Could not search for an existing successor: {e}")
            continue
        out["problems"] += successor_conflicts(op["fields"], cands, exclude=set(ids) | set(refs.values()))

    # ---- exact requests + already-applied detection
    noop_all = True
    for i, op in enumerate(ops):
        if i in done:
            out["requests"].append({"index": i, "state": "done", "method": "—",
                                    "path": f"(completed earlier: {done[i].get('returned_id') or op.get('account_id')})",
                                    "body": op["fields"]})
            continue
        if op["type"] == "create":
            noop_all = False
            out["requests"].append({"index": i, "state": "recovered" if i in out["recovered"] else "will_run",
                                    "method": "POST", "path": "/accounts", "body": op["fields"]})
            continue
        acct = fresh.get(op["account_id"], {})
        body = {k: (f"<id from op {[j for j, o in enumerate(ops) if o.get('ref') == v[5:]][0]}>"
                    if isinstance(v, str) and v.startswith("$ref:") else v) for k, v in op["fields"].items()}
        already = all(not (isinstance(v, str) and v.startswith("$ref:")) and acct.get(k) == v
                      for k, v in op["fields"].items())
        noop_all &= already
        out["requests"].append({"index": i, "state": "already_applied" if already else "will_run", "method": "PATCH",
                                "path": f"/accounts/{op['account_id']}", "body": body,
                                "before": {k: acct.get(k) for k in op["fields"]}})
    if noop_all and not done:
        out["noop"] = True
        out["notes"].append("CRM already holds every target value: nothing will be written.")

    digest = {"fp": p["fingerprint"], "fresh": fresh, "done": sorted(done), "recovered": out["recovered"]}
    out["token"] = hashlib.sha256(json.dumps(digest, sort_keys=True, default=str).encode()).hexdigest()[:24]
    return out


# ------------------------------------------------------------------ execute (writes)

def _authorize(ledger, pid: int, confirmation: str, writes_enabled):
    p = ledger.get_proposal(pid)
    if p is None:
        raise ExecutionError("No such proposal")
    if p["status"] not in (L.APPROVED, L.FAILED, L.APPLYING):
        raise ExecutionError(f"Proposal {pid} is '{p['status']}', not approved — refusing to write")
    if not p["actionable"]:
        raise ExecutionError("HOLD item: nothing executable")
    appr = ledger.last_decision(pid, "approved")
    if not appr or appr.get("fingerprint") != p["fingerprint"]:
        raise ExecutionError("No approval recorded for this exact proposal version")
    if normalize_phrase(confirmation) != confirmation_phrase(pid):
        raise ExecutionError(phrase_mismatch(confirmation_phrase(pid), confirmation))
    enabled = config.WRITES_ENABLED if writes_enabled is None else writes_enabled
    if not enabled:
        raise WritesDisabled("Live CRM writes are disabled (dry-run mode). Restart the server with "
                             "CRM_WRITES_ENABLED=1 to allow approved, confirmed writes.")
    return p


def execute(crm, ledger, pid: int, *, confirmation: str, plan_token: str, writes_enabled=None,
            actor: str = "local-reviewer") -> dict:
    if not _EXEC_LOCK.acquire(blocking=False):
        ledger.log("execute_refused", pid, reason="another execution is in progress", actor=actor)
        raise ExecutionError("Another execution is in progress in this server; wait for it to finish.")
    try:
        return _execute(crm, ledger, pid, confirmation=confirmation, plan_token=plan_token,
                        writes_enabled=writes_enabled, actor=actor)
    finally:
        _EXEC_LOCK.release()


def _execute(crm, ledger, pid: int, *, confirmation: str, plan_token: str, writes_enabled, actor: str) -> dict:
    try:
        p = _authorize(ledger, pid, confirmation, writes_enabled)
    except ExecutionError as e:
        ledger.log("execute_refused", pid, reason=str(e), actor=actor)
        raise
    pv = preview(crm, ledger, pid)
    if not plan_token or pv["token"] != plan_token:
        ledger.log("execute_refused", pid, reason="plan token mismatch: CRM state changed since preview")
        raise ExecutionError("CRM state changed since you reviewed the preview. Review the new preview and confirm "
                             "again.")
    if pv["problems"]:
        ledger.set_status(pid, L.CONFLICT, "Blocked at pre-write revalidation: " + "; ".join(pv["problems"]))
        return {"status": L.CONFLICT, "problems": pv["problems"]}
    if pv["noop"]:
        ledger.set_status(pid, L.RESOLVED, None, reason="CRM already in desired state at execution time; no write")
        return {"status": L.RESOLVED, "noop": True}

    ops = p["payload"]["ops"]
    done = _done_ops(ledger, pid, len(ops))
    ledger.decide(pid, "executed" if not done else "resumed", f"confirmed '{confirmation}', token {plan_token}", actor)
    ledger.set_status(pid, L.APPLYING)
    refs = {ops[i]["ref"]: rec["returned_id"] for i, rec in done.items() if ops[i]["type"] == "create"}
    try:
        for i, op in enumerate(ops):
            if i in done:
                continue
            if op["type"] == "create":
                if i in pv["recovered"]:
                    rid = pv["recovered"][i]
                    ledger.record_op(pid, i, "create", rid, op["fields"], "succeeded",
                                     response={"recovered_existing": rid}, returned_id=rid)
                    refs[op["ref"]] = rid
                    continue
                op_id = ledger.record_op(pid, i, "create", None, op["fields"], "started")
                try:
                    resp = crm.create_account(op["fields"])
                except Exception as e:  # outcome unknown: do NOT blindly retry
                    ledger.update_op(op_id, status="uncertain", error=str(e))
                    raise ExecutionError(f"Create failed/uncertain: {e}") from e
                new_id = (resp or {}).get("account_id")
                if not new_id:
                    ledger.update_op(op_id, status="uncertain", response=resp, error="no account_id in response")
                    raise ExecutionError("Create returned no account_id")
                ledger.update_op(op_id, status="succeeded", response=resp, returned_id=new_id)
                refs[op["ref"]] = new_id
            else:
                fields = _resolve(op["fields"], refs)
                op_id = ledger.record_op(pid, i, "update", op["account_id"], fields, "started")
                try:
                    resp = crm.update_account(op["account_id"], fields)
                except Exception as e:  # noqa: BLE001
                    ledger.update_op(op_id, status="failed", error=str(e))
                    raise ExecutionError(f"Update of {op['account_id']} failed: {e}") from e
                ledger.update_op(op_id, status="succeeded", response=resp)

        # ---- read-back verification: never report success without it
        problems, receipts = [], []
        for i, op in enumerate(ops):
            aid = refs[op["ref"]] if op["type"] == "create" else op["account_id"]
            expect = op["fields"] if op["type"] == "create" else _resolve(op["fields"], refs)
            got = crm.get_account(aid)
            mism = [f"{aid}.{k}: expected {v!r}, CRM has {got.get(k)!r}" for k, v in expect.items() if got.get(k) != v]
            problems += mism
            receipts.append({"account_id": aid, "fields": {k: got.get(k) for k in expect}})
            rec = ledger.op(pid, i)
            if rec:
                ledger.update_op(rec["id"], status="verified" if not mism else "verify_failed")
        ledger.log("readback", pid, receipts=receipts, ok=not problems)
        if problems:
            ledger.set_status(pid, L.FAILED, "Readback mismatch: " + "; ".join(problems))
            return {"status": L.FAILED, "problems": problems}
        ledger.set_status(pid, L.VERIFIED)
        return {"status": L.VERIFIED, "refs": refs, "receipts": receipts}
    except ExecutionError as e:
        ledger.set_status(pid, L.FAILED, str(e))
        return {"status": L.FAILED, "error": str(e)}
    except Exception as e:  # noqa: BLE001  (network errors during reads etc.)
        ledger.set_status(pid, L.FAILED, f"{type(e).__name__}: {e}")
        return {"status": L.FAILED, "error": str(e)}


def proposal_accounts(p: dict) -> set:
    """Every account a proposal reads as baseline or writes."""
    pl = p["payload"]
    return set(pl.get("baseline", {})) | proposal_writes(p)


def proposal_writes(p: dict) -> set:
    return {op["account_id"] for op in p["payload"].get("ops", []) if op["type"] == "update"}


def batch_overlaps(ledger, pids: list) -> list:
    """Messages for pairs in one batch where one item WRITES an account the other reads or writes. All batch plan
    tokens are taken before the first write, so the later item would always fail its token check mid-batch.
    Two items that merely read the same account (e.g. two duplicates of one survivor) do not conflict."""
    out, prior = [], []
    for pid in pids:
        p = ledger.get_proposal(pid)
        if not p:
            continue
        reads, writes = proposal_accounts(p), proposal_writes(p)
        for qid, q_reads, q_writes in prior:
            shared = sorted((writes & q_reads) | (q_writes & reads))
            if shared:
                out.append(f"#{qid} and #{pid} both touch {shared[0]} (one of them writes it)")
        prior.append((pid, reads, writes))
    return out


def execute_batch(crm, ledger, items: list, *, confirmation: str, writes_enabled=None,
                  actor: str = "local-reviewer") -> list:
    """items: [(pid, plan_token), ...] the operator reviewed together. Each is still authorized, previewed,
    executed and audited individually; CHOW proposals are excluded (always one at a time). Stops at the first
    item that does not verify."""
    if normalize_phrase(confirmation) != batch_phrase(len(items)):
        raise ExecutionError(phrase_mismatch(batch_phrase(len(items)), confirmation, "Batch confirmation"))
    for pid, _ in items:
        p = ledger.get_proposal(pid)
        if p is None or p["kind"] == "CHOW":
            raise ExecutionError(f"Proposal {pid} cannot be batch-executed (CHOW runs individually)")
    overlap = batch_overlaps(ledger, [pid for pid, _ in items])
    if overlap:
        raise ExecutionError("Batch refused: " + "; ".join(overlap) + ". Run these in separate batches so the "
                             "second one is previewed against the CRM after the first is verified.")
    ledger.log("batch_started", None, pids=[pid for pid, _ in items], actor=actor)
    results = []
    for pid, token in items:
        try:
            r = execute(crm, ledger, pid, confirmation=confirmation_phrase(pid), plan_token=token,
                        writes_enabled=writes_enabled, actor=actor)
        except ExecutionError as e:
            r = {"status": "refused", "error": str(e)}
        results.append({"pid": pid, **r})
        if r["status"] not in (L.VERIFIED, L.RESOLVED):
            break
    ledger.log("batch_finished", None, results=[{"pid": r["pid"], "status": r["status"]} for r in results])
    return results
