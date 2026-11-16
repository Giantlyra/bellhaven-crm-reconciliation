"""One command line for the whole workflow. None of these commands writes to the CRM.

  ./bh scan                 live read-only scan: website + every CRM page -> proposals (pending review)
  ./bh scan --offline FILE  same, from a saved snapshot (no network; clearly labelled stale)
  ./bh status               last run, proposal counts, write count, whether live writes are enabled
  ./bh list [--status S]    proposal queue
  ./bh show ID              one proposal with evidence and exact operations
  ./bh test                 run the mocked test-suite and save a report for the Test tab
  ./bh serve [--port N]     start the review workspace (the ONLY place a write can be confirmed)
  ./bh resolve HOLD_ID distinct --note WHY             identity HOLD: the look-alike CRM account is another facility
  ./bh resolve HOLD_ID survivor ACCOUNT_ID --note WHY  same-address HOLD: keep this account, the others are duplicates
  ./bh resolve HOLD_ID revoke --note WHY               withdraw an earlier resolution
        A resolution is an operator decision recorded in the ledger. It writes nothing to the CRM: the next scan
        turns it into ordinary pending proposals that still need approve -> live preview -> typed confirmation.
"""
from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from . import config
from . import ledger as L


def _ledger():
    return L.Ledger()


def cmd_scan(a):
    from .pipeline import offline_source, run_pipeline
    led = _ledger()
    if a.offline:
        scrape_fn, crm, prov = offline_source(a.offline)
        print(f"Offline scan from {a.offline} — no network calls.")
    else:
        from .crm import CRMClient
        from .scrape import scrape as scrape_fn
        crm, prov = CRMClient(), "live"
        print("Live read-only scan: website + CRM (GET requests only). This takes ~30–60 seconds…", flush=True)
    res = run_pipeline(crm, led, scrape_fn, provenance=prov, save_snapshot=True)
    print(json.dumps({k: v for k, v in res.items() if k != "errors"}, indent=2))
    for e in res.get("errors", []):
        print(f"  [{e.get('stage')}] {e.get('error') or e.get('info')} {e.get('url', '')}")
    print("\nNothing was written to the CRM. Review proposals with:  ./bh serve")
    return 0 if res.get("status") == "completed" else 1


def cmd_status(a):
    led = _ledger()
    run = led.latest_run()
    print(f"Ledger: {led.path}")
    print(f"Live CRM writes enabled in THIS shell: {'YES' if config.WRITES_ENABLED else 'no (dry-run)'}")
    if run:
        print(f"Last run #{run['id']} {run['status']} at {run['finished_at']}: "
              f"{run['website_facilities']} website facilities, {run['crm_accounts']} CRM accounts")
        for s in led.sources(run["id"]):
            print(f"  source {s['source']:<8} {s['records']:>4} records  sha256:{s['fingerprint'][:16]}…  {s['provenance']}")
    print("Proposals:", json.dumps(led.counts()))
    print(f"CRM write calls ever attempted by this engine: {led.write_count()}")
    for r in led.receipts():
        print(f"Legacy verified write: {r['account_id']}.{r['field']} = {r['value']} at {r['verified_at']}")
    return 0


def cmd_list(a):
    led = _ledger()
    rows = led.proposals(status=a.status or None)
    for p in rows:
        print(f"#{p['id']:<4} {p['status']:<10} {p['risk']:<6} {p['kind']:<13} {p['title'][:90]}")
    print(f"{len(rows)} proposals")
    return 0


def cmd_show(a):
    p = _ledger().get_proposal(a.id)
    if not p:
        print("No such proposal")
        return 1
    pl = p["payload"]
    print(f"#{p['id']} [{p['status']}] {p['kind']} risk={p['risk']} confidence={p['confidence']}\n{p['title']}\n")
    print(pl["explanation"])
    for w in pl.get("warnings", []):
        print("  ⚠", w)
    print("\nOperations:")
    for op in pl["ops"]:
        print(" ", "POST /accounts" if op["type"] == "create" else f"PATCH /accounts/{op['account_id']}",
              json.dumps({k: v for k, v in op["fields"].items() if k != "note"}))
    return 0


def validate_resolution(led, hold_id: int, decision: str, account_id=None) -> dict:
    """Returns the HOLD proposal or raises ValueError. Pure ledger read."""
    p = led.get_proposal(hold_id)
    if not p:
        raise ValueError(f"No proposal #{hold_id}")
    subj = p["subject_key"]
    if decision == "revoke":
        if subj not in led.active_resolutions():
            raise ValueError(f"#{hold_id} ({subj}) has no active resolution to revoke")
        return p
    if p["kind"] != "HOLD" or p["status"] != "hold":
        raise ValueError(f"#{hold_id} is a {p['kind']} in status '{p['status']}'; only open HOLD items can be resolved")
    if not subj.startswith("web:"):
        raise ValueError(f"#{hold_id} ({subj}) is not a website-identity HOLD; resolve it in the CRM / with finance")
    if decision == "distinct":
        if p["account_ids"] or not p["payload"].get("evidence", {}).get("alternatives"):
            raise ValueError(f"#{hold_id} is not a look-alike identity HOLD; 'distinct' does not apply")
    elif decision == "survivor":
        if len(p["account_ids"]) < 2:
            raise ValueError(f"#{hold_id} is not a same-address group HOLD; 'survivor' does not apply")
        if account_id not in p["account_ids"]:
            raise ValueError(f"{account_id} is not one of #{hold_id}'s accounts: {', '.join(p['account_ids'])}")
    else:
        raise ValueError(f"Unknown decision '{decision}'")
    return p


def cmd_resolve(a):
    led = _ledger()
    if not (a.note or "").strip():
        print("--note is required: record why (it is shown on every proposal this resolution produces).")
        return 2
    try:
        p = validate_resolution(led, a.id, a.decision, a.account_id)
    except ValueError as e:
        print(f"Refused: {e}")
        return 1
    rid = led.add_resolution(p["subject_key"], a.decision, hold_proposal_id=p["id"],
                             hold_fingerprint=p["fingerprint"], account_id=a.account_id, note=a.note.strip())
    print(f"Recorded resolution #{rid}: {p['subject_key']} -> {a.decision} {a.account_id or ''}".rstrip())
    print("Nothing was written to the CRM. Run  ./bh scan  to turn this into pending proposals for review.")
    return 0


def _port_free(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def cmd_serve(a):
    if not _port_free(a.port):
        print(f"Port {a.port} is already in use (an older server?). Find it with:\n"
              f"  lsof -nP -iTCP:{a.port} -sTCP:LISTEN\nor start on another port:  ./bh serve --port {a.port + 1}")
        return 1
    mode = "LIVE WRITES ENABLED (each still needs approve + preview + typed confirm)" if config.WRITES_ENABLED \
        else "dry-run: CRM writes disabled"
    print(f"Serving http://127.0.0.1:{a.port}  [{mode}]\n"
          "The terminal will look idle/frozen while the server runs — that is normal. Press Ctrl+C to stop.",
          flush=True)
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=a.port, log_level="warning")
    return 0


def run_tests() -> dict:
    xml = config.DATA_DIR / "test_report.xml"
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={xml}"],
                          cwd=str(config.ROOT), capture_output=True, text=True, timeout=300)
    cases = []
    try:
        for tc in ET.parse(str(xml)).getroot().iter("testcase"):
            outcome = "passed"
            for child in tc:
                if child.tag in ("failure", "error"):
                    outcome = "failed"
                elif child.tag == "skipped":
                    outcome = "skipped"
            cases.append({"name": tc.get("name"), "module": (tc.get("classname") or "").split(".")[-1],
                          "time": float(tc.get("time") or 0), "outcome": outcome})
    except (ET.ParseError, OSError):
        pass
    report = {"ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "exit_code": proc.returncode,
              "summary": (proc.stdout.strip().splitlines() or [""])[-1], "cases": cases,
              "output_tail": proc.stdout[-4000:]}
    (config.DATA_DIR / "test_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return report


def cmd_test(a):
    r = run_tests()
    print(r["output_tail"])
    print(f"Report saved for the Test tab ({len(r['cases'])} cases).")
    return r["exit_code"]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bh", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--offline", metavar="FILE")
    s.set_defaults(fn=cmd_scan)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    s = sub.add_parser("list")
    s.add_argument("--status")
    s.set_defaults(fn=cmd_list)
    s = sub.add_parser("show")
    s.add_argument("id", type=int)
    s.set_defaults(fn=cmd_show)
    sub.add_parser("test").set_defaults(fn=cmd_test)
    s = sub.add_parser("resolve")
    s.add_argument("id", type=int)
    s.add_argument("decision", choices=["distinct", "survivor", "revoke"])
    s.add_argument("account_id", nargs="?")
    s.add_argument("--note", required=True)
    s.set_defaults(fn=cmd_resolve)
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(fn=cmd_serve)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
