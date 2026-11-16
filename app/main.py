"""Review & Monitoring Interface: the local review workspace. Start with `./bh serve` (one server, one port).

Write safety in the web layer:
  * No GET route, import, startup hook or scan writes to the CRM. GETs may READ the CRM (live preview).
  * Every POST requires: a local client, a same-origin (or absent) Origin header, and this process's
    random CSRF token. Writes additionally go through executor.execute (approval + fresh preview token +
    typed "APPLY <id>" + CRM_WRITES_ENABLED=1 for this process).
  * The API token is never rendered. (The old /crm/<id> redirect embedded it in a URL; it was removed.)
"""
from __future__ import annotations

import json
import secrets
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote, urlparse

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from . import config
from . import evidence as E
from . import exec_queue as Q
from . import executor as X
from . import ledger as L
from .policy import chow_required, financials

app = FastAPI(title="Bellhaven CRM Reconciliation")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.filters["pretty"] = lambda v: json.dumps(v, indent=2, ensure_ascii=False, default=str)
templates.env.filters["money"] = lambda v: (f"${v:,.0f}" if isinstance(v, (int, float)) and not isinstance(v, bool)
                                            else ("missing" if v in (None, "") else repr(v)))
templates.env.filters["fromjson"] = lambda v: json.loads(v) if v else {}

# Display names for the ledger's status machine. "Applied" is never shown for a proposal unless the CRM read-back
# verified it (VERIFIED); a write without a matching read-back is FAILED.
STATE_LABELS = {"pending": "PENDING", "hold": "HELD", "approved": "APPROVED", "applying": "EXECUTING",
                "verified": "VERIFIED", "failed": "FAILED", "superseded": "SUPERSEDED", "conflict": "BLOCKED",
                "rejected": "REJECTED", "resolved": "RESOLVED", "applied": "WRITTEN, NOT VERIFIED"}
templates.env.filters["state"] = lambda v: STATE_LABELS.get(v, (v or "").upper())
templates.env.globals["needs_verification"] = X.address_purpose_check

CSRF = secrets.token_urlsafe(32)
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


class State:
    ledger: L.Ledger = None
    crm = None


state = State()


def ledger() -> L.Ledger:
    if state.ledger is None:
        state.ledger = L.Ledger()
    return state.ledger


def crm():
    if state.crm is None:
        from .crm import CRMClient
        state.crm = CRMClient()
    return state.crm


def render(request: Request, name: str, **ctx):
    ctx.setdefault("tab", "")
    return templates.TemplateResponse(request, name, {
        "csrf": CSRF, "writes_enabled": config.WRITES_ENABLED, "counts": ledger().counts(), **ctx})


def guard(request: Request, csrf: str):
    host = request.client.host if request.client else ""
    if host not in LOCAL_HOSTS:
        raise HTTPException(403, "Local access only")
    origin = request.headers.get("origin")
    if origin and urlparse(origin).hostname not in ("127.0.0.1", "localhost", "testserver"):
        raise HTTPException(403, "Cross-origin request refused")
    if not secrets.compare_digest(csrf or "", CSRF):
        raise HTTPException(403, "Stale or missing form token: reload the page and try again")


def _latest():
    run = ledger().latest_run(completed_only=True)
    summary = json.loads(run["summary"]) if run and run.get("summary") else {}
    return run, summary


KIND_ORDER = ["CHOW", "WRONG_PARENT", "DUPLICATE", "WEBSITE_ONLY", "CRM_ONLY", "FIELD_UPDATE", "HOLD"]
RISK_ORDER = {"hold": 0, "high": 1, "medium": 2, "low": 3}


# ------------------------------------------------------------------ Start Here

@app.get("/", response_class=HTMLResponse)
def start(request: Request, msg: str = ""):
    led = ledger()
    last_any = led.latest_run()
    run, summary = _latest()
    results = summary.get("results", [])
    cls = Counter(c.split(" ")[0] for r in results for c in r["classification"].split(" + "))
    props = led.proposals()
    return render(request, "dashboard.html", tab="start", run=run, last_any=last_any, summary=summary,
                  schedule=schedule_status(led), completeness=_completeness(run, summary, last_any),
                  state_labels=STATE_LABELS,
                  results=results, cls=cls, msg=msg, runs=led.runs(8),
                  errors=json.loads(last_any["errors"]) if last_any and last_any.get("errors") else [],
                  sources=led.sources(run["id"]) if run else [], receipts=led.receipts(),
                  open_kinds=Counter(p["kind"] for p in props if p["status"] in L.OPEN),
                  write_count=led.write_count(),
                  snapshot_exists=(config.DATA_DIR / "snapshot.json").exists())


def _completeness(run, summary, last_any) -> dict:
    """Is the latest completed scan complete enough to trust? (Incomplete scans create no proposals at all.)"""
    if not run:
        return {"ok": False, "text": "No completed scan yet."}
    home = summary.get("homepage_count")
    web = run.get("website_facilities") or 0
    parts = [f"{web} website facilities" + (f" (homepage states {home}, directory lists "
                                             f"{summary.get('directory_count')})" if home else ""),
             f"{run.get('crm_accounts') or 0} CRM accounts (every page)"]
    ok = run["status"] == "completed" and (not home or web >= home)
    later_failed = last_any and last_any["id"] != run["id"] and last_any["status"] != "completed"
    if later_failed:
        parts.append(f"a later run #{last_any['id']} ended '{last_any['status']}' and changed nothing")
    return {"ok": ok and not later_failed, "text": "; ".join(parts)}


def schedule_status(led) -> dict:
    """Daily read-only scan status from the ledger (runs started by scripts/run_daily.py) and data/daily.log."""
    sched = []
    for r in led.runs(200):
        try:
            prov = (json.loads(r["summary"]) if r.get("summary") else {}).get("provenance") or ""
        except ValueError:
            prov = ""
        if not prov:
            prov = " ".join(s["provenance"] or "" for s in led.sources(r["id"]))
        if "scheduled" in prov:
            sched.append(r)
    log = config.DATA_DIR / "daily.log"
    tail = ""
    if log.exists():
        try:
            tail = "\n".join(log.read_text(errors="replace").splitlines()[-8:])
        except OSError:
            tail = ""
    installed = None
    try:
        import subprocess
        out = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=3)
        installed = "run_daily.py" in (out.stdout or "")
    except Exception:  # noqa: BLE001  (no crontab binary, sandbox, timeout)
        installed = None
    failures = [r for r in sched if r["status"] != "completed"]
    return {"runs": sched[:10], "last": sched[0] if sched else None, "failures": failures[:10],
            "installed": installed, "log_tail": tail}


@app.post("/run")
def run_scan(request: Request, csrf: str = Form(""), mode: str = Form("live")):
    """Read-only scan. Never writes to the CRM."""
    guard(request, csrf)
    from .pipeline import offline_source, run_pipeline
    if mode == "offline":
        snap = config.DATA_DIR / "snapshot.json"
        if not snap.exists():
            return RedirectResponse("/?msg=" + quote("No data/snapshot.json for offline scan"), status_code=303)
        scrape_fn, src, prov = offline_source(snap)
        res = run_pipeline(src, ledger(), scrape_fn, provenance=prov, save_snapshot=False)
    else:
        from .scrape import scrape
        res = run_pipeline(crm(), ledger(), scrape, provenance="live", save_snapshot=True)
    return RedirectResponse("/?msg=" + quote(f"Scan #{res['run_id']} {res['status']}: {res.get('new', 0)} new, "
                                             f"{res.get('known', 0)} already known, {res.get('resolved', 0)} "
                                             "resolved. Nothing was written to the CRM."), status_code=303)


# ------------------------------------------------------------------ Data Review

@app.get("/data", response_class=HTMLResponse)
def data_review(request: Request, q: str = "", cls: str = ""):
    run, summary = _latest()
    results = summary.get("results", [])
    by_acct, by_url = defaultdict(list), defaultdict(list)
    for p in ledger().proposals():
        if p["status"] in (L.SUPERSEDED,):
            continue
        for a in p["account_ids"]:
            by_acct[a].append(p)
        w = (p["payload"].get("evidence") or {}).get("website") or {}
        if w.get("source_url"):
            by_url[w["source_url"]].append(p)
    rows = []
    for r in results:
        linked = {p["id"]: p for a in r.get("account_ids", []) for p in by_acct[a]}
        linked.update({p["id"]: p for p in by_url.get(r.get("source_url"), [])})
        r = dict(r, proposals=sorted(linked.values(), key=lambda p: p["id"]))
        text = json.dumps([r.get("facility"), r.get("crm_name"), r.get("account_ids"), r.get("website"),
                           [c.get("name") for c in r.get("crm") or []]]).lower()
        if q and q.lower() not in text:
            continue
        if cls and cls not in r["classification"]:
            continue
        rows.append(r)
    all_cls = sorted({c.split(" ")[0] for r in results for c in r["classification"].split(" + ")})
    return render(request, "data.html", tab="data", run=run, summary=summary, rows=rows, q=q, cls=cls,
                  all_cls=all_cls, total=len(results))


# ------------------------------------------------------------------ Find Problems

CATEGORY = {
    "HOLD": ("Held — identity or ownership unresolved", "No operations exist for these. A human must resolve them "
             "outside the tool; a later scan will pick up the corrected CRM."),
    "CHOW": ("Change of ownership (billing-protected)", "Revenue AND AR > 0: original account preserved; successor "
             "created and linked, or linked to an existing current-owner account."),
    "WRONG_PARENT": ("Parent issue", "Same facility by address, wrong parent; SOP allows a direct re-parent."),
    "DUPLICATE": ("Duplicate accounts", "Several accounts at one address with a defensible survivor."),
    "WEBSITE_ONLY": ("Missing from CRM", "On the website, no CRM account at that address."),
    "CRM_ONLY": ("Under Bellhaven in CRM but not on website", "Flag for review; ownership unknown."),
    "FIELD_UPDATE": ("Renamed / alias / field differences", "Same address; CRM name/phone/address differ from website."),
}


@app.get("/problems", response_class=HTMLResponse)
def problems(request: Request, show: str = "open"):
    props = ledger().proposals(statuses=L.OPEN if show == "open" else None)
    groups = []
    for k in KIND_ORDER:
        items = sorted([p for p in props if p["kind"] == k], key=lambda p: (RISK_ORDER.get(p["risk"], 9), p["id"]))
        if items:
            groups.append((k, CATEGORY[k][0], CATEGORY[k][1], items))
    return render(request, "problems.html", tab="problems", groups=groups, show=show)


# ------------------------------------------------------------------ Build / Modify

@app.get("/review", response_class=HTMLResponse)
def review(request: Request, status: str = "open", kind: str = "", risk: str = "", q: str = ""):
    led = ledger()
    if status == "open":
        props = led.proposals(statuses=L.OPEN, kind=kind or None)
    else:
        props = led.proposals(status=status or None, kind=kind or None)
    if risk:
        props = [p for p in props if p["risk"] == risk]
    if q:
        props = [p for p in props if q.lower() in (p["title"] + json.dumps(p["account_ids"])).lower()]
    props.sort(key=lambda p: (KIND_ORDER.index(p["kind"]) if p["kind"] in KIND_ORDER else 99, p["id"]))
    batchable = [p for p in led.proposals(status=L.APPROVED) if p["kind"] != "CHOW"]
    return render(request, "review.html", tab="review", props=props, status=status, kind=kind, risk=risk, q=q,
                  kinds=KIND_ORDER, statuses=["open"] + L.ALL_STATUSES + [""], batchable=batchable)


def _financial_context(pl: dict, fresh: Optional[dict] = None) -> list:
    out, seen = [], set()
    accts = []
    ev = pl.get("evidence") or {}
    for key in ("crm", "survivor", "current_owner_account"):
        if ev.get(key):
            accts.append((key, ev[key]))
    for a in (ev.get("alternatives") or []):
        accts.append(("candidate", a))
    for role, a in accts:
        aid = a.get("account_id")
        if not aid or aid in seen:
            continue
        seen.add(aid)
        cur = (fresh or {}).get(aid, a)
        rev, ar = financials(cur)
        req, why = chow_required(cur)
        out.append({"role": role, "account_id": aid, "name": cur.get("name"), "parent": cur.get("parent_name")
                    or cur.get("parent_id") or "none", "revenue": rev, "ar": ar, "status": cur.get("status"),
                    "sop": why, "chow": req})
    return out


@app.get("/proposal/{pid}", response_class=HTMLResponse)
def proposal(request: Request, pid: int, msg: str = ""):
    led = ledger()
    p = led.get_proposal(pid)
    if not p:
        raise HTTPException(404, "No such proposal")
    pl = p["payload"]
    decisions = [d for d in led.decisions(1000) if d["proposal_id"] == pid][::-1]
    holds = [d for d in decisions if d["decision"] == "hold" and (d.get("note") or "").strip()]
    return render(request, "proposal.html", tab="review", p=p, pl=pl, ops_log=led.operations(pid), msg=msg,
                  addr=X.address_purpose_check(p), hold_note=holds[-1]["note"] if holds and p["status"] == "hold" else "",
                  decisions=decisions,
                  audit=led.audit(pid), fin=_financial_context(pl), phrase=X.confirmation_phrase(pid),
                  cmp=E.build(led, p, str(config.DATA_DIR)))


@app.post("/proposal/{pid}/decide")
def decide(request: Request, pid: int, action: str = Form(...), note: str = Form(""), csrf: str = Form(""),
           next: str = Form("")):
    guard(request, csrf)
    fn = {"approve": X.approve, "reject": X.reject, "hold": X.hold, "release": X.release, "note": X.annotate}.get(action)
    if not fn:
        raise HTTPException(400, "Unknown action")
    try:
        fn(ledger(), pid, note)
        msg = {"approve": "Approved (decision recorded). Nothing written yet — open the live preview to execute.",
               "note": "Note saved."}.get(action, f"{action} recorded")
    except X.ExecutionError as e:
        msg = f"error: {e}"
    if next == "queue":
        return RedirectResponse(f"/queue?msg={quote(f'#{pid}: {msg}')}", status_code=303)
    return RedirectResponse(f"/proposal/{pid}?msg={quote(msg)}", status_code=303)


@app.get("/proposal/{pid}/preview", response_class=HTMLResponse)
def preview(request: Request, pid: int):
    """READ-ONLY: re-reads the CRM and shows exactly what would be sent. Writes nothing."""
    led = ledger()
    p = led.get_proposal(pid)
    if not p:
        raise HTTPException(404, "No such proposal")
    try:
        pv = X.preview(crm(), led, pid)
        err = ""
    except Exception as e:  # noqa: BLE001
        pv, err = None, f"{type(e).__name__}: {e}"
    led.log("preview", pid, ok=bool(pv and not pv["problems"]), token=pv["token"] if pv else None)
    return render(request, "preview.html", tab="review", p=p, pl=p["payload"], pv=pv, err=err,
                  phrase=X.confirmation_phrase(pid), fin=_financial_context(p["payload"], pv["fresh"] if pv else None))


@app.post("/proposal/{pid}/execute")
def execute(request: Request, pid: int, csrf: str = Form(""), confirmation: str = Form(""),
            plan_token: str = Form(""), reviewed: str = Form("")):
    guard(request, csrf)
    if reviewed != "yes":
        return RedirectResponse(f"/proposal/{pid}?msg={quote('error: tick the reviewed box')}", status_code=303)
    try:
        res = X.execute(crm(), ledger(), pid, confirmation=confirmation, plan_token=plan_token)
        msg = f"Result: {res['status']}" + (f" — {res.get('error') or '; '.join(res.get('problems', []))}"
                                            if res["status"] not in (L.VERIFIED, L.RESOLVED) else "")
    except X.ExecutionError as e:
        msg = f"error: {e}"
    return RedirectResponse(f"/proposal/{pid}?msg={quote(msg)}", status_code=303)


@app.post("/batch/preview", response_class=HTMLResponse)
def batch_preview(request: Request, csrf: str = Form(""), pids: List[int] = Form(default=[])):
    guard(request, csrf)
    led = ledger()
    items, included = [], []
    for pid in pids:
        p = led.get_proposal(pid)
        if not p or p["status"] != L.APPROVED or p["kind"] == "CHOW":
            continue
        clash = X.batch_overlaps(led, included + [pid])
        if clash:
            items.append((p, None, f"Deferred to a follow-up batch: {clash[0]}. Preview it again after this batch "
                                   "is verified."))
            continue
        try:
            items.append((p, X.preview(crm(), led, pid), ""))
            included.append(pid)
        except Exception as e:  # noqa: BLE001
            items.append((p, None, str(e)))
    return render(request, "batch.html", tab="review", items=items, phrase=X.batch_phrase(len(items)))


@app.post("/batch/execute", response_class=HTMLResponse)
def batch_execute(request: Request, csrf: str = Form(""), confirmation: str = Form(""),
                  pids: List[int] = Form(default=[]), tokens: List[str] = Form(default=[]),
                  reviewed: str = Form("")):
    guard(request, csrf)
    if reviewed != "yes" or len(pids) != len(tokens):
        return RedirectResponse("/review?status=approved", status_code=303)
    try:
        results = X.execute_batch(crm(), ledger(), list(zip(pids, tokens)), confirmation=confirmation)
        err = ""
    except X.ExecutionError as e:
        results, err = [], str(e)
    return render(request, "batch_result.html", tab="review", results=results, err=err)


# ------------------------------------------------------------------ Controlled execution queue

@app.get("/queue", response_class=HTMLResponse)
def queue(request: Request, msg: str = ""):
    """READ-ONLY (ledger only, no CRM calls). Sorts open proposals into queue-eligible and manual-review."""
    led = ledger()
    ready, awaiting, manual = [], [], []
    for p in led.proposals(statuses=L.OPEN):
        why = Q.eligibility(p)
        op = (p["payload"].get("ops") or [{}])[0]
        row = {"p": p, "why": why, "fields": op.get("fields") or {},
               "current": p["payload"].get("current") or {}, "account_id": op.get("account_id", "")}
        if why:
            manual.append(row)
        elif p["status"] == L.APPROVED:
            ready.append(row)
        elif p["status"] == L.PENDING:
            awaiting.append(row)
        else:
            manual.append({**row, "why": [f"status is {p['status']}"]})
    done = [r for r in led.audit(limit=2000) if r["event"] == "queue_finished"][:5]
    return render(request, "queue.html", tab="queue", ready=ready, awaiting=awaiting, manual=manual, msg=msg,
                  runs=done)


@app.post("/queue/preview", response_class=HTMLResponse)
def queue_preview(request: Request, csrf: str = Form(""), pids: List[int] = Form(default=[])):
    """READ-ONLY: validates every selected item against the live CRM and the live website."""
    guard(request, csrf)
    items = Q.preview_queue(crm(), ledger(), pids)
    for it in items:
        ledger().log("queue_preview", it["pid"], ok=it["ok"], problems=it["problems"],
                     token=it["pv"]["token"] if it["pv"] else None)
    ok = [it for it in items if it["ok"]]
    return render(request, "queue_preview.html", tab="queue", items=items, ok=ok, phrase=Q.queue_phrase(len(ok)))


@app.post("/queue/run", response_class=HTMLResponse)
def queue_run(request: Request, csrf: str = Form(""), confirmation: str = Form(""), reviewed: str = Form(""),
              pids: List[int] = Form(default=[]), tokens: List[str] = Form(default=[])):
    guard(request, csrf)
    if reviewed != "yes" or len(pids) != len(tokens):
        return RedirectResponse(f"/queue?msg={quote('error: tick the reviewed box')}", status_code=303)
    try:
        out, err = Q.run_queue(crm(), ledger(), list(zip(pids, tokens)), confirmation=confirmation), ""
    except X.ExecutionError as e:
        out, err = None, str(e)
    return render(request, "queue_result.html", tab="queue", out=out, err=err)


# ------------------------------------------------------------------ History / audit

def _legacy_events():
    db = config.DATA_DIR / "execution_audit.db"
    if not db.exists():
        return []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute("SELECT at, event, account_id, message FROM events ORDER BY rowid").fetchall()
    except sqlite3.Error:
        return []
    finally:
        con.close()


@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    led = ledger()
    return render(request, "history.html", tab="history", decisions=led.decisions(), ops=led.operations(),
                  runs=led.runs(50), audit=led.audit(limit=300), receipts=led.receipts(),
                  legacy=_legacy_events())


# ------------------------------------------------------------------ Test / Walkthrough / Submit

def _test_report():
    p = config.DATA_DIR / "test_report.json"
    return json.loads(p.read_text()) if p.exists() else None


@app.get("/test", response_class=HTMLResponse)
def test_tab(request: Request):
    return render(request, "test.html", tab="test", report=_test_report())


@app.post("/test/run")
def test_run(request: Request, csrf: str = Form("")):
    guard(request, csrf)
    from .cli import run_tests
    run_tests()
    return RedirectResponse("/test", status_code=303)


@app.get("/walkthrough", response_class=HTMLResponse)
def walkthrough(request: Request):
    return render(request, "walkthrough.html", tab="walkthrough")


@app.get("/submit", response_class=HTMLResponse)
def submit(request: Request):
    led = ledger()
    run = led.latest_run(completed_only=True)
    live_run = next((r for r in led.runs(200) if r["status"] == "completed"
                     and any(s["provenance"].startswith("live") for s in led.sources(r["id"]))), None)
    rep = _test_report()
    props = led.proposals()
    checks = [
        ("Automated tests pass (mocked HTTP, temp SQLite)", bool(rep and rep["exit_code"] == 0),
         rep["summary"] if rep else "not run yet — Test tab or ./bh test"),
        ("Live read-only scan completed", bool(live_run),
         f"run #{live_run['id']} at {live_run['finished_at']}" if live_run else "./bh scan"),
        ("Findlay recognised as already resolved (no re-proposal)",
         bool(led.receipts()) and not any(p["status"] in L.OPEN and p["kind"] == "WRONG_PARENT" and
                                          "001UKEFGADQ8YCZ4YM" in p["account_ids"] for p in props),
         f"{len(led.receipts())} legacy receipt(s)"),
        ("Ambiguous identities held or operator-resolved (Kettering / Union Square / Amberly)",
         sum(1 for p in props if p["kind"] == "HOLD" and p["status"] in L.OPEN) + len(led.active_resolutions()) >= 3,
         f"{sum(1 for p in props if p['kind'] == 'HOLD' and p['status'] in L.OPEN)} open HOLD items · "
         f"{len(led.active_resolutions())} identity resolution(s)"),
        ("CHOW proposals present and never direct re-parents",
         all(not any("parent_id" in op.get("fields", {}) for op in p["payload"]["ops"] if op["type"] == "update")
             for p in props if p["kind"] == "CHOW") and any(p["kind"] == "CHOW" for p in props), ""),
        ("No write left without read-back (no started/uncertain/unverified ops)",
         not [o for o in led.operations() if o["status"] in ("started", "succeeded", "uncertain", "verify_failed")],
         f"{sum(1 for p in props if p['status'] == L.VERIFIED)} verified · {led.write_count()} write calls ever"),
        ("README with setup, architecture, policy, limits, demo script", (config.ROOT / "README.md").exists(), ""),
        ("Approved corrections executed and read-back verified by this engine",
         any(p["status"] == L.VERIFIED for p in props),
         f"{sum(1 for p in props if p['status'] == L.VERIFIED)} verified · {sum(1 for p in props if p['status'] == L.PENDING)} "
         "pending human decision — each needs your fresh approval, live preview and typed confirmation"),
        ("Requirements traceability matrix and nine-path review", (config.ROOT / "docs" / "REQUIREMENTS_MATRIX.md").exists(),
         "docs/REQUIREMENTS_MATRIX.md · docs/NINE_PATH_REVIEW.md"),
        ("Demo video recorded", False, "NOT recorded — follow the Walkthrough tab, then paste the link in README"),
        ("Public repository link", False, "not published — commit and push only when you decide to"),
    ]
    return render(request, "submit.html", tab="submit", checks=checks, run=run)


# ------------------------------------------------------------------ live read-only account JSON

@app.get("/api/account/{account_id}")
def live_account(account_id: str):
    """Live READ-ONLY view of a CRM account (for verification during review)."""
    return JSONResponse(crm().get_account(account_id))


# ------------------------------------------------------------------ legacy pages (kept working)

@app.get("/legacy", response_class=HTMLResponse)
def legacy_index(request: Request):
    return render(request, "legacy.html", tab="legacy")


from app.investigate import router as _investigate_router  # noqa: E402
from app.proposals import router as _findlay_router  # noqa: E402
from app.records import router as _records_router  # noqa: E402
from app.review import router as _cards_router  # noqa: E402
from app.workspace import install as _install_nav  # noqa: E402

app.include_router(_cards_router)
app.include_router(_investigate_router)
app.include_router(_records_router)
app.include_router(_findlay_router)
_install_nav(app)   # also redirects old /workspace/* placeholders to the real tabs
