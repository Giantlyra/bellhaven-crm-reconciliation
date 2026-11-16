"""Regression tests for the issues found in the final pre-submission review (2026-11-15):

1. Sibling proposals on one account (Lima parent + Lima phone) must not block each other as 'drift' once one of
   them is verified, while unexplained drift still blocks.
2. A batch whose items share an account is refused (plan tokens would go stale mid-batch).
3. The website fingerprint is content-only (fetch timestamps excluded).
4. The legacy Findlay write route obeys CRM_WRITES_ENABLED like the main executor.
5. Operator identity resolutions turn HOLDs into ordinary proposals (still needing approval), are append-only,
   validated, revocable, and never write to the CRM.
"""
import sqlite3

import pytest

from app import executor as X
from app import ledger as L
from app.cli import validate_resolution
from app.reconcile import reconcile
from tests.conftest import BH, CT, FakeCRM, acct, approve_exec, parents, site

HV = "P_HV"


def _ingest(ledger, crm, facilities, resolutions=None):
    _, props = reconcile(facilities, list(crm.accounts.values()), True, resolutions=resolutions)
    return {p["subject_key"]: ledger.upsert_proposal(1, p)[0] for p in props}


# ---------------------------------------------------------------- 1. sibling drift
LIMA = [acct("L1", "Bellhaven Crossings of Lima", parent=CT, street="3115 N Cole St", city="Lima", state="OH",
             zip_="45801", phone="(734) 872-9575", rev=47000, ar=0)]
LIMA_SITE = [site("Bellhaven Crossings of Lima", "3115 N Cole St", "Lima", "OH", "45801", phone="(231) 539-3617")]


def test_sibling_proposals_on_one_account_both_verify(ledger):
    crm = FakeCRM(parents() + LIMA)
    ids = _ingest(ledger, crm, LIMA_SITE)
    parent_pid, phone_pid = ids["acct:L1:parent"], ids["acct:L1:fields"]
    assert approve_exec(crm, ledger, parent_pid)["status"] == L.VERIFIED
    pv = X.preview(crm, ledger, phone_pid)
    assert pv["problems"] == []
    assert any(f"verified proposal #{parent_pid}" in n for n in pv["notes"])
    assert approve_exec(crm, ledger, phone_pid)["status"] == L.VERIFIED
    assert crm.accounts["L1"]["parent_id"] == BH and crm.accounts["L1"]["phone"] == "(231) 539-3617"


def test_unexplained_drift_still_blocks(ledger):
    crm = FakeCRM(parents() + LIMA)
    ids = _ingest(ledger, crm, LIMA_SITE)
    crm.accounts["L1"]["parent_id"] = "SOMEONE_ELSE"   # changed outside this engine
    pv = X.preview(crm, ledger, ids["acct:L1:fields"])
    assert any("Drift: L1.parent_id" in p for p in pv["problems"])


def test_drift_to_a_value_we_did_not_write_still_blocks(ledger):
    crm = FakeCRM(parents() + LIMA)
    ids = _ingest(ledger, crm, LIMA_SITE)
    assert approve_exec(crm, ledger, ids["acct:L1:parent"])["status"] == L.VERIFIED
    crm.accounts["L1"]["parent_id"] = CT              # someone moved it back afterwards
    crm.accounts["L1"]["outstanding_ar"] = 500
    pv = X.preview(crm, ledger, ids["acct:L1:fields"])
    assert any("outstanding_ar" in p for p in pv["problems"])


def test_sibling_tolerance_does_not_bypass_financial_policy(ledger):
    """After a verified re-parent, AR appearing on the account must still block a sibling edit as drift."""
    crm = FakeCRM(parents() + LIMA)
    ids = _ingest(ledger, crm, LIMA_SITE)
    assert approve_exec(crm, ledger, ids["acct:L1:parent"])["status"] == L.VERIFIED
    crm.accounts["L1"]["outstanding_ar"] = 900
    pv = X.preview(crm, ledger, ids["acct:L1:fields"])
    assert pv["problems"]


# ---------------------------------------------------------------- 2. overlapping batch
def test_batch_with_shared_account_is_refused_before_any_write(ledger):
    crm = FakeCRM(parents() + LIMA)
    ids = _ingest(ledger, crm, LIMA_SITE)
    pids = [ids["acct:L1:fields"], ids["acct:L1:parent"]]
    for pid in pids:
        X.approve(ledger, pid, "t")
    items = [(pid, X.preview(crm, ledger, pid)["token"]) for pid in pids]
    with pytest.raises(X.ExecutionError, match="both touch L1"):
        X.execute_batch(crm, ledger, items, confirmation=X.batch_phrase(2), writes_enabled=True)
    assert crm.writes() == []


def test_batch_overlaps_reports_duplicate_survivor_shared_with_phone_fix(ledger):
    accts = parents() + [
        acct("S1", "Bellhaven of Port Clinton", street="1420 Harbor Point Dr", city="Port Clinton", state="OH",
             zip_="43452", phone="(614) 512-8712"),
        acct("D1", "Harborview N&R of Port Clinton", parent=CT, street="1420 Harbor Point Drive",
             city="Port Clinton", state="OH", zip_="43452", phone="(216) 314-1338")]
    crm = FakeCRM(accts)
    ids = _ingest(ledger, crm, [site("Bellhaven of Port Clinton", "1420 Harbor Point Dr", "Port Clinton", "OH",
                                     "43452", phone="(330) 733-6423")])
    assert X.batch_overlaps(ledger, [ids["dup:D1"], ids["acct:S1:fields"]])
    # sequential waves work: phone first, then the duplicate is previewed fresh and verifies
    assert approve_exec(crm, ledger, ids["acct:S1:fields"])["status"] == L.VERIFIED
    assert approve_exec(crm, ledger, ids["dup:D1"])["status"] == L.VERIFIED
    assert crm.accounts["D1"]["duplicate_of_account"] == "S1"


# ---------------------------------------------------------------- 3. fingerprint
def test_website_fingerprint_ignores_fetch_timestamps(ledger):
    from app.pipeline import run_pipeline
    from app.scrape import ScrapeResult

    def scraper(ts):
        def fn():
            sr = ScrapeResult()
            sr.facilities = [dict(LIMA_SITE[0], retrieved_at=ts)]
            sr.homepage_count = sr.directory_count = 1
            sr.complete = True
            return sr
        return fn
    crm = FakeCRM(parents() + LIMA)
    r1 = run_pipeline(crm, ledger, scraper("2026-11-15T10:00:00"), legacy_dir=False)
    r2 = run_pipeline(crm, ledger, scraper("2026-11-15T11:00:00"), legacy_dir=False)
    fp = [s["fingerprint"] for r in (r1, r2) for s in ledger.sources(r["run_id"]) if s["source"] == "website"]
    assert fp[0] == fp[1]


# ---------------------------------------------------------------- 4. legacy Findlay route
def test_legacy_findlay_route_refuses_in_dry_run(monkeypatch):
    from fastapi.testclient import TestClient

    from app import crm as crm_mod
    from app import proposals as legacy
    from app.main import app
    called = []
    monkeypatch.setattr(crm_mod.CRMClient, "update_account", lambda *a, **k: called.append(a))
    monkeypatch.setattr(legacy, "audit", lambda *a, **k: called.append(("audit",) + a))
    c = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 5000))
    r = c.post("/proposals/findlay/apply", data={"csrf": legacy.CSRF, "approved": "yes",
                                                 "confirmation": legacy.CONFIRMATION})
    assert r.status_code == 403 and "disabled" in r.text
    assert called == []


# ---------------------------------------------------------------- 5. identity resolutions
AMBERLY_ACCTS = parents() + [acct("J1", "Amberly Manor", parent="P_JP", street="918 S Nevada Ave",
                                  city="Colorado Springs", state="CO", zip_="80903")]
AMBERLY_SITE = [site("Amberly Manor", "4390 Darrow Rd", "Hudson", "OH", "44236", slug="amberly-manor")]

KETTERING = parents() + [
    acct("K1", "Kettering Care Centre", parent=HV, street="3313 Wilmington Pike", city="Kettering", state="OH",
         zip_="45429", phone="(419) 600-2603", care="Skilled Nursing"),
    acct("K2", "Kettering Senior Campus", parent=CT, street="3313 Wilmington Pk", city="Kettering", state="OH",
         zip_="45429", phone="(517) 646-8751", care="Skilled Nursing"),
    acct("K3", "Kettering Nursing & Rehabilitation", parent="", street="3313 Wilmington Pike", city="Kettering",
         state="OH", zip_="45429", phone="(216) 345-3441", care="Skilled Nursing")]
KETTERING_SITE = [site("Bellhaven of Kettering", "3313 Wilmington Pike", "Kettering", "OH", "45429",
                       phone="(231) 269-5449", care=("Short-Term Rehabilitation & Nursing",),
                       slug="bellhaven-of-kettering")]


def test_distinct_resolution_turns_identity_hold_into_create_and_leaves_lookalike_alone(ledger):
    crm = FakeCRM(AMBERLY_ACCTS)
    hold = _ingest(ledger, crm, AMBERLY_SITE)["web:amberly-manor"]
    assert ledger.get_proposal(hold)["status"] == L.HOLD
    validate_resolution(ledger, hold, "distinct")
    ledger.add_resolution("web:amberly-manor", "distinct", hold_proposal_id=hold, note="CO vs OH")
    new = _ingest(ledger, crm, AMBERLY_SITE, ledger.active_resolutions())["web:amberly-manor"]
    p = ledger.get_proposal(new)
    assert p["kind"] == "WEBSITE_ONLY" and p["status"] == L.PENDING
    assert ledger.get_proposal(hold)["status"] == L.SUPERSEDED
    assert any("J1" in w and "untouched" in w for w in p["payload"]["warnings"])
    assert crm.writes() == []                       # recording + re-scan wrote nothing
    res = approve_exec(crm, ledger, new)
    assert res["status"] == L.VERIFIED
    assert crm.accounts["J1"]["parent_id"] == "P_JP"  # look-alike untouched


def test_survivor_resolution_produces_normal_proposals(ledger):
    crm = FakeCRM(KETTERING)
    hold = _ingest(ledger, crm, KETTERING_SITE)["web:bellhaven-of-kettering"]
    with pytest.raises(ValueError):
        validate_resolution(ledger, hold, "survivor", "NOT_IN_GROUP")
    with pytest.raises(ValueError):
        validate_resolution(ledger, hold, "distinct")
    ledger.add_resolution("web:bellhaven-of-kettering", "survivor", account_id="K1", hold_proposal_id=hold,
                          note="Harborview = 2025 acquisition")
    ids = _ingest(ledger, crm, KETTERING_SITE, ledger.active_resolutions())
    kinds = {k: ledger.get_proposal(v)["kind"] for k, v in ids.items()}
    assert kinds == {"dup:K2": "DUPLICATE", "dup:K3": "DUPLICATE", "acct:K1:parent": "WRONG_PARENT",
                     "acct:K1:fields": "FIELD_UPDATE"}
    for pid in ids.values():
        assert ledger.get_proposal(pid)["status"] == L.PENDING
    assert crm.writes() == []


def test_resolution_only_for_open_web_holds(ledger):
    crm = FakeCRM(parents() + LIMA)
    ids = _ingest(ledger, crm, LIMA_SITE)
    with pytest.raises(ValueError, match="only open HOLD"):
        validate_resolution(ledger, ids["acct:L1:parent"], "distinct")
    with pytest.raises(ValueError, match="No proposal"):
        validate_resolution(ledger, 9999, "distinct")


def test_revoked_resolution_restores_hold_and_resolutions_are_append_only(ledger):
    crm = FakeCRM(AMBERLY_ACCTS)
    hold = _ingest(ledger, crm, AMBERLY_SITE)["web:amberly-manor"]
    ledger.add_resolution("web:amberly-manor", "distinct", hold_proposal_id=hold, note="x")
    created = _ingest(ledger, crm, AMBERLY_SITE, ledger.active_resolutions())["web:amberly-manor"]
    ledger.add_resolution("web:amberly-manor", "revoke", hold_proposal_id=hold, note="changed my mind")
    assert ledger.active_resolutions() == {}
    again = _ingest(ledger, crm, AMBERLY_SITE, ledger.active_resolutions())["web:amberly-manor"]
    assert ledger.get_proposal(again)["kind"] == "HOLD"
    assert ledger.get_proposal(created)["status"] == L.SUPERSEDED
    with pytest.raises(sqlite3.DatabaseError):
        ledger.db.execute("DELETE FROM resolutions")
    with pytest.raises(sqlite3.DatabaseError):
        ledger.db.execute("UPDATE resolutions SET decision='x'")


def test_stale_survivor_resolution_is_ignored_and_hold_returns(ledger):
    crm = FakeCRM(KETTERING)
    _ingest(ledger, crm, KETTERING_SITE)
    gone = {"web:bellhaven-of-kettering": {"decision": "survivor", "account_id": "K_DELETED", "id": 1}}
    _, props = reconcile(KETTERING_SITE, list(crm.accounts.values()), True, resolutions=gone)
    assert [p["kind"] for p in props] == ["HOLD"]


def test_reverted_proposal_reopens_pending_never_approved(ledger):
    crm = FakeCRM(parents() + LIMA)
    pid = _ingest(ledger, crm, LIMA_SITE)["acct:L1:fields"]
    X.approve(ledger, pid, "old approval")
    _ingest(ledger, crm, [dict(LIMA_SITE[0], phone="(999) 111-2222")])   # website changes -> supersedes
    assert ledger.get_proposal(pid)["status"] == L.SUPERSEDED
    assert _ingest(ledger, crm, LIMA_SITE)["acct:L1:fields"] == pid          # website reverts
    assert ledger.get_proposal(pid)["status"] == L.PENDING
    assert [p["id"] for p in ledger.proposals(status=L.PENDING) if p["subject_key"] == "acct:L1:fields"] == [pid]
    assert not ledger.proposals(status=L.APPROVED)


def test_batch_items_that_only_read_the_same_survivor_do_not_conflict(ledger):
    accts = parents() + [
        acct("S1", "Bellhaven Gardens of Monroe", street="750 Stewart Rd", city="Monroe", state="MI", zip_="48162",
             phone="(814) 412-2218"),
        acct("D1", "Cedar Trail of Monroe", parent=CT, street="750 Stewart Road", city="Monroe", state="MI",
             zip_="48162"),
        acct("D2", "Monroe Gardens Care Center", parent=HV, street="750 Stewart Rd", city="Monroe", state="MI",
             zip_="48162")]
    crm = FakeCRM(accts)
    ids = _ingest(ledger, crm, [site("Bellhaven Gardens of Monroe", "750 Stewart Rd", "Monroe", "MI", "48162",
                                     phone="(814) 412-2218")])
    pids = [ids["dup:D1"], ids["dup:D2"]]
    assert X.batch_overlaps(ledger, pids) == []
    for pid in pids:
        X.approve(ledger, pid, "t")
    items = [(pid, X.preview(crm, ledger, pid)["token"]) for pid in pids]
    res = X.execute_batch(crm, ledger, items, confirmation=X.batch_phrase(2), writes_enabled=True)
    assert [r["status"] for r in res] == [L.VERIFIED, L.VERIFIED]
