"""Daily job: READ-ONLY scan. scrape -> read CRM -> reconcile -> record proposals as pending.

It never approves, previews or executes anything, and it refuses to run if CRM_WRITES_ENABLED is set,
so a scheduler can never be the process that holds write permission. Exit code 1 if the run failed.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if os.getenv("CRM_WRITES_ENABLED") == "1":
    sys.exit("Refusing to run the scheduled scan with CRM_WRITES_ENABLED=1 (scheduled jobs are read-only).")

from app import config  # noqa: E402
if config.WRITES_ENABLED:
    sys.exit("Refusing to run: scheduled scans are read-only.")
from app.crm import CRMClient  # noqa: E402
from app.ledger import Ledger  # noqa: E402
from app.pipeline import run_pipeline  # noqa: E402
from app.scrape import scrape  # noqa: E402

if __name__ == "__main__":
    res = run_pipeline(CRMClient(), Ledger(), scrape, provenance="live (scheduled)", save_snapshot=True)
    print(json.dumps({k: v for k, v in res.items()}, indent=2, default=str))
    sys.exit(0 if res.get("status") == "completed" else 1)
