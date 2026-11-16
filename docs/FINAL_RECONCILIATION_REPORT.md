# Bellhaven CRM Reconciliation: Final Report

_Generated 2026-11-16 05:28 UTC. Final state after all authorized work. Every number below comes from the ledger and the read-only final audit (`docs/FINAL_AUDIT.md`)._

## 1. Outcome

| | |
|---|---|
| Website communities reconciled | **35** (homepage 35, directory 34; one listed on the homepage only) |
| CRM accounts | **125** (121 at the start + 4 created: Batavia, Carlisle, and the Tiffin and Marietta successors) |
| Proposals reviewed | **36** (35 in the review + #71 from the follow-up scan) |
| CRM changes made by the engine | **25 operations on 23 proposals, all VERIFIED** by read-back. Plus the earlier Findlay parent correction |
| Integrity audit | **PASS.** 25 of 25 operations live-matched and receipted; protected fields and contacts intact; no CRM change outside the ledger |
| Communities now matching the CRM exactly | **23 of 35**. The other 12 are explained below |
| Website vs CRM today | **DIFFERS: 2** · **MATCH: 23** · **MULTIPLE ACCOUNTS: 7** · **NO CRM ACCOUNT: 3** |

## 2. What was changed (all human-approved, previewed live, typed-confirmed, read back)

| # | Category | Case | Exact change | Ops | Verified (UTC) |
|---|---|---|---|---|---|
| #37 | Field update | Bellhaven of Sycamore Ridge | `00191H7JR16471SZ34`: name → Bellhaven at Sycamore Ridge, phone → (260) 365-6510 | 7 | 2026-11-16 03:26:52 |
| #39 | Parent correction | Bellhaven Crossings of Lima (Harborview Care Group (Parent A | `001LGFPBJY4N9MB6KL`: parent_id → 0015QAPLGS3FVYEEEM | 12 | 2026-11-16 04:25:02 |
| #40 | Field update | Bellhaven Crossings of Lima | `001LGFPBJY4N9MB6KL`: phone → (231) 539-3617 | 19 | 2026-11-16 04:42:23 |
| #43 | Field update | Bellhaven Gardens of Monroe | `001U1750VLVJAGG1S5`: phone → (814) 412-2218 | 1 | 2026-11-16 01:17:47 |
| #44 | Field update | Bellhaven Health Care Center of Ashland | `001RJ0D7Z5MAZN5HX5`: name → Bellhaven Healthcare Centre of Ashland, phone → (517) 314-5115 | 8 | 2026-11-16 03:26:53 |
| #45 | Field update | Bellhaven Meadows of Findlay | `001UKEFGADQ8YCZ4YM`: phone → (231) 533-2969 | 6 | 2026-11-16 03:05:33 |
| #47 | New account | Bellhaven of Batavia | created `00163AAEB690110611` (Bellhaven of Batavia, Batavia OH) | 13 | 2026-11-16 04:25:03 |
| #48 | New account | Bellhaven of Carlisle | created `00163ED66F49793F79` (Bellhaven of Carlisle, Carlisle PA) | 14 | 2026-11-16 04:25:03 |
| #50 | Field update | Chesterton Senior Commons | `0013NUZQHQUEZ8DXEG`: name → Bellhaven of Chesterton | 15 | 2026-11-16 04:25:03 |
| #51 | Field update | Bellhaven of Defiance | `001R4PXTUD9R6FNN8V`: phone → (330) 691-2711 | 9 | 2026-11-16 03:26:54 |
| #52 | Field update | Bellhaven of Goshen | `001JQER1RMYKNRLNME`: phone → (330) 405-6040 | 4 | 2026-11-16 02:58:21 |
| #54 | Change of ownership | Bellhaven of Marietta (Cedar Trail Communities (Parent Accou | created `0014861C0619562203` (Bellhaven of Marietta, Marietta OH); `001A34WFSUYHCRBLFT`: chow_current_account → 0014861C0619562203 | 24, 25 | 2026-11-16 05:09:05 |
| #55 | Field update | Bellhaven of Marion | `0015L38R1Z5947ZZP7`: phone → (517) 847-7948 | 5 | 2026-11-16 03:00:50 |
| #56 | Duplicate | Bellhaven of Owosso (001QU150PM4Z15UA71) → Bellhaven of Owos | `001QU150PM4Z15UA71`: duplicate_of_account → 001EGU7BMJ942ZTRE6, status → Inactive | 16 | 2026-11-16 04:25:03 |
| #58 | Field update | Bellhaven of Port Clinton | `001UELXDAKFRKB8932`: phone → (330) 733-6423 | 2 | 2026-11-16 02:47:11 |
| #59 | Field update | Bellhaven of Portsmouth | `001CF3LDWVRGL09P4F`: billing_zip → 45662 | 17 | 2026-11-16 04:25:04 |
| #60 | Change of ownership | Bellhaven of Tiffin (Cedar Trail Communities (Parent Account | created `00164AE214A6588944` (Bellhaven of Tiffin, Tiffin OH); `001U6RW32TY0WSXZZB`: chow_current_account → 00164AE214A6588944 | 21, 22 | 2026-11-16 05:06:38 |
| #61 | Parent correction | Cedar Trail of Zanesville (Cedar Trail Communities (Parent A | `001H1JMVZWP46D5VUF`: parent_id → 0015QAPLGS3FVYEEEM | 18 | 2026-11-16 04:25:04 |
| #62 | Field update | Cedar Trail of Zanesville | `001H1JMVZWP46D5VUF`: name → Bellhaven of Zanesville, phone → (814) 599-2533 | 20 | 2026-11-16 04:42:23 |
| #63 | Field update | Bellhaven Rehab and Nursing of Grove City | `001TZCSTBZFM6K5BGN`: name → Bellhaven Rehabilitation & Nursing of Grove City | 10 | 2026-11-16 03:26:54 |
| #65 | Field update | Bellhaven Shores of Erie | `001CVBBCSDM7YHN220`: phone → (614) 792-9343 | 3 | 2026-11-16 02:52:27 |
| #67 | Field update | Arbors at Bellhaven Dayton | `0010KJFP601YNTZVDA`: name → The Arbors at Bellhaven - Dayton, phone → (260) 254-7592 | 11 | 2026-11-16 03:26:55 |
| #70 | Change of ownership | Bellhaven of Sandusky → Millstone Care of Sandusky (Millston | `001SXSF4ELF0Z2LGDM`: chow_current_account → 0017JP8Z1UQ763BVK3 | 23 | 2026-11-16 05:08:24 |

Legacy, before this engine: Findlay `001UKEFGADQ8YCZ4YM.parent_id` → Bellhaven (2026-11-15 10:14 UTC).

## 3. How each category was handled

- **Field update** (15). Exact address+ZIP identity, value taken from the live website, only those fields sent. Five were run through the controlled low-risk queue (#37, #44, #51, #63, #67).
- **Parent correction** (2). Lima and Zanesville. The billing SOP allows a direct re-parent only because AR = $0. Lima keeps its $47,000 revenue history under Bellhaven, following the Findlay precedent.
- **Duplicate** (1). Owosso: same parent; the survivor holds the website phone and administrator; the loser was inactivated and linked, nothing deleted.
- **New account** (2). Batavia and Carlisle, after name, street, phone, ZIP-area and alternate-name searches found no existing record. Each exists exactly once.
- **Change of ownership** (3). Tiffin and Marietta: historical Cedar Trail accounts preserved, with $84,000 / $12,400 and $51,250 / $3,800 revenue / AR. New Bellhaven successors start at $0 / $0, linked via `chow_current_account`. Sandusky: the historical Bellhaven account is linked to the existing Millstone account, with $130,000 / $5,200 preserved.

## 4. Decided without a CRM write

| # | Decision | Why |
|---|---|---|
| #57 Port Clinton, #64 Erie, #42 Monroe (Harborview) | **Closed: historical predecessor records; both accounts preserved** | Same building, predecessor-brand parent, $0 / $0, no contacts. Ownership history is **inferred**, not confirmed |
| #68 Alliance, #69 Coldwater | **Rejected as written** | The proposed status "Needs Review" is not a CRM value |
| #36 Amberly Manor | **Resolved: distinct facility** | The CRM's Amberly Manor is in Colorado (different administrator and parent); the follow-up scan produced #71 |

## 5. Unresolved: business questions for Bellhaven (documented, not forced)

| # | Status | Question |
|---|---|---|
| #41 Monroe "Cedar Trail of Monroe" | HOLD | Did 750 Stewart Rd ever operate under Cedar Trail, or is this record an error? |
| #53 Kettering (3 records) | HOLD | Which record is the live facility: `001WR41PYNWXCAE2X4`, `001B7XZAA3AFALS9GP` or `0016KTS1UAWBRXS09J`? |
| #38 Union Square | HOLD | Is 240 Market St (Juniper Point, administrator Dale Croft) a different community from 118 Union Square Dr? |
| #46 Ashtabula | HOLD · **Needs verification** (mailing vs physical address) | Is PO Box 517 the invoice mailing address? Where should the physical street 3156 W Prospect Rd be recorded? Both are preserved; release or approval requires an evidence note |
| #49 Chagrin Falls | HOLD | Was "Riverbend Manor Care Center" a prior operator or a former name? |
| #66 Willow Creek | HOLD | Is "Sunny Acres Retirement Home" the same facility? There are no contacts to confirm it |
| #71 Amberly Manor, Hudson OH | HOLD | Confirm the Hudson OH community before the create is applied |
| #70 Sandusky | **TECHNICALLY VERIFIED · BUSINESS UNCONFIRMED** | The link exists and matches the authorized operation. The sale's direction, date and the $5,200 collection responsibility are **not independently proven**. The original investigation had recommended HOLD |
| #60 Tiffin / #54 Marietta | **TECHNICALLY VERIFIED · collection responsibility open** | Successors verified; historical balances preserved on the old accounts. Who collects the $12,400 / $3,800? |
| #68 / #69 | Rejected, **finding** | Are Alliance and Coldwater still Bellhaven communities? |

## 5a. Distinctions a reviewer should not miss

**Technical verification is not business certainty.**
- "VERIFIED" means the CRM now holds exactly what was authorized, confirmed by read-back.
- It does **not** prove that the underlying business event happened.
- **#70 Sandusky** is the clearest case: the Bellhaven → Millstone link is technically verified, but the sale itself is business-unconfirmed and is **not** described here as independently proven.

**"No account at the physical address" is not "no CRM account".**
- **Ashtabula** (#46) has no CRM account at 3156 W Prospect Rd, but it **does** have an existing Bellhaven account, `001NXP9X46CWEPSLSV`. That account was identified by other evidence: name, phone and ZIP match, and its billing address is **PO Box 517**.
- The PO box is **deliberately preserved** until finance confirms whether it should change. No second account is created, and nothing is overwritten.

**Three different "not done" states:**

| State | Meaning | Cases |
|---|---|---|
| **Identity HOLD (not actionable)** | The engine could not decide identity, so it created a HOLD with **no CRM operation** at all | #38 Union Square, #53 Kettering |
| **Actionable proposal, manually held** | A concrete operation exists but was put on hold by a human pending business evidence; it can be released later | #41 Monroe/Cedar Trail, #46 Ashtabula, #49 Chagrin Falls, #66 Willow Creek |
| **Rejected / closed without write** | The proposed operation will never run | #42, #57, #64: predecessor records preserved, not inactivated · #68, #69: "Needs Review" is not a CRM status; their business questions remain documented |
| **Held after approval** | Approved, then put back on hold by a human; never applied | #71 Amberly Manor, Hudson OH (the Colorado account was resolved as a separate facility). Approved in the app at 22:21:51 UTC, held at 22:55:27 UTC on 2026-11-16; nothing created |

**Two records at one address are not automatically duplicates.**
- One may be a historical predecessor. Treating it as a duplicate (inactivate + "Duplicate of") versus as history (preserve) has different consequences for reporting and finances.
- Owosso was a true same-parent duplicate and was inactivated. Port Clinton, Erie and Monroe/Harborview were preserved as likely predecessor records, with their history **inferred, not confirmed**.

## 5b. Why the dashboard shows 71 proposals

Only **35** are current decisions: 23 verified + 6 held + 5 rejected + 1 pending. The other **36 are kept as audit history**, never deleted:

- **10 superseded:** earlier versions replaced by a materially changed proposal for the same case.
  - #1 → #36 and #3 → #38: the first scan would have **created** Amberly Manor and Union Square. The stricter scan found look-alike accounts and escalated both to identity holds, so an **unsafe create was prevented**.
  - #5, #6, #11, #12, #22, #23, #29 → #41, #42, #47, #48, #56, #57, #64: the same operations, with risk ratings and warnings added.
  - #36 → #71, after the operator resolved Amberly as a distinct facility.
- **26 resolved:** proposals from the very first scan that the first complete live scan (#3) no longer observed in that form, and re-derived under the final rules (for example #7 → #43).

The ledger reconciles exactly: 23 verified proposals equal 25 read-back-verified operations (#60 and #54 have two each). There are 0 approved-but-unexecuted, interrupted, failed or blocked writes. 7 refused attempts were stopped before any write.

## 6. Controls that held

- **No write without all of:** a server started with `CRM_WRITES_ENABLED=1`, a human approval bound to the proposal fingerprint, a fresh live preview with a plan token, and a typed confirmation phrase.
- **During the session these guards refused writes:** dry-run attempts, a wrong confirmation phrase, stale form tokens after server restarts, and an execute attempt while the proposal was on hold.
- **Every write is read back.** Claude Code also diffed each touched account against pre-write snapshots, including contacts.
- **CHOW:** the historical accounts are never edited beyond the link; the successor-duplicate guard and the partial-failure recovery are in place.
- **The audit log is append-only**, and a ledger backup was taken before each execution window.
- **Scheduled scans are read-only** and refuse to run with writes enabled (see `MONITORING_RESULTS.md`).
  - The brief requires only a schedule *configuration*.
  - At the user's direct request, the local cron job was additionally **installed and tested** on the author's Mac on 2026-11-16 (06:00 daily).
  - The GitHub Actions workflow exists on GitHub with no `CRM_TOKEN` secret, so it cannot read the CRM.

## 7. Evidence index

- `FINAL_AUDIT.md`: the read-only integrity audit.
- `CRM_CHANGE_HISTORY.md`: per-write receipts.
- `EVALUATION_TABLE.md`: all cases with category, evidence and limitations.
- `CHOW_REVIEW.md`: the ownership-change cases.
- `WAVE_A_FINAL_VALIDATION.md`, `GROUP_A_PREVIEW.md`, `EVIDENCE_DECISION_REVIEW.md`: earlier review stages.
- `data/queue_receipts/`: queue receipt files (local, gitignored).
