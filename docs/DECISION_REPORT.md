# Bellhaven Reconciliation: Consolidated Proposal Decision Report (2026-11-15)

> **PRE-EXECUTION SNAPSHOT (2026-11-15).** Kept unchanged as historical evidence. Recommendations made before any approval. Final dispositions differ for several items, for example #41/#42/#57/#64 and #70. **Final, authoritative outcome:** [FINAL_AUDIT.md](FINAL_AUDIT.md) · [FINAL_RECONCILIATION_REPORT.md](FINAL_RECONCILIATION_REPORT.md).

**Source:** live read-only scans #5–#9 (latest #9, 2026-11-15 22:51 UTC). Website: 35 communities (homepage says 35, directory lists 34; *Bellhaven
Meadows of Findlay* is linked only from the homepage). CRM: 121 accounts, 3 pages. CRM content fingerprint `5daed874…` is identical
in every scan since #3, so the CRM has not changed since the Findlay write. Every scan: **0 new proposals, 35 known**.
Counts recalculated from scan #9 and the ledger, not carried over: **32 PENDING, 3 HELD**, 0 approved, 0 executing,
0 verified, 0 failed, 9 superseded, 26 resolved. Every open proposal's baseline equals the live CRM value (0 drift).
Exact before/after values, waves and confirmation phrases are in **[APPROVAL_BATCH.md](APPROVAL_BATCH.md)**.

Writes to date: one, made before this engine existed. Findlay `parent_id` was set to Bellhaven at 10:14 UTC and confirmed by read-back. It is
imported as a legacy receipt and is not retried. The engine itself has made **0** write calls.

## Corrections to the previous report

| Previous claim | Finding | Status |
|---|---|---|
| "Website and CRM content hashes unchanged since run #3" | The **website** fingerprint changed on every run because it included each page's `retrieved_at` timestamp. The content itself was identical. | Fixed: the fingerprint is now content-only and stable across runs #6–#8. |
| "Approve all 32" | Four items are speculative or unsafe: #70, #46, #68, #69 (see below). | Now recommend 28 approve and 4 hold. |
| Batch approval would apply groups A–F | 8 proposals share accounts (Lima, Zanesville, and the Monroe, Port Clinton and Erie survivors). After the first write, siblings were blocked as "drift", and a single batch would stop partway. | Fixed: explained-drift tolerance (only for values this engine wrote and verified) plus an overlap guard on batches, so the work runs in two waves. |
| "Writes are off unless the flag is set" | The legacy Findlay route (`/proposals/findlay/apply`) was mounted and ignored `CRM_WRITES_ENABLED`. It still required CSRF and a typed phrase. | Fixed: it now refuses in dry-run before touching the CRM or the legacy audit file. |
| Holds need "a small code change" | Built: `./bh resolve` records an operator identity decision, and the next scan turns it into normal proposals. | Done. Decisions are still yours. |
| "Resolve Amberly and Union Square as distinct" | Identity isn't substantiated by a human source, and the directive forbids automatic action on such records. | Now **INVESTIGATE**, with questions in [INVESTIGATION_QUESTIONS.md](INVESTIGATION_QUESTIONS.md). |
| "Batch waves 1 and 2" | Each mutation needs fresh, explicit authorization. | Individual `APPLY <id>` is the default; the waves now give the order only. |
| An interrupted execution could be resumed | A proposal left EXECUTING by a killed server was stuck: only APPROVED or FAILED could execute. | Fixed: it resumes through a fresh preview and confirmation, and a process lock prevents two executions at once. |

## Classification of all 35 open items

Risk: the engine's rating. Confidence: identity confidence. Evidence: address = exact street+ZIP match; About = About page names
the acquisition; phone = CRM phone equals the website phone.

| # | Kind | Subject (account) | Risk | Conf. | Supporting evidence | Required action → recommendation |
|---|---|---|---|---|---|---|
| 37 | Rename+phone | Sycamore Ridge (00191H7JR16471SZ34) | med | high | address; already Bellhaven | approve (wave 1) |
| 44 | Rename+phone | Ashland (001RJ0D7Z5MAZN5HX5) | med | high | address; already Bellhaven | approve (wave 1) |
| 49 | Rename+phone | Riverbend Manor → Chagrin Falls (001RJU1X4NBWC1Q0G7) | med | high | address; already Bellhaven; $0 | approve (wave 1) |
| 50 | Rename | Chesterton (0013NUZQHQUEZ8DXEG) | med | high | address (NW/Northwest normalized); phone | approve (wave 1) |
| 63 | Rename | Grove City (001TZCSTBZFM6K5BGN) | med | high | address; phone | approve (wave 1) |
| 66 | Rename+phone | Sunny Acres → Willow Creek (0017MN2JYAJBDS8WQZ) | med | high | address; already Bellhaven; care type matches | approve (wave 1) |
| 67 | Rename+phone | Arbors Dayton (0010KJFP601YNTZVDA) | med | high | address | approve (wave 1) |
| 59 | ZIP | Portsmouth (001CF3LDWVRGL09P4F) | med | med | street + phone match; 45626→45662 transposition | approve (wave 1) |
| 45 | Phone | Findlay (001UKEFGADQ8YCZ4YM) | low | high | address; does not touch the verified `parent_id` | approve (wave 1) |
| 51 | Phone | Defiance (001R4PXTUD9R6FNN8V) | low | high | address; has AR, but phone only | approve (wave 1) |
| 52, 55 | Phone | Goshen, Marion | low | high | address | approve (wave 1) |
| 43, 58, 65 | Phone | Monroe, Port Clinton, Erie survivors | low | high | address | approve (wave 1) |
| 39 | Re-parent | Lima (001LGFPBJY4N9MB6KL) Harborview → BH | high | high | address; About (Harborview 2025); AR $0 → SOP allows direct | approve (wave 1) |
| 61 | Re-parent | Zanesville (001H1JMVZWP46D5VUF) Cedar Trail → BH | high | med | address; About (Cedar Trail 2026); $0 | approve (wave 1) |
| 56 | Duplicate | Owosso 001QU150… → 001EGU7B… | med | high | same address; survivor phone matches the website; $0 | approve (wave 1); move the contact later |
| 47, 48 | Create | Batavia OH, Carlisle PA | high | med | no account at the ZIP/street; Carlisle PA ≠ New Carlisle OH | approve (wave 1) |
| 40, 62 | Phone; rename+phone | Lima, Zanesville | low/med | high | address; siblings of #39/#61 | approve (wave 2) |
| 41, 42 | Duplicate | Monroe losers (Cedar Trail, Harborview) | high | high | same address; $0; survivor under BH | approve (wave 2) |
| 57, 64 | Duplicate | Port Clinton, Erie losers (Harborview) | high | high | same address; $0; survivor under BH | approve (wave 2) |
| 54 | CHOW | Marietta (001A34WFSUYHCRBLFT) $51,250 / $3,800 | high | high | address; About; protected by SOP | approve individually (one ordered operation: preserve → POST successor → link → read back) |
| 60 | CHOW | Tiffin (001U6RW32TY0WSXZZB) $84,000 / $12,400 | high | high | address; About; protected by SOP | approve individually and **alone**, after one simple PATCH (#43) has verified on the real API; before #54 (one ordered operation) |
| **70** | CHOW link | Sandusky → Millstone (001SXSF4ELF0Z2LGDM → 0017JP8Z1UQ763BVK3) | high | **med** | only absence from the website + a same-address account; Millstone not in About | **INVESTIGATE: speculative** |
| **46** | Billing street | Ashtabula PO Box → street (001NXP9X46CWEPSLSV) | med | med | name, ZIP and phone match; but the field is **billing** | **hold: possibly unsafe for invoicing** |
| **68, 69** | Status | Alliance, Coldwater → "Needs Review" | med | med | not on the website; $0 | **hold: status value not in CRM vocabulary** |
| 36 | HOLD | Amberly Manor | — | low | same name, CO vs OH, different phone and administrator | **INVESTIGATE** (leaning distinct): answer the questions first |
| 38 | HOLD | Union Square | — | low | different street, phone and administrator; Juniper Point | **INVESTIGATE** (leaning distinct): answer the questions first |
| 53 | HOLD | Kettering ×3 | — | low | three $0 accounts at one address, no phone match | **HOLD** until you know which record is in use |

Independent check (not using the engine's matcher): each of the 35 facilities was compared with all 121 accounts by ZIP plus street
number. Every facility and every Bellhaven-parented account is accounted for above. `care_type` agrees everywhere
(Short-Term Rehabilitation & Nursing → Skilled Nursing, Memory Support → Memory Care). No CRM notes exist, so no
`note` write overwrites anything.

## What remains unresolved

1. **No approved changes have been written.** The CRM still differs from the website on 30+ points until you approve.
2. Four held proposals (#46, #68, #69, #70) and three identity holds (#36, #38, #53).
3. **Contacts are not reconciled.** Website administrators are not compared with CRM contacts. The Owosso loser and Sandusky
   contacts are noted, not moved.
4. "Needs Review" status validity is unknown: the API spec has no enums, and the data contains only Active/Inactive.
5. Ownership is inferred from the website and About page, not from a human source.
6. Not done: the demo video, the git commit / public repo, the time-spent figure, and form submission.
7. Nine stale server processes from earlier sessions are still running old code. Stop them before any approval session (`OPERATIONS.md`).
8. The original Clipboard brief isn't in the workspace, so three requirements can't be verified (`REQUIREMENTS_MATRIX.md`, rows 34–36).
