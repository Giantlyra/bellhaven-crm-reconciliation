"""Requirement-level checks added in the final review: repeated approvals, re-execution of verified work, CHOW with
changed or missing financials, CHOW partial failure with a fresh-confirmation resume, scheduled-scan safety, and the
review interface's state, schedule and completeness displays."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import executor as X
from app import ledger as L
from app import main
from app.pipeline import run_pipeline
from app.reconcile import reconcile
from app.scrape import ScrapeResult
from tests.conftest import BH, CT, FakeCRM, acct, approve_exec, parents, site

ROOT = Path(__file__).resolve().parent.parent

CHOW_ACCTS = parents() + [acct("A1", "Bellhaven of Tiffin", parent=CT, street="45 St Lawrence Dr", city="Tiffin",
                               state="OH", zip_="44883", phone="(260) 589-2589", rev=84000, ar=12400)]
CHOW_SITE = [site("Bellhaven of Tiffin", "45 St Lawrence Dr", "Tiffin", "OH", "44883", phone="(260) 589-2589")]
FIELD_ACCTS = parents() + [acct("A2", "Old Name", street="1 A St", city="C", state="OH", zip_="11111",
                                phone="(555) 000-0000")]
FIELD_SITE = [site("New Name", "1 A St", "C", "OH", "11111")]


def setup(ledger, accounts, facilities):
    crm = FakeCRM(accounts)
    _, props = reconcile(facilities, list(crm.accounts.values()), True)
    return crm, [ledger.upsert_proposal(1, p)[0] for p in props]


# ---------------------------------------------------------------- approvals

def test_repeated_approval_is_refused_and_recorded_once(ledger):
    crm, [pid] = setup(ledger, FIELD_ACCTS, FIELD_SITE)
    X.approve(ledger, pid, "first")
    with pytest.raises(X.ExecutionError):
        X.approve(ledger, pid, "second")
    assert [d["decision"] for d in ledger.decisions() if d["proposal_id"] == pid] == ["approved"]
    assert crm.writes() == []


def test_verified_proposal_cannot_be_executed_again(ledger):
    crm, [pid] = setup(ledger, FIELD_ACCTS, FIELD_SITE)
    assert approve_exec(crm, ledger, pid)["status"] == L.VERIFIED
    n = len(crm.writes())
    pv = X.preview(crm, ledger, pid)
    with pytest.raises(X.ExecutionError):
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                  writes_enabled=True)
    with pytest.raises(X.ExecutionError):
        X.approve(ledger, pid, "again")
    assert len(crm.writes()) == n


def test_approval_from_another_proposal_version_does_not_authorize(ledger):
    """An approval is bound to the proposal fingerprint; editing the payload (a new version) voids it."""
    crm, [pid] = setup(ledger, FIELD_ACCTS, FIELD_SITE)
    X.approve(ledger, pid, "ok")
    ledger.db.execute("UPDATE proposals SET fingerprint='other-version' WHERE id=?", (pid,))
    ledger.db.commit()
    pv = X.preview(crm, ledger, pid)
    with pytest.raises(X.ExecutionError, match="exact proposal version"):
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                  writes_enabled=True)
    assert crm.writes() == []


# ---------------------------------------------------------------- CHOW and financial data

def test_chow_blocks_when_financials_become_missing(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    X.approve(ledger, pid, "ok")
    crm.accounts["A1"]["outstanding_ar"] = None
    pv = X.preview(crm, ledger, pid)
    assert pv["problems"], "missing financial values must block the write"
    res = X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                    writes_enabled=True)
    assert res["status"] == L.CONFLICT
    assert crm.writes() == []


def test_chow_blocks_when_financials_change_after_proposal(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    X.approve(ledger, pid, "ok")
    crm.accounts["A1"]["outstanding_ar"] = 0          # AR paid off since the proposal: a different decision
    pv = X.preview(crm, ledger, pid)
    assert any("outstanding_ar" in p for p in pv["problems"])
    assert crm.writes() == []


def test_chow_partial_failure_resume_needs_fresh_confirmation_and_reuses_successor(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    before = dict(crm.accounts["A1"])
    crm.fail_update_for.add("A1")                     # step 2 (link) fails after step 1 (create) succeeded
    assert approve_exec(crm, ledger, pid)["status"] == L.FAILED
    created = ledger.op(pid, 0)
    assert created["status"] == "succeeded" and created["returned_id"]
    crm.fail_update_for.clear()

    pv = X.preview(crm, ledger, pid)
    assert pv["requests"][0]["state"] == "done"       # the preview shows the create as already completed
    with pytest.raises(X.ExecutionError):              # an old/blank confirmation does not resume it
        X.execute(crm, ledger, pid, confirmation="", plan_token=pv["token"], writes_enabled=True)
    with pytest.raises(X.ExecutionError):              # neither does a stale plan token
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token="stale",
                  writes_enabled=True)
    res = X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                    writes_enabled=True)
    assert res["status"] == L.VERIFIED
    assert len([c for c in crm.calls if c[0] == "create"]) == 1
    old = crm.accounts["A1"]
    assert old["chow_current_account"] == created["returned_id"]
    for k in ("parent_id", "name", "status", "lifetime_revenue", "outstanding_ar"):
        assert old[k] == before[k], k
    assert crm.accounts[created["returned_id"]]["parent_id"] == BH


# ---------------------------------------------------------------- scheduled scans

def _scrape_ok():
    r = ScrapeResult()
    r.facilities, r.complete = [dict(f) for f in CHOW_SITE + FIELD_SITE], True
    return r


def test_scheduled_scan_makes_zero_writes_and_is_reported(ledger):
    crm = FakeCRM(CHOW_ACCTS + FIELD_ACCTS[2:])
    for _ in range(3):
        res = run_pipeline(crm, ledger, _scrape_ok, provenance="live (scheduled)", legacy_dir=False)
        assert res["status"] == "completed"
    assert crm.writes() == []
    assert all(p["status"] in (L.PENDING, L.HOLD) for p in ledger.proposals())
    st = main.schedule_status(ledger)
    assert st["last"]["status"] == "completed" and len(st["runs"]) == 3 and not st["failures"]


def test_failed_scheduled_scan_is_shown_as_failure(ledger):
    class Broken(FakeCRM):
        def list_accounts(self, **f):
            raise ConnectionError("CRM down")
    res = run_pipeline(Broken([]), ledger, _scrape_ok, provenance="live (scheduled)", legacy_dir=False)
    assert res["status"] == "failed"
    st = main.schedule_status(ledger)
    assert len(st["failures"]) == 1 and st["failures"][0]["status"] == "failed"
    assert ledger.proposals() == []


def test_daily_job_refuses_to_start_with_writes_enabled():
    env = {k: v for k, v in os.environ.items() if k != "CRM_WRITES_ENABLED"}
    env["CRM_WRITES_ENABLED"] = "1"
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_daily.py")], env=env, cwd=str(ROOT),
                         capture_output=True, text=True, timeout=60)
    assert out.returncode != 0
    assert "Refusing" in (out.stderr + out.stdout)


# ---------------------------------------------------------------- review interface

@pytest.fixture
def client(monkeypatch):
    led = L.Ledger(":memory:")
    monkeypatch.setattr(main.state, "ledger", led)
    monkeypatch.setattr(main.state, "crm", FakeCRM(CHOW_ACCTS))
    return TestClient(main.app), led


def test_dashboard_shows_lifecycle_states_completeness_and_schedule(client):
    c, led = client
    run_pipeline(main.state.crm, led, lambda: _only(CHOW_SITE), provenance="live (scheduled)", legacy_dir=False)
    html = c.get("/").text
    for label in ("PENDING", "HELD", "APPROVED", "EXECUTING", "VERIFIED", "FAILED", "SUPERSEDED"):
        assert label in html, label
    assert "Scan completeness" in html and "Daily schedule" in html


def test_executing_state_is_labelled_and_never_called_applied(client):
    c, led = client
    _, props = reconcile(CHOW_SITE, CHOW_ACCTS, True)
    pid = led.upsert_proposal(1, props[0])[0]
    led.set_status(pid, L.APPLYING)
    html = c.get(f"/proposal/{pid}").text
    assert "EXECUTING" in html and "VERIFIED" in html  # VERIFIED appears only in the plan's final-step text
    assert "Ordered transaction plan" in html and "historical financial record" in html


def test_chat_and_ask_routes_are_not_part_of_the_app(client):
    c, _ = client
    assert c.get("/ask").status_code == 404
    assert c.get("/api/ask?q=approve%2060").status_code == 404


def _only(facs):
    r = ScrapeResult()
    r.facilities, r.complete = [dict(f) for f in facs], True
    return r


# ---------------------------------------------------------------- interrupted execution

def test_interrupted_chow_execution_resumes_without_second_create(ledger):
    """Server killed after the successor POST was recorded as 'started' (outcome unknown), proposal left EXECUTING."""
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    X.approve(ledger, pid, "ok")
    op = ledger.get_proposal(pid)["payload"]["ops"][0]
    crm.create_account(op["fields"])                    # the POST reached the CRM ...
    ledger.record_op(pid, 0, "create", None, op["fields"], "started")   # ... but the process died before recording it
    ledger.set_status(pid, L.APPLYING)
    n_creates = len([c for c in crm.calls if c[0] == "create"])

    pv = X.preview(crm, ledger, pid)
    assert 0 in pv["recovered"] and not pv["problems"]
    res = X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                    writes_enabled=True)
    assert res["status"] == L.VERIFIED
    assert len([c for c in crm.calls if c[0] == "create"]) == n_creates   # adopted, never re-posted


def test_second_concurrent_execution_is_refused(ledger):
    crm, [pid] = setup(ledger, FIELD_ACCTS, FIELD_SITE)
    X.approve(ledger, pid, "ok")
    pv = X.preview(crm, ledger, pid)
    assert X._EXEC_LOCK.acquire(blocking=False)
    try:
        with pytest.raises(X.ExecutionError, match="in progress"):
            X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                      writes_enabled=True)
    finally:
        X._EXEC_LOCK.release()
    assert crm.writes() == []
