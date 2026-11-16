# Assessment Walkthrough

_For the reviewer. Every step is read-only unless stated otherwise._

## Setup (1 minute)
```
cd ~/clipboard-assessment
./bh test          # 130 tests, mocked CRM, about 1 s
./bh status        # last scan, proposal counts, write calls (25)
./bh serve         # http://127.0.0.1:8000, DRY-RUN
```

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
- [x] Read-only daily schedule demonstrated (cron optional, not installed)
- [x] Code committed locally on branch `bellhaven-assessment`
- [ ] **Re-check against the original Clipboard brief.** It isn't in this repository; confirm the required form fields and deliverables
- [ ] Public GitHub repository (`.env`, `data/` and `investigation.txt` are gitignored; `docs/` contain assessment account IDs and phones)
- [ ] 2-minute video
- [ ] Form: repo link, video link, honest time spent, write-up
