"""Import verified writes made by the earlier guarded Findlay page (app/proposals.py) as receipts.

Read-only on the legacy files. Only VERIFIED events (PATCH + successful read-back) become receipts.
The nine-card console decisions (data/review.db) are deliberately NOT imported: they were local demo
decisions and never authorized a CRM write.
"""
from __future__ import annotations

import json
import sqlite3

from . import config

SOURCE = "legacy:proposals.py (guarded Findlay page)"
PARENT_NAME = config.BELLHAVEN_PARENT_NAME


def _bellhaven_parent_id(data_dir) -> str | None:
    ids = set()
    snap = data_dir / "snapshot.json"
    if snap.exists():
        accts = json.loads(snap.read_text(encoding="utf-8")).get("accounts", [])
        ids |= {a["account_id"] for a in accts if a.get("name") == PARENT_NAME}
    fp = data_dir / "findlay_proposal.json"
    if fp.exists():
        pid = json.loads(fp.read_text(encoding="utf-8")).get("proposed_parent_id")
        if pid:
            ids.add(pid)
    return ids.pop() if len(ids) == 1 else None   # disagreement or absence -> import nothing


def import_legacy_receipts(ledger, data_dir=None) -> int:
    data_dir = data_dir or config.DATA_DIR
    db = data_dir / "execution_audit.db"
    if not db.exists():
        return 0
    parent = _bellhaven_parent_id(data_dir)
    if not parent:
        return 0
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        rows = con.execute("SELECT at, event, account_id, message FROM events WHERE event='VERIFIED'").fetchall()
    except sqlite3.Error:
        return 0
    finally:
        con.close()
    n = 0
    for at, _event, account_id, message in rows:
        if account_id and "parent_id" in (message or ""):
            n += ledger.add_receipt(SOURCE, account_id, "parent_id", parent, at, message)
    return n
