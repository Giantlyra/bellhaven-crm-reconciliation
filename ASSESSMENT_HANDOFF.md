# Assessment Handoff: Bellhaven CRM Reconciliation

This is the authoritative operational handoff. Claude Code updates it after each meaningful action.
It contains no credentials or tokens.
Labels: **[V]** verified this session by a live read, ledger query or test run · **[R]** from an earlier report or document, not re-checked · **[A]** assumption · **[Rec]** recommendation.

_Last updated: 2026-11-16 ~15:10 UTC by Claude Code. Local cron INSTALLED and tested (run #14 PASS; failure capture PASS; CRM writes still 25)._

---

## 0. Consolidated assessment (authoritative, 2026-11-16)
**Full report: [`docs/RECONCILIATION_DECISION_REPORT.md`](docs/RECONCILIATION_DECISION_REPORT.md).** It supersedes the one-at-a-time review in §6b–§6d.

- [V] Inputs: 34 open proposals, a live read of all 121 CRM accounts and 67 contacts, scan #11 and the About page. No baseline has drifted. No existing CHOW or duplicate links, and no notes. Status values in use: Active and Inactive only.
- [V] Coverage: 35 website communities, of which 10 are clean matches and 25 have proposals. All 5 off-website Bellhaven accounts are covered.

| Decision | Count | Proposals |
|---|---|---|
| READY FOR APPROVAL | 23 | #58, #65, #52, #55, #45, #51, #37, #44, #49, #50, #63, #66, #67, #59, #56, #39, #61, #40 (after #39), #62 (after #61), #47, #48, #60, #54 (after #60) |
| NEEDS INVESTIGATION | 9 | #41, #42, #57, #64 (Q1, predecessor records), #53 (Q2), #36 and #38 (Q4), #70 (Q3), #46 (Q5) |
| NOT RECOMMENDED | 2 | #68, #69 ("Needs Review" is not a CRM status value; Q6) |

- Changed from earlier recommendations:
  - #57 and #64 moved to NEEDS INVESTIGATION, to stay consistent with the user's Monroe hold, since they follow the same pattern.
  - #68 and #69 are now REJECT as written; they were previously HOLD.
  - #36 is now "resolve as distinct", because the CRM's Amberly Manor is in Colorado, outside Bellhaven's four states.
- Execution waves: A field fixes (14) → B #56 → C #39, #61 → D #40, #62 (after C verifies) → E #47, #48 → F #60, then #54 → G re-scan → H investigation.
- No approvals were granted and no CRM writes were made in this assessment.

## 0b. Controlled execution queue (added 2026-11-16 at the user's request)
**Page:** http://127.0.0.1:8020/queue (nav "Queue"). **Code:** `app/exec_queue.py`, plus 3 routes in `app/main.py` and the templates `queue*.html`. **Tests:** `tests/test_queue.py` (11 tests).

**What stays the same:** the queue adds **no new write path**. Each item still goes through `executor.execute`: approval bound to the proposal fingerprint, fresh preview with plan token, policy and SOP re-check, per-operation audit, read-back, and the `CRM_WRITES_ENABLED` requirement.

**What it adds:**
- An eligibility gate.
- Automatic per-item pre-write validation, including a live website re-fetch.
- An independent full-record and contacts diff after each read-back.
- Stop-on-first-error.
- Receipts: audit events `queue_started`, `queue_item` and `queue_finished`, plus a JSON file in `data/queue_receipts/`.

**Eligible (all must hold):**
- FIELD_UPDATE changing only `phone` and/or `name` on one account.
- Exact address+ZIP match and high confidence.
- No competing CRM records and no warnings.
- The account is already under Bellhaven, Active, with no CHOW or duplicate link.
- For a rename, name similarity ≥ 0.80.

**Never queueable (manual review):** parent changes, CHOW, duplicates, creates, CRM_ONLY, HOLD, billing-address fields, uncertain matches and material renames.

**Never automatic:** the queue does **not** approve. The user approves each record, from the queue page or the proposal page. Running needs one review tick plus the typed `APPLY QUEUE OF <n>`, and is refused in dry-run before any write.

**Current sort of the real ledger:**
- **5 eligible and awaiting your approval:** #51 Defiance, #44 Ashland, #63 Grove City, #67 Dayton, #37 Sycamore Ridge.
- **24 manual review.** From Wave A this includes #49, #50 and #66 (material renames) and #59 (billing ZIP, name+city match).

**Queue status (verified 2026-11-16 ~03:30 UTC):**
- The user **approved** #37, #44, #51, #63 and #67 in the app at 03:20:18–03:20:29 UTC (decisions in audit #156–#165).
- **No queue has been validated or run.** The ledger has no `queue_*` events and still 6 operations, and there is no receipt file.
- A live GET shows all five accounts identical to `data/wave_a_pre_execution_snapshot.json`.
- **Nothing to verify yet.** The five stay APPROVED, with nothing written.

**Queue run 1 (2026-11-16 03:26:52–03:26:55 UTC): 5/5 VERIFIED.**
- Items: #37, #44, #51, #63, #67. The user typed `APPLY QUEUE OF 5`; one earlier attempt with a mismatched phrase was refused before any write.
- Receipt: `data/queue_receipts/queue-20261116T032655Z.json`. Audit #176–#217 (stopped=false). Operations #7–#11.
- **Independent live check:** for every account only the approved fields plus `updated_at` changed. Parent, status, revenue, AR, links and note are unchanged; contacts are unchanged. Every receipt equals the live CRM. #51 is still $66,000 / AR $9,500.
- Dry-run restored afterwards. Backup: `data/ledger.pre-queue2.db`.

**Queue session 1 (2026-11-16): not run.**
- The server was switched to live writes (PID 85605) and `/queue` was shown with the 5 approved items. Ledger backup: `data/ledger.pre-queue1.db`.
- **No validation or run took place.** There are no audit events after #165, still 6 operations, and no receipt.
- A live GET shows all 5 accounts and their contacts identical to the pre-Wave A snapshot.
- Status: **#37, #44, #51, #63 and #67 are APPROVED, not executed.** The server was restored to dry-run (PID 85810).

**Demo (2026-11-16):** run on a **throwaway copy** of the ledger with sandbox approvals, against the live CRM and website, in dry-run.
- All 5 validated READY, with the exact before-values and request bodies.
- The run was refused before any write (dry-run).
- The real ledger is unchanged: the 5 are still PENDING, and 6 operations in total.

## 0a. Wave A: 14 field corrections (validated 2026-11-16, NOT authorized)
**Final validation:** [`docs/WAVE_A_FINAL_VALIDATION.md`](docs/WAVE_A_FINAL_VALIDATION.md).
- All 14 are **verified**: no drift; the PRD register, ledger, CRM and live website all agree.
- Conditional checks ★ #49, #66 and #59 all passed, with documented residuals.
- Pre-execution snapshot for protected-field diffs: `data/wave_a_pre_execution_snapshot.json`.
- The user and ChatGPT **tentatively approved all 14** in conversation (PRD dated 2026-11-15). **These are not authorizations.**
- Recommended individual order: #58, #65, #52, #55, #45, #51, #44, #63, #67, #37, #50, #59, #49, #66.
Review sheet: [`docs/WAVE_A_REVIEW.md`](docs/WAVE_A_REVIEW.md). It was built from a fresh live read; no Wave A proposal has drifted.

**Rules (from the user):**
- "Ready" ≠ authorized. The user decides each item.
- Execution is **one item at a time**, each with a fresh preview, `APPLY <id>`, a live read-back and an audit receipt.
- **No batch writes.**
- The 9 investigation cases and 2 not-recommended cases are preserved untouched.

| # | Account | Change | User decision | Executed | Read-back / receipt |
|---|---|---|---|---|---|
| 58 | `001UELXDAKFRKB8932` Port Clinton | phone → (330) 733-6423 | tentative ✔ · verified · **authorized in chat + in-app** | ✅ 2026-11-16 02:47:11 UTC (`APPLY 58`) | ✅ live diff: phone only · decisions #3–4 · op #2 · audit #100–109 |
| 65 | `001CVBBCSDM7YHN220` Erie | phone → (614) 792-9343 | tentative ✔ · verified · **authorized in chat + in-app** | ✅ 2026-11-16 02:52:27 UTC (`APPLY 65`) | ✅ live diff: phone only · decisions #5–6 · op #3 · audit #110–119 |
| 52 | `001JQER1RMYKNRLNME` Goshen | phone → (330) 405-6040 | tentative ✔ · verified · **authorized in chat + in-app** | ✅ 2026-11-16 02:58:21 UTC (`APPLY 52`; one earlier attempt refused by the dry-run gate, audit #123) | ✅ live diff: phone only · decisions #7–8 · op #4 · audit #120–131 |
| 55 | `0015L38R1Z5947ZZP7` Marion | phone → (517) 847-7948 | tentative ✔ · verified · **authorized in chat + in-app** | ✅ 2026-11-16 03:00:50 UTC (`APPLY 55`) | ✅ live diff: phone only · decisions #9–10 · op #5 · audit #132–141 |
| 45 | `001UKEFGADQ8YCZ4YM` Findlay | phone → (231) 533-2969 | tentative ✔ · verified · **authorized in-app** | ✅ 2026-11-16 03:05:33 UTC (`APPLY 45`; earlier attempts refused by the dry-run gate, audit #145/#147) | ✅ live diff: phone only, parent still Bellhaven · decisions #11–12 · op #6 · audit #142–155 |
| 51 | `001R4PXTUD9R6FNN8V` Defiance | phone → (330) 691-2711 | tentative ✔ · verified · **approved in-app → queue run 1** | ✅ 2026-11-16 03:26:54 UTC (`APPLY QUEUE OF 5`) | ✅ live diff: approved fields only; contacts unchanged · decision #20 · op #9 · #200 |
| 37 | `00191H7JR16471SZ34` Sycamore Ridge | name, phone | tentative ✔ · verified · **approved in-app → queue run 1** | ✅ 2026-11-16 03:26:52 UTC (`APPLY QUEUE OF 5`) | ✅ live diff: approved fields only; contacts unchanged · decision #18 · op #7 · #184 |
| 44 | `001RJ0D7Z5MAZN5HX5` Ashland | name, phone | tentative ✔ · verified · **approved in-app → queue run 1** | ✅ 2026-11-16 03:26:53 UTC (`APPLY QUEUE OF 5`) | ✅ live diff: approved fields only; contacts unchanged · decision #19 · op #8 · #192 |
| 49 | `001RJU1X4NBWC1Q0G7` Chagrin Falls | name, phone | tentative ✔ (chat) · **verified** · awaiting authorization | — | — |
| 50 | `0013NUZQHQUEZ8DXEG` Chesterton | name | tentative ✔ (chat) · **verified** · awaiting authorization | — | — |
| 63 | `001TZCSTBZFM6K5BGN` Grove City | name | tentative ✔ · verified · **approved in-app → queue run 1** | ✅ 2026-11-16 03:26:54 UTC (`APPLY QUEUE OF 5`) | ✅ live diff: approved fields only; contacts unchanged · decision #21 · op #10 · #208 |
| 66 | `0017MN2JYAJBDS8WQZ` Willow Creek | name, phone | tentative ✔ (chat) · **verified** · awaiting authorization | — | — |
| 67 | `0010KJFP601YNTZVDA` Dayton | name, phone | tentative ✔ · verified · **approved in-app → queue run 1** | ✅ 2026-11-16 03:26:55 UTC (`APPLY QUEUE OF 5`) | ✅ live diff: approved fields only; contacts unchanged · decision #22 · op #11 · #216 |
| 59 | `001CF3LDWVRGL09P4F` Portsmouth | billing_zip → 45662 | tentative ✔ (chat) · **verified** · awaiting authorization | — | — |

## 1. Application status
- [V] One server is running: `./bh serve --port 8020` (PID 95736), in **dry-run**. The CHOW window is closed.
- [V] **CRM write mode: DRY-RUN.**
- [V] No other app servers are listening.
- [V] Claude Code can read the UI in its built-in browser pane.
- To execute an approved item later, the user restarts deliberately: `CRM_WRITES_ENABLED=1 ./bh serve --port 8020`.

## 2. Latest scan
- [V] **Run #11** · 2026-11-16 01:24:55 UTC · complete · live · read-only. It found 35 website facilities and 121 CRM accounts, with **0 new, 34 known, 0 resolved**.
  "Known" fell from 35 to 34 because Monroe is now a clean match and produced no proposal.
- [V] Fingerprints: website `fbc4662186122d50…` (unchanged), CRM `b7f40908632c630d…` (changed from `5daed874…`).
- [V] Snapshot diff, run #10 vs #11: the **only** CRM change across all 121 accounts is `001U1750VLVJAGG1S5` phone (814) 291-2902 → (814) 412-2218 and its `updated_at`. No unexpected changes.
- [V] The proposal table (id, status, fingerprint) is identical before and after the scan, so there are no unexpected proposals.
- Ledger backup taken before the scan: `data/ledger.pre-scan11.db`.

## 3. Proposal counts (ledger, verified)
| Status | Count |
|---|---|
| PENDING | 21 (FIELD_UPDATE 7, DUPLICATE 5, CHOW 3, WRONG_PARENT 2, WEBSITE_ONLY 2, CRM_ONLY 2) |
| HELD | 3 (#36 Amberly, #38 Union Square, #53 Kettering) |
| VERIFIED | 11 (#43, #58, #65, #52, #55, #45, #37, #44, #51, #63, #67) |
| APPROVED / EXECUTING / FAILED / BLOCKED / REJECTED | 0 |
| SUPERSEDED / RESOLVED | 9 / 26 |

## 4. Verified CRM changes
| # | Change | Evidence |
|---|---|---|
| Legacy | Findlay `001UKEFGADQ8YCZ4YM.parent_id` "" → `0015QAPLGS3FVYEEEM` (Bellhaven) | `data/execution_audit.db` STARTED→VERIFIED at 2026-11-15 10:14:01 UTC. [R] Live scans #3–#10 confirm it. **Do not retry.** |
| **#37, #44, #51, #63, #67** | Wave A field fixes (names/phones) via the controlled execution queue, run 1 | [V] decisions #18–#22, operations #7–#11, queue receipt `queue-20261116T032655Z.json`. Live full-record and contacts diff: only the approved fields changed. |
| **#45** | Findlay `001UKEFGADQ8YCZ4YM.phone` (330) 975-2492 → **(231) 533-2969** (Wave A) | [V] decisions #11–#12, operation #6 verified, audit #142–#155. Full-record diff: only `phone` and `updated_at` changed; `parent_id` still Bellhaven; $22,000 / AR $0 unchanged. |
| **#55** | Marion `0015L38R1Z5947ZZP7.phone` (330) 314-3109 → **(517) 847-7948** (Wave A) | [V] decisions #9–#10, operation #5 verified, audit #132–#141. Full-record diff: only `phone` and `updated_at` changed. |
| **#52** | Goshen `001JQER1RMYKNRLNME.phone` (517) 409-8156 → **(330) 405-6040** (Wave A) | [V] decisions #7–#8, operation #4 verified, audit #120–#131. Full-record diff: only `phone` and `updated_at` changed; $121,000 / AR $0 unchanged. |
| **#65** | Erie `001CVBBCSDM7YHN220.phone` (419) 495-1741 → **(614) 792-9343** (Wave A) | [V] decisions #5–#6, operation #3 verified, audit #110–#119. Full-record diff: only `phone` and `updated_at` changed. Harborview `001BLYF02K97SZLZHH` untouched. |
| **#58** | Port Clinton `001UELXDAKFRKB8932.phone` (614) 512-8712 → **(330) 733-6423** (Wave A) | [V] decisions #3–#4, operation #2 verified, audit #100–#109. Independent full-record diff vs `data/wave_a_pre_execution_snapshot.json`: only `phone` and `updated_at` changed. Harborview `001JD2MWRA74LTSN24` untouched. |
| **#43** | Monroe `001U1750VLVJAGG1S5.phone` (814) 291-2902 → **(814) 412-2218** | [V] Ledger decisions #1 (approved 01:17:13) and #2 (executed: `APPLY 43`, token `9294078f…`, actor `local-reviewer`). Operation #1 is PATCH `{phone}` → verified. Audit log #88–#97. Pre-write snapshot: `data/pre_43_001U1750VLVJAGG1S5.json`. **[V] Independent live GET in this session: phone = (814) 412-2218, CRM `updated_at` 2026-11-16 01:17:47Z. No other field changed (parent, status, financials unchanged).** |

The engine's lifetime write-call count is **11** (#43, #58, #65, #52, #55, #45, #37, #44, #51, #63, #67). [V] After scan #11, #43 is still **VERIFIED**. Its audit records are intact: decisions 2, operations 1, audit entries #88–#97. The scan only appended #98–#99 (run_started/run_finished), and audit_log is append-only by trigger.

## 5. Proposal #43 (Monroe): post-execution review
- Website (live, [V]): Bellhaven Gardens of Monroe, 750 Stewart Rd, Monroe MI 48162, (814) 412-2218, Assisted Living, administrator Phil Mabry.
- The CRM has three Active accounts at that address, all $0 revenue and $0 AR [V]:

| Account | Name | Parent | Phone |
|---|---|---|---|
| `001U1750VLVJAGG1S5` | Bellhaven Gardens of Monroe | Bellhaven | (814) 412-2218 (fixed by #43) |
| `0011AB44D05WLA9HTX` | Cedar Trail of Monroe | Cedar Trail Communities | (216) 748-7799 ("750 Stewart **Road**") |
| `00159PL81N38KM4FHM` | Monroe Gardens Care Center | Harborview Care Group | (330) 501-4496 |

- Why the correction was justified: the account's name, street, city, ZIP and care type match the website exactly, and the account sits under the Bellhaven parent. The website is the source of truth for phone. The old number (814) 291-2902 does not appear anywhere on the website.
- Remaining uncertainty:
  - None of the three CRM phones matched the website before the fix, so identity rests on address, name and parent, not on phone.
  - Area code 814 is a Pennsylvania code, not a Monroe MI code. That holds for both the old and the new number. This looks like synthetic assessment data rather than a reason to doubt the change. [A]
  - The CRM `updated_at` was 2026-11-15 04:29:11Z before the write. The website shows no timestamp of its own; we have only our retrieval time.

## 6. Pending items and dependencies
- **#41 / #42 Monroe duplicates**: **kept unapproved by the user's decision, pending clarification** (§6a). They stay PENDING in the ledger; nothing was rejected or changed.
- **#45 Findlay phone**: prepared for review (§6b). Not approved.
- **#39 → #40 Lima**: a re-parent and a phone fix on the same account. Run them one at a time; the batch overlap guard defers the second.
- **#61 → #62 Zanesville**: a re-parent and a name/phone fix on the same account. The account has $0 revenue, which may mean a rebrand.
- **#56, #57, #64**: duplicates (Owosso, Port Clinton, Erie). #58 and #65 are phone fixes on the Port Clinton and Erie survivors.
- **#47, #48 WEBSITE_ONLY**: create accounts for Batavia and Carlisle.
- [R] Recommended for hold or investigation: #70 Sandusky (speculative CHOW link), #46 Ashtabula (the PO Box is a billing address), #68 and #69 Alliance and Coldwater ("Needs Review" is not a status value in the CRM).

## 6a. #41 / #42 evidence comparison (read-only, 2026-11-16)
| | Survivor `001U1750VLVJAGG1S5` | #41 loser `0011AB44D05WLA9HTX` | #42 loser `00159PL81N38KM4FHM` |
|---|---|---|---|
| Name | Bellhaven Gardens of Monroe | Cedar Trail of Monroe | Monroe Gardens Care Center |
| Parent | Bellhaven | Cedar Trail Communities | Harborview Care Group |
| Street | 750 Stewart Rd | 750 Stewart **Road** | 750 Stewart Rd |
| City/State/ZIP | Monroe MI 48162 | same | same |
| Care type | Assisted Living | Assisted Living | Assisted Living |
| Phone | (814) 412-2218 (website, via #43) | (216) 748-7799 (unique in CRM) | (330) 501-4496 (unique in CRM) |
| Revenue / AR | $0 / $0 | $0 / $0 | $0 / $0 |
| Status / CHOW / dup links / note | Active / – / – / – | Active / – / – / – | Active / – / – / – |
| Contacts | 1 (Elaine Vogel, Billing Coordinator) | none | none |
| CRM updated_at | 2026-11-16 01:17:47Z (#43) | 2026-11-15 04:29:11Z (seed) | 2026-11-15 04:29:11Z (seed) |

What the evidence shows:
- [V] The website lists **one** community at 750 Stewart Rd with a single care offering. No evidence suggests a second facility at that address.
- [V] The About page says Harborview Care Group joined Bellhaven in 2025 and "select communities" from Cedar Trail joined in 2026. Monroe is not named.
- [V] Each loser's name follows its parent's brand ("Cedar Trail of …" like Zanesville; "… Care Center" like other Harborview records). "Monroe Gardens" and "Bellhaven Gardens of Monroe" share "Gardens", which suggests a rebrand. The "Road" spelling suggests the Cedar Trail record came from a separate source.
- [V] The same pattern of a $0 predecessor-brand record next to a Bellhaven record appears at Port Clinton (#57) and Erie (#64). It also appears at Kettering (#53, HELD), where no Bellhaven-parented record exists.
- Conclusion [A/Rec]: these look like **predecessor-operator (historical ownership) records** of the same building, not separate facilities. They carry no billing history, AR or contacts, so the SOP does not require CHOW preservation; that applies only when revenue > 0 and AR > 0. Treating them as duplicates (link + Inactive + note, nothing deleted) is allowed and reversible.
- Uncertainty:
  1. The survivor wins only on "under Bellhaven parent". Before #43 no phone matched, so its phone match now is a result of #43, not independent evidence.
  2. The order of ownership cannot be determined. It is unclear why one building would have both a Harborview and a Cedar Trail record; one may simply be a data-entry duplicate.
  3. The appended note says "Duplicate of …" rather than "prior-operator record". Changing that wording would require a code change and a new proposal fingerprint.
- [V] Execution readiness: the baselines match the live data, and the survivor's phone is not in either baseline, so #43 causes no drift block. Each item writes only its own loser account (PATCH `duplicate_of_account`, `status=Inactive`, `note`).
- [Rec, earlier] Both are reasonable to approve **individually**. If the user wants ownership history recorded explicitly, hold them and decide on the note wording first.

**User decision (2026-11-16): keep #41 and #42 unapproved until it is clear whether they are historical ownership records or true duplicates.**

Why the question cannot be settled from the data we have:
- **Historical ownership (predecessor-operator records)** is supported by: parent brands that match the 2025 Harborview and 2026 Cedar Trail acquisitions on the About page; the brand-style names and the shared "Gardens" in the names; and the same pattern at Port Clinton and Erie.
- **True duplicates (accidental re-entry)** are supported by: $0 revenue on all three records, so no billing ever ran through the old operators; no contacts; identical care type; and the identical seed `updated_at`. Nothing in the CRM (no notes, no `chow_current_account`, no history field) records a change of ownership.
- **Missing evidence**: dates of acquisition or account creation, any billing or contract history, and confirmation from someone at Bellhaven or Clipboard of whether Monroe came via Harborview, via Cedar Trail, or neither. It is also unclear why one building would carry both predecessor brands.
- **Why it matters**: the write is the same either way and reversible. But if these are ownership records, the note "Duplicate of …" mislabels history, and `chow_current_account` might be the more accurate link. The SOP only *requires* CHOW handling when revenue > 0 and AR > 0, which is not the case here.
- Evidence is preserved in the ledger payloads for #41 and #42, the run #11 snapshot `data/snapshots/run-0011-*.json`, and this section.

## 6b. #45 Findlay phone: prepared for review (read-only, 2026-11-16, not approved)
Why this one: it is the first phone-only item in Approval Batch wave 1a. It is **independent**: no other open proposal touches this account, there is no sibling in the same building, and no other account in ZIP 45840. #51, #52 and #55 were also checked and are equally clean; they follow it in batch order. #58 and #65 are not independent because they belong to the duplicate proposals #57 and #64.

| Field | Website (live, run #11 + direct fetch) | CRM `001UKEFGADQ8YCZ4YM` (live GET) | Match |
|---|---|---|---|
| Name | Bellhaven Meadows of Findlay | Bellhaven Meadows of Findlay | ✅ |
| Street | 1800 N Blanchard St | 1800 N Blanchard St | ✅ exact |
| City/State/ZIP | Findlay OH 45840 | Findlay OH 45840 | ✅ |
| Care | Assisted Living, Memory Support | Assisted Living | ≈ (primary matches; out of scope) |
| Parent | — | Bellhaven (legacy-verified write) | ✅ |
| **Phone** | **(231) 533-2969** | **(330) 975-2492** | ❌ |
| Revenue / AR | — | $22,000 / $0 | n/a for a phone change |
| Status / CHOW / dup | — | Active / – / – | ✅ |
| Contacts | Administrator Sam Pruitt | Sam Pruitt, Administrator, (614) 629-5995 | ✅ name |

- **Proposed operation:** `PATCH /api/v1/accounts/001UKEFGADQ8YCZ4YM {"phone": "(231) 533-2969"}`. Only `phone` is sent; `parent_id` and the financial fields are untouched.
- **Competing candidates:** none. No other CRM account is in ZIP 45840. Neither the old nor the new phone appears on any other account. The website has one Findlay community, linked only from the homepage.
- **Drift:** none. All baseline fields equal the live values. CRM `updated_at` is still 2026-11-15 10:14:01Z, the legacy parent write.
- **Risks:**
  1. This is the account that has the legacy verified Findlay re-parent. The phone change is a separate proposal and does not re-run that write, but reviewers may confuse the two ("Do not retry Findlay" refers to `parent_id` only).
  2. Findlay is the homepage-only listing, missing from the directory. The page itself is live and complete.
  3. The care-type difference (Memory Support) is not part of this proposal.
  4. The contact's personal phone, (614) 629-5995, differs from both numbers. That is expected for a person versus a facility line.
- **Assessment [Rec]:** low risk, high confidence. It is ready for the user's individual decision.

## 6c. Review order (user decision, 2026-11-16)
One proposal at a time: evidence → recommendation → **user decides** → separate in-app authorization → live read-back → handoff update.
1. Phone-only: #58, #65, #52, #55, #45, #51
2. Name/phone/ZIP: #37, #44, #49, #50, #63, #66, #67, #59
3. Parent: #39, #61
4. Dependent, only after their prerequisites verify: #40 (after #39), #62 (after #61), #57, #64
5. Create: #47, #48
6. CHOW: #60 Tiffin, then #54 Marietta
7. Duplicates and ambiguous: #41, #42, #56, #36, #38, #46, #53, #68, #69, #70

| # | Status | Recommendation | User decision | Executed / read-back |
|---|---|---|---|---|
| 58 | presented (§6d) | APPROVE | pending | — |

_The one-at-a-time tracker was superseded on 2026-11-16 by the user's request for one consolidated assessment (§0)._

## 6d. #58 Port Clinton phone (read-only review, 2026-11-16; not approved)
| Field | Website (live) | CRM `001UELXDAKFRKB8932` (live) | |
|---|---|---|---|
| Name | Bellhaven of Port Clinton | Bellhaven of Port Clinton | ✅ |
| Address | 1420 Harbor Point Dr, Port Clinton OH 43452 | same | ✅ exact |
| Care | Short-Term Rehabilitation & Nursing | Skilled Nursing | ✅ (standard mapping) |
| Parent | — | Bellhaven | ✅ |
| **Phone** | **(330) 733-6423** | **(614) 512-8712** | ❌ |
| Administrator | Brenda Whitfield | contact Brenda Whitfield, Administrator (also Angela McAllister, DON) | ✅ (checked by Claude; the app's page does not cross-check contacts) |
| Revenue / AR, status | — | $0 / $0, Active | — |

- **Operation:** PATCH `001UELXDAKFRKB8932` `{"phone": "(330) 733-6423"}`. Nothing else is sent.
- **Competing candidate:** `001JD2MWRA74LTSN24` Harborview Nursing & Rehab of Port Clinton, at the same address ("Drive"), with Harborview parent, phone (216) 314-1338, $0/$0, no contacts. That account is the subject of #57 (duplicate, phase 4). Neither CRM phone matches the website. The Bellhaven account wins on parent and on the administrator contact.
- **Independence:** #57 writes only the Harborview account, and its baseline for the Bellhaven account excludes `phone`. So #58 and #57 do not block each other, and #58 does not decide #57.
- **Drift:** none; scan #11 and live GET both match the baseline.
- **Risks:**
  1. The website is the only source for the phone number.
  2. If #57 is later rejected because both records are judged real, #58 is still correct for the Bellhaven-branded account.
- **Recommendation: APPROVE.**

## 7. Financial safeguards and CHOW protections (from code and README; enforced at preview time)
- If revenue > 0 and AR > 0, it is a CHOW. The old account is left untouched. The engine POSTs a successor under Bellhaven, then PATCHes the old account's `chow_current_account`. Only one CHOW runs at a time.
- Missing, malformed or negative financials put the item on HOLD. They are never treated as 0.
- The preview re-reads live data. Drift invalidates the plan token. An existing `chow_current_account` is never overwritten, and no POST is made if a successor already exists at the address. A partial-failure retry reuses the saved successor id.
- An account with billing history or a CHOW link cannot be inactivated.
- CHOW queue: **#60 Tiffin** ($84,000 / AR $12,400), **#54 Marietta** ($51,250 / AR $3,800), **#70 Sandusky** ($130,000 / AR $5,200; link only). All are PENDING and unexecuted. [V]

## 8. Unresolved investigation questions
- #36 Amberly Manor (same name, different address), #38 Union Square (conflicting street), #53 Kettering (3 indistinguishable accounts). All three are HELD and need `./bh resolve`.
- #41 and #42: historical ownership records or true duplicates? Kept unapproved by the user; see §6a for the missing evidence.
- #70, #46, #68, #69, as listed above. Details: `docs/INVESTIGATION_QUESTIONS.md`.

## 9. Tests
- [V] `./bh test`: **128 passed** (117 existing + 11 queue). Earlier: 117 passed (0.85 s, mocked, no CRM access). Report: `data/test_report.xml` and `data/test_report.json`.
- [R] `docs/DEMO_SCRIPT.md` still says 112. That document is stale.

## 10. Submission requirements
| Requirement | Status |
|---|---|
| Scraper covers all 35 communities, including the homepage-only one | [V] run #10 |
| All 121 CRM accounts, fail-closed pagination | [V] run #10 |
| Matching with evidence, SOP, duplicate handling, typed-confirm write path, ledger, idempotency | [R] docs and tests; test suite [V] |
| At least one engine-executed write with read-back | [V] #43 |
| Daily read-only schedule | [R] script exists; cron **not installed** [V] |
| Stop stale servers | [V] done (only :8020 is running, dry-run) |
| Operator approvals executed, re-scan shows only held items | ❌ 1 of ~28 executed. Re-scan #11 after #43 is clean |
| Answers to the investigation questions | ❌ open |
| Demo recording (keep #60 Tiffin CHOW for the camera) | ❌ not done [R] |

## 11. User decisions
- [V] 2026-11-16 ~22:40 UTC: **investigation categories added (display only)**, at the user's request. The ledger was inspected first: #38, #41, #46, #49, #53 and #66 are HELD. **#71 is APPROVED, not pending**: the user approved it in the app at 22:21:51 UTC (decision #74, empty note). It hasn't been executed; there are still 25 operations. Categories: possible change of ownership / rebrand (#41, #49, #66), address verification (#46), identity verification (#38, #53), new account confirmation (#71). Shown on Start Here ("Why the remaining cases aren't finished"), as a tag in Build / Modify, and as a five-row card on each proposal page. They are defined in `app/investigation.py`, which nothing in the executor, batch or queue reads. Completed proposals (#56 Owosso and #60 Tiffin both checked) show no card. No status, decision or CRM change. `FINAL_AUDIT.md` regenerated (integrity PASS; open: approved 1, hold 6). Tests: 145 passed (11 new in `tests/test_investigation.py`).
- [V] 2026-11-16 22:16 UTC: **#46 Ashtabula re-held as NEEDS VERIFICATION (mailing vs physical address)**, at the user's request. Inspection first: #46 had been **released to pending at 22:04:11 UTC** (`local-reviewer`, empty note, presumably in the app), so it was approvable. It was re-held (decision #73) with the user's reviewer note: "Potential mailing-versus-physical-address discrepancy… Do not overwrite either address without sufficient evidence." Ledger only; **no CRM write** (25 operations; `billing_street` is still PO Box 517). New safety control: a proposal that would replace a PO-box billing address with a street address shows a Needs Verification banner and an address-purpose table (physical = website street, not in the CRM; mailing/billing = PO Box 517, kept; purpose UNVERIFIED). Its **release and approval now require an evidence note**, so the empty-note release seen at 22:04 is refused. Holds stay out of batches and the queue. Tests: 134 passed (4 new in `tests/test_address_purpose.py`). Open status counts are unchanged from the docs: hold 6, pending 1 (#71).
- [V] 2026-11-16: the user decided to **keep the local cron job installed** (06:00 daily, read-only), despite a later handoff suggesting "configured, not activated". The docs already state that it is installed.
- [V] 2026-11-16 ~15:05 UTC: the user authorized installing the **local daily cron job**. The crontab was empty before (backed up). One entry was installed, tagged `bellhaven-daily-reconcile`; a re-install is idempotent; macOS required the user to approve the "administer your computer" dialog.
  - The exact command was run in a cron-like environment: scan #14 completed (exit 0).
  - A forced-refusal test was logged with exit 1.
  - CRM writes stayed at 25. `/usr/sbin/cron` is running.
  - Limitation: runs are skipped (not caught up) if the Mac is asleep or off at 06:00.
- [V] 2026-11-16: the user authorized publishing a **public GitHub repo**: https://github.com/Giantlyra/bellhaven-crm-reconciliation.
  - Pre-publish checks: no token, `.env`, data, ledgers or snapshots anywhere in history; no home paths in tracked files.
  - Commit author and committer were rewritten from the user's personal email to the GitHub no-reply address before pushing (file trees unchanged).
  - Published: 83 files, default branch `main`.
  - The GitHub Actions workflow `daily-reconcile` is **active** on GitHub: scheduled daily at 11:00 UTC, but no `CRM_TOKEN` secret is set, so runs will fail at the CRM read. It is read-only either way.
- [V] 2026-11-16: final delivery pass, with no CRM writes.
  - **Re-confirmed:** 25 of 25 operations verified, with read-back receipts for all 23 executed proposals. The 4 created accounts each exist once at $0/$0. The #70 and #41 notes are present. #71 is pending, and no Hudson account exists.
  - **Scheduler:** `crontab -l` shows no crontab for this user and there is no `data/daily.log`, so **cron is not installed**. Only manually triggered runs exist (#8, #13).
  - The final audit was regenerated (PASS); 130 tests pass.
  - Requirements matrix rows 21, 22, 28 and 35 updated. Reconciliation report final status corrected (6 hold, #71 pending). 5-minute script added to `docs/WALKTHROUGH.md`.
- [V] 2026-11-16 ~05:26–05:30 UTC: wrap-up run, with no CRM writes.
  - Follow-up scan #12 produced **#71** (create Amberly Manor, Hudson OH, pending review; #36 superseded).
  - The scheduled job refused to start with writes enabled; its read-only run #13 was idempotent (0 new / 12 known).
  - `docs/FINAL_AUDIT.md`: integrity PASS, 25 of 25 operations.
  - New: `docs/FINAL_RECONCILIATION_REPORT.md`, `docs/MONITORING_RESULTS.md`, `docs/WALKTHROUGH.md`. Stale counts refreshed (130 tests).
  - Ledger backup before the scan: `data/ledger.pre-scan12.db`.
- [V] 2026-11-16: duplicate review accepted. **#57, #64, #42 closed in the ledger (status REJECTED = proposed inactivate/link/note never executed)** as likely historical predecessor records; both accounts in each pair preserved; ownership history inferred, not confirmed. **#41 stays HOLD** until Cedar Trail's relationship to 750 Stewart Rd is established. **#70** recorded as a documented exception (sale unconfirmed; $5,200 AR responsibility unresolved). No CRM changes.
- [V] 2026-11-16 05:08 UTC: the user also **released #70 Sandusky from HOLD, approved it and executed it** (`APPLY 70`, operation 23). Independent check: only `chow_current_account` → Millstone `0017JP8Z1UQ763BVK3` changed; $130,000 / AR $5,200, Bellhaven parent, contact and status are unchanged; the Millstone account is unchanged. Q3 (sale confirmation, AR ownership) is still open. Whole-CRM check: all 23 accounts changed since the seed are explained by verified ledger operations; 0 unexplained writes; 25 of 25 operations verified. A later "stale form token" error came from a page opened before the dry-run restart; nothing was written.
- [V] 2026-11-16 05:05–05:09 UTC: the user approved and executed **#60 Tiffin** (`APPLY 60`, 05:06:38) and then **#54 Marietta** (`APPLY 54`, 05:09:05) in the app. #54 was approved, held, released and re-approved; one attempt while on hold was refused (audit #357). Both verified (operations 21–22, 24–25). Independent check: each historical account changed **only** in `chow_current_account`, keeping its revenue/AR ($84,000/$12,400; $51,250/$3,800), Cedar Trail parent, name, phone and contacts. Each successor exists once, under Bellhaven, at $0/$0. Note: #54 ran before Claude Code had verified #60 (the agreed order was to verify #60 first); both are correct.
- [V] 2026-11-16: the user asked to prepare **#60 then #54** for separate human-approved CHOW execution. **Claude Code must not approve or execute either.** Verified read-only (see `docs/CHOW_REVIEW.md` § Direction): direction Cedar Trail → Bellhaven for both; each successor equals the live website (name, address, phone), under Bellhaven, with no revenue/AR fields sent (starts $0/$0); only `chow_current_account` is written on the historical account. **Open question Q8:** who collects the $12,400 and $3,800 balances. Not assumed and not changed. Live window opened for #60 (backup `data/ledger.pre-chow60.db`). #54 is not presented until #60 is verified.
- [V] 2026-11-16 04:42:23 UTC: the user authorized **stage 2** in chat (approvals for #40 and #62 recorded from it) and ran `APPLY BATCH OF 2` in the app. Both verified (operations 19–20, audit `batch_started` #322 / `batch_finished` #337). Independent check: only the approved fields changed; Lima $47,000 / $0, Bellhaven parent, status and contacts intact; Zanesville contacts intact; no phone collisions. A fresh audit run: **20 of 20 operations live-matched and receipted, integrity PASS.** The CHOW cases (#60, #54) were **not** touched.
- [V] 2026-11-16 04:25:02–04:25:04 UTC: the user ran **stage 1** (`APPLY BATCH OF 7`) in the app. All 7 verified: #39, #47, #48, #50, #56, #59, #61. `batch_started` #267 / `batch_finished` #317; operations #12–#18. Independent check: only the approved fields changed (the `parent_name` display value follows the new `parent_id`); financials, contacts and the Owosso survivor are unchanged; Batavia `00163AAEB690110611` and Carlisle `00163ED66F49793F79` each exist exactly once. A fresh `scripts/final_audit.py` run: **18 of 18 operations live-matched and receipted, integrity PASS**. The earlier "not executed" observations were made before the batch ran.
- [V] 2026-11-16: the user requested a comprehensive read-only evaluation with the business category taxonomy; no CRM changes. Delivered: `docs/EVALUATION_TABLE.md`.
- [V] 2026-11-16 ~04:22 UTC: the user authorized **preparation of stage 1** (#50, #59, #39, #61, #56, #47, #48); approvals recorded from that chat authorization (#50, #59 were already approved). Final live validation: all 7 pass — no overlaps; no drift; approvals bound to current fingerprints; SOP: Lima AR $0 and Zanesville $0/$0 so direct re-parents are allowed; Owosso survivor `001EGU7BMJ942ZTRE6` matches the website phone and administrator, is Active under Bellhaven, and the loser has $0/$0 and no links; Portsmouth billing street identical to the website street; Batavia and Carlisle have no account with the same name, city, ZIP, phone or street. The user will personally type `APPLY BATCH OF 7`. Stage 2 (#40, #62) and CHOW (#60, #54) are **not** authorized.
- [V] 2026-11-16: the user moved to **final execution and audit mode**. Plan: Group A executed only after explicit in-app authorization, with each write verified as it happens; B/C/D recorded; then one comprehensive read-only audit and the final report, monitoring results and walkthrough. Not an authorization to write; no approvals were given beyond those already recorded.
- [V] 2026-11-16: the user confirmed **#49 and #66: HOLD** (superseding the earlier approval of both). They are recorded as HOLD in the ledger; no CRM change. Group B is now fully recorded (9 holds: #49, #66, #57, #41, #42, #38, #53, #70, #46).
- [V] 2026-11-16: **batch decision plan (all 24 cases).**
  - **Group A, approval candidates:** #50, #59, #39, #40, #61, #62, #56, #47, #48. Approved as a group only after final validation, and **not** an authorization to write. Read-only preview: `docs/GROUP_A_PREVIEW.md`. All 9 validate clean against the live CRM.
  - **Group B, HOLD:** #57, #41, #42 (recorded), #38, #53 (already held), #70 and #46 (recorded as HOLD). #49 and #66: **not recorded as hold; see the conflict note below.**
  - **Group C, special:** #64 stays HOLD, documented as a possible predecessor or duplicate, with no inactivation or link authorized. #60 and #54 (CHOW) stay pending with an explicit-review note.
  - **Group D, close without writes:** #36 resolved as a distinct facility (resolution #1; the next scan will propose creating Hudson OH, needing its own approval). #68 and #69 REJECTED.
  - **Conflict to confirm:** #49 and #66 are listed as HOLD in the plan, but the user explicitly approved them on 2026-11-16 ("APPROVE #50, #59, #49, #66"). They stay APPROVED and unexecuted until the user confirms hold or execute.
- [V] 2026-11-16: **#41 Monroe (Cedar Trail of Monroe): HOLD** (user decision; no CRM change). #42 is the last of the four predecessor-brand cases to decide.
- [V] 2026-11-16: **#64 Erie: HOLD** (user decision; same reasoning as #57; no CRM change). The proposed inactivate + `duplicate_of_account` + note on `001BLYF02K97SZLZHH` stays unexecuted. Next: #41 and #42 Monroe, one at a time.
- [V] 2026-11-16: **#57 Port Clinton: HOLD** (user decision, recorded in the ledger as status HOLD, no CRM change). Reason: preserve history until it is confirmed whether the Harborview record is a historical operator or a duplicate. The proposed operation (inactivate + link `duplicate_of_account` + note on `001JD2MWRA74LTSN24`) stays unexecuted. #64 Erie, #41 and #42 Monroe are being decided next, one at a time.
- [V] 2026-11-16: lane A batch attempts did **not** execute. One reached the dry-run server; one failed the phrase check; one never reached the app (stale page). All were refused before any write. The phrase check now ignores whitespace and shows the received text (commit `a769011`). The user then asked for an evidence-based review (alternatives → challenge → consistency → recommendation) of all open proposals, with no new software and no automatic approvals.
- [V] 2026-11-16: the user's explicit decisions were **APPROVE #50, #59, #49, #66** (hold none, reject none), stated as *not* an execution authorization. #50 was approved by the user in the app (03:45:56). The approvals for #59, #49 and #66 were recorded in the ledger by Claude Code from that chat decision, with the actor labelled accordingly. A live re-check showed no drift and the website unchanged. The dry-run batch preview shows 4 of 4 `will_run` with the exact bodies.
- [V] 2026-11-16: the user switched to **batch completion mode**: one read-only review of all remaining items, a decision table, then sequential execution of explicitly approved changes with stop-on-error. CHOW, duplicates, conflicting identities and financial-risk cases stay manual unless their requirements are met. Not an authorization.
- [V] 2026-11-16 03:26 UTC: the user ran the queue (`APPLY QUEUE OF 5`). All 5 were verified by the app and by Claude Code's independent live check.
- [V] 2026-11-16 03:20 UTC: the user approved #37, #44, #51, #63 and #67 in the app for the queue. No queue run followed. On request, the code was committed: `c3ef0a7` on branch `bellhaven-assessment`, the repo's first commit. Stray empty files `Y`, `app/au_`, `app/ci_` and `app/r⏎⏎R` were left out and not deleted.
- [V] 2026-11-16: the user asked to switch from manual walkthroughs to a controlled execution queue for **explicitly approved low-risk corrections**. No auto-approval, no high-risk execution; ownership, duplicates and uncertain matches stay manual. Built and dry-run demonstrated; no new writes.
- [V] 2026-11-16: the user approved **#45** in the app (03:01:56 UTC) and attempted `APPLY 45` while in dry-run (refused). Claude Code treated that as authorization for #45 only and restarted with live writes; the user then typed `APPLY 45` (03:05:33 UTC). Verified by live read-back.
- [V] 2026-11-16: the user authorized **#55 only**, approved it and typed `APPLY 55` in the app (03:00 UTC). Verified by live read-back. The user will open the app pages themselves; Claude Code reports verification and the next item.
- [V] 2026-11-16: the user switched to concise execution mode and authorized **#52 only**, with instructions to pause after it and then present #55. #52 was executed at 02:58:21 UTC and verified. #55 is **not** authorized.
- [V] 2026-11-16: the user authorized **#65 only** in chat, then approved it and typed `APPLY 65` in the app (02:51–02:52 UTC). Verified by live read-back.
- [V] 2026-11-16: the user authorized **#58 only** in chat, then approved it and typed `APPLY 58` in the app (02:46–02:47 UTC). Verified by live read-back. Claude Code's first check at ~02:45 UTC found nothing yet recorded; the user's execution followed.
- [V] 2026-11-16 (PRD): the user and ChatGPT **tentatively approved all 14 Wave A items**. Conditions: #49 ownership check, #66 identity check, #59 billing-ZIP check. Explicitly **not** authorization. Phase 1 (read-only verification) is complete.
- [V] 2026-11-16: the user wants **no batch approval** for Wave A. All 14 are reviewed individually with ChatGPT, one at a time in sheet order, starting with #58. Writes stay disabled. All existing decisions are preserved.
- [V] 2026-11-16: the user adopted the consolidated report as the working plan and asked for the Wave A review. **No batch writes.** Each item is to be authorized individually. Investigation and not-recommended cases stay untouched.
- [V] 2026-11-16: the user asked for one consolidated READ-ONLY assessment of all remaining proposals instead of one-at-a-time review. No approvals and no writes. Delivered in §0 and in `docs/RECONCILIATION_DECISION_REPORT.md`.
- [V] 2026-11-16: the user kept **#41 and #42 unapproved** pending clarification, and asked for the next independent low-risk phone fix (#45) to be prepared only. No CRM changes, no architecture changes, server to stay in dry-run.
- [V] 2026-11-16: the user asked for a read-only re-scan, a dry-run restart and the #41/#42 evidence, with **no additional CRM corrections**. #41 and #42 are not approved.
- [V] #43 was approved and executed through the UI at 01:17 UTC (actor `local-reviewer`). Claude Code did not do this.
- No other approvals exist in the ledger. Earlier discussion, ChatGPT recommendations and the nine-card console's "APPROVE Marietta" are **not** authorizations.
- Standing policy: no live CRM mutation without the user's separate, explicit approval of that exact operation.

## 12. Housekeeping notes
- [V] Empty stray files, probably from shell typos at 19:10: `Y`, `app/au_`, `app/ci_`. They are harmless and were left in place pending the user's OK to delete.
- [V] Git: first commit `c3ef0a7` on branch `bellhaven-assessment`; `main` has no commits. The commit excludes `.env`, `data/`, the ledgers and snapshots, and `investigation.txt` (per `.gitignore`), plus the stray files. `docs/` and this handoff contain assessment CRM account IDs and phone numbers: review before any push.

## 13. Exact next action
**Delivery is complete on the engineering side.** Blocking items are the user's:
1. **The original Clipboard brief.** It is not in the repo or the session. The deliverables can't be checked against it (matrix rows 34–36: contacts? status flag? form fields and deadline).
2. **Public GitHub repository.** The work is on local branch `bellhaven-assessment` (`main` has no commits). Push it (or merge to `main`) and make the repo public. `docs/` contains assessment account IDs and phones; secrets and data are gitignored.
3. **2-minute video** (script: `docs/WALKTHROUGH.md`).
4. **Time spent** (README) and the **form submission**.
5. **The deadline is unverified:** the matrix notes Nov 17 2026 04:29 UTC was likely inferred, not sourced.

Optional: decide #71; install cron. Server in dry-run (PID 95736). Operations total 25.
