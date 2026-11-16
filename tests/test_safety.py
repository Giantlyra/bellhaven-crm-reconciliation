"""Risk / executor / audit-state safety guarantees required by the handoff."""
import json
import sqlite3

import pytest

from app import executor as X
from app import ledger as L
from app.legacy import import_legacy_receipts
from app.pipeline import run_pipeline
from app.reconcile import reconcile
from app.scrape import ScrapeResult
from tests.conftest import BH, CT, FakeCRM, acct, approve_exec, parents, site

HP = "P_HV"


def _setup(ledger, accounts, facilities):
    crm = FakeCRM(accounts)
    _, props = reconcile(facilities, list(crm.accounts.values()), True)
    ids = [ledger.upsert_proposal(1, p)[0] for p in props]
    return crm, ids, props


def _scrape(facs, complete=True, homepage_count=None):
    def fn():
        r = ScrapeResult()
        r.facilities, r.complete, r.homepage_count = [dict(f) for f in facs], complete, homepage_count
        return r
    return fn


# ---------------------------------------------------------------- reconciliation classification

KETTERING = parents() + [
    acct("K1", "Kettering Care Centre", parent=HP, street="3313 Wilmington Pike", city="Kettering", state="OH",
         zip_="45429", phone="(419) 600-2603"),
    acct("K2", "Kettering Senior Campus", parent=CT, street="3313 Wilmington Pk", city="Kettering", state="OH",
         zip_="45429", phone="(517) 646-8751"),
    acct("K3", "Kettering Nursing & Rehabilitation", parent="", street="3313 Wilmington Pike", city="Kettering",
         state="OH", zip_="45429", phone="(216) 345-3441")]
KETTERING_SITE = [site("Bellhaven of Kettering", "3313 Wilmington Pike", "Kettering", "OH", "45429",
                       phone="(231) 269-5449")]


def test_indistinguishable_same_address_accounts_are_held_not_guessed():
    res, props = reconcile(KETTERING_SITE, KETTERING, True)
    assert [p["kind"] for p in props] == ["HOLD"]
    assert props[0]["ops"] == [] and props[0]["actionable"] is False
    assert sorted(props[0]["account_ids"]) == ["K1", "K2", "K3"]
    assert res[0]["classification"] == "HOLD"


def test_duplicate_survivor_needs_decisive_evidence():
    accts = parents() + [
        acct("O1", "Bellhaven of Owosso", street="1120 W Main St", city="Owosso", state="MI", zip_="48867",
             phone="(734) 503-1363"),
        acct("O2", "Bellhaven of Owosso", street="1120 West Main Street", city="Owosso", state="MI", zip_="48867",
             phone="(330) 383-5991")]
    _, props = reconcile([site("Bellhaven of Owosso", "1120 W Main St", "Owosso", "MI", "48867",
                               phone="(734) 503-1363")], accts, True)
    dup = [p for p in props if p["kind"] == "DUPLICATE"]
    assert len(dup) == 1 and dup[0]["evidence"]["survivor"]["account_id"] == "O1"
    assert dup[0]["ops"][0]["account_id"] == "O2"
    assert "phone matches website" in dup[0]["explanation"]


def test_duplicate_loser_with_billing_history_is_held():
    accts = parents() + [
        acct("S1", "Bellhaven Shores of Erie", street="4930 W Lake Rd", city="Erie", state="PA", zip_="16505"),
        acct("S2", "Harborview Shores of Erie", parent=HP, street="4930 West Lake Road", city="Erie", state="PA",
             zip_="16505", rev=9000, ar=0)]
    _, props = reconcile([site("Bellhaven Shores of Erie", "4930 W Lake Rd", "Erie", "PA", "16505")], accts, True)
    assert not [p for p in props if p["kind"] == "DUPLICATE"]
    hold = [p for p in props if p["kind"] == "HOLD"]
    assert hold and hold[0]["ops"] == []


def test_chow_predecessor_is_not_field_edited():
    accts = parents() + [acct("M1", "Bellhaven of Marietta", parent=CT, street="805 Colegate Drive", city="Marietta",
                              state="OH", zip_="45750", phone="(000) 000-0000", rev=51250, ar=3800)]
    _, props = reconcile([site("Bellhaven of Marietta", "805 Colegate Drive", "Marietta", "OH", "45750",
                               phone="(614) 337-1967")], accts, True)
    assert [p["kind"] for p in props] == ["CHOW"]
    assert props[0]["ops"][0]["fields"]["phone"] == "(614) 337-1967"   # successor carries website values


def test_reparent_is_separate_from_field_edits():
    accts = parents() + [acct("L1", "Bellhaven Crossings of Lima", parent=HP, street="3115 N Cole St", city="Lima",
                              state="OH", zip_="45801", phone="(111) 111-1111", rev=47000, ar=0)]
    _, props = reconcile([site("Bellhaven Crossings of Lima", "3115 N Cole St", "Lima", "OH", "45801")], accts, True)
    rp = next(p for p in props if p["kind"] == "WRONG_PARENT")
    assert rp["ops"] == [{"type": "update", "account_id": "L1", "fields": {"parent_id": BH}}]
    assert rp["risk"] == "high"
    assert any(p["kind"] == "FIELD_UPDATE" for p in props)


# ---------------------------------------------------------------- executor gates

MARIETTA = parents() + [acct("A1", "Bellhaven of Marietta", parent=CT, street="805 Colegate Dr", city="Marietta",
                             state="OH", zip_="45750", phone="(614) 337-1967", rev=51250, ar=3800)]
MARIETTA_SITE = [site("Bellhaven of Marietta", "805 Colegate Dr", "Marietta", "OH", "45750", phone="(614) 337-1967")]


def test_hold_cannot_be_approved(ledger):
    crm, [pid], _ = _setup(ledger, KETTERING, KETTERING_SITE)
    assert ledger.get_proposal(pid)["status"] == L.HOLD
    with pytest.raises(X.ExecutionError):
        X.approve(ledger, pid)
    with pytest.raises(X.ExecutionError):
        X.release(ledger, pid)
    assert crm.writes() == []


def test_approval_alone_never_writes(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    X.approve(ledger, pid)
    X.preview(crm, ledger, pid)
    assert ledger.get_proposal(pid)["status"] == L.APPROVED
    assert crm.writes() == []


def test_writes_disabled_by_default_blocks_execution(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    X.approve(ledger, pid)
    pv = X.preview(crm, ledger, pid)
    with pytest.raises(X.WritesDisabled):
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"])
    assert crm.writes() == [] and ledger.get_proposal(pid)["status"] == L.APPROVED


@pytest.mark.parametrize("phrase", ["", "apply 1", "APPLY 999", "yes"])
def test_wrong_confirmation_phrase_refused(ledger, phrase):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    X.approve(ledger, pid)
    pv = X.preview(crm, ledger, pid)
    with pytest.raises(X.ExecutionError):
        X.execute(crm, ledger, pid, confirmation=phrase, plan_token=pv["token"], writes_enabled=True)
    assert crm.writes() == []


def test_state_change_between_preview_and_confirm_is_refused(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    X.approve(ledger, pid)
    token = X.preview(crm, ledger, pid)["token"]
    crm.accounts["A1"]["updated_at"] = "someone edited it"
    with pytest.raises(X.ExecutionError, match="changed since you reviewed"):
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=token, writes_enabled=True)
    assert crm.writes() == []


def test_superseded_approval_cannot_execute(ledger):
    accts = parents() + [acct("A1", "Old", street="1 A St", city="C", state="OH", zip_="11111", phone="(555) 000-0000")]
    crm = FakeCRM(accts)
    _, [p1] = reconcile([site("New", "1 A St", "C", "OH", "11111")], accts, True)
    pid, _ = ledger.upsert_proposal(1, p1)
    X.approve(ledger, pid)
    _, [p2] = reconcile([site("Newer", "1 A St", "C", "OH", "11111")], accts, True)
    ledger.upsert_proposal(2, p2)
    assert ledger.get_proposal(pid)["status"] == L.SUPERSEDED
    with pytest.raises(X.ExecutionError):
        approve_exec(crm, ledger, pid, approve=False)
    assert crm.writes() == []


def test_direct_reparent_blocked_when_account_became_chow_protected(ledger):
    accts = parents() + [acct("L1", "Bellhaven Crossings of Lima", parent=HP, street="3115 N Cole St", city="Lima",
                              state="OH", zip_="45801", phone="(555) 000-0000", rev=47000, ar=0)]
    crm, ids, props = _setup(ledger, accts, [site("Bellhaven Crossings of Lima", "3115 N Cole St", "Lima", "OH",
                                                  "45801")])
    pid = ids[[p["kind"] for p in props].index("WRONG_PARENT")]
    crm.accounts["L1"]["outstanding_ar"] = 2500          # AR appeared after the proposal
    res = approve_exec(crm, ledger, pid)
    assert res["status"] == L.CONFLICT
    assert any("outstanding_ar" in x or "SOP" in x for x in res["problems"])
    assert crm.writes() == []


def test_chow_blocked_when_successor_already_exists(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    crm.accounts["X9"] = acct("X9", "Bellhaven of Marietta (new)", parent=BH, street="805 Colegate Dr",
                              city="Marietta", state="OH", zip_="45750")
    res = approve_exec(crm, ledger, pid)
    assert res["status"] == L.CONFLICT and "successor" in " ".join(res["problems"])
    assert crm.writes() == []


def test_chow_preserves_all_financials_and_parent(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    before = dict(crm.accounts["A1"])
    res = approve_exec(crm, ledger, pid)
    assert res["status"] == L.VERIFIED
    after = crm.accounts["A1"]
    for k in ("parent_id", "lifetime_revenue", "outstanding_ar", "name", "status", "billing_street"):
        assert after[k] == before[k]
    assert not any(c[0] == "update" and "parent_id" in c[2] for c in crm.writes())
    succ = crm.accounts[res["refs"]["new"]]
    assert succ["parent_id"] == BH and after["chow_current_account"] == succ["account_id"]


def test_already_in_desired_state_is_resolved_without_write(ledger):
    accts = parents() + [acct("F1", "Bellhaven Meadows of Findlay", parent="", street="1800 N Blanchard St",
                              city="Findlay", state="OH", zip_="45840", phone="(330) 975-2492", rev=22000, ar=0)]
    crm, ids, props = _setup(ledger, accts, [site("Bellhaven Meadows of Findlay", "1800 N Blanchard St", "Findlay",
                                                  "OH", "45840", phone="(330) 975-2492")])
    pid = ids[0]
    X.approve(ledger, pid)
    crm.accounts["F1"]["parent_id"] = BH                     # fixed elsewhere (the legacy page) meanwhile
    pv = X.preview(crm, ledger, pid)
    assert pv["noop"] and not pv["problems"]
    res = X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                    writes_enabled=True)
    assert res["status"] == L.RESOLVED and crm.writes() == []   # redundant execution blocked, classified resolved


def test_drift_to_a_different_value_is_a_conflict(ledger):
    crm, ids, _ = _setup(ledger, FINDLAY, FINDLAY_SITE)
    X.approve(ledger, ids[0])
    crm.accounts["F1"]["parent_id"] = CT
    res = approve_exec(crm, ledger, ids[0], approve=False)
    assert res["status"] == L.CONFLICT and crm.writes() == []


def test_noop_proposal_resolves_without_write(ledger):
    accts = parents() + [acct("A1", "Old", street="1 A St", city="C", state="OH", zip_="11111", phone="(555) 000-0000")]
    crm, [pid], _ = _setup(ledger, accts, [site("New", "1 A St", "C", "OH", "11111")])
    X.approve(ledger, pid)
    # simulate: the baseline did not guard 'name' drift because the same value was set by someone else
    crm.accounts["A1"]["name"] = "New"
    ledger.db.execute("UPDATE proposals SET payload=? WHERE id=?", (json.dumps(dict(
        ledger.get_proposal(pid)["payload"], baseline={})), pid))
    res = approve_exec(crm, ledger, pid, approve=False)
    assert res["status"] == L.RESOLVED and crm.writes() == []


def test_readback_failure_never_reports_success(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    real = crm.get_account
    calls = {"n": 0}

    def flaky(aid):
        calls["n"] += 1
        a = real(aid)
        if aid == "A1" and a.get("chow_current_account"):
            a["chow_current_account"] = ""          # read-back does not show the write
        return a
    crm.get_account = flaky
    res = approve_exec(crm, ledger, pid)
    assert res["status"] == L.FAILED and "Readback mismatch" in ledger.get_proposal(pid)["last_error"]


def test_batch_excludes_chow_and_requires_phrase(ledger):
    crm, [pid], _ = _setup(ledger, MARIETTA, MARIETTA_SITE)
    X.approve(ledger, pid)
    tok = X.preview(crm, ledger, pid)["token"]
    with pytest.raises(X.ExecutionError):
        X.execute_batch(crm, ledger, [(pid, tok)], confirmation=X.batch_phrase(1), writes_enabled=True)
    assert crm.writes() == []


def test_batch_executes_each_individually(ledger):
    accts = parents() + [
        acct("A1", "Old1", street="1 A St", city="C", state="OH", zip_="11111", phone="(555) 000-0000"),
        acct("A2", "Old2", street="2 B St", city="C", state="OH", zip_="11111", phone="(555) 000-0000")]
    crm, ids, _ = _setup(ledger, accts, [site("New1", "1 A St", "C", "OH", "11111"),
                                         site("New2", "2 B St", "C", "OH", "11111")])
    items = []
    for pid in ids:
        X.approve(ledger, pid)
        items.append((pid, X.preview(crm, ledger, pid)["token"]))
    with pytest.raises(X.ExecutionError):
        X.execute_batch(crm, ledger, items, confirmation="APPLY BATCH OF 1", writes_enabled=True)
    out = X.execute_batch(crm, ledger, items, confirmation=X.batch_phrase(2), writes_enabled=True)
    assert [r["status"] for r in out] == [L.VERIFIED, L.VERIFIED]
    assert len(crm.writes()) == 2


# ---------------------------------------------------------------- audit & state

def test_audit_log_is_append_only(ledger):
    ledger.log("x", None, a=1)
    with pytest.raises(sqlite3.DatabaseError):
        ledger.db.execute("UPDATE audit_log SET event='tampered'")
    with pytest.raises(sqlite3.DatabaseError):
        ledger.db.execute("DELETE FROM audit_log")


def test_migrates_old_ledger_in_place(tmp_path):
    db = tmp_path / "old.db"
    con = sqlite3.connect(str(db))
    con.executescript("CREATE TABLE proposals (id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT UNIQUE, "
                      "subject_key TEXT, run_id INTEGER, kind TEXT, title TEXT, account_ids TEXT, confidence TEXT, "
                      "payload TEXT, status TEXT, created_at TEXT, updated_at TEXT, last_error TEXT);"
                      "INSERT INTO proposals(fingerprint,subject_key,kind,title,account_ids,confidence,payload,status)"
                      " VALUES('f','s','CHOW','t','[]','high','{\"ops\":[]}','pending');")
    con.commit()
    con.close()
    led = L.Ledger(db)
    assert led.get_proposal(1)["status"] == "pending"


def _legacy_files(d, verified=True):
    (d / "snapshot.json").write_text(json.dumps({"accounts": [{"account_id": BH, "name":
                                                               "Bellhaven Senior Living (Parent Account)"}],
                                                 "facilities": []}))
    con = sqlite3.connect(str(d / "execution_audit.db"))
    con.execute("CREATE TABLE events (at TEXT, event TEXT, account_id TEXT, message TEXT)")
    con.execute("INSERT INTO events VALUES ('2026-11-15T10:14:01', 'STARTED', 'F1', 'PATCH parent_id')")
    if verified:
        con.execute("INSERT INTO events VALUES ('2026-11-15T10:14:02', 'VERIFIED', 'F1', "
                    "'Read-back parent_id matches target')")
    con.commit()
    con.close()


FINDLAY = parents() + [acct("F1", "Bellhaven Meadows of Findlay", parent="", street="1800 N Blanchard St",
                            city="Findlay", state="OH", zip_="45840", phone="(330) 975-2492", rev=22000, ar=0)]
FINDLAY_SITE = [site("Bellhaven Meadows of Findlay", "1800 N Blanchard St", "Findlay", "OH", "45840",
                     phone="(330) 975-2492")]


def test_findlay_receipt_marks_stale_proposal_resolved(ledger, tmp_path):
    _legacy_files(tmp_path)
    crm = FakeCRM(FINDLAY)      # stale data: parent still blank, as in the pre-Findlay snapshot
    run_pipeline(crm, ledger, _scrape(FINDLAY_SITE), legacy_dir=tmp_path)
    p = ledger.proposals(kind="WRONG_PARENT")[0]
    assert p["status"] == L.RESOLVED and "read-back verified" in p["resolution"]
    run_pipeline(crm, ledger, _scrape(FINDLAY_SITE), legacy_dir=tmp_path)    # re-run: stays resolved
    assert ledger.get_proposal(p["id"])["status"] == L.RESOLVED
    assert crm.writes() == []


def test_unverified_legacy_attempt_is_not_a_receipt(ledger, tmp_path):
    _legacy_files(tmp_path, verified=False)
    assert import_legacy_receipts(ledger, tmp_path) == 0


def test_findlay_live_state_produces_no_proposal(ledger):
    fixed = [dict(a, parent_id=BH) if a["account_id"] == "F1" else a for a in FINDLAY]
    run_pipeline(FakeCRM(fixed), ledger, _scrape(FINDLAY_SITE), legacy_dir=False)
    assert not ledger.proposals(kind="WRONG_PARENT")


def test_nine_card_decisions_are_not_execution_approvals(ledger, tmp_path):
    con = sqlite3.connect(str(tmp_path / "review.db"))
    con.execute("CREATE TABLE decisions (case_id TEXT PRIMARY KEY, decision TEXT, updated_at TEXT)")
    con.execute("INSERT INTO decisions VALUES ('marietta','APPROVE','t')")
    con.commit()
    con.close()
    crm = FakeCRM(MARIETTA)
    run_pipeline(crm, ledger, _scrape(MARIETTA_SITE), legacy_dir=tmp_path)
    p = ledger.proposals(kind="CHOW")[0]
    assert p["status"] == L.PENDING and ledger.decisions() == []
    with pytest.raises(X.ExecutionError):
        approve_exec(crm, ledger, p["id"], approve=False)


# ---------------------------------------------------------------- fail closed

def test_incomplete_scrape_creates_no_proposals(ledger):
    r = run_pipeline(FakeCRM(MARIETTA), ledger, _scrape(MARIETTA_SITE, complete=False), legacy_dir=False)
    assert r["status"] == "incomplete" and ledger.proposals() == []


def test_fewer_facilities_than_homepage_count_fails_closed(ledger):
    r = run_pipeline(FakeCRM(MARIETTA), ledger, _scrape(MARIETTA_SITE, homepage_count=35), legacy_dir=False)
    assert r["status"] == "incomplete" and ledger.proposals() == []


def test_incomplete_scan_never_resolves_open_items(ledger):
    crm = FakeCRM(MARIETTA)
    run_pipeline(crm, ledger, _scrape(MARIETTA_SITE), legacy_dir=False)
    run_pipeline(crm, ledger, _scrape([], complete=False), legacy_dir=False)
    assert ledger.proposals(kind="CHOW")[0]["status"] == L.PENDING
    run_pipeline(crm, ledger, _scrape([site("Elsewhere", "9 Z St", "Q", "OH", "99999")]), legacy_dir=False)
    assert ledger.proposals(kind="CHOW")[0]["status"] == L.RESOLVED   # complete scan, no longer observed


def test_crm_listing_failure_fails_run(ledger):
    class Broken(FakeCRM):
        def list_accounts(self, **f):
            raise RuntimeError("Incomplete account listing: got 50 of 121")
    r = run_pipeline(Broken(MARIETTA), ledger, _scrape(MARIETTA_SITE), legacy_dir=False)
    assert r["status"] == "failed" and ledger.proposals() == []


def test_pipeline_saves_fingerprinted_snapshot(ledger, isolated_data):
    r = run_pipeline(FakeCRM(MARIETTA), ledger, _scrape(MARIETTA_SITE), save_snapshot=True, legacy_dir=False)
    srcs = ledger.sources(r["run_id"])
    assert {s["source"] for s in srcs} == {"website", "crm"}
    assert all(len(s["fingerprint"]) == 64 for s in srcs)
    saved = list((isolated_data / "snapshots").glob("run-*.json"))
    assert len(saved) == 1 and json.loads(saved[0].read_text())["fingerprints"]["crm"] == \
        next(s["fingerprint"] for s in srcs if s["source"] == "crm")
