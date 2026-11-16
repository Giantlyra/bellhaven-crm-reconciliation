# Assessment Walkthrough

_For the reviewer. Every step is read-only unless stated otherwise._

## Setup (1 minute)
```
cd ~/clipboard-assessment
./bh test          # 130 tests, mocked CRM, about 1 s
./bh status        # last scan, proposal counts, write calls (25)
./bh serve         # http://127.0.0.1:8000, DRY-RUN
```

## 5-minute walkthrough script

| Time | Screen | Say / show |
|---|---|---|
| **0:00–0:40 · Problem** | Website homepage → **Start Here** | "Bellhaven's public website lists **35 communities**. The CRM had **121 accounts** with wrong names, phones, ZIPs and parents, duplicates, missing facilities, and acquired communities still under their old operator. The website is the source of truth for identity and contact data; the CRM holds financial history that must not be damaged." |
| **0:40–1:30 · Reconciliation engine** | **Start Here**: completeness card, source fingerprints | "One read-only scan pages through the whole website, including the homepage-only listing, and every CRM page. If anything is incomplete it fails closed and proposes nothing. It matches on exact address+ZIP, then classifies each case: field update, parent correction, change of ownership, duplicate, new account, or insufficient evidence. No LLM, no guessing." |
| **1:30–2:15 · Evidence** | **Build/Modify** → #60 Tiffin | "Every proposal shows website vs CRM side by side, the sources and timestamps, and what's still missing. Tiffin sits under Cedar Trail with **$84,000 revenue and $12,400 unpaid**. The billing rules forbid simply re-parenting it, so the engine proposes a **change of ownership**: keep the historical account untouched, create a $0 Bellhaven successor, and link them." |
| **2:15–3:00 · Human approval** | #60 page: Approve → **Live preview & confirm** | "Nothing writes without a human. Approval records a decision bound to this exact proposal version. The live preview re-reads the CRM, re-checks the rules, blocks if a successor already exists, and shows the exact POST and PATCH. Then I type `APPLY 60`. The server must also have been started with writes enabled; in dry-run, everything is refused." |
| **3:00–3:45 · Verified execution** | **History** tab; **Queue** run 1 | "Every write is persisted, then read back and compared, and only then marked VERIFIED. **25 operations on 23 proposals**, all verified. Low-risk phone and name fixes ran through a controlled queue with a website re-check, a protected-field diff and stop-on-first-error. The audit also logs the refusals: wrong phrase, stale page, a held proposal." |
| **3:45–4:20 · Exceptions** | `docs/FINAL_RECONCILIATION_REPORT.md` §4–5 | "Not everything should be forced. Three old-operator records were **closed and preserved** rather than mislabelled as duplicates. Six cases stay on **HOLD** with a specific question for Bellhaven, for example Kettering's three records. Sandusky's link is verified, but the sale and the **$5,200** remain a documented exception. An unresolved case with its evidence is a valid result." |
| **4:20–5:00 · Monitoring** | Terminal: `scripts/run_daily.py` (with and without the flag) → Start Here schedule card → `docs/FINAL_AUDIT.md` | "The daily job is read-only and **refuses to run if writes are enabled**. Re-running finds **0 new** items. The dashboard shows the last scheduled run and failures. The 6 AM cron job is **installed and tested** on this Mac (configuration alone would satisfy the brief). The final audit re-checks every write against the live CRM: **integrity PASS**." |

## 2-minute demo video (required: evidence, approval, rejection, verified CRM change)

**Teleprompter:** open `docs/teleprompter.html` in any browser by double-clicking it in Finder; it works offline with no server. It has 7 beats with time targets and screen cues, a 2:00 timer, ←/→ to move between beats, T to start the timer, C for clean reading mode, and D for dark mode.


**Before recording:**
- The server is in **dry-run**: `./bh serve` (or the session server on :8020). The green DRY-RUN banner is on.
- Open these tabs in order: `/` · `/proposal/60` · `/proposal/68` · `/history` · `docs/FINAL_AUDIT.md`.
- Crop the address bar; the token is never shown in pages.
- **Do not run a new write on camera.** The verified changes are already recorded, and the brief asks to *show* one.

| Time | Screen | Say |
|---|---|---|
| 0:00–0:15 | **Start Here** | "Bellhaven's website lists 35 communities; the CRM had 121 accounts. One read-only scan reads both, fails closed if anything is incomplete, and matches by address and ZIP, never by name alone." |
| 0:15–0:45 | **#60 Tiffin: evidence** (scroll the comparison and financial table) | "Every proposal shows website vs CRM side by side, the sources and what's missing. Tiffin sits under Cedar Trail with $84,000 revenue and $12,400 unpaid, so the billing rule forbids re-parenting it. The engine proposes a change of ownership: preserve the old account, create a $0 Bellhaven successor, link them." |
| 0:45–1:15 | **#60: approval → verified change** (Decisions and Write log sections) | "I approved it, ran the live preview, which re-reads the CRM, re-checks the rules and blocks duplicate successors, and typed APPLY 60. Two writes, a POST and a PATCH, then a read-back. Status VERIFIED; successor `00164AE214A6588944`. The old account still holds its $84,000 and $12,400." |
| 1:15–1:35 | **#68 Alliance: rejection** | "Not every proposal should run. This one would have set a status, 'Needs Review', that the CRM never uses. I rejected it: nothing written, and Alliance stays a documented finding. Three old-operator records were also closed and preserved rather than mislabelled as duplicates." |
| 1:35–1:50 | **History** (filter or scroll to `execute_refused`) | "Everything is in an append-only audit log, including refusals: dry-run attempts, a wrong confirmation phrase, a proposal on hold. 25 writes in total, all read back." |
| 1:50–2:00 | **`docs/FINAL_AUDIT.md`** or Start Here schedule card | "A daily read-only scan is configured, as a cron line and a GitHub Actions workflow, and refuses to run with writes enabled. The final audit re-checks every write: integrity PASS." |

## Live 45-minute walkthrough: preparation for the "small modification"

- **Run tests first and last:** `./bh test` (130 tests, about 1 s). Keep the server in dry-run while changing code.
- **Where common changes go:**
  - *Compare a new field* (e.g. care type): `app/normalize.py` (normalizer), `app/reconcile.py` (`_website_fields` and the field-diff block), then a test in `tests/test_matching.py`.
  - *Change matching strictness*: the street-similarity threshold and match tiers in `app/reconcile.py`.
  - *Add or tighten a safety rule*: `app/policy.py` (`check_ops`), then a test in `tests/test_policy.py`. The rule runs automatically at preview and execute time.
  - *Change queue eligibility*: `app/exec_queue.py` (`ALLOWED_FIELDS`, `MIN_NAME_SIMILARITY`), tests in `tests/test_queue.py`.
  - *Add a column or page*: route in `app/main.py`, template in `app/templates/`.
  - *Schedule*: `scripts/crontab.txt` or `.github/workflows/daily-reconcile.yml`.
- **Show the safety model while modifying:** only `executor.execute` writes; anything else, such as scans, GETs, tests and the scheduler, is proven write-free by tests.

## Technical walkthrough (on request)
1. `app/scrape.py`, `app/reconcile.py`: website + CRM ingestion (fail-closed), address+ZIP matching, classification.
2. `app/policy.py`: billing / CHOW SOP and financial invariants.
3. `app/executor.py`: the **only** write path: approval bound to a fingerprint, live preview with plan token, typed confirmation, per-op persistence, read-back.
4. `app/exec_queue.py`: controlled queue (eligibility gate, website re-check, protected-field diff, stop-on-error).
5. `app/ledger.py`: SQLite ledger and append-only audit log.
6. `scripts/run_daily.py` (read-only schedule), `scripts/final_audit.py` (integrity audit).

## How a write would be made (not needed for the demo)
1. `CRM_WRITES_ENABLED=1 ./bh serve`.
2. Approve the proposal.
3. **Live preview & confirm**.
4. Type `APPLY <id>`.
5. Read-back. In dry-run every write is refused.

## Submission checklist
- [x] All 35 communities and all CRM accounts reconciled; evidence for every proposal
- [x] 25 CRM operations human-approved, executed and verified; integrity audit PASS
- [x] Unresolved cases documented with business questions (report §5)
- [x] 130 tests passing
- [x] Read-only daily schedule **installed** as a local cron job (06:00 daily, idempotent) and tested: run #14 PASS, failure capture PASS, 0 CRM writes
- [x] Code committed locally on branch `bellhaven-assessment`
- [x] Cross-checked against the original brief (welcome page): deadline Nov 16 2026 11:29 PM EST; schedule config only (no live cron needed); no hosting
- [x] Public GitHub repository: https://github.com/Giantlyra/bellhaven-crm-reconciliation (`.env`, `data/`, `investigation.txt` are gitignored; `docs/` contains assessment account IDs and phones)
- [ ] ~2-minute video showing evidence, approval, **rejection** and a verified CRM change (script above)
- [ ] Honest actual time spent (`docs/WRITEUP.md`, README)
- [x] Write-up: matching approach, AI tools used, what we'd build next (`docs/WRITEUP.md`). Confirm the AI-tools list
- [ ] Submit before **Nov 16 2026, 11:29 PM EST**
