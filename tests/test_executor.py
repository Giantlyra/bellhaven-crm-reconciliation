import pytest

from app import executor as X
from app import ledger as L
from app.reconcile import reconcile
from tests.conftest import BH, CT, FakeCRM, acct, approve_exec, parents, site


def setup(ledger, accounts, facilities):
    crm = FakeCRM(accounts)
    _, props = reconcile(facilities, list(crm.accounts.values()), True)
    ids = [ledger.upsert_proposal(1, p)[0] for p in props]
    return crm, ids


CHOW_ACCTS = parents() + [acct("A1", "Bellhaven of Marietta", parent=CT, street="805 Colegate Dr", city="Marietta",
                               state="OH", zip_="45750", phone="(614) 337-1967", rev=51250, ar=3800)]
CHOW_SITE = [site("Bellhaven of Marietta", "805 Colegate Dr", "Marietta", "OH", "45750", phone="(614) 337-1967")]


def test_chow_creates_and_links_and_preserves_original(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    before = dict(crm.accounts["A1"])
    res = approve_exec(crm, ledger, pid)
    assert res["status"] == L.VERIFIED
    new_id = res["refs"]["new"]
    old = crm.accounts["A1"]
    assert old["chow_current_account"] == new_id
    assert {k: v for k, v in old.items() if k != "chow_current_account"} == \
           {k: v for k, v in before.items() if k != "chow_current_account"}
    assert crm.accounts[new_id]["parent_id"] == BH


def test_chow_partial_failure_retry_does_not_recreate(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    crm.fail_update_for.add("A1")
    assert approve_exec(crm, ledger, pid)["status"] == L.FAILED
    created = [c for c in crm.calls if c[0] == "create"]
    assert len(created) == 1
    crm.fail_update_for.clear()
    res = approve_exec(crm, ledger, pid)  # retry
    assert res["status"] == L.VERIFIED
    assert len([c for c in crm.calls if c[0] == "create"]) == 1
    assert crm.accounts["A1"]["chow_current_account"] == res["refs"]["new"]


def test_uncertain_create_is_resolved_by_lookup_not_blind_retry(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    crm.create_lost = True  # server created it but client saw a timeout
    assert approve_exec(crm, ledger, pid)["status"] == L.FAILED
    res = approve_exec(crm, ledger, pid)
    assert res["status"] == L.VERIFIED
    assert len([c for c in crm.calls if c[0] == "create"]) == 1
    assert sum(1 for a in crm.accounts.values() if a["name"] == "Bellhaven of Marietta" and a["parent_id"] == BH) == 1


def test_duplicate_inactivation(ledger):
    accts = parents() + [
        acct("A1", "Bellhaven of Owosso", street="1120 W Main St", city="Owosso", state="MI", zip_="48867",
             phone="(734) 503-1363"),
        acct("A2", "Bellhaven of Owosso", street="1120 West Main Street", city="Owosso", state="MI", zip_="48867",
             phone="(330) 383-5991", note="keep me")]
    crm, [pid] = setup(ledger, accts, [site("Bellhaven of Owosso", "1120 W Main St", "Owosso", "MI", "48867",
                                            phone="(734) 503-1363")])
    assert approve_exec(crm, ledger, pid)["status"] == L.VERIFIED
    a2 = crm.accounts["A2"]
    assert a2["duplicate_of_account"] == "A1" and a2["status"] == "Inactive"
    assert a2["note"].startswith("keep me\n")


def test_rejected_never_writes(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    X.reject(ledger, pid, "no")
    with pytest.raises(X.ExecutionError):
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token="x", writes_enabled=True)
    with pytest.raises(X.ExecutionError):
        X.approve(ledger, pid)
    with pytest.raises(X.ExecutionError):
        approve_exec(crm, ledger, pid, approve=False)
    assert crm.writes() == []


def test_pending_cannot_execute_without_approval(ledger):
    crm, [pid] = setup(ledger, CHOW_ACCTS, CHOW_SITE)
    with pytest.raises(X.ExecutionError):
        approve_exec(crm, ledger, pid, approve=False)
    assert crm.writes() == []


def test_approved_field_update_writes_and_verifies(ledger):
    accts = parents() + [acct("A1", "Chesterton Senior Commons", street="1250 NW Franklin St", city="Chesterton",
                              state="IN", zip_="46304", phone="(216) 551-3978", care="Skilled Nursing")]
    crm, [pid] = setup(ledger, accts, [site("Bellhaven of Chesterton", "1250 NW Franklin Street", "Chesterton", "IN",
                                            "46304", phone="(216) 551-3978", care=("Short-Term Rehabilitation & Nursing",))])
    assert approve_exec(crm, ledger, pid)["status"] == L.VERIFIED
    assert crm.writes() == [("update", "A1", {"name": "Bellhaven of Chesterton"})]
    assert all(o["status"] == "verified" for o in ledger.operations(pid))


def test_readback_mismatch_marks_failed(ledger):
    accts = parents() + [acct("A1", "Old", street="1 A St", city="C", state="OH", zip_="11111", phone="(555) 000-0000")]
    crm, [pid] = setup(ledger, accts, [site("New", "1 A St", "C", "OH", "11111")])
    real = crm.update_account
    crm.update_account = lambda aid, f: real(aid, {"name": "Silently ignored"})
    assert approve_exec(crm, ledger, pid)["status"] == L.FAILED
    assert "Readback mismatch" in ledger.get_proposal(pid)["last_error"]


def test_stale_record_conflict_stops_write(ledger):
    accts = parents() + [acct("A1", "Bellhaven of Zanesville", parent=CT, street="2680 Maple Ave", city="Zanesville",
                              state="OH", zip_="43701", phone="(555) 000-0000")]
    crm, [pid] = setup(ledger, accts, [site("Bellhaven of Zanesville", "2680 Maple Ave", "Zanesville", "OH", "43701")])
    crm.accounts["A1"]["outstanding_ar"] = 500  # changed after the proposal was generated
    crm.accounts["A1"]["lifetime_revenue"] = 1000
    assert approve_exec(crm, ledger, pid)["status"] == L.CONFLICT
    assert crm.writes() == []
