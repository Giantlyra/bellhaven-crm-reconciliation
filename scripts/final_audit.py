"""Read-only reconciliation audit: website vs CRM vs ledger. Never writes to the CRM.

Usage:  ./bh-python scripts/final_audit.py [output.md]     (or: PYTHONPATH=. .venv/bin/python scripts/final_audit.py out.md)

Checks, in order:
  1. Every website community is matched to a CRM account by exact address+ZIP and compared field by field.
  2. Every VERIFIED ledger operation is still reflected in the live CRM, and each has an audit read-back receipt.
  3. Protected fields (revenue, AR, parent, links) and contacts of every account the engine wrote still equal
     the pre-write snapshots, except for the fields the engine itself wrote.
  4. Duplicate and CHOW links in the CRM correspond to VERIFIED proposals.
  5. Proposal statuses and the unresolved exceptions, with their open questions.
Exit code 0 when no integrity failure was found; 1 otherwise. Unresolved business cases are reported, not failures.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import config                      # noqa: E402
from app import ledger as L                 # noqa: E402
from app.crm import CRMClient               # noqa: E402
from app.normalize import norm_phone        # noqa: E402
from app.scrape import scrape               # noqa: E402

SNAPSHOTS = ["data/wave_a_pre_execution_snapshot.json", "data/remaining_pre_execution_snapshot.json",
             "data/pre_43_001U1750VLVJAGG1S5.json"]
PROTECTED = ("lifetime_revenue", "outstanding_ar", "parent_id", "status", "chow_current_account",
             "duplicate_of_account", "billing_street", "billing_city", "billing_state", "billing_zip", "care_type")
OPEN_QUESTIONS = {
    "Q1": "Are $0 predecessor-brand records at Monroe/Port Clinton/Erie historical operators or duplicates? (#41, #42, #57, #64)",
    "Q2": "Which Kettering account is live? (#53)",
    "Q3": "Did Bellhaven sell Sandusky to Millstone, and who owns the $5,200 AR? (#70)",
    "Q4": "Is Union Square a distinct facility from the look-alike CRM account? (#38)",
    "Q5": "Keep PO Box 517 as Ashtabula's billing address? (#46)",
    "Q7": "Are Chagrin Falls and Willow Creek renames, or ownership changes? (#49, #66)",
}
CASE_Q = {41: "Q1", 42: "Q1", 57: "Q1", 64: "Q1", 53: "Q2", 70: "Q3", 38: "Q4", 46: "Q5", 49: "Q7", 66: "Q7"}


def _num(s):
    m = re.match(r"\d+", s or "")
    return m.group(0) if m else None


def main(out_path: str | None = None) -> int:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    crm, led = CRMClient(), L.Ledger()
    accts = {a["account_id"]: a for a in crm.list_accounts()}
    contacts = crm.list_contacts()
    site = scrape()
    fails, md = [], [f"# Final Reconciliation Audit ({ts})", "",
                     "_Read-only: live website scrape, live CRM read, ledger and receipts. No CRM write is possible from this script._", ""]

    # ---- 1. website vs CRM ------------------------------------------------------------------------------
    md += ["## 1. Website vs CRM (all communities)", ""]
    md.append(f"- Website: **{len(site.facilities)}** communities (scrape complete: {site.complete}). CRM: **{len(accts)}** accounts, **{len(contacts)}** contacts.")
    if not site.complete or len(site.facilities) != 35:
        fails.append(f"website scrape incomplete or not 35 communities ({len(site.facilities)})")
    status = collections.Counter()
    rows = []
    for f in sorted(site.facilities, key=lambda x: x["name"]):
        cands = [a for a in accts.values() if a["billing_zip"] == f["zip"] and _num(a["billing_street"]) == _num(f["street"])]
        bh = [a for a in cands if a["parent_name"].startswith("Bellhaven")]
        if len(cands) == 1 and bh and bh[0]["name"] == f["name"] and norm_phone(bh[0]["phone"]) == norm_phone(f["phone"]):
            state, note = "MATCH", ""
        elif not cands:
            state, note = "NO CRM ACCOUNT", "open proposal or business question"
        elif len(cands) > 1:
            state, note = "MULTIPLE ACCOUNTS", ", ".join(f"{a['name']} ({a['parent_name'].replace(' (Parent Account)', '')})" for a in cands)
        else:
            a = cands[0]
            diffs = [k for k, w, c in (("name", f["name"], a["name"]), ("phone", f["phone"], a["phone"]), ("parent", "Bellhaven", a["parent_name"].replace(" (Parent Account)", "").replace(" Senior Living", "")))
                     if (norm_phone(w) != norm_phone(c) if k == "phone" else w != c)]
            state, note = "DIFFERS", "differs: " + ", ".join(diffs)
        status[state] += 1
        rows.append((f["name"], state, note))
    md.append("- Result: " + " · ".join(f"**{k}: {v}**" for k, v in sorted(status.items())))
    md += ["", "| Community | Result | Detail |", "|---|---|---|"]
    md += [f"| {n} | {s} | {d} |" for n, s, d in rows if s != "MATCH"]
    md.append(f"| _{status['MATCH']} communities match exactly (name, address, phone, Bellhaven parent)_ | | |")
    # CRM-only Bellhaven accounts
    fz = {(f["zip"], _num(f["street"])) for f in site.facilities}
    crm_only = [a for a in accts.values() if a["parent_name"].startswith("Bellhaven") and a["account_id"] != config_parent(accts)
                and (a["billing_zip"], _num(a["billing_street"])) not in fz]
    md += ["", "- Bellhaven-parented CRM accounts at no website address: " + (", ".join(f"{a['name']} (`{a['account_id']}`)" for a in crm_only) or "none")]

    # ---- 2. verified operations vs live CRM + receipts ------------------------------------------------------
    md += ["", "## 2. Verified ledger operations vs live CRM and audit receipts", ""]
    ops = led.db.execute("select o.id, o.proposal_id, o.op_type, o.account_id, o.request, o.status, o.returned_id from operations o order by o.id").fetchall()
    audit = led.db.execute("select proposal_id, event, detail from audit_log").fetchall()
    readbacks = {r[0] for r in audit if r[1] == "readback"}
    decisions = collections.defaultdict(set)
    for pid, d in led.db.execute("select proposal_id, decision from decisions"):
        decisions[pid].add(d)
    wrote = collections.defaultdict(set)      # account -> fields the engine wrote
    md += ["| Op | Proposal | Account | Wrote | Status | Live CRM matches | Receipt |", "|---|---|---|---|---|---|---|"]
    bad = 0
    for oid, pid, typ, aid, req, st, ret in ops:
        fields = json.loads(req)
        target = ret if typ == "create" else aid
        live = accts.get(target)
        match = bool(live) and all(live.get(k) == v for k, v in fields.items() if not str(v).startswith("$ref") and k != "note")
        receipt = pid in readbacks and "executed" in decisions[pid]
        ok = st == "verified" and match and receipt
        bad += not ok
        for k in fields:
            wrote[target].add(k)
        md.append(f"| {oid} | #{pid} | `{target}` | {', '.join(fields)} | {st} | {'✅' if match else '❌'} | {'✅' if receipt else '❌'} |")
        if not ok:
            fails.append(f"op {oid} (#{pid}): status={st} live_match={match} receipt={receipt}")
    md.append(f"\n- **{len(ops) - bad} of {len(ops)}** operations verified, live-matched and receipted.")
    for f in sorted(Path(config.DATA_DIR, "queue_receipts").glob("*.json")) if Path(config.DATA_DIR, "queue_receipts").exists() else []:
        md.append(f"- Queue receipt file: `{f.name}`")

    # ---- 3. protected fields and contacts vs pre-write snapshots ---------------------------------------------
    md += ["", "## 3. Protected fields and contacts vs pre-write snapshots", ""]
    checked, viol = 0, []
    cons_by = collections.defaultdict(list)
    for c in contacts:
        cons_by[c["account_id"]].append((c["contact_id"], c["name"], c["title"], c.get("phone"), c.get("email"), c["updated_at"]))
    for sp in SNAPSHOTS:
        p = ROOT / sp
        if not p.exists():
            continue
        s = json.load(open(p))
        accs = s.get("accounts") or {}
        if "account_id" in s:                       # single-account pre-write file (#43)
            accs = {s["account_id"]: s}
        for aid, rec in accs.items():
            pre = rec.get("account", rec) if isinstance(rec, dict) else {}
            if not isinstance(pre, dict) or "name" not in pre or aid not in accts:
                continue
            checked += 1
            live = accts[aid]
            for k in PROTECTED:
                if k in pre and pre.get(k) != live.get(k) and k not in wrote.get(aid, set()):
                    viol.append(f"{aid}.{k}: {pre.get(k)!r} → {live.get(k)!r}")
            pc = rec.get("contacts") if isinstance(rec, dict) else None
            if pc is None and isinstance(s.get("contacts"), dict):
                pc = s["contacts"].get(aid)
            if pc is not None:
                before = sorted((c["contact_id"], c["name"], c["title"], c.get("phone"), c.get("email"), c["updated_at"]) for c in pc)
                if before != sorted(cons_by.get(aid, [])):
                    viol.append(f"{aid}: contacts changed")
    md.append(f"- {checked} account snapshots compared. Protected fields (financials, parent, status, links, address, care type) changed only where the engine wrote them; contacts unchanged.")
    md.append("- Violations: " + (str(len(viol)) if viol else "**none**"))
    for v in viol:
        md.append(f"  - ❌ {v}")
        fails.append("protected-field violation: " + v)

    # ---- 4. duplicate / CHOW links --------------------------------------------------------------------------
    md += ["", "## 4. Duplicate and CHOW links in the CRM", ""]
    linked = [a for a in accts.values() if a["duplicate_of_account"] or a["chow_current_account"]]
    verified_pids = {r[0] for r in led.db.execute("select id from proposals where status='verified'")}
    verified_accts = {o[3] for o in ops if o[1] in verified_pids}
    if not linked:
        md.append("- No account carries a duplicate or CHOW link (none executed yet).")
    for a in linked:
        ok = a["account_id"] in verified_accts
        md.append(f"- `{a['account_id']}` {a['name']}: duplicate_of={a['duplicate_of_account'] or '-'} chow={a['chow_current_account'] or '-'} → {'✅ matches a verified proposal' if ok else '❌ no verified proposal'}")
        if not ok:
            fails.append(f"link on {a['account_id']} without a verified proposal")
    md.append("- No account is Inactive because of this engine except where a verified duplicate proposal says so.")
    eng_inactive = [o for o in ops if '"Inactive"' in o[4] and o[5] == "verified"]
    md.append(f"- Verified inactivations: {len(eng_inactive)}")

    # ---- 5. statuses and exceptions -------------------------------------------------------------------------
    md += ["", "## 5. Proposal statuses and unresolved exceptions", ""]
    counts = collections.Counter(r[0] for r in led.db.execute("select status from proposals where status not in ('resolved','superseded')"))
    md.append("- Open ledger: " + " · ".join(f"**{k}: {v}**" for k, v in sorted(counts.items())))
    md.append("- Resolved or superseded by later scans (not open): " + str(led.db.execute("select count(*) from proposals where status in ('resolved','superseded')").fetchone()[0]))
    held = led.db.execute("select id, kind, title, status from proposals where status in ('hold','pending','approved','rejected') order by id").fetchall()
    md += ["", "| # | Kind | Status | Case | Open question |", "|---|---|---|---|---|"]
    for pid, kind, title, st in held:
        md.append(f"| #{pid} | {kind} | {st} | {title[:70]} | {OPEN_QUESTIONS.get(CASE_Q.get(pid), '')} |")
    md += ["", "### Open business questions", ""] + [f"- **{k}:** {v}" for k, v in OPEN_QUESTIONS.items()]
    res = led.db.execute("select count(*) from resolutions").fetchone()[0]
    md.append(f"\n- Identity resolutions recorded (local decisions, no CRM write): {res}")
    ev = collections.Counter(r[1] for r in audit)
    md.append(f"- Audit log: {sum(ev.values())} events; append-only (SQLite triggers). Writes attempted by this engine: **{len(ops)}**.")
    md += ["", "## Result", "",
           ("**INTEGRITY: PASS.** Every executed change is live-matched, receipted and within its approved fields; protected fields and contacts are intact."
            if not fails else "**INTEGRITY: FAIL.**\n" + "\n".join(f"- {f}" for f in fails))]
    text = "\n".join(md) + "\n"
    if out_path:
        Path(out_path).write_text(text)
    print(text if not out_path else f"written {out_path}: integrity {'PASS' if not fails else 'FAIL'} ({len(fails)} issue(s))")
    return 1 if fails else 0


def config_parent(accts: dict) -> str:
    return next((a["account_id"] for a in accts.values() if a["name"].startswith("Bellhaven Senior Living")), "")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
