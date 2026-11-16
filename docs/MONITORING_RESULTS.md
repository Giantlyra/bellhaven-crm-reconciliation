# Monitoring Results

_Generated 2026-11-16 05:28 UTC. All read-only._

## Scheduled read-only scan (the daily job)

| Check | Result |
|---|---|
| Safety gate: `CRM_WRITES_ENABLED=1 python scripts/run_daily.py` | **Refused**, exit 1: "Refusing to run the scheduled scan with CRM_WRITES_ENABLED=1 (scheduled jobs are read-only)." |
| Scheduled run (`scripts/run_daily.py`) | Run **#13** completed: 35 website communities, 125 CRM accounts, complete scrape. **0 new, 12 already known**, so re-runs are idempotent |
| Manual follow-up scan | Run **#12** completed: 1 new proposal (#71 Amberly Manor, Hudson OH, from the operator's identity resolution) |
| CRM writes during monitoring | **0** (operations total unchanged at 25) |
| Dashboard (Start Here) | Shows the latest scan #13 (live, scheduled), completeness, "Last scheduled run #13, completed", "Scheduled failures recorded: 0", and "CRM write calls ever: 25" |
| Cron | The line is in `scripts/crontab.txt` (daily 06:00, read-only). **Not installed** on this machine (optional) |

## Integrity monitoring

`scripts/final_audit.py` compares:
- the live website with the CRM;
- every ledger write with the live CRM and its read-back receipt;
- protected fields and contacts with the pre-write snapshots;
- duplicate and CHOW links with the verified proposals.

Latest result: **INTEGRITY PASS**. 25 of 25 operations are verified; there are no violations.

Recent runs: #13 completed (2026-11-16T05:27:02), #12 completed (2026-11-16T05:26:22), #11 completed (2026-11-16T01:24:54)
