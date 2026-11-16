"""Configuration loaded from environment / .env (token never hard-coded, never printed)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
# Read the write kill-switch from the real process environment BEFORE .env is loaded, so it can only be
# enabled deliberately on the command line for one server launch, never left on in a file.
_WRITES_FLAG = os.environ.get("CRM_WRITES_ENABLED", "")
load_dotenv(ROOT / ".env")

SITE_BASE = os.getenv("SITE_BASE", "https://analyst-assessment-production.up.railway.app").rstrip("/")
CRM_API_BASE = os.getenv("CRM_API_BASE", f"{SITE_BASE}/api/v1").rstrip("/")
CRM_TOKEN = os.getenv("CRM_TOKEN", "")
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "ledger.db")))
SNAPSHOT_DIR = DATA_DIR / "snapshots"

# Kill-switch. Default OFF: the executor refuses every CRM write (dry-run) unless the server process was
# started with CRM_WRITES_ENABLED=1. Even then each write needs approval + preview + typed confirmation.
WRITES_ENABLED = _WRITES_FLAG == "1"

BELLHAVEN_PARENT_NAME = "Bellhaven Senior Living (Parent Account)"
