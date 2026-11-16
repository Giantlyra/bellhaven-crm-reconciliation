# Nine-path review (2026-11-15, after live read-only scan #9)

> **PRE-EXECUTION SNAPSHOT (2026-11-15, after scan #9).** Kept unchanged as historical evidence. Review of the system before execution. **Final, authoritative outcome:** [FINAL_AUDIT.md](FINAL_AUDIT.md) · [FINAL_RECONCILIATION_REPORT.md](FINAL_RECONCILIATION_REPORT.md).

Each path was evaluated on its own against the code, the live data (scan #9, plus a read-only diff of the snapshot, ledger
and CRM) and the test suite. Conflicting conclusions are reconciled at the end, in a prioritized remediation plan.

**Baseline facts used by every path**

- Scan #9: 35 website facilities (homepage 35, directory 34) and 121 CRM accounts.
  - Website fingerprint `fbc46621…`, CRM fingerprint `5daed874…`. Both have been unchanged since scans #6 and #3.
- Ledger: 32 PENDING, 3 HELD, 0 APPROVED, 0 EXECUTING, 0 VERIFIED, 0 FAILED, 9 SUPERSEDED, 26 RESOLVED.
- 0 CRM write calls by this engine.
- The old `data/snapshot.json` differs from live CRM data **only** in Findlay's `parent_id` / `parent_name` / `updated_at`. That is the verified legacy write.
- All 35 open proposals' baseline values equal the live values, so there is no drift.

---

## 1. Requirements compliance

- **Finding.** 30 of the 36 traced requirements are Met (see `REQUIREMENTS_MATRIX.md`).
  - Three are incomplete only because they need your action: execution, time spent, video.
  - Three cannot be verified, because the original Clipboard brief is not in the workspace: contacts reconciliation, the "Needs Review" vocabulary, and the submission form.
  - The billing SOP is taken from the handoff's restatement.
- **Risk.** If the original brief requires contact reconciliation or defines statuses, the work is incomplete in ways
  this review cannot detect.
- **Action.** Re-read the original brief before submitting, and check rows 34–36 of the matrix.

## 2. Website and CRM completeness

- **Finding.** The scraper follows directory pagination *and* homepage links (Findlay is homepage-only). It fails closed when fewer facilities are found than the homepage advertises.
  - The CRM listing is paginated (3 pages) and fails closed when short.
  - An independent ZIP + street-number cross-check accounts for all 35 facilities and every Bellhaven-parented account.
  - The contacts endpoint is read only ad hoc, for identity evidence. It isn't ingested.
- **Risk.** Low for accounts. Contacts aren't covered (see path 5).
- **Action.** None for accounts.

## 3. Matching quality and false-positive risk

- **Finding.** Identity is decided by exact street+ZIP, by number+ZIP with a similar street, or by a same-city name *supported* by a phone match or a PO Box. A name alone never decides identity.
  - Lower-confidence matches in the actionable queue:
    - #59 Portsmouth: ZIP 45626 → 45662; street and phone match.
    - #46 Ashtabula: PO Box tier; name, ZIP and phone match.
    - #61/#62 Zanesville: exact address; the About page says only "select communities" from Cedar Trail.
    - #70 Sandusky: inferred from absence alone.
  - CRM phones disagree with the website for most accounts, so phone fixes rest on the website as the source of truth.
- **Risk.** #70 is the one proposal where a false positive moves financial history. #61 is medium confidence on ownership, but the account has $0 / $0, so it is reversible.
- **Action.** INVESTIGATE #70. Keep #61/#62 in the approval list, flagged medium confidence.

## 4. Financial safeguards and CHOW

- **Finding.** The SOP is enforced at proposal time **and** on live data at preview time.
  - Missing or malformed values block.
  - Any change in revenue or AR after the proposal blocks (tested, including AR going to 0).
  - No proposal writes `lifetime_revenue` or `outstanding_ar`.
  - CHOW is a single proposal with an ordered plan: preserve the old record, `POST` the successor, `PATCH` the link, read back. It runs under one approval and one typed confirmation, and each step's state is recorded.
  - A link failure resumes with the saved successor id, after a fresh preview and confirmation. An unknown create outcome is looked up, never re-posted.
  - Defiance (#51) has AR, but only its phone changes. Lima (#39) has $47,000 revenue and $0 AR, so the SOP allows a direct re-parent.
- **Risk.** Low in code. Two residual risks:
  - The SOP wording can't be checked against the original brief.
  - CHOW on #54/#60 has never run against the real API. The `POST` fields' acceptance (`care_type`, `status`, `note`) is untested live.
- **Action.** Execute #60 or #54 first, alone, on a write-enabled server, and inspect the read-back before anything else (see the plan below).

## 5. Duplicate-account integrity

- **Finding.** Survivors win on decisive evidence: Bellhaven parent > billing history > website phone.
  - Losers get `duplicate_of_account`, Inactive and a note. A loser with billing history is held; nothing is merged or deleted.
  - All five duplicate losers (#56, #41, #42, #57, #64) have $0 / $0, and every survivor is active and under Bellhaven.
- **Risk.** Contacts on losers stay attached to inactive records. The Owosso loser has Tricia Lindqvist (Admissions). The other four losers have no contacts (read-only `GET /contacts?account_id=…`, 2026-11-15).
- **Action.** After #56 is verified, decide by hand whether to re-point that contact. No contact writes are proposed.

## 6. Approval and execution safety

- **Finding.**
  - Every POST is local-only, same-origin and CSRF-protected.
  - Approval is bound to the proposal fingerprint and writes nothing.
  - A write needs approval, a fresh live preview, a matching plan token, the typed `APPLY <id>`, and a process started with `CRM_WRITES_ENABLED=1`, which can't be set from `.env`.
  - The legacy Findlay route now honours the flag.
  - Nine-card decisions are never imported.
- **Risk (new, operational).** Nine server processes started earlier today from this project directory are **still running pre-fix code**:
  - `app.review` on 8000–8006 (started 00:52–05:03)
  - `app.main` on 8010 (03:19) and 8011 (13:17)

  They predate the legacy-route fix and the sibling-drift logic. Their environment (write flag) can't be inspected from here. The engine's write count is 0, so none of them has written. Still, a reviewer could act from a stale page.
- **Risk (design).** An approval has no expiry. That is mitigated: the typed phrase, the fresh preview token and the fingerprint binding are the real authorization at execution time.
- **Risk (design).** One batch confirmation covers N items. Each item is still previewed, validated, executed and audited on its own, and the batch stops at the first failure.
- **Action.**
  - **P0: stop the stale servers** before any approval session.
  - Execute **individually** by default. Use a batch only for items you have reviewed one by one.

## 7. Persistent state, recovery and safe reruns

- **Finding.** Nine scans: re-runs are no-ops (0 new / 35 known since #4). Decisions survive re-runs.
  - A materially changed proposal supersedes the old one.
  - A proposal that comes back reopens as *pending*, never *approved*.
  - Incomplete scans resolve nothing.
  - `audit_log` and `resolutions` are append-only; operations are persisted before and after each call.
  - **Fixed in this review:** a proposal left in EXECUTING by a killed server couldn't be resumed (only APPROVED or FAILED were accepted). It now resumes through a fresh preview and typed confirmation; an unconfirmed create is looked up and adopted. A process-wide lock refuses a second simultaneous execution. Both are tested.
  - Findlay is imported as a verified receipt and never re-proposed.
- **Risk.** `data/ledger.db` is the only copy of decisions and receipts, and `data/` is gitignored, so there is no backup.
- **Action.** Back up the ledger before the first live write: `cp data/ledger.db data/ledger.pre-approval.db` (see `OPERATIONS.md`).

## 8. Daily scheduling and operational behaviour

- **Finding.**
  - `scripts/run_daily.py` scans only, and refuses to run with `CRM_WRITES_ENABLED=1` (tested in a subprocess).
  - Scheduled runs are tagged `live (scheduled)`. The dashboard shows the last scheduled run, failures (failed runs now record their provenance) and the log tail.
  - The exact cron command has run once (scan #8).
- **Risk.**
  - Cron isn't installed.
  - On macOS, cron only runs while the machine is awake, and may need Full Disk Access for the project folder.
  - There is no alerting beyond the dashboard and `data/daily.log`.
  - The optional GitHub Action would upload the private ledger as an artifact.
- **Action.** Optional: install the local cron line. Don't enable the GitHub Action for this assessment.

## 9. Adversarial testing and submission readiness

- **Finding.** Tests cover:
  - CSRF and cross-origin refusal, and that the token is never rendered
  - the removed token-bearing redirect
  - every GET route making zero writes
  - stale plan tokens, wrong phrases, drift, AR appearing or disappearing, and missing financials
  - superseded, rejected and repeated approvals, and re-execution of verified items
  - batch overlap, uncertain creates, and read-back mismatch

  Jinja autoescaping covers website-sourced text, so a hostile name renders as text. All 112 tests pass in about 0.8 s.
- **Risk.** Submission isn't ready: no commits, no public repository, no video, no time-spent figure, and the form isn't submitted.
- **Action.** See the remaining steps below.

---

## Conflicts between paths, and how they were resolved

| Conflict | Paths | Resolution |
|---|---|---|
| "Prepare *all* evidence-supported corrections" vs "hold speculative ones" | 1 vs 3/4 | Every proposal is prepared, with exact operations. #70, #46, #68 and #69 are prepared but **recommended for hold or investigation**, because their evidence or field semantics are insufficient. |
| Batch convenience vs "each mutation requires fresh explicit authorization" | 6 vs 1 | Execute individually by default (`APPLY <id>`). A batch is allowed only for items already reviewed individually; each item is still separately previewed and audited. |
| Execute duplicates now vs contacts on losers | 5 vs 1 | Duplicates go ahead: nothing is deleted, and contacts remain reachable on the inactive record. Contact re-pointing is a manual follow-up. |
| The engine says the CRM is unchanged vs stale servers could act | 7 vs 6 | Stop the stale servers first. |
| Earlier docs recommended "resolve Amberly/Union Square as distinct" vs the new rule: no automatic action on unsubstantiated identity | 3 vs 1 | Both are now **INVESTIGATE**, with questions and consequences (`INVESTIGATION_QUESTIONS.md`). A resolution is recorded only on your answer. |
| A scheduled job adds confidence vs privacy (GitHub Action) | 8 vs 9 | Local cron only. |

## Prioritized remediation plan

| Priority | Item | Owner | Status |
|---|---|---|---|
| P0 | Stop the 9 stale servers (ports 8000–8006, 8010, 8011): `lsof -nP -iTCP -sTCP:LISTEN \| grep -E ':80(0[0-9]\|1[01])'`, then `kill <PID>` | you | open |
| P0 | Back up the ledger before any live write: `cp data/ledger.db data/ledger.pre-approval.db` | you | open |
| P1 | Approve and execute the evidence-supported items **one at a time** (`APPROVAL_BATCH.md`). Do one CHOW first and inspect its read-back. Then re-scan and confirm only held items remain | you, then the tool verifies | open |
| P1 | Answer the investigation questions for #36, #38, #53, #70, #46, #68 and #69 | you | open |
| P2 | Owosso loser contact: re-point it by hand if wanted, after #56 | you | open |
| P2 | Optional local cron install | you | open |
| P3 | Submission: commit, public repo, video, time spent, form, before the deadline (unverified: Nov 17 2026 04:29 UTC is inferred, not sourced) | you | open |
| Done | UI: full state labels, scan completeness, schedule status and failures, CHOW ordered plan, duplicate survivor/inactive explanation | tool | done |
| Done | Failed scheduled runs record their provenance, so the dashboard can show them | tool | done |
| Done | Optional chat removed from the app; neutral layer names | tool | done |
| Done | Interrupted-execution recovery: a proposal left EXECUTING by a killed server can now be resumed through a fresh preview and confirmation. A process lock prevents two simultaneous executions | tool | done |
| Done | 14 new tests (112 total) | tool | done |
