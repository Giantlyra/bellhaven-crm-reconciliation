"""Evidence comparison on the proposal page: side-by-side website vs CRM values, "Not available" never counted as a
mismatch, competing candidates, source timestamps, record freshness, and no writes from viewing."""
import json

import pytest
from fastapi.testclient import TestClient

from app import config, main
from app import evidence as E
from app import ledger as L
from app.pipeline import run_pipeline
from app.scrape import ScrapeResult
from tests.conftest import BH, CT, FakeCRM, acct, parents, site

# Monroe-like case: the Bellhaven account has the wrong phone; two other-parent accounts share the address.
ACCTS = parents() + [
    acct("M1", "Bellhaven Gardens of Monroe", street="750 Stewart Rd", city="Monroe", state="MI", zip_="48162",
         phone="(814) 291-2902"),
    acct("M2", "Cedar Trail of Monroe", parent=CT, street="750 Stewart Road", city="Monroe", state="MI",
         zip_="48162", phone="(216) 748-7799"),
]
SITE = [site("Bellhaven Gardens of Monroe", "750 Stewart Rd", "Monroe", "MI", "48162", phone="(814) 412-2218",
             slug="bellhaven-gardens-of-monroe")]


def _scrape(facs):
    def fn():
        r = ScrapeResult()
        r.facilities, r.complete = [dict(f) for f in facs], True
        return r
    return fn


@pytest.fixture
def setup(monkeypatch):
    led = L.Ledger(":memory:")
    crm = FakeCRM(ACCTS)
    monkeypatch.setattr(main.state, "ledger", led)
    monkeypatch.setattr(main.state, "crm", crm)
    run_pipeline(crm, led, _scrape(SITE), provenance="live", legacy_dir=False, save_snapshot=True)
    phone = next(p for p in led.proposals() if p["kind"] == "FIELD_UPDATE" and "M1" in p["account_ids"])
    return TestClient(main.app), led, crm, phone["id"]


def test_missing_field_is_not_available_never_a_mismatch():
    web = {"name": "A", "street": "1 Main St", "city": "X", "state": "OH", "zip": "11111", "phone": ""}
    crm = {"name": "A", "billing_street": "1 Main Street", "billing_city": "X", "billing_state": "OH",
           "billing_zip": "11111", "phone": "(555) 111-2222", "status": "Active"}
    rows = {r["label"]: r for r in E.compare(web, crm)}
    assert rows["Phone"]["result"] == "not available" and rows["Phone"]["website"] == E.NA
    assert rows["Street"]["result"] == "match"            # abbreviations normalised
    assert rows["Account status"]["result"] == "not available"   # the website never publishes status
    assert all(r["result"] != "differs" for r in rows.values())
    assert all(r["result"] == "not available" for r in E.compare(web, None))


def test_proposal_page_shows_side_by_side_evidence(setup):
    c, led, crm, pid = setup
    html = c.get(f"/proposal/{pid}").text
    assert "Evidence comparison" in html
    assert 'href="http://site/communities/bellhaven-gardens-of-monroe"' in html     # clickable source URL
    assert "(814) 412-2218" in html and "(814) 291-2902" in html
    assert "Not available" in html                                                   # administrator / status etc.
    for q in ("Why do we think these records are the same facility?",
              "Which source supports the proposed correction?",
              "What evidence is still missing?", "What precisely would change if approved and confirmed?"):
        assert q in html
    assert "PATCH /accounts/M1: phone: &#39;(814) 291-2902&#39; → &#39;(814) 412-2218&#39;" in html
    assert "No other field is sent" in html
    assert "M2" in html and "Cedar Trail of Monroe" in html                         # competing candidate, named
    assert "Evidence captured in scan #1" in html and "this CRM account is unchanged" in html


def test_viewing_evidence_writes_nothing(setup):
    c, led, crm, pid = setup
    before = (len(led.db.execute("SELECT * FROM audit_log").fetchall()), len(led.decisions(1000)))
    for p in led.proposals():
        assert c.get(f"/proposal/{p['id']}").status_code == 200
    after = (len(led.db.execute("SELECT * FROM audit_log").fetchall()), len(led.decisions(1000)))
    assert crm.writes() == [] and before == after
    assert led.get_proposal(pid)["status"] == L.PENDING


def test_record_freshness_reports_changed_fields(tmp_path):
    snap = {"facilities": [dict(SITE[0], phone="(000) 000-0000")],
            "accounts": [dict(ACCTS[2], status="Inactive")]}
    (tmp_path / "snapshots").mkdir()
    (tmp_path / "snapshots" / "run-0007-x.json").write_text(json.dumps(snap))
    fr = E.record_freshness({"website": SITE[0], "crm": ACCTS[2]}, 7, str(tmp_path))
    assert fr["website"] == ["phone"] and fr["crm"] == ["status"]
    fr = E.record_freshness({"website": dict(SITE[0], source_url="gone"), "crm": dict(ACCTS[2], account_id="ZZ")},
                            7, str(tmp_path))
    assert fr["website"] == ["community no longer listed"] and fr["crm"] == ["account not found"]


def test_hold_candidates_show_identity_check(monkeypatch):
    led = L.Ledger(":memory:")
    crm = FakeCRM(parents() + [acct("C9", "Amberly Manor", parent=CT, street="918 S Nevada Ave",
                                    city="Colorado Springs", state="CO", zip_="80903")])
    monkeypatch.setattr(main.state, "ledger", led)
    monkeypatch.setattr(main.state, "crm", crm)
    run_pipeline(crm, led, _scrape([site("Amberly Manor", "4390 Darrow Rd", "Hudson", "OH", "44236")]),
                 provenance="live", legacy_dir=False, save_snapshot=True)
    hold = next(p for p in led.proposals() if p["kind"] == "HOLD")
    html = TestClient(main.app).get(f"/proposal/{hold['id']}").text
    assert "C9" in html and "Street differs" in html and "Name match" in html
    assert "Nothing. This item has no CRM operation" in html
    assert crm.writes() == []
    assert config.SNAPSHOT_DIR.exists()          # the snapshot went to the isolated test directory
