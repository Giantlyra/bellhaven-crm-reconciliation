import copy
import itertools

import pytest

from app.ledger import Ledger

BH = "P_BH"
CT = "P_CT"


class FakeCRM:
    """In-memory CRM with failure injection. Mirrors the real client's methods."""

    def __init__(self, accounts):
        self.accounts = {a["account_id"]: copy.deepcopy(a) for a in accounts}
        self.calls = []
        self.fail_update_for = set()   # account ids whose PATCH raises
        self.fail_create = 0           # raise on next N creates (after actually creating -> uncertain)
        self.create_lost = False       # create raises AND the account is persisted (timeout after commit)
        self._ids = itertools.count(1)

    def list_accounts(self, **f):
        self.calls.append(("list", f))
        out = list(self.accounts.values())
        if f.get("q"):
            out = [a for a in out if f["q"].lower() in a["name"].lower()]
        if f.get("zip"):
            out = [a for a in out if a.get("billing_zip") == f["zip"]]
        if f.get("parent_id"):
            out = [a for a in out if a.get("parent_id") == f["parent_id"]]
        return copy.deepcopy(out)

    def get_account(self, aid):
        self.calls.append(("get", aid))
        return copy.deepcopy(self.accounts[aid])

    def create_account(self, fields):
        self.calls.append(("create", fields))
        new = {**acct("NEW%d" % next(self._ids), "", parent=""), **fields, "created_by_candidate": True,
               "lifetime_revenue": 0, "outstanding_ar": 0}
        if self.create_lost:
            self.create_lost = False
            self.accounts[new["account_id"]] = new
            raise TimeoutError("read timeout")
        if self.fail_create:
            self.fail_create -= 1
            raise ConnectionError("refused")
        self.accounts[new["account_id"]] = new
        return copy.deepcopy(new)

    def update_account(self, aid, fields):
        self.calls.append(("update", aid, fields))
        if aid in self.fail_update_for:
            raise ConnectionError("boom")
        self.accounts[aid].update(fields)
        return copy.deepcopy(self.accounts[aid])

    def writes(self):
        return [c for c in self.calls if c[0] in ("create", "update")]


def acct(aid, name, parent=BH, street="", city="", state="", zip_="", phone="", care="Assisted Living",
         rev=0, ar=0, status="Active", **kw):
    return {"account_id": aid, "name": name, "parent_id": parent, "parent_name": "", "billing_street": street,
            "billing_city": city, "billing_state": state, "billing_zip": zip_, "phone": phone, "care_type": care,
            "status": status, "lifetime_revenue": rev, "outstanding_ar": ar, "chow_current_account": "",
            "duplicate_of_account": "", "note": "", "created_by_candidate": False, **kw}


def parents():
    return [acct(BH, "Bellhaven Senior Living (Parent Account)", parent=""),
            acct(CT, "Cedar Trail Communities (Parent Account)", parent="")]


def site(name, street, city, state, zip_, phone="(555) 000-0000", care=("Assisted Living",), slug=None):
    return {"name": name, "street": street, "city": city, "state": state, "zip": zip_, "phone": phone,
            "care_offerings": list(care), "administrator": "X", "source_url": f"http://site/communities/{slug or name}",
            "slug": slug or name.lower().replace(" ", "-"), "in_directory": True, "retrieved_at": "t"}


@pytest.fixture
def ledger():
    return Ledger(":memory:")


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    """Every test gets an empty data dir and live writes DISABLED unless a test opts in explicitly."""
    from app import config
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "SNAPSHOT_DIR", tmp_path / "snapshots")
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "ledger.db")
    monkeypatch.setattr(config, "WRITES_ENABLED", False)
    return tmp_path


def approve_exec(crm, ledger, pid, approve=True):
    """The full human path: approve -> read-only preview -> typed confirmation with that plan token."""
    from app import executor as X
    from app import ledger as L
    if approve and ledger.get_proposal(pid)["status"] == L.PENDING:
        X.approve(ledger, pid, "test")
    pv = X.preview(crm, ledger, pid)
    return X.execute(crm, ledger, pid, confirmation=X.confirmation_phrase(pid), plan_token=pv["token"],
                     writes_enabled=True)
