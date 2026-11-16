import pytest

from app.policy import check_ops, chow_required
from app.reconcile import reconcile
from tests.conftest import BH, CT, acct, parents, site

W = [site("Bellhaven of Tiffin", "45 St Lawrence Dr", "Tiffin", "OH", "44883")]


def _crm(rev, ar):
    return parents() + [acct("A1", "Bellhaven of Tiffin", parent=CT, street="45 St Lawrence Dr", city="Tiffin",
                             state="OH", zip_="44883", phone="(555) 000-0000", rev=rev, ar=ar)]


def test_revenue_and_ar_requires_chow():
    _, props = reconcile(W, _crm(40000, 2000), True)
    p = props[0]
    assert p["kind"] == "CHOW"
    create, link = p["ops"]
    assert create["type"] == "create" and create["fields"]["parent_id"] == BH
    assert link == {"type": "update", "account_id": "A1", "fields": {"chow_current_account": "$ref:new"}}
    # the original account's parent is never in any write
    assert not any(o.get("account_id") == "A1" and "parent_id" in o["fields"] for o in p["ops"])


@pytest.mark.parametrize("rev,ar", [(40000, 0), (0, 2000), (0, 0)])
def test_direct_reparent_when_not_protected(rev, ar):
    _, props = reconcile(W, _crm(rev, ar), True)
    props = [p for p in props if p["kind"] != "FIELD_UPDATE"]
    assert props[0]["kind"] == "WRONG_PARENT"
    assert props[0]["ops"] == [{"type": "update", "account_id": "A1", "fields": {"parent_id": BH}}]


@pytest.mark.parametrize("rev,ar", [(None, 0), ("", 5), (100, "n/a"), (True, 5)])
def test_missing_or_malformed_financials_block(rev, ar):
    assert chow_required({"lifetime_revenue": rev, "outstanding_ar": ar})[0] is None
    _, props = reconcile(W, _crm(rev, ar), True)
    assert props[0]["kind"] == "HOLD"
    assert props[0]["ops"] == [] and props[0]["actionable"] is False


def test_recheck_blocks_reparent_if_account_became_protected():
    ops = [{"type": "update", "account_id": "A1", "fields": {"parent_id": BH}}]
    fresh = {"A1": acct("A1", "x", parent=CT, rev=5000, ar=100)}
    assert check_ops(ops, fresh)
    fresh = {"A1": acct("A1", "x", parent=CT, rev=5000, ar=0)}
    assert check_ops(ops, fresh) == []
