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
| **4:20–5:00 · Monitoring** | Terminal: `scripts/run_daily.py` (with and without the flag) → Start Here schedule card → `docs/FINAL_AUDIT.md` | "The daily job is read-only and **refuses to run if writes are enabled**. Re-running finds **0 new** items. The dashboard shows the last scheduled run and failures. The cron line is provided but **not installed** on this machine. The final audit re-checks every write against the live CRM: **integrity PASS**." |

## 2-minute demo
| Time | Screen | What to show |
|---|---|---|
| 0:00 | **Start Here** | 35 communities vs 125 CRM accounts; the scan is complete and fail-closed; DRY-RUN banner; "CRM write calls ever: 25"; the daily read-only schedule and 0 failures |
| 0:20 | **Find Problems / Build–Modify** | How a discrepancy is classified: field update, parent correction, change of ownership, duplicate, new account, or insufficient evidence. Open #60 Tiffin |
| 0:40 | **#60 proposal page** | Evidence comparison: website vs CRM, $84,000 / $12,400 → CHOW. The historical account is preserved; the successor starts at $0; the open question about who collects the AR is shown |
| 1:00 | **Queue** | Low-risk queue: eligibility rules, manual-review reasons, the receipts of run 1 (5 of 5 verified) |
| 1:20 | **History** | Append-only audit: approve → preview → typed `APPLY` → op → read-back, per write; the refused attempts are logged too |
| 1:40 | `docs/FINAL_AUDIT.md` | Integrity PASS: 25 of 25 operations live-matched; protected fields and contacts intact |
| 1:50 | `docs/FINAL_RECONCILIATION_REPORT.md` §5 | The unresolved cases left open on purpose, each with its business question |

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
- [x] Read-only daily schedule demonstrated; **cron is not installed** (no crontab for this user); the line is in `scripts/crontab.txt`
- [x] Code committed locally on branch `bellhaven-assessment`
- [ ] **Re-check against the original Clipboard brief.** It isn't in this repository; confirm the required form fields and deliverables
- [ ] Public GitHub repository (`.env`, `data/` and `investigation.txt` are gitignored; `docs/` contain assessment account IDs and phones)
- [ ] 2-minute video
- [ ] Form: repo link, video link, honest time spent, write-up
