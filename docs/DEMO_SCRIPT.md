# Demo (~2 minutes), technical walkthrough, and submission checklist

## Before recording

1. Stop the stale servers (see `OPERATIONS.md`), then start **one**:
   - **Version B (no write, always safe):** `./bh serve`. The dry-run refusal at the confirm step demonstrates the gate itself.
   - **Version A (live write):** only for an item you have freshly approved. Back up the ledger, then run `CRM_WRITES_ENABLED=1 ./bh serve --port 8020`.
     Execute your other approved items *before* recording, and keep **#60 Tiffin (CHOW)** for the camera.
2. Run `./bh scan` first, so Start Here shows a fresh scan.
3. Crop the browser address bar on any `/api/account/...` view. The token is never shown, but keep the frame clean.

## Script (2:00)

| Time | Screen | Say |
|---|---|---|
| 0:00–0:15 | **Start Here** | "Bellhaven's website lists 35 communities; the CRM has 121 accounts. The scan reads both, read-only, and fails closed if anything is incomplete. Here it's complete: 35 of 35, because I follow homepage links as well as the directory. Proposal states, zero engine writes, and the daily schedule are all on this page." |
| 0:15–0:35 | **Find Problems** → #53 Kettering, #36 Amberly | "Identity is decided by address, never by name. Kettering has three $0 accounts at one address and nothing to tell them apart. Amberly has the same name, but it's in Colorado. Both are HELD with no operations, and I've written the questions a human must answer." |
| 0:35–1:00 | **#60 Tiffin** | "Tiffin is under Cedar Trail with $84,000 revenue and $12,400 open AR. The SOP forbids moving it. So the plan is one ordered operation: keep the old account as the financial record, create a successor under Bellhaven, point the old account at it, then read both back. Each step's state is saved, so a failure resumes without a second successor." |
| 1:00–1:25 | Approve → **Live preview** → type `APPLY 60` | "Approving records a decision; it writes nothing. The preview re-reads the CRM, re-runs the SOP on live numbers, checks for an existing successor, and binds a plan token to that state. The write only happens after this typed confirmation, then every field is read back." *(B: show the dry-run refusal. A: show VERIFIED with the read-back.)* |
| 1:25–1:40 | **#56 Owosso** | "Duplicates are never merged or deleted. The survivor is the record whose phone matches the website; the other becomes Inactive and points at it." |
| 1:40–1:52 | **History** | "Every decision, preview, write and read-back is in an append-only log. Findlay was fixed earlier; it's imported as a verified receipt and never re-proposed." |
| 1:52–2:00 | **Test** tab | "130 tests on a mocked CRM cover partial failures, stale data and repeated approvals. The daily job only scans, and refuses to start if writes are enabled." |

## Technical walkthrough (for follow-up questions)

- **Reconciliation Engine** (`scrape.py`, `crm.py`, `normalize.py`, `reconcile.py`, `pipeline.py`)
  - Paginated scrape plus homepage links; fails closed on short pages or short CRM pagination.
  - Match tiers: exact address → same number+ZIP with a similar street → same-city name *supported* by a phone match or a PO Box.
  - Classifies each case as FIELD_UPDATE / ALIAS / WRONG_PARENT / CHOW / DUPLICATE / WEBSITE_ONLY / CRM_ONLY / HOLD.
  - Reads operator identity resolutions as inputs.
- **Risk & Validation Engine** (`policy.py`, `executor.preview`)
  - The SOP table; unreadable financials → HOLD.
  - Re-checks protected accounts on **fresh** data.
  - Guards against duplicate successors and recovers from uncertain creates.
  - Tells explained drift from unexplained drift, and refuses overlapping batches.
- **Audit & State Manager** (`ledger.py`, `legacy.py`)
  - Records runs and content-only source fingerprints, plus snapshots.
  - Deduplicates proposals by an operation fingerprint; decisions are bound to that fingerprint.
  - Persists each operation before and after the call.
  - `audit_log` and `resolutions` are append-only (SQLite triggers). The Findlay receipt is imported from the legacy audit file.
- **Review & Monitoring Interface** (`main.py` and templates; `cli.py` / `./bh`)
  - One local server with CSRF and same-origin checks on every POST; the token is never rendered.
  - The write flag is process-only, so `.env` can't set it.
  - Pages show scan completeness, state labels (PENDING / HELD / APPROVED / EXECUTING / VERIFIED / FAILED / SUPERSEDED / BLOCKED / REJECTED / RESOLVED), the schedule, tests and readiness.
- **Design choices worth defending**
  - Approvals are narrow: parent, name/phone and duplicate are separate proposals.
  - CHOW is a single ordered operation and never batches.
  - A rejected proposal can never execute.
  - A reverted proposal reopens as *pending*, never *approved*.
  - An interrupted execution resumes only through a fresh preview and confirmation.

> **Superseded for the final submission by `WALKTHROUGH.md`** (2-minute and 5-minute scripts), which reflects the executed and verified state (25 operations, audit PASS).

## Submission checklist

- [x] The scraper covers all 35 communities, including the homepage-only listing (scan #9)
- [x] All 121 CRM accounts are retrieved; pagination verified, fail-closed
- [x] Matching and classification with evidence for every proposal, plus an independent coverage cross-check
- [x] Billing SOP enforced and re-checked on live data before every write
- [x] Duplicates: survivor evidence, `duplicate_of_account` + Inactive + note; nothing deleted
- [x] Approve → live preview → typed confirmation → write → read-back; CHOW as one recoverable ordered operation
- [x] Persistent ledger; re-runs idempotent (scans #5–#9: 0 new / 35 known)
- [x] Daily read-only schedule (`scripts/crontab.txt`), with status and failures on Start Here
- [x] Tests: 130 passing (`./bh test`; `docs/TEST_REPORT.md`)
- [x] README, requirements matrix, nine-path review, decision report, operations list, investigation questions, change history, operations guide, demo script
- [ ] **Stop the stale servers** (ports 8000–8006, 8010, 8011)
- [ ] **Your approvals executed** one at a time (`APPROVAL_BATCH.md`), then a re-scan shows only held items open
- [ ] Answers to `INVESTIGATION_QUESTIONS.md` (#36, #38, #53, #70, #46, #68, #69)
- [ ] Optional: install the cron line
- [ ] Re-read the original Clipboard brief: contacts? the "Needs Review" status? the form fields? (matrix rows 34–36)
- [ ] Git commit + public GitHub repo (`.env`, `data/`, `investigation.txt` and backups are gitignored)
- [ ] 2-minute video recorded and shared as "anyone with the link"
- [ ] Form: repo link, video link, honest time spent, writeup
- [ ] Deadline: **unverified**. Nov 17 2026, 04:29 UTC (= Nov 16, 11:29 PM EST) is an inference from the CRM seed time + 48 h; confirm it from the original invitation
