# Operations: startup, daily schedule and recovery

Every command runs from the project folder: `cd ~/clipboard-assessment`. Copy and paste one line at a time.

## Start the application (single command)

```bash
./bh serve
```

- This opens http://127.0.0.1:8000 in **dry-run**: scans, reviews and live previews are read-only.
- The terminal looks frozen while the server runs; that is normal. `Ctrl+C` stops it.
- If the port is busy, the command says so. Use `./bh serve --port 8020`, or stop the old servers (below).
- The first run creates `.venv` automatically. The token goes in `.env` as `CRM_TOKEN` and is never printed.

### Stop old server windows first

Nine servers from earlier sessions are still running old code: ports 8000–8006, 8010 and 8011.

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':80(0[0-9]|1[01])'
kill <PID>          # repeat for each PID from the line above
```

### Write-enabled session (only after you decide to approve specific items)

```bash
cp data/ledger.db data/ledger.pre-approval.db     # back up decisions and receipts first
CRM_WRITES_ENABLED=1 ./bh serve --port 8020
```

- A red "LIVE WRITES ENABLED" bar appears.
- Every write still needs all of these: **Approve** on the proposal page, a **Live preview**, the reviewed checkbox, and the typed `APPLY <id>`.
- Stop the server with `Ctrl+C` when you're done, and restart without the flag.
- The flag is read from the command line only; `.env` can't turn it on.

## Daily schedule (read-only)

`scripts/run_daily.py` scrapes the website and reads every CRM page. It records new or changed proposals as PENDING, and does nothing else.

- It refuses to start if `CRM_WRITES_ENABLED=1`.
- It never approves, previews or executes.
- An incomplete or failed scan creates no proposals and resolves nothing. The run is recorded as `incomplete` or `failed`, and its exit code is 1.

**Status (2026-11-16): INSTALLED** on the author's Mac. `crontab -l` shows one entry tagged `bellhaven-daily-reconcile`, and a test run passed (see `MONITORING_RESULTS.md`). If the Mac is asleep at 06:00, that day's run is skipped.

**Install or re-install (idempotent; replaces the tagged line instead of duplicating it):**

```bash
(crontab -l 2>/dev/null | grep -v 'bellhaven-daily-reconcile'; grep -v '^#' scripts/crontab.txt | grep .) | crontab -
```

The installed line comes from `scripts/crontab.txt`. For a manual install with `crontab -e`, paste it and save:

```
0 6 * * * cd "$HOME/clipboard-assessment" && { echo "=== bellhaven daily scan $(date -u +\%Y-\%m-\%dT\%H:\%M:\%SZ)"; env -u CRM_WRITES_ENABLED .venv/bin/python scripts/run_daily.py; echo "=== exit $?"; } >> data/daily.log 2>&1 # bellhaven-daily-reconcile
```

**Check that it works.** Run the exact command once by hand:

```bash
.venv/bin/python scripts/run_daily.py
```

It should print `"status": "completed"`, with `"new": 0` while the CRM is unchanged.

**Monitor.**

- The **Start Here → Daily schedule** card shows:
  - whether the cron line is installed
  - the last scheduled run and its status
  - every failed scheduled run, with its error
  - the tail of `data/daily.log`
- `./bh status` shows the latest run of any kind.

**macOS notes.**

- cron runs only while the Mac is awake.
- If `data/daily.log` stays empty, give `/usr/sbin/cron` Full Disk Access in System Settings → Privacy & Security.
- The GitHub Action in `.github/workflows/` is an alternative, but it would upload the private ledger as an artifact. Don't enable it for this assessment.

## Recovery

| Situation | What the system did | What you do |
|---|---|---|
| A scan fails or is incomplete (site or API down, short page) | Run marked `failed` or `incomplete`; no proposal created, changed or resolved | Re-run `./bh scan` later. Nothing to repair |
| A proposal is **BLOCKED** (drift, a policy change on live data, an existing successor) | Nothing written; the reason is shown on the proposal | Run `./bh scan`. A fresh proposal is created from current data and needs a new approval |
| The plan token changed between preview and confirm | Execution refused; nothing written | Open the live preview again and re-confirm |
| A write raises an error, or the read-back mismatches: **FAILED** | Each operation's outcome is saved; nothing is reported as applied | Open the proposal: the write log shows which step failed. **Live preview to resume**, which skips completed steps, then type `APPLY <id>` again |
| CHOW link step fails after the successor was created | Successor id saved; proposal FAILED | Resume as above. The saved successor is reused, and no second `POST` is sent |
| CHOW create times out (outcome unknown) | Operation marked `uncertain` | Resume. The preview searches for the account this candidate created and adopts it. If none is found, it blocks and asks you to check the CRM by hand |
| The server is killed mid-write | The operation stays `started` and the proposal stays EXECUTING. The Submit check "No write left without read-back" turns red | Open the proposal and run a live preview. It re-reads the CRM, recovers a created account if one exists, and shows exactly what remains |
| The ledger is corrupted or lost | — | Restore `data/ledger.pre-approval.db` (or `~/clipboard-assessment-backups/restore-20261115-052425.tgz`), then `./bh scan`. Findlay is re-imported from `data/execution_audit.db` as a receipt |
| You want to undo an identity resolution | — | `./bh resolve <hold#> revoke --note "why"`, then `./bh scan`. The HOLD returns; nothing in the CRM changes |

The engine never deletes CRM records, never merges, and never retries a create blindly. Any change it reverses by hand should go through a new proposal, or be recorded in the History notes.
