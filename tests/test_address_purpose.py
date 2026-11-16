"""Ashtabula-style case: a PO-box billing address must not be overwritten with the facility's street
address until a human verifies what each address is for (#46)."""
import pytest

from app import executor as X
from app import ledger as L
from app.reconcile import reconcile
from tests.conftest import FakeCRM, acct, approve_exec, parents, site

PO = parents() + [acct("A46", "Bellhaven of Ashtabula", street="PO Box 517", city="Ashtabula", state="OH",
                       zip_="44004", phone="(260) 440-4975")]
PO_SITE = [site("Bellhaven of Ashtabula", "3156 W Prospect Rd", "Ashtabula", "OH", "44004", phone="(260) 440-4975")]
OTHER = parents() + [acct("A9", "Bellhaven of Elsewhere", street="10 Main St", city="Kent", state="OH",
                          zip_="44240", phone="(330) 111-2222")]
OTHER_SITE = [site("Bellhaven of Elsewhere", "10 Main St", "Kent", "OH", "44240", phone="(330) 999-8888")]
NOTE = ("Potential mailing-versus-physical-address discrepancy. The PO Box appears to serve as a billing or "
        "mailing address. Preserve both address records until the facility's physical location and "
        "mailing-address purpose are verified. Do not overwrite either address without sufficient evidence.")


def _load(ledger, accounts, sites):
    crm = FakeCRM(accounts)
    _, props = reconcile(sites, list(crm.accounts.values()), True)
    ids = [ledger.upsert_proposal(1, p)[0] for p in props]
    return crm, ids


def _po_pid(ledger, ids):
    hits = [i for i in ids if X.address_purpose_check(ledger.get_proposal(i))]
    assert len(hits) == 1
    return hits[0]


def test_po_box_overwrite_is_flagged_with_both_addresses(ledger):
    _, ids = _load(ledger, PO, PO_SITE)
    chk = X.address_purpose_check(ledger.get_proposal(_po_pid(ledger, ids)))
    assert chk["mailing"] == "PO Box 517" and chk["physical"] == "3156 W Prospect Rd"
    assert chk["status"] == "UNVERIFIED" and "PO box" in chk["reason"]


def test_held_po_box_proposal_cannot_be_approved_executed_or_batched(ledger):
    crm, ids = _load(ledger, PO, PO_SITE)
    pid = _po_pid(ledger, ids)
    X.hold(ledger, pid, NOTE)
    assert ledger.get_proposal(pid)["status"] == L.HOLD
    with pytest.raises(X.ExecutionError):
        X.approve(ledger, pid, "ok")
    with pytest.raises(X.ExecutionError):
        X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token="x", writes_enabled=True)
    with pytest.raises(X.ExecutionError):
        X.execute_batch(crm, ledger, [{"pid": pid, "token": "x"}], confirmation=X.batch_phrase(1),
                        writes_enabled=True)
    assert pid not in [p["id"] for p in ledger.proposals(status=L.APPROVED)]  # /review batchable source
    assert crm.writes() == []
    assert crm.accounts["A46"]["billing_street"] == "PO Box 517"


def test_release_and_approval_need_an_evidence_note(ledger):
    _, ids = _load(ledger, PO, PO_SITE)
    pid = _po_pid(ledger, ids)
    X.hold(ledger, pid, NOTE)
    with pytest.raises(X.ExecutionError, match="evidence note"):
        X.release(ledger, pid, "")
    assert ledger.get_proposal(pid)["status"] == L.HOLD
    X.release(ledger, pid, "Finance confirmed PO Box 517 is not used for invoices")
    with pytest.raises(X.ExecutionError, match="evidence note"):
        X.approve(ledger, pid, "  ")
    assert ledger.get_proposal(pid)["status"] == L.PENDING


def test_unrelated_proposals_are_unaffected(ledger):
    crm, ids = _load(ledger, OTHER, OTHER_SITE)
    assert ids and not any(X.address_purpose_check(ledger.get_proposal(i)) for i in ids)
    pid = ids[0]
    X.approve(ledger, pid, "")  # no note required for ordinary field updates
    r = approve_exec(crm, ledger, pid, approve=False)
    assert ledger.get_proposal(pid)["status"] == L.VERIFIED, r
