"""Read-only reconciliation run: sources -> reconcile -> ledger. NEVER writes to the CRM.

Fail-closed: if the website scrape or the CRM listing is incomplete, the run is recorded as
'incomplete'/'failed' and NO proposals are created or resolved (a broken page must never look like
a closed facility, and partial data must never look like a clean bill of health).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config
from . import ledger as L
from .legacy import import_legacy_receipts
from .reconcile import reconcile
from .scrape import ScrapeResult
from .scrape import scrape as default_scrape


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def offline_source(path):
    """Use a saved snapshot instead of the live site/CRM (demo / no network). Clearly labelled as stale."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    facilities = data.get("facilities") or data.get("website") or []
    accounts = data.get("accounts") or data.get("crm") or []
    when = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")

    def scrape_fn():
        r = ScrapeResult()
        r.facilities = [dict(f) for f in facilities]
        r.complete = bool(facilities)
        r.homepage_count = data.get("homepage_count")
        return r

    class SnapshotCRM:
        def list_accounts(self, **_):
            return [dict(a) for a in accounts]

    return scrape_fn, SnapshotCRM(), f"offline snapshot {path.name} (saved {when}; may be stale)"


def _save_snapshot(run_id, provenance, sr, accounts, fps) -> str:
    try:
        config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        p = config.SNAPSHOT_DIR / f"run-{run_id:04d}-{_now().replace(':', '')}.json"
        p.write_text(json.dumps({"run_id": run_id, "provenance": provenance, "saved_at": _now(),
                                 "fingerprints": fps, "homepage_count": sr.homepage_count,
                                 "directory_count": sr.directory_count, "facilities": sr.facilities,
                                 "accounts": accounts}, indent=1, default=str), encoding="utf-8")
        return str(p)
    except OSError:
        return ""


def run_pipeline(crm, ledger: L.Ledger, scrape_fn=default_scrape, provenance: str = "live",
                 save_snapshot: bool = False, legacy_dir=None) -> dict:
    run_id = ledger.start_run()
    errors = []
    try:
        sr = scrape_fn()
        errors += [{"stage": "scrape", **e} for e in sr.errors]
        for f in sr.facilities:
            ledger.add_snapshot(run_id, f)
        complete = sr.complete
        if sr.homepage_count and sr.directory_count and sr.homepage_count != sr.directory_count:
            errors.append({"stage": "scrape", "info":
                           f"Homepage says {sr.homepage_count} communities, directory lists {sr.directory_count}; "
                           f"scraper found {len(sr.facilities)} detail pages "
                           f"({sum(1 for f in sr.facilities if not f.get('in_directory', True))} linked only from "
                           "homepage)."})
        if sr.homepage_count and len(sr.facilities) < sr.homepage_count:
            complete = False
            errors.append({"stage": "scrape", "error": f"Only {len(sr.facilities)} of {sr.homepage_count} "
                                                       "advertised communities retrieved"})

        accounts = crm.list_accounts()   # raises on incomplete pagination -> run fails closed
        now = _now()
        # Content only: per-page fetch timestamps are excluded so an unchanged website keeps the same fingerprint.
        fps = {"website": L.content_fingerprint(sorted(({k: v for k, v in f.items() if k != "retrieved_at"}
                                                        for f in sr.facilities),
                                                       key=lambda f: f.get("source_url") or "")),
               "crm": L.content_fingerprint(sorted(accounts, key=lambda a: a.get("account_id") or ""))}
        ledger.add_source(run_id, "website", provenance, fps["website"], len(sr.facilities), now)
        ledger.add_source(run_id, "crm", provenance, fps["crm"], len(accounts), now,
                          _save_snapshot(run_id, provenance, sr, accounts, fps) if save_snapshot else "")

        if not complete:
            errors.append({"stage": "scrape", "error": "Scrape incomplete: run fails closed — no proposals were "
                                                       "created, changed or resolved."})
            ledger.finish_run(run_id, "incomplete", website_facilities=len(sr.facilities),
                              crm_accounts=len(accounts), new_proposals=0, known_proposals=0,
                              summary={"provenance": provenance, "fingerprints": fps}, errors=errors)
            return {"run_id": run_id, "status": "incomplete", "new": 0, "known": 0, "errors": errors}

        results, proposals = reconcile(sr.facilities, accounts, scrape_complete=True,
                                       resolutions=ledger.active_resolutions())

        if legacy_dir is not False:
            import_legacy_receipts(ledger, legacy_dir)

        new = known = resolved = 0
        seen = set()
        for p in proposals:
            pid, is_new = ledger.upsert_proposal(run_id, p)
            seen.add(p["subject_key"])
            new += is_new
            known += not is_new
            row = ledger.get_proposal(pid)
            if row["status"] in L.OPEN and p["ops"] and all(op["type"] == "update" for op in p["ops"]):
                recs = [ledger.receipt_covering(op) for op in p["ops"]]
                if all(recs):
                    ledger.set_status(pid, L.RESOLVED, None, reason=(
                        f"Already applied and read-back verified by {recs[0]['source']} at "
                        f"{recs[0]['verified_at']}; this scan's source data predates that write. Not re-proposed."))
                    resolved += 1
        resolved += ledger.resolve_unobserved(run_id, seen)

        summary = {"results": results, "homepage_count": sr.homepage_count, "directory_count": sr.directory_count,
                   "scrape_complete": True, "provenance": provenance, "fingerprints": fps}
        ledger.finish_run(run_id, "completed", website_facilities=len(sr.facilities), crm_accounts=len(accounts),
                          new_proposals=new, known_proposals=known, summary=summary, errors=errors)
        return {"run_id": run_id, "status": "completed", "new": new, "known": known, "resolved": resolved,
                "facilities": len(sr.facilities), "accounts": len(accounts), "errors": errors}
    except Exception as e:  # noqa: BLE001
        errors.append({"stage": "pipeline", "error": f"{type(e).__name__}: {e}"})
        ledger.finish_run(run_id, "failed", summary={"provenance": provenance}, errors=errors)
        return {"run_id": run_id, "status": "failed", "errors": errors}
