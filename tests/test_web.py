"""Web interface: no writes on GET/scan/startup, CSRF + typed confirmation, dry-run default, no token leak."""
import re

import pytest
from fastapi.testclient import TestClient

from app import config
from app import ledger as L
from app import main
from app.scrape import ScrapeResult
from tests.conftest import CT, FakeCRM, acct, parents, site

SECRET = "tok_SHOULD_NEVER_APPEAR_123"
ACCTS = parents() + [
    acct("A1", "Bellhaven of Marietta", parent=CT, street="805 Colegate Dr", city="Marietta", state="OH",
         zip_="45750", phone="(614) 337-1967", rev=51250, ar=3800),
    acct("A2", "Old Name", street="1 A St", city="C", state="OH", zip_="11111", phone="(555) 000-0000")]
FACS = [site("Bellhaven of Marietta", "805 Colegate Dr", "Marietta", "OH", "45750", phone="(614) 337-1967"),
        site("New Name", "1 A St", "C", "OH", "11111")]


def _scrape():
    r = ScrapeResult()
    r.facilities, r.complete = [dict(f) for f in FACS], True
    return r


@pytest.fixture
def env(monkeypatch):
    crm = FakeCRM(ACCTS)
    monkeypatch.setattr(main.state, "ledger", L.Ledger(":memory:"))
    monkeypatch.setattr(main.state, "crm", crm)
    monkeypatch.setattr(config, "CRM_TOKEN", SECRET)
    import app.scrape
    monkeypatch.setattr(app.scrape, "scrape", _scrape)
    import app.proposals   # legacy Findlay page builds its own client: give it the fake too
    monkeypatch.setattr(app.proposals, "CRMClient", lambda: crm)
    return TestClient(main.app), crm


def _scan(client):
    return client.post("/run", data={"csrf": main.CSRF, "mode": "live"}, follow_redirects=False)


def _pid(kind):
    return next(p["id"] for p in main.state.ledger.proposals() if p["kind"] == kind)


GET_ROUTES = ["/", "/data", "/problems", "/problems?show=all", "/review", "/review?status=", "/history", "/test",
              "/walkthrough", "/submit", "/legacy", "/legacy/cards", "/workspace/build"]


def test_scan_and_every_get_route_never_write(env):
    client, crm = env
    assert _scan(client).status_code == 303
    pages = GET_ROUTES + [f"/proposal/{p['id']}" for p in main.state.ledger.proposals()] + \
        [f"/proposal/{p['id']}/preview" for p in main.state.ledger.proposals()]
    for url in pages:
        r = client.get(url)
        assert r.status_code == 200, url
        assert SECRET not in r.text, f"token leaked on {url}"
    assert crm.writes() == []
    assert main.state.ledger.write_count() == 0


def test_post_without_csrf_is_refused(env):
    client, crm = env
    assert client.post("/run", data={"csrf": "nope"}).status_code == 403
    _scan(client)
    pid = _pid("FIELD_UPDATE")
    assert client.post(f"/proposal/{pid}/decide", data={"action": "approve"}).status_code == 403
    assert client.post(f"/proposal/{pid}/execute", data={"confirmation": f"APPLY {pid}"}).status_code == 403
    assert main.state.ledger.get_proposal(pid)["status"] == L.PENDING


def test_cross_origin_post_refused(env):
    client, _ = env
    r = client.post("/run", data={"csrf": main.CSRF}, headers={"origin": "https://evil.example"})
    assert r.status_code == 403


def _approve_and_token(client, pid):
    client.post(f"/proposal/{pid}/decide", data={"csrf": main.CSRF, "action": "approve"})
    page = client.get(f"/proposal/{pid}/preview").text
    return re.search(r'name="plan_token" value="([0-9a-f]+)"', page).group(1)


def test_dry_run_server_refuses_confirmed_write(env):
    client, crm = env
    _scan(client)
    pid = _pid("FIELD_UPDATE")
    tok = _approve_and_token(client, pid)
    r = client.post(f"/proposal/{pid}/execute", data={"csrf": main.CSRF, "confirmation": f"APPLY {pid}",
                                                      "plan_token": tok, "reviewed": "yes"})
    assert "dry-run" in r.text
    assert crm.writes() == [] and main.state.ledger.get_proposal(pid)["status"] == L.APPROVED


def test_full_ui_flow_with_writes_enabled(env, monkeypatch):
    client, crm = env
    monkeypatch.setattr(config, "WRITES_ENABLED", True)
    _scan(client)
    pid = _pid("FIELD_UPDATE")
    tok = _approve_and_token(client, pid)
    # wrong phrase first: refused
    client.post(f"/proposal/{pid}/execute", data={"csrf": main.CSRF, "confirmation": "APPLY",
                                                  "plan_token": tok, "reviewed": "yes"})
    assert crm.writes() == []
    r = client.post(f"/proposal/{pid}/execute", data={"csrf": main.CSRF, "confirmation": f"APPLY {pid}",
                                                      "plan_token": tok, "reviewed": "yes"})
    assert "verified" in r.text
    assert crm.writes() == [("update", "A2", {"name": "New Name"})]
    assert crm.accounts["A1"]["chow_current_account"] == ""          # CHOW proposal untouched
    events = [a["event"] for a in main.state.ledger.audit(pid)]
    assert "readback" in events and events.count("decision") >= 2


def test_rejected_via_ui_never_executes(env, monkeypatch):
    client, crm = env
    monkeypatch.setattr(config, "WRITES_ENABLED", True)
    _scan(client)
    pid = _pid("CHOW")
    client.post(f"/proposal/{pid}/decide", data={"csrf": main.CSRF, "action": "reject", "note": "no"})
    r = client.post(f"/proposal/{pid}/execute", data={"csrf": main.CSRF, "confirmation": f"APPLY {pid}",
                                                      "plan_token": "x", "reviewed": "yes"})
    assert "rejected" in r.text and crm.writes() == []


def test_removed_token_bearing_redirect(env):
    client, _ = env
    assert client.get("/crm/A1", follow_redirects=False).status_code == 404
