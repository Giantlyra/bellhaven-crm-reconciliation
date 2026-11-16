"""Acceptance checks on the real (private, gitignored) pre-Findlay snapshot. Skipped when it is absent.

Pins the handoff's case-by-case expectations so a matching change cannot silently regress them.
"""
import json

import pytest

from app import config
from app.reconcile import reconcile

SNAP = config.ROOT / "data" / "snapshot.json"
pytestmark = pytest.mark.skipif(not SNAP.exists(), reason="private snapshot not present")

BH = "0015QAPLGS3FVYEEEM"


@pytest.fixture(scope="module")
def run():
    d = json.loads(SNAP.read_text())
    assert len(d["facilities"]) == 35 and len(d["accounts"]) == 121
    res, props = reconcile(d["facilities"], d["accounts"], True, today="2026-11-15")
    return {r.get("facility") or r.get("crm_name"): r for r in res}, props


def _for(props, account_id=None, title=None):
    return [p for p in props if (account_id and account_id in p["account_ids"]) or (title and title in p["title"])]


def test_holds(run):
    res, props = run
    for name in ("Amberly Manor", "Bellhaven at Union Square", "Bellhaven of Kettering"):
        assert res[name]["classification"] == "HOLD", name
    for aid in ("0015D74ZLRY810RGY5", "001GNU41AVXZRLLJ9P", "001WR41PYNWXCAE2X4", "001B7XZAA3AFALS9GP",
                "0016KTS1UAWBRXS09J"):
        touching = [p for p in props for op in p["ops"] if op.get("account_id") == aid]
        assert touching == [], f"{aid} must not be modified"


def test_chow_marietta_tiffin_never_direct_reparent(run):
    _, props = run
    for aid in ("001A34WFSUYHCRBLFT", "001U6RW32TY0WSXZZB"):
        ps = _for(props, aid)
        assert [p["kind"] for p in ps] == ["CHOW"]
        assert ps[0]["ops"][0]["type"] == "create" and ps[0]["ops"][0]["fields"]["parent_id"] == BH
        assert ps[0]["ops"][1] == {"type": "update", "account_id": aid, "fields": {"chow_current_account": "$ref:new"}}


def test_lima_direct_reparent(run):
    _, props = run
    rp = [p for p in _for(props, "001LGFPBJY4N9MB6KL") if p["kind"] == "WRONG_PARENT"]
    assert rp and rp[0]["ops"] == [{"type": "update", "account_id": "001LGFPBJY4N9MB6KL",
                                    "fields": {"parent_id": BH}}]


def test_owosso_survivor(run):
    _, props = run
    d = [p for p in props if p["kind"] == "DUPLICATE" and "001QU150PM4Z15UA71" in p["account_ids"]]
    assert d and d[0]["evidence"]["survivor"]["account_id"] == "001EGU7BMJ942ZTRE6"


def test_aliases_are_reviewable_renames(run):
    res, _ = run
    for name in ("Bellhaven of Chagrin Falls", "Bellhaven of Chesterton", "Bellhaven Willow Creek"):
        assert "ALIAS" in res[name]["classification"] or "FIELD_UPDATE" in res[name]["classification"]


def test_carlisle_and_batavia_not_conflated(run):
    _, props = run
    for t in ("Bellhaven of Carlisle", "Bellhaven of Batavia"):
        p = _for(props, title=t)
        assert p and p[0]["kind"] == "WEBSITE_ONLY" and p[0]["ops"][0]["type"] == "create"


def test_findlay_pre_fix_snapshot_proposal_is_exactly_the_applied_change(run):
    """On the stale snapshot the engine re-derives the Findlay fix; it must equal what was applied, so the
    imported receipt covers it and the pipeline resolves it instead of re-proposing."""
    _, props = run
    rp = [p for p in _for(props, "001UKEFGADQ8YCZ4YM") if p["kind"] == "WRONG_PARENT"]
    assert rp[0]["ops"] == [{"type": "update", "account_id": "001UKEFGADQ8YCZ4YM", "fields": {"parent_id": BH}}]
