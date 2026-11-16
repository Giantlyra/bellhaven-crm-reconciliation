"""Audit & State Manager: durable SQLite decision memory, provenance and append-only audit trail.

Tables
  runs             one row per scan (read-only pipeline run)
  sources          fingerprint + record count + file path of each source snapshot per run
  snapshots        per-facility website evidence per run
  proposals        one row per distinct proposal (fingerprint UNIQUE); status machine below
  decisions        human decisions (approve / reject / hold / note), bound to the proposal fingerprint
  operations       every attempted CRM write, persisted BEFORE and AFTER the call
  audit_log        append-only event log (UPDATE/DELETE rejected by triggers)
  legacy_receipts  verified writes made outside this engine (e.g. the guarded Findlay page)
  resolutions      operator identity decisions for HOLD subjects (append-only; latest per subject wins).
                   They are INPUTS to the next scan, never CRM writes: the scan turns them into ordinary
                   proposals that still need approve -> live preview -> typed confirm.

Status machine
  pending ──approve──> approved ──execute(typed confirm)──> applying ──readback ok──> verified
     │  └─reject──> rejected (terminal: never executed)            └──error──> failed ──retry──> applying
     └─hold──> hold                                                └──drift/policy──> conflict (re-scan)
  hold: non-actionable (no ops) or parked by reviewer; cannot execute
  superseded: replaced by a materially different proposal for the same subject
  resolved: no longer observed by a complete scan, or CRM already in the desired state
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT, finished_at TEXT, status TEXT,
  website_facilities INTEGER, crm_accounts INTEGER, new_proposals INTEGER, known_proposals INTEGER,
  summary TEXT, errors TEXT);
CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, source TEXT, provenance TEXT, fingerprint TEXT,
  records INTEGER, retrieved_at TEXT, path TEXT);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, source_url TEXT, data TEXT,
  content_hash TEXT, retrieved_at TEXT);
CREATE TABLE IF NOT EXISTS proposals (
  id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT UNIQUE, subject_key TEXT, run_id INTEGER,
  kind TEXT, title TEXT, account_ids TEXT, confidence TEXT, payload TEXT, status TEXT,
  created_at TEXT, updated_at TEXT, last_error TEXT);
CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, proposal_id INTEGER, decision TEXT, note TEXT, decided_at TEXT);
CREATE TABLE IF NOT EXISTS operations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, proposal_id INTEGER, op_index INTEGER, op_type TEXT,
  account_id TEXT, request TEXT, status TEXT, response TEXT, returned_id TEXT, error TEXT,
  created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, proposal_id INTEGER, event TEXT NOT NULL,
  detail TEXT);
CREATE TRIGGER IF NOT EXISTS audit_log_no_update BEFORE UPDATE ON audit_log
  BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log
  BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
CREATE TABLE IF NOT EXISTS legacy_receipts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, account_id TEXT, field TEXT, value TEXT,
  verified_at TEXT, detail TEXT, imported_at TEXT, UNIQUE(source, account_id, field, verified_at));
CREATE TABLE IF NOT EXISTS resolutions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, subject_key TEXT NOT NULL, hold_proposal_id INTEGER,
  hold_fingerprint TEXT, decision TEXT NOT NULL, account_id TEXT, note TEXT, actor TEXT, decided_at TEXT);
CREATE TRIGGER IF NOT EXISTS resolutions_no_update BEFORE UPDATE ON resolutions
  BEGIN SELECT RAISE(ABORT, 'resolutions are append-only; record a revoke instead'); END;
CREATE TRIGGER IF NOT EXISTS resolutions_no_delete BEFORE DELETE ON resolutions
  BEGIN SELECT RAISE(ABORT, 'resolutions are append-only; record a revoke instead'); END;
"""

# columns added after the first version of the schema (migrated in place, existing rows kept)
MIGRATIONS = {
    "proposals": [("risk", "TEXT"), ("actionable", "INTEGER DEFAULT 1"), ("resolution", "TEXT")],
    "decisions": [("actor", "TEXT"), ("fingerprint", "TEXT")],
}

PENDING, HOLD, APPROVED, REJECTED, APPLYING, APPLIED, VERIFIED, FAILED, CONFLICT, SUPERSEDED, RESOLVED = (
    "pending", "hold", "approved", "rejected", "applying", "applied", "verified", "failed", "conflict",
    "superseded", "resolved")
OPEN = (PENDING, HOLD, APPROVED)                 # still awaiting a human / execution
TERMINAL = (REJECTED, VERIFIED, SUPERSEDED, RESOLVED)
ALL_STATUSES = [PENDING, HOLD, APPROVED, APPLYING, VERIFIED, FAILED, CONFLICT, REJECTED, SUPERSEDED, RESOLVED]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fingerprint(p: dict) -> str:
    """Stable identity of a proposal: kind + subject + operations, ignoring free-text notes
    (which carry dates) so a re-run on unchanged evidence produces the same fingerprint."""
    ops = []
    for op in p["ops"]:
        fields = {k: v for k, v in op.get("fields", {}).items() if k != "note"}
        ops.append({"type": op["type"], "account_id": op.get("account_id"), "fields": fields})
    blob = json.dumps({"kind": p["kind"], "subject": p["subject_key"], "ops": ops,
                       "accounts": sorted(p.get("account_ids", [])) if not ops else None}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:20]


def content_fingerprint(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


class Ledger:
    def __init__(self, path=None):
        path = Path(path or config.DB_PATH)
        if str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self._migrate()
        self.db.commit()

    def _migrate(self):
        for table, cols in MIGRATIONS.items():
            have = {r["name"] for r in self.db.execute(f"PRAGMA table_info({table})")}
            for name, decl in cols:
                if name not in have:
                    self.db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")

    # ---- audit ----
    def log(self, event: str, proposal_id: Optional[int] = None, **detail):
        self.db.execute("INSERT INTO audit_log(at,proposal_id,event,detail) VALUES(?,?,?,?)",
                        (now(), proposal_id, event, json.dumps(detail, default=str)))
        self.db.commit()

    def audit(self, proposal_id: Optional[int] = None, limit=500) -> list:
        if proposal_id is None:
            rows = self.db.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
        else:
            rows = self.db.execute("SELECT * FROM audit_log WHERE proposal_id=? ORDER BY id", (proposal_id,))
        return [dict(r) for r in rows]

    # ---- runs / sources / snapshots ----
    def start_run(self) -> int:
        cur = self.db.execute("INSERT INTO runs(started_at,status) VALUES(?,?)", (now(), "running"))
        self.db.commit()
        self.log("run_started", run_id=cur.lastrowid)
        return cur.lastrowid

    def finish_run(self, run_id: int, status: str, **kw):
        self.db.execute(
            "UPDATE runs SET finished_at=?, status=?, website_facilities=?, crm_accounts=?, new_proposals=?, "
            "known_proposals=?, summary=?, errors=? WHERE id=?",
            (now(), status, kw.get("website_facilities"), kw.get("crm_accounts"), kw.get("new_proposals"),
             kw.get("known_proposals"), json.dumps(kw.get("summary", {})), json.dumps(kw.get("errors", [])), run_id))
        self.db.commit()
        self.log("run_finished", run_id=run_id, status=status, new=kw.get("new_proposals"),
                 known=kw.get("known_proposals"))

    def add_source(self, run_id: int, source: str, provenance: str, fp: str, records: int, retrieved_at: str,
                   path: str = ""):
        self.db.execute("INSERT INTO sources(run_id,source,provenance,fingerprint,records,retrieved_at,path) "
                        "VALUES(?,?,?,?,?,?,?)", (run_id, source, provenance, fp, records, retrieved_at, path))
        self.db.commit()

    def sources(self, run_id: int) -> list:
        return [dict(r) for r in self.db.execute("SELECT * FROM sources WHERE run_id=? ORDER BY id", (run_id,))]

    def add_snapshot(self, run_id: int, rec: dict):
        self.db.execute("INSERT INTO snapshots(run_id,source_url,data,content_hash,retrieved_at) VALUES(?,?,?,?,?)",
                        (run_id, rec.get("source_url"), json.dumps(rec), rec.get("content_hash"),
                         rec.get("retrieved_at")))

    def runs(self, limit=20):
        return [dict(r) for r in self.db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))]

    def latest_run(self, completed_only=False):
        q = "SELECT * FROM runs WHERE status " + ("='completed'" if completed_only else "!='running'")
        r = self.db.execute(q + " ORDER BY id DESC LIMIT 1").fetchone()
        return dict(r) if r else None

    # ---- proposals ----
    def upsert_proposal(self, run_id: int, p: dict) -> tuple:
        """Insert unless an identical (same fingerprint) proposal already exists. Returns (id, is_new).
        Existing decisions are never overwritten by a re-run."""
        fp = fingerprint(p)
        row = self.db.execute("SELECT id, status, resolution FROM proposals WHERE fingerprint=?", (fp,)).fetchone()
        if row:
            # observed again after it had disappeared -> reopen for review. (Items resolved because the CRM is
            # already in the desired state / a verified receipt exists stay resolved.)
            if row["status"] == RESOLVED and (row["resolution"] or "").startswith("no longer observed"):
                status = PENDING if p.get("actionable", True) else HOLD
                self.set_status(row["id"], status, None, reason="observed again by scan")
            elif row["status"] == SUPERSEDED:
                # Evidence (or an operator resolution) reverted to this exact proposal. Retire whatever replaced
                # it and reopen this one for review. Never restored to 'approved': any earlier approval is void.
                for old in self.db.execute("SELECT id FROM proposals WHERE subject_key=? AND id!=? AND status IN "
                                           "(?,?,?)", (p["subject_key"], row["id"], PENDING, HOLD, APPROVED)):
                    self.set_status(old["id"], SUPERSEDED, None, reason="evidence reverted; replaced by "
                                                                         f"#{row['id']}")
                status = PENDING if p.get("actionable", True) else HOLD
                self.set_status(row["id"], status, None, reason="observed again by scan; earlier approval void")
            return row["id"], False
        # A materially different proposal for the same subject replaces any undecided / unexecuted older one.
        for old in self.db.execute("SELECT id FROM proposals WHERE subject_key=? AND status IN (?,?,?)",
                                   (p["subject_key"], PENDING, HOLD, APPROVED)).fetchall():
            self.set_status(old["id"], SUPERSEDED, None, reason="evidence changed; replaced by new proposal")
        status = PENDING if p.get("actionable", True) else HOLD
        cur = self.db.execute(
            "INSERT INTO proposals(fingerprint,subject_key,run_id,kind,title,account_ids,confidence,payload,status,"
            "created_at,updated_at,risk,actionable) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (fp, p["subject_key"], run_id, p["kind"], p["title"], json.dumps(p["account_ids"]), p["confidence"],
             json.dumps(p), status, now(), now(), p.get("risk"), int(p.get("actionable", True))))
        self.db.commit()
        self.log("proposal_created", cur.lastrowid, fingerprint=fp, kind=p["kind"], status=status, run_id=run_id)
        return cur.lastrowid, True

    def _row(self, r) -> dict:
        d = dict(r)
        d["payload"] = json.loads(d["payload"])
        d["account_ids"] = json.loads(d["account_ids"])
        d["risk"] = d.get("risk") or d["payload"].get("risk") or "medium"
        d["actionable"] = bool(d["payload"].get("actionable", True)) and bool(d["payload"].get("ops"))
        return d

    def get_proposal(self, pid: int) -> Optional[dict]:
        r = self.db.execute("SELECT * FROM proposals WHERE id=?", (pid,)).fetchone()
        return self._row(r) if r else None

    def proposals(self, status=None, kind=None, statuses=None) -> list:
        q, args = "SELECT * FROM proposals WHERE 1=1", []
        if status:
            q += " AND status=?"
            args.append(status)
        if statuses:
            q += " AND status IN (%s)" % ",".join("?" * len(statuses))
            args += list(statuses)
        if kind:
            q += " AND kind=?"
            args.append(kind)
        return [self._row(r) for r in self.db.execute(q + " ORDER BY id", args)]

    def set_status(self, pid: int, status: str, error: Optional[str] = None, **detail):
        prev = self.db.execute("SELECT status FROM proposals WHERE id=?", (pid,)).fetchone()
        self.db.execute("UPDATE proposals SET status=?, updated_at=?, last_error=? WHERE id=?",
                        (status, now(), error, pid))
        if status == RESOLVED and detail.get("reason"):
            self.db.execute("UPDATE proposals SET resolution=? WHERE id=?", (detail["reason"], pid))
        self.db.commit()
        self.log("status", pid, frm=prev["status"] if prev else None, to=status, error=error, **detail)

    def counts(self) -> dict:
        return {r["status"]: r["n"] for r in self.db.execute("SELECT status, COUNT(*) n FROM proposals GROUP BY status")}

    def resolve_unobserved(self, run_id: int, seen_subjects: set) -> int:
        """After a COMPLETE scan: open proposals whose subject no longer appears are resolved (not deleted)."""
        n = 0
        for r in self.db.execute("SELECT id, subject_key FROM proposals WHERE status IN (?,?,?)", OPEN).fetchall():
            if r["subject_key"] not in seen_subjects:
                self.set_status(r["id"], RESOLVED, None, reason=f"no longer observed by complete scan #{run_id}")
                n += 1
        return n

    # ---- decisions ----
    def decide(self, pid: int, decision: str, note: str = "", actor: str = "local-reviewer"):
        p = self.get_proposal(pid)
        self.db.execute("INSERT INTO decisions(proposal_id,decision,note,decided_at,actor,fingerprint) "
                        "VALUES(?,?,?,?,?,?)", (pid, decision, note, now(), actor, p["fingerprint"] if p else None))
        self.db.commit()
        self.log("decision", pid, decision=decision, note=note, actor=actor)

    def last_decision(self, pid: int, decision: Optional[str] = None) -> Optional[dict]:
        q, args = "SELECT * FROM decisions WHERE proposal_id=?", [pid]
        if decision:
            q += " AND decision=?"
            args.append(decision)
        r = self.db.execute(q + " ORDER BY id DESC LIMIT 1", args).fetchone()
        return dict(r) if r else None

    def decisions(self, limit=200):
        return [dict(r) for r in self.db.execute(
            "SELECT d.*, p.title, p.kind FROM decisions d JOIN proposals p ON p.id=d.proposal_id "
            "ORDER BY d.id DESC LIMIT ?", (limit,))]

    # ---- operations ----
    def op(self, pid: int, idx: int) -> Optional[dict]:
        r = self.db.execute("SELECT * FROM operations WHERE proposal_id=? AND op_index=? ORDER BY id DESC LIMIT 1",
                            (pid, idx)).fetchone()
        return dict(r) if r else None

    def record_op(self, pid: int, idx: int, op_type: str, account_id, request: dict,
                  status: str, response=None, returned_id=None, error=None) -> int:
        cur = self.db.execute(
            "INSERT INTO operations(proposal_id,op_index,op_type,account_id,request,status,response,returned_id,error,"
            "created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (pid, idx, op_type, account_id, json.dumps(request), status,
             json.dumps(response) if response is not None else None, returned_id, error, now(), now()))
        self.db.commit()
        self.log("op", pid, op_index=idx, op_type=op_type, account_id=account_id, status=status,
                 request=request, returned_id=returned_id, error=error)
        return cur.lastrowid

    def update_op(self, op_id: int, **kw):
        sets = ", ".join(f"{k}=?" for k in kw) + ", updated_at=?"
        vals = [json.dumps(v) if k == "response" and v is not None else v for k, v in kw.items()]
        self.db.execute(f"UPDATE operations SET {sets} WHERE id=?", (*vals, now(), op_id))
        self.db.commit()
        row = self.db.execute("SELECT proposal_id, op_index FROM operations WHERE id=?", (op_id,)).fetchone()
        self.log("op_update", row["proposal_id"] if row else None, op_id=op_id,
                 op_index=row["op_index"] if row else None,
                 **{k: v for k, v in kw.items() if k != "response"})

    def operations(self, pid: Optional[int] = None, limit=500):
        if pid is not None:
            rows = self.db.execute("SELECT * FROM operations WHERE proposal_id=? ORDER BY id", (pid,))
        else:
            rows = self.db.execute(
                "SELECT o.*, p.title FROM operations o JOIN proposals p ON p.id=o.proposal_id ORDER BY o.id DESC LIMIT ?",
                (limit,))
        return [dict(r) for r in rows]

    def verified_writes(self, account_id: str, exclude_pid: Optional[int] = None) -> dict:
        """{field: (value, proposal_id)} for update ops on this account that this engine wrote AND read back
        successfully (latest wins). Used to tell our own audited changes apart from unexplained drift."""
        q = ("SELECT proposal_id, request FROM operations WHERE account_id=? AND op_type='update' "
             "AND status='verified'")
        args = [account_id]
        if exclude_pid is not None:
            q += " AND proposal_id != ?"
            args.append(exclude_pid)
        out = {}
        for r in self.db.execute(q + " ORDER BY id", args):
            for k, v in (json.loads(r["request"]) or {}).items():
                out[k] = (v, r["proposal_id"])
        return out

    def write_count(self) -> int:
        """Number of CRM write calls this engine has ever attempted."""
        return self.db.execute("SELECT COUNT(*) FROM operations").fetchone()[0]

    # ---- legacy receipts ----
    def add_receipt(self, source: str, account_id: str, field: str, value, verified_at: str, detail: str) -> bool:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO legacy_receipts(source,account_id,field,value,verified_at,detail,imported_at) "
            "VALUES(?,?,?,?,?,?,?)", (source, account_id, field, json.dumps(value), verified_at, detail, now()))
        self.db.commit()
        if cur.rowcount:
            self.log("legacy_receipt_imported", None, source=source, account_id=account_id, field=field,
                     verified_at=verified_at)
        return bool(cur.rowcount)

    def receipts(self) -> list:
        out = []
        for r in self.db.execute("SELECT * FROM legacy_receipts ORDER BY id"):
            d = dict(r)
            d["value"] = json.loads(d["value"])
            out.append(d)
        return out

    # ---- operator identity resolutions (inputs to reconcile; never CRM writes) ----
    def add_resolution(self, subject_key: str, decision: str, *, hold_proposal_id=None, hold_fingerprint=None,
                       account_id=None, note: str = "", actor: str = "local-reviewer") -> int:
        cur = self.db.execute(
            "INSERT INTO resolutions(subject_key,hold_proposal_id,hold_fingerprint,decision,account_id,note,actor,"
            "decided_at) VALUES(?,?,?,?,?,?,?,?)",
            (subject_key, hold_proposal_id, hold_fingerprint, decision, account_id, note, actor, now()))
        self.db.commit()
        self.log("identity_resolution", hold_proposal_id, subject_key=subject_key, decision=decision,
                 account_id=account_id, note=note, actor=actor)
        return cur.lastrowid

    def resolutions(self) -> list:
        return [dict(r) for r in self.db.execute("SELECT * FROM resolutions ORDER BY id")]

    def active_resolutions(self) -> dict:
        """{subject_key: resolution} - latest record per subject, omitting subjects whose latest is a revoke."""
        out = {}
        for r in self.resolutions():
            if r["decision"] == "revoke":
                out.pop(r["subject_key"], None)
            else:
                out[r["subject_key"]] = r
        return out

    def receipt_covering(self, op: dict) -> Optional[dict]:
        """A verified legacy write that already set every field of this update op."""
        if op.get("type") != "update" or not op.get("fields"):
            return None
        recs = [r for r in self.receipts() if r["account_id"] == op["account_id"]]
        hit = None
        for k, v in op["fields"].items():
            m = [r for r in recs if r["field"] == k and r["value"] == v]
            if not m:
                return None
            hit = m[-1]
        return hit
