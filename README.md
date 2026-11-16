# Bellhaven CRM Reconciliation

Reconciles Bellhaven Senior Living's public community website against the assessment CRM. It proposes
evidence-backed corrections and writes **only** the changes a human approves and confirms. Each write gets a
live re-check before it runs and a read-back check after.

## Results at a glance (final, 2026-11-16)

| | |
|---|---|
| Website communities reconciled | **35** (homepage 35, directory 34; one listed on the homepage only) |
| CRM accounts | **121** at the start → **125** (Batavia, Carlisle, and the Tiffin and Marietta successors created) |
| CRM changes | **25 operations on 23 proposals**, each human-approved, live-previewed, typed-confirmed and **read-back VERIFIED**. Plus one earlier Findlay parent correction |
| Integrity audit | **PASS**: every write live-matched and receipted; protected financial fields and contacts intact; no change outside the ledger |
| Communities matching the CRM exactly | **23 of 35**. The rest are documented cases, not guesses: 6 HELD with business questions, 5 closed without a write, 1 new pending create |
| Tests | **130 passing** (mocked CRM, temporary SQLite). On a fresh clone, **123 pass and 7 are skipped**: those 7 need the private assessment snapshot, which is gitignored |

**Start here:** [docs/FINAL_RECONCILIATION_REPORT.md](docs/FINAL_RECONCILIATION_REPORT.md) · [docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md) · [docs/WRITEUP.md](docs/WRITEUP.md) · [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md)

## Quick start (fresh clone)

```bash
git clone https://github.com/Giantlyra/bellhaven-crm-reconciliation.git
cd bellhaven-crm-reconciliation
./bh test                 # first run creates .venv and installs requirements; mocked tests (~1 s), no token or network needed
./bh scan                 # live READ-ONLY scan: website + every CRM page -> pending proposals
./bh serve                # review workspace at http://127.0.0.1:8000  (dry-run: writes disabled)
```

- `./bh serve` keeps running. **The terminal looks frozen while it serves; that is normal.** Press `Ctrl+C` to stop it.
- If port 8000 is busy (an older server window), `./bh serve` says so. Use `./bh serve --port 8010`, or stop old servers (see *Operator notes*).
- `./bh status` shows the last run, source fingerprints, proposal counts, and the number of CRM write calls ever made.
  `./bh list --status pending` and `./bh show <id>` show the queue in the terminal.
- `./bh scan --offline data/snapshot.json` runs on the saved snapshot with no network. It is labelled stale.
- `./run.sh` still works; it is the same as `./bh serve`.
- `./bh resolve <hold-id> distinct|survivor <account>|revoke --note "why"` records an operator identity decision for a
  HOLD. It writes nothing to the CRM: the next `./bh scan` turns it into ordinary pending proposals.
**Documents** (in `docs/`):

| Document | Contents |
|---|---|
| [FINAL_RECONCILIATION_REPORT.md](docs/FINAL_RECONCILIATION_REPORT.md) | **Final results**: every verified change, the decisions made without a write, unresolved business questions |
| [FINAL_AUDIT.md](docs/FINAL_AUDIT.md) | Read-only integrity audit: website vs CRM, writes vs receipts, protected fields and contacts |
| [WRITEUP.md](docs/WRITEUP.md) | Submission write-up: matching approach, AI tools used, what we'd build next |
| [WALKTHROUGH.md](docs/WALKTHROUGH.md) | 2- and 5-minute demo scripts and prep for the live session |
| [EVALUATION_TABLE.md](docs/EVALUATION_TABLE.md) · [CHOW_REVIEW.md](docs/CHOW_REVIEW.md) · [MONITORING_RESULTS.md](docs/MONITORING_RESULTS.md) | Per-case evaluation, change-of-ownership review, scheduler demonstration |
| [REQUIREMENTS_MATRIX.md](docs/REQUIREMENTS_MATRIX.md) | Every traced requirement: source, module, UI location, tests, status |
| [NINE_PATH_REVIEW.md](docs/NINE_PATH_REVIEW.md) | Nine independent evaluations, the conflicts between them, and a prioritized remediation plan |
| [DECISION_REPORT.md](docs/DECISION_REPORT.md) | Risk, confidence, evidence and recommendation for all 35 open items |
| [APPROVAL_BATCH.md](docs/APPROVAL_BATCH.md) | Every operation that needs your authorization: exact IDs, before/after values, safeguards |
| [INVESTIGATION_QUESTIONS.md](docs/INVESTIGATION_QUESTIONS.md) | Ambiguous records: evidence for and against, what's missing, the questions to answer, consequences of each choice |
| [TEST_REPORT.md](docs/TEST_REPORT.md) | The automated test report, mapped to the required scenarios |
| [CRM_CHANGE_HISTORY.md](docs/CRM_CHANGE_HISTORY.md) | Read-back-verified CRM changes only |
| [OPERATIONS.md](docs/OPERATIONS.md) | Startup, the daily schedule, and recovery from every failure state |
| [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | 2-minute demo, technical walkthrough, submission checklist |

Requirements: Python 3.9+ and macOS/Linux (`./bh` creates `.venv` on first run). **`./bh test` needs no credentials.**
For `./bh scan` and `./bh serve`, first run `cp .env.example .env` and put the assessment CRM token in `CRM_TOKEN`. The token never leaves `.env`, which is gitignored.
The ledger and snapshots are created under `data/`, which is gitignored, so a fresh clone starts with an empty ledger. Run `./bh scan` to populate it.

## Making a real CRM change (only with explicit operator consent)

Live writes are **off** unless the server process is started like this:

```bash
CRM_WRITES_ENABLED=1 ./bh serve
```

The flag is read from the command line only; it is ignored in `.env` by design. The UI then shows a red "LIVE WRITES ENABLED" bar.
Even with the flag, every write needs all four steps:

1. **Approve** on the proposal page. This records a decision bound to the proposal's fingerprint. It writes nothing.
2. **Live preview**. This step is read-only. It re-reads every touched account, checks for drift since the proposal was made, re-runs the
   SOP on live financials, checks for an existing CHOW successor, and shows the exact `POST`/`PATCH` bodies plus a plan token.
3. **Confirm**: tick "I reviewed…" and type `APPLY <id>`. If the CRM changed after the preview, the plan token no longer
   matches and execution is refused.
4. **Read-back**: every touched account is re-read and compared. Only then is the status `verified`.

Batch: approved non-CHOW items can be previewed together and confirmed with `APPLY BATCH OF <n>`. Each item is still
validated, executed and audited on its own, and the batch stops at the first item that does not verify. CHOW always runs one at a time.
A batch is refused if one item writes an account another item reads (its plan token would go stale mid-batch); the
preview defers such items to a follow-up batch. In that follow-up, a baseline difference is accepted **only** if it equals a value
this engine wrote and read back for another proposal; any other drift still blocks.

## Controlled execution queue (low-risk corrections only)

Open **Queue** (`/queue`).

**What can be queued:** single-account `phone`/`name` corrections that meet all of these:
- exact address+ZIP match and high confidence;
- no competing records;
- the account is already under Bellhaven;
- for renames, the name is recognisably the same.

Everything else stays in manual review: ownership, parent, CHOW, duplicates, creates, billing address, uncertain matches and material renames.

**Running it:**
1. You approve each record yourself (the queue never approves).
2. **Validate** re-checks every item read-only, against the live CRM and the live website.
3. Tick the review box and type `APPLY QUEUE OF <n>`.

The queue then runs each item through the normal `executor.execute` path, one at a time:
- re-validated immediately before its write;
- read back;
- diffed field by field, including contacts, against the pre-write record;
- receipted in the audit log and `data/queue_receipts/`.

It stops at the first item that does not verify. A dry-run server refuses the whole queue before any write.

## Architecture

Four deterministic layers, written as plain Python modules. There are no LLM calls, no agent runtime and no external services beyond the website and the CRM API.

| Layer | Modules | Responsibility |
|---|---|---|
| **Reconciliation Engine** | `scrape.py`, `crm.py` (GET only during scans), `normalize.py`, `reconcile.py`, `pipeline.py` | Ingest the website and every CRM page (fail closed), normalize, match by address, classify, and generate proposals with evidence, risk and confidence |
| **Risk & Validation Engine** | `policy.py`, `executor.preview` | Billing/CHOW SOP, financial invariants, duplicate and successor guards, live pre-write revalidation, drift detection, batch overlap |
| **Audit & State Manager** | `ledger.py` (SQLite), `legacy.py` | Runs, source fingerprints, snapshots, proposals and their state machine, decisions bound to fingerprints, operations persisted before and after each call, append-only audit log, identity resolutions, legacy receipts (Findlay) |
| **Review & Monitoring Interface** | `main.py` + templates, `cli.py` / `./bh` | Start Here · Data Review · Find Problems · Build/Modify · Test · Walkthrough · Submit · History · Legacy. Approve, reject and hold controls; live preview; typed confirmation; schedule and test status |

`executor.execute` is the **only** code path that writes to the CRM (approve → preview → typed confirm → write → read-back).

## Matching and classification (Reconciliation Engine)

1. **Scrape** the directory's "Next" pagination **and** every `/communities/<slug>` link on the homepage. The homepage says
   35 communities and the directory lists 34. *Bellhaven Meadows of Findlay* is linked only from the homepage.
2. **Fail closed.** The run is recorded as `incomplete` or `failed` and **no proposals are created or resolved** if any page fails,
   if fewer facilities are found than the homepage advertises, or if CRM pagination is short or inconsistent.
3. **Normalize** street suffixes and directions, the 5-digit ZIP, the 10-digit phone, and the name "core".
4. **Match tiers**: exact street+ZIP; same number+ZIP with ≥0.8 street similarity; same city plus a similar name that is
   *supported* by a phone match or a PO-Box CRM address. A name alone never decides identity.
5. **Classify**: `MATCH_OK`, `FIELD_UPDATE` / `ALIAS` (same address, renamed), `WRONG_PARENT`, `CHOW`, `DUPLICATE`,
   `WEBSITE_ONLY` (missing), `CRM_ONLY`, `HOLD`.
6. **HOLD (no operations at all; cannot be approved, only resolved via `./bh resolve`, which re-proposes normally):**
   - same name at a different address (**Amberly Manor**: website Hudson OH, CRM Colorado Springs CO);
   - a similar same-city name with a conflicting street (**Union Square**: 118 Union Square Dr vs 240 Market St);
   - several same-address accounts with no evidence to separate them (**Kettering**: 3 accounts, 3 different parents, $0, no phone match);
   - a duplicate "loser" with billing history, or financials that are unreadable.
7. **Duplicate survivor.** It must win on *decisive* evidence (under the Bellhaven parent > billing history > website phone match),
   otherwise the case is a HOLD. **Owosso**: `001EGU7BMJ942ZTRE6` survives because its phone matches the website. The loser gets
   `duplicate_of_account`, `Inactive` and an appended note. Nothing is merged or deleted.
8. Parent changes are their own proposals (`parent_id` only). Name and phone fixes are separate, so each approval stays narrow.

## Billing SOP and financial safeguards (Risk & Validation Engine, `app/policy.py`)

| lifetime_revenue | outstanding_ar | Action on a parent change |
|---|---|---|
| > 0 | > 0 | **CHOW**: the old account is left exactly as it is (it gets no field edits either). `POST` a successor under Bellhaven, then `PATCH` the old account's `chow_current_account` to the new id |
| > 0 | 0 | direct re-parent (Lima, Findlay) |
| 0 | any | direct re-parent (Zanesville; flagged as a possible rebrand, verify ownership) |
| missing / malformed / negative | any | **HOLD**, blocked (never treated as 0) |

Re-applied on live data right before writing: protected accounts cannot be re-parented, an account with billing history or
a CHOW link cannot be inactivated, the survivor must still be active, an existing `chow_current_account` is never
overwritten, and no `POST` is made if an account already sits at that address under the target parent (duplicate-successor
protection). CHOW partial failure: if the `POST` succeeded and the link `PATCH` failed, the retry reuses the saved successor id.
If a `POST` outcome is unknown (timeout), the retry first searches for the candidate-created account and adopts it, and it never
blindly re-creates.

## Ledger and audit (Audit & State Manager, `data/ledger.db`)

- Every scan stores a content-only SHA-256 fingerprint (fetch timestamps excluded) and record count for each source, plus a full JSON snapshot in `data/snapshots/`. The old
  `data/snapshot.json` (pre-Findlay) is kept untouched as evidence.
- Proposals are deduplicated by a canonical fingerprint (kind + subject + exact ops, ignoring dated note text), so re-runs
  are no-ops. A materially changed proposal supersedes the undecided one. Open items that a *complete* scan no longer
  observes become `resolved` (never deleted).
- Statuses (shown in the UI as PENDING · HELD · APPROVED · EXECUTING · VERIFIED · FAILED · BLOCKED · REJECTED · SUPERSEDED · RESOLVED).
  Only VERIFIED means "applied", and only after a read-back. `rejected` proposals can never execute. A proposal left
  EXECUTING by a killed server resumes only through a fresh preview and confirmation. A process lock prevents two executions at once.
- `audit_log` and `resolutions` are append-only: SQLite triggers reject `UPDATE` and `DELETE`. Every decision, preview, op start/finish,
  read-back and identity resolution is logged. A proposal that comes back after being superseded reopens as *pending*, never *approved*.
- **Findlay**: the verified write made earlier by the guarded Findlay page (`data/execution_audit.db`, STARTED → VERIFIED,
  2026-11-15 10:14 UTC) is imported read-only as a *legacy receipt*. On stale data the re-derived Findlay re-parent is marked
  resolved, and on live data it is simply `MATCH_OK`. If someone tried to re-execute it, the preview would detect that the target
  value is already present and no write would be made. **Do not retry Findlay.**
- The nine-card console decisions (`data/review.db`, e.g. a local "APPROVE Marietta") are **not** imported. They were
  demo notes and never authorized a write.

## Historical: initial findings before any execution (scans #3–#9, 2026-11-15)

> **Historical snapshot, superseded.** This section records what the first scans found *before* anything was approved. Since then, 25 writes were executed and verified; see **Results at a glance** above and `docs/FINAL_RECONCILIATION_REPORT.md`. The counts below (for example "0 engine write calls", "28 operations ready") describe 2026-11-15 only.

- **28 operations** are ready for your individual authorization.
- **4** are prepared but recommended for HOLD or INVESTIGATE:
  - #70 Sandusky: speculative CHOW link
  - #46 Ashtabula: the PO Box is a billing address
  - #68 / #69 Alliance and Coldwater: "Needs Review" isn't a status value seen anywhere in the CRM
- **3** identity holds have no operations (Amberly, Union Square, Kettering).

See `docs/APPROVAL_BATCH.md` and `docs/INVESTIGATION_QUESTIONS.md`.

| Category | Items |
|---|---|
| HOLD (3) | Amberly Manor · Bellhaven at Union Square · Bellhaven of Kettering |
| CHOW (3) | Marietta ($51,250 / AR $3,800) and Tiffin ($84,000 / AR $12,400): successor + link · Sandusky ($130,000 / AR $5,200, not on the website, Millstone account at the same address): link to the existing owner |
| Parent issue (2) | Lima (Harborview → Bellhaven, AR $0) · Zanesville (Cedar Trail → Bellhaven, $0; possible rebrand) |
| Duplicates (5) | Owosso · Monroe ×2 · Port Clinton · Erie (losers under other parents, all $0) |
| Missing (2) | Bellhaven of Batavia · Bellhaven of Carlisle (PA, not New Carlisle OH) |
| Not on website (2) | Alliance · Coldwater → `Needs Review` (recommended HOLD) |
| Renames / fields (18) | aliases (Sycamore Ridge, Chagrin Falls, Chesterton, Willow Creek, Arbors-Dayton, Zanesville, Ashland, Grove City), Ashtabula PO Box, Portsmouth ZIP, phone mismatches |
| Already resolved | Findlay parent (live: under Bellhaven). The only CRM difference from the pre-Findlay snapshot |

_As of 2026-11-15 these were proposals awaiting review, and 0 engine writes had been made. Final outcomes are in the final report._

## Tests

`./bh test`: **130 passed** (was 112 before the queue and confirmation-phrase work) (Python 3.9.6). Everything runs on mocked HTTP and in-memory or temporary SQLite. The report appears in the Test
tab and in [docs/TEST_REPORT.md](docs/TEST_REPORT.md), which maps tests to the required scenarios:

- incomplete ingestion
- duplicate survivor selection
- changed or missing financial data
- CHOW partial failure, uncertain creates and interrupted execution
- repeated approvals and re-execution
- idempotency and rejected proposals
- read-back verification
- zero writes from scans, GET pages and the scheduler
- authorization gates

`tests/test_bellhaven_snapshot.py` pins the case-by-case expectations on the private snapshot, and skips when that file is absent.

## Daily schedule (read-only)

`scripts/run_daily.py` runs the scan only (verified 2026-11-15 by running the exact cron command: scan #8 completed, 0 new). Start Here shows the last scheduled run, every scheduled failure, and the log tail. Install and recovery steps are in [docs/OPERATIONS.md](docs/OPERATIONS.md). It refuses to start if `CRM_WRITES_ENABLED=1`, so a scheduler can never hold
write permission. Local cron: `scripts/crontab.txt` (06:00 daily). `.github/workflows/daily-reconcile.yml` is an optional
alternative; it would store the private ledger as a GitHub artifact, so **local cron is recommended** for this assessment.
Status: as the brief allows, this is **configuration only**. The cron line is not installed on the author's machine. On GitHub the workflow exists, but no `CRM_TOKEN` secret is configured, so it cannot read the CRM.

## Operator notes (author's machine)

- Stop old servers from earlier sessions. They run old code on ports 8000–8006, 8010 and 8011: `lsof -nP -iTCP -sTCP:LISTEN | grep -E ':80(0[0-9]|1[01])'`, then
  `kill <PID>` for each. Or close those terminal windows.
- The token lives only in `.env` (gitignored), is sent only as a Bearer header, and never appears in pages, logs or errors.
  `data/` (snapshots, ledgers, reports) and `investigation.txt` are gitignored as private assessment data.
- A restore point from before this refactor is in `~/clipboard-assessment-backups/` (contains `.env`; keep private).

## Known limits

- Website data is trusted as the source of truth. Ownership changes are inferred, not confirmed with a human source.
- Phone mismatches are frequent in the CRM data; they are proposed as low-risk edits, not verified by calling.
- Contacts (website administrator vs CRM contacts) are not reconciled. Known: the Owosso loser has a contact (Tricia
  Lindqvist); Sandusky has Frank Dietz (DON). Contacts were used as identity evidence for Amberly and Union Square.
- The API spec (`/api/openapi.json`) has no field enums. The two "Needs Review" status proposals (#68, #69) were rejected as written; Alliance and Coldwater stay documented findings.
- Field-level read-back uses exact equality; if the CRM normalizes a value (e.g. phone format), the result is reported
  `failed` with the mismatch rather than silently accepted.
- Single local operator: no login. The "actor" is recorded as `local-reviewer`.

## Demo (~2 minutes) and submission

**Deadline: Nov 16 2026, 11:29 PM EST.**

- **Write-up** (matching approach, AI tools used, what we'd build next): [docs/WRITEUP.md](docs/WRITEUP.md).
- **Demo script** (evidence, approval, rejection, verified CRM change): [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md), with 2- and 5-minute versions and prep for the live 45-minute session.
- **Final results:** [docs/FINAL_RECONCILIATION_REPORT.md](docs/FINAL_RECONCILIATION_REPORT.md) · [docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md) · [docs/MONITORING_RESULTS.md](docs/MONITORING_RESULTS.md).
- **Daily schedule** (configuration only, as the brief allows): `scripts/crontab.txt` and `.github/workflows/daily-reconcile.yml`. Neither is installed live.

The **Submit** tab shows a live checklist.

- Repository: https://github.com/Giantlyra/bellhaven-crm-reconciliation
- Demo video: _add link (not recorded)_
- Time spent: _fill in your actual total_
