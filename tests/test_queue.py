"""Controlled execution queue: eligibility gate, automatic pre-write validation, stop-on-error, protected-field
diff, receipts, dry-run refusal. Never approves anything by itself."""
import json

import pytest
from fastapi.testclient import TestClient

from app import config
from app import exec_queue as Q
from app import executor as X
from app import ledger as L
from app import main
from app.reconcile import reconcile
from tests.conftest import BH, CT, FakeCRM, acct, parents, site


@pytest.fixture(autouse=True)
def bh_parent(monkeypatch):
    monkeypatch.setattr(Q, "BELLHAVEN_PARENT_IDS", {BH})


class ContactCRM(FakeCRM):
    def __init__(self, accounts, contacts=()):
        super().__init__(accounts)
        self.contacts = [dict(c) for c in contacts]

    def list_contacts(self, **f):
        self.calls.append(("contacts", f))
        return [dict(c) for c in self.contacts]


ACCTS = parents() + [
    acct("A1", "Bellhaven of Goshen", street="1610 College Ave", city="Goshen", state="IN", zip_="46526",
         phone="(517) 409-8156", rev=121000),
    acct("A2", "Bellhaven of Marion", street="199 Barks Rd W", city="Marion", state="OH", zip_="43302",
         phone="(330) 314-3109"),
    acct("A3", "Riverbend Manor Care Center", street="150 River St", city="Chagrin Falls", state="OH",
         zip_="44022", phone="(231) 283-7448"),                                       # material rename
    acct("A4", "Bellhaven of Lima", parent=CT, street="3115 N Cole St", city="Lima", state="OH", zip_="45801",
         phone="(231) 539-3617"),                                                     # parent change
    acct("A5", "Bellhaven Rehab and Nursing of Grove City", street="3985 Broadway", city="Grove City", state="OH",
         zip_="43123", phone="(614) 555-7729"),                                       # similar rename
]
SITES = [site("Bellhaven of Goshen", "1610 College Ave", "Goshen", "IN", "46526", phone="(330) 405-6040",
              slug="goshen"),
         site("Bellhaven of Marion", "199 Barks Rd W", "Marion", "OH", "43302", phone="(517) 847-7948",
              slug="marion"),
         site("Bellhaven of Chagrin Falls", "150 River St", "Chagrin Falls", "OH", "44022", phone="(231) 283-7448",
              slug="chagrin"),
         site("Bellhaven of Lima", "3115 N Cole St", "Lima", "OH", "45801", phone="(231) 539-3617", slug="lima"),
         site("Bellhaven Rehabilitation & Nursing of Grove City", "3985 Broadway", "Grove City", "OH", "43123",
              phone="(614) 555-7729", slug="grove")]
CONTACTS = [{"contact_id": "C1", "account_id": "A1", "name": "Tanya", "title": "Administrator", "phone": "",
             "email": "", "is_active": True, "updated_at": "t"}]


def build(ledger, accounts=ACCTS, sites=SITES, contacts=CONTACTS):
    crm = ContactCRM(accounts, contacts)
    _, props = reconcile([dict(s) for s in sites], list(crm.accounts.values()), True)
    for p in props:
        ledger.upsert_proposal(1, p)
    web = {s["source_url"]: dict(s) for s in sites}
    return crm, web, (lambda url: dict(web[url]))


def pid_for(ledger, account_id, kind="FIELD_UPDATE"):
    for p in ledger.proposals():
        if p["kind"] == kind and account_id in json.dumps(p["payload"]["ops"]):
            return p["id"]
    raise AssertionError(f"no {kind} proposal for {account_id}")


def queue_items(crm, ledger, pids, fetch):
    items = Q.preview_queue(crm, ledger, pids, fetch)
    assert all(it["ok"] for it in items), [it["problems"] for it in items]
    return [(it["pid"], it["pv"]["token"]) for it in items]


def test_eligibility_gate(ledger):
    build(ledger)
    goshen, marion = pid_for(ledger, "A1"), pid_for(ledger, "A2")
    grove = pid_for(ledger, "A5")
    assert Q.eligibility(ledger.get_proposal(goshen)) == []
    assert Q.eligibility(ledger.get_proposal(marion)) == []
    assert Q.eligibility(ledger.get_proposal(grove)) == []           # 'Rehab and' -> 'Rehabilitation &'
    rename = Q.eligibility(ledger.get_proposal(pid_for(ledger, "A3")))
    assert any("material rename" in r for r in rename)
    parent = Q.eligibility(ledger.get_proposal(pid_for(ledger, "A4", "WRONG_PARENT")))
    assert parent and "always manual review" in parent[0]
    lima_phone = [p for p in ledger.proposals() if p["kind"] == "FIELD_UPDATE" and "A4" in json.dumps(p["payload"])]
    for p in lima_phone:                                              # account not yet under Bellhaven
        assert any("not already under Bellhaven" in r for r in Q.eligibility(p))


def test_unapproved_items_cannot_be_queued_and_nothing_is_auto_approved(ledger):
    crm, _, fetch = build(ledger)
    goshen = pid_for(ledger, "A1")
    items = Q.preview_queue(crm, ledger, [goshen], fetch)
    assert not items[0]["ok"] and "approved by a human" in items[0]["problems"][0]
    assert ledger.get_proposal(goshen)["status"] == L.PENDING
    with pytest.raises(X.ExecutionError):
        Q.run_queue(crm, ledger, [(goshen, "x")], confirmation="APPLY QUEUE OF 1", writes_enabled=True,
                    fetch_site=fetch)
    assert crm.writes() == []


def test_manual_review_items_are_refused_even_if_approved(ledger):
    crm, _, fetch = build(ledger)
    lima = pid_for(ledger, "A4", "WRONG_PARENT")
    X.approve(ledger, lima)
    assert not Q.preview_queue(crm, ledger, [lima], fetch)[0]["ok"]
    with pytest.raises(X.ExecutionError, match="manual review only"):
        Q.run_queue(crm, ledger, [(lima, X.preview(crm, ledger, lima)["token"])], confirmation="APPLY QUEUE OF 1",
                    writes_enabled=True, fetch_site=fetch)
    assert crm.writes() == []


def test_dry_run_refuses_whole_queue_before_any_write(ledger):
    crm, _, fetch = build(ledger)
    pids = [pid_for(ledger, "A1"), pid_for(ledger, "A2")]
    for p in pids:
        X.approve(ledger, p)
    items = queue_items(crm, ledger, pids, fetch)
    with pytest.raises(X.WritesDisabled):
        Q.run_queue(crm, ledger, items, confirmation="APPLY QUEUE OF 2", fetch_site=fetch)   # config: dry-run
    assert crm.writes() == []
    assert any(a["event"] == "queue_refused" for a in ledger.audit())


def test_wrong_phrase_refused(ledger):
    crm, _, fetch = build(ledger)
    p = pid_for(ledger, "A1")
    X.approve(ledger, p)
    with pytest.raises(X.ExecutionError, match="APPLY QUEUE OF 1"):
        Q.run_queue(crm, ledger, queue_items(crm, ledger, [p], fetch), confirmation="APPLY 1", writes_enabled=True,
                    fetch_site=fetch)
    assert crm.writes() == []


def test_happy_path_verifies_each_item_with_receipts(ledger, isolated_data):
    crm, _, fetch = build(ledger)
    pids = [pid_for(ledger, "A1"), pid_for(ledger, "A2")]
    for p in pids:
        X.approve(ledger, p)
    out = Q.run_queue(crm, ledger, queue_items(crm, ledger, pids, fetch), confirmation="APPLY QUEUE OF 2",
                      writes_enabled=True, fetch_site=fetch)
    assert not out["stopped_early"]
    assert [r["status"] for r in out["results"]] == [L.VERIFIED, L.VERIFIED]
    assert all(r["protected_ok"] and r["contacts_checked"] for r in out["results"])
    assert crm.accounts["A1"]["phone"] == "(330) 405-6040" and crm.accounts["A1"]["lifetime_revenue"] == 121000
    assert crm.accounts["A2"]["phone"] == "(517) 847-7948"
    assert [c for c in crm.writes()] == [("update", "A1", {"phone": "(330) 405-6040"}),
                                         ("update", "A2", {"phone": "(517) 847-7948"})]
    events = [a["event"] for a in ledger.audit()]
    assert {"queue_started", "queue_item", "queue_finished", "readback"} <= set(events)
    receipt = json.loads(open(out["receipt_file"]).read())
    assert receipt["results"][0]["before"] == {"phone": "(517) 409-8156"}


def test_stop_on_error_leaves_later_items_untouched(ledger):
    crm, _, fetch = build(ledger)
    pids = [pid_for(ledger, "A1"), pid_for(ledger, "A2")]
    for p in pids:
        X.approve(ledger, p)
    items = queue_items(crm, ledger, pids, fetch)
    crm.fail_update_for.add("A1")
    out = Q.run_queue(crm, ledger, items, confirmation="APPLY QUEUE OF 2", writes_enabled=True, fetch_site=fetch)
    assert out["stopped_early"]
    assert [r["status"] for r in out["results"]] == [L.FAILED, "not_run"]
    assert crm.accounts["A2"]["phone"] == "(330) 314-3109"
    assert ("update", "A2", {"phone": "(517) 847-7948"}) not in crm.writes()


def test_website_change_blocks_item_at_run_time(ledger):
    crm, web, fetch = build(ledger)
    pids = [pid_for(ledger, "A1"), pid_for(ledger, "A2")]
    for p in pids:
        X.approve(ledger, p)
    items = queue_items(crm, ledger, pids, fetch)
    web[SITES[0]["source_url"]]["phone"] = "(999) 999-9999"          # website changed after review
    out = Q.run_queue(crm, ledger, items, confirmation="APPLY QUEUE OF 2", writes_enabled=True, fetch_site=fetch)
    assert out["results"][0]["status"] == "blocked" and out["results"][1]["status"] == "not_run"
    assert crm.writes() == []


def test_crm_drift_after_review_blocks(ledger):
    crm, _, fetch = build(ledger)
    p = pid_for(ledger, "A1")
    X.approve(ledger, p)
    items = queue_items(crm, ledger, [p], fetch)
    crm.accounts["A1"]["outstanding_ar"] = 500                         # someone changed the account
    out = Q.run_queue(crm, ledger, items, confirmation="APPLY QUEUE OF 1", writes_enabled=True, fetch_site=fetch)
    assert out["stopped_early"] and out["results"][0]["status"] in ("blocked", "refused")
    assert crm.writes() == []


def test_protected_field_change_is_detected_and_stops(ledger):
    class SideEffectCRM(ContactCRM):
        def update_account(self, aid, fields):
            r = super().update_account(aid, fields)
            self.accounts[aid]["note"] = "server-side side effect"
            return r
    crm = SideEffectCRM(ACCTS, CONTACTS)
    _, props = reconcile([dict(s) for s in SITES], list(crm.accounts.values()), True)
    for pr in props:
        ledger.upsert_proposal(1, pr)
    fetch = {s["source_url"]: dict(s) for s in SITES}.__getitem__
    pids = [pid_for(ledger, "A1"), pid_for(ledger, "A2")]
    for p in pids:
        X.approve(ledger, p)
    out = Q.run_queue(crm, ledger, queue_items(crm, ledger, pids, fetch), confirmation="APPLY QUEUE OF 2",
                      writes_enabled=True, fetch_site=fetch)
    first = out["results"][0]
    assert first["status"] == "verified_but_protected_field_changed" and "note" in first["problems"][0]
    assert out["results"][1]["status"] == "not_run" and out["stopped_early"]


def test_queue_pages(monkeypatch):
    led = L.Ledger(":memory:")
    crm, web, fetch = build(led)
    monkeypatch.setattr(main.state, "ledger", led)
    monkeypatch.setattr(main.state, "crm", crm)
    monkeypatch.setattr(Q, "default_fetch_site", fetch)
    c = TestClient(main.app)
    goshen = pid_for(led, "A1")
    page = c.get("/queue").text
    assert "awaiting your approval" in page and f"#{goshen}" in page and "Manual review only" in page
    assert crm.writes() == []
    r = c.post(f"/proposal/{goshen}/decide", data={"action": "approve", "csrf": main.CSRF, "next": "queue"},
               follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/queue")
    pv = c.post("/queue/preview", data={"csrf": main.CSRF, "pids": [goshen]}).text
    assert "APPLY QUEUE OF 1" in pv and "Dry-run server" in pv
    tok = led.audit(limit=5)[0]
    token = json.loads(tok["detail"])["token"]
    res = c.post("/queue/run", data={"csrf": main.CSRF, "pids": [goshen], "tokens": [token], "reviewed": "yes",
                                      "confirmation": "APPLY QUEUE OF 1"}).text
    assert "Refused before any write" in res and crm.writes() == []
    assert c.post("/queue/run", data={"pids": [goshen], "tokens": [token], "reviewed": "yes",
                                      "confirmation": "APPLY QUEUE OF 1"}).status_code == 403   # no CSRF
