"""Investigation categories are display-only: they never change status or execution eligibility."""
import inspect

import pytest

from app import exec_queue as Q
from app import executor as X
from app import investigation as I
from app import ledger as L

OPEN_IDS = {38, 41, 46, 49, 53, 66, 71}


def test_every_case_has_all_reviewer_fields():
    assert set(I.CASES) == OPEN_IDS
    for pid, c in I.CASES.items():
        assert c["category"] in I.CATEGORIES
        for k in ("place", "known", "uncertain", "confirm", "next"):
            assert c[k].strip(), (pid, k)


def test_assigned_categories():
    cat = {pid: c["category"] for pid, c in I.CASES.items()}
    assert {p for p, c in cat.items() if c == "CHOW_REBRAND"} == {41, 49, 66}
    assert cat[46] == "ADDRESS"
    assert {p for p, c in cat.items() if c == "IDENTITY"} == {38, 53, 71}  # #71: not an ownership change
    assert "confirmed" not in I.CATEGORIES["CHOW_REBRAND"][0].lower()


@pytest.mark.parametrize("status", ["pending", "hold", "approved"])
def test_card_reports_live_status_and_is_pure(status):
    p = {"id": 71, "status": status, "kind": "WEBSITE_ONLY"}
    before = dict(p)
    card = I.for_proposal(p)
    assert card["status"] == status and p == before


@pytest.mark.parametrize("status", sorted(I.CLOSED))
def test_closed_proposals_show_no_card(status):
    assert I.for_proposal({"id": 41, "status": status}) is None
    assert I.for_proposal({"id": 56, "status": "verified"}) is None  # Owosso
    assert I.for_proposal({"id": 60, "status": "verified"}) is None  # Tiffin


def test_execution_paths_never_read_categories():
    for mod in (X, Q, L):
        src = inspect.getsource(mod)
        assert "investigation" not in src and "CATEGORIES" not in src, mod.__name__


def test_labels_do_not_change_status_or_eligibility(ledger):
    from tests.test_address_purpose import PO, PO_SITE, _load
    crm, ids = _load(ledger, PO, PO_SITE)
    pid = ids[0]
    saved = I.CASES.get(pid)
    I.CASES[pid] = dict(I.CASES[46])  # pretend this proposal is categorised
    try:
        X.hold(ledger, pid, "held")
        status = ledger.get_proposal(pid)["status"]
        assert I.for_proposal(ledger.get_proposal(pid))["label"] == "Address verification"
        assert ledger.get_proposal(pid)["status"] == status == L.HOLD
        with pytest.raises(X.ExecutionError):
            X.approve(ledger, pid, "a note")
        assert crm.writes() == []
    finally:
        if saved is None:
            I.CASES.pop(pid, None)
        else:
            I.CASES[pid] = saved
