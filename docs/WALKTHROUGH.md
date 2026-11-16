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

## 2-minute demo video: BEFORE → WHAT WE FOUND → HOW WE DECIDED → AFTER

**Presentation view and teleprompter:** `docs/teleprompter.html`. Double-click it in Finder; it works offline.
- Each of the 7 beats has a **visual panel** built from authentic data: the scan #3 snapshot for *Before*, the ledger for the findings, and `FINAL_AUDIT.md` for *After*. Each panel shows its source.
- **S** = slide view (panels only, large: show this on screen while recording).
- **C** = narration only (for reading).
- ←/→ move between beats · **T** starts the 2:00 timer.

The narration is **256 words, about 2:00**.

| # | Time | Screen | Narration |
|---|---|---|---|
| 1 BEFORE | 0:00–0:20 | Presentation, slide view, beat 1 ("Before" panel) | Bellhaven's website lists thirty-five communities. The CRM had a hundred and twenty-one accounts, and only nine matched cleanly. The first full scan found thirty-five issues: wrong phones and names, wrong parent companies, duplicates, missing communities, and accounts with unpaid balances. |
| 2 FOUND | 0:20–0:35 | Slide beat 2 (optionally app `/proposal/56`, Owosso) | Six addresses had more than one account. I learned that two accounts at the same address don't automatically mean one is a duplicate. One might be a historical predecessor, and the financial consequences are very different. |
| 3 FOUND | 0:35–0:55 | Slide beat 3 (optionally app `/proposal/53`, Kettering) | Owosso was a true duplicate, so it was inactivated and linked. Monroe, Port Clinton and Erie kept their earlier operators' records. The first scan even proposed creating Amberly Manor and Union Square; stricter identity checks found conflicting records and stopped those creates. |
| 4 DECIDED | 0:55–1:15 | App **`/proposal/60`**, financial table | Tiffin sat under Cedar Trail with eighty-four thousand dollars of revenue and twelve thousand four hundred still owed. Re-parenting it would break the billing rules. So we kept that history, created a new Bellhaven account at zero, and linked them: two verified writes. |
| 5 DECIDED | 1:15–1:30 | App `/proposal/60` Decisions and Write log → **`/history`** | The system is deterministic Python; AI helped me build and review it, never to change the CRM. I approve, the live preview re-checks everything, I type APPLY, and the result is read back. |
| 6 DECIDED | 1:30–1:40 | App **`/proposal/68`** (REJECTED) | Alliance's proposed status doesn't exist in the CRM, so I rejected it. Nothing was written. |
| 7 AFTER | 1:40–2:00 | Slide beat 7 (Before/After table) → app Start Here | Now: twenty-five verified operations, twenty-three exact matches, an audit that passes, and a daily read-only scan. I didn't just build a system that finds differences. I built a workflow that evaluates the evidence, protects financial history, requires human approval, and recognizes when a change shouldn't be made. |

**Before recording:**
- Run the app in **dry-run**: http://127.0.0.1:8020.
- Open two browser windows: the presentation in slide view, and the app.
- Crop the address bar.
- **Do not make a CRM write on camera.**

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
