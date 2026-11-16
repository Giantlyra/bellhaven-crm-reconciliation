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
| Cron | **INSTALLED** (2026-11-16) on the author's Mac. `crontab -l` shows one entry tagged `bellhaven-daily-reconcile`, daily 06:00 local, read-only, logging to `data/daily.log`. The installer is idempotent: a second install still leaves one entry |

## Integrity monitoring

`scripts/final_audit.py` compares:
- the live website with the CRM;
- every ledger write with the live CRM and its read-back receipt;
- protected fields and contacts with the pre-write snapshots;
- duplicate and CHOW links with the verified proposals.

Latest result: **INTEGRITY PASS**. 25 of 25 operations are verified; there are no violations.

Recent runs: #13 completed (2026-11-16T05:27:02), #12 completed (2026-11-16T05:26:22), #11 completed (2026-11-16T01:24:54)

## Cron installation test (2026-11-16 ~15:07 UTC)

| Step | Result |
|---|---|
| Existing crontab before install | none ("no crontab for seale"); backed up anyway |
| Install | 1 entry; re-running the installer still leaves 1 (no duplicates) |
| `crontab -l` | `0 6 * * * cd "$HOME/clipboard-assessment" && { echo "=== bellhaven daily scan <UTC>"; env -u CRM_WRITES_ENABLED .venv/bin/python scripts/run_daily.py; echo "=== exit $?"; } >> data/daily.log 2>&1 # bellhaven-daily-reconcile` |
| Cron daemon | `/usr/sbin/cron` running |
| Exact command, run once in a cron-like minimal environment (`env -i`, PATH=/usr/bin:/bin) | **PASS**: scan **#14** completed, 35 communities / 125 accounts, 0 new / 12 known, `=== exit 0` in `data/daily.log` |
| Failure capture (write flag deliberately forced on) | **PASS**: "Refusing to run the scheduled scan with CRM_WRITES_ENABLED=1…" and `=== exit 1` logged; no scan started |
| CRM write count | **25 before, 25 after** (no writes) |

### Limitation: sleep and power-off
**If the Mac is asleep or off at 06:00, macOS cron does not run the job later. That day's scan is simply skipped** (there is no catch-up) until 06:00 the next day. A missed day is visible because the dashboard's "Last scheduled run" date and `data/daily.log` show no entry for it. Mitigations, if needed: keep the Mac awake at 06:00; schedule a wake with `sudo pmset repeat wakeorpoweron MTWRFSU 05:55:00` (needs an admin password, so the user runs it); or switch to a launchd LaunchAgent with `StartCalendarInterval`, which runs a missed job once when the Mac wakes. A run already in progress is not affected by later sleep settings.
