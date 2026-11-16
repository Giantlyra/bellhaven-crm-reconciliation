# Operations that require your fresh authorization

> **PRE-EXECUTION SNAPSHOT (2026-11-15).** Kept unchanged as historical evidence. Lists operations that were *awaiting* authorization at that time. Since then, 25 operations on 23 proposals were executed and read-back verified, and others were held or closed. **Final, authoritative outcome:** [FINAL_AUDIT.md](FINAL_AUDIT.md) · [FINAL_RECONCILIATION_REPORT.md](FINAL_RECONCILIATION_REPORT.md).

Prepared 2026-11-15 from **live read-only scan #9** (35 website facilities / 121 CRM accounts, CRM fingerprint
`5daed874…`, unchanged since scan #3; 0 baseline drift on every open proposal). **Nothing in this document has been
approved or executed.**

**How each operation gets authorized.** Every row below is one proposal. Each needs your own decision, made fresh:

1. **Approve** on its page. This writes nothing.
2. Open the **Live preview**. It re-reads the CRM.
3. Tick "reviewed" and type **`APPLY <id>`**.

This only works on a server started with `CRM_WRITES_ENABLED=1`.

- **Default: execute one at a time.** The waves below only show a safe *order*.
- Batch execution (`APPLY BATCH OF n`) is optional, and only for items you have already reviewed individually. Even in a batch, each item is still separately previewed, executed, read back and audited.
- Approvals and console notes from earlier sessions, including the nine-card decisions, do **not** count.

Bellhaven parent = `0015QAPLGS3FVYEEEM`. Engine CRM write calls to date: **0**.

The legacy verified write is preserved, and nothing below changes it: Findlay `001UKEFGADQ8YCZ4YM.parent_id` → Bellhaven at 2026-11-15 10:14 UTC.

Before the first write:

1. Stop the stale servers.
2. Back up the ledger.

Both are in `OPERATIONS.md`.

## Financial safeguards that apply to every row (enforced in code, not by this document)

1. **SOP (Risk & Validation Engine, `app/policy.py`).** Revenue > 0 **and** AR > 0 means CHOW: the old account keeps its parent and financials, and only
   `chow_current_account` is set. Otherwise a direct re-parent is allowed. Unreadable financials mean HOLD.
2. **Fresh re-read before writing.** The preview re-reads every account involved, refuses on unexplained drift, and re-runs the SOP on
   **live** financials. If AR has appeared on Lima since the scan, #39 is blocked automatically.
3. **No field writes on financial fields.** No proposal touches `lifetime_revenue` or `outstanding_ar`.
4. **Successor guard.** No `POST` is made if an account already exists at that ZIP under Bellhaven. An uncertain `POST` is
   looked up and adopted, never re-sent.
5. **Duplicates.** A loser is inactivated only with $0 revenue and $0 AR, no CHOW link, and an active survivor. Nothing is deleted,
   and the note is appended.
6. **Read-back.** Every field is compared after the write. A mismatch is recorded as `failed`, never assumed to have worked.
7. **Batches (new).** A batch is refused if one item writes an account another item reads. The waves below are built
   so this never triggers. Wave 2 items are previewed **after** wave 1 is verified, and the drift check accepts
   only the values that wave 1 itself wrote and verified.

---

## Wave 1: 20 independent items (each `APPLY <id>`; optional batch `APPLY BATCH OF 20`)

### 1a. Renames and field fixes (same building: exact street+ZIP, already under Bellhaven unless noted)

| # | Account ID | Field(s) | Before (CRM) | After (website) | Revenue / AR | Risk |
|---|---|---|---|---|---|---|
| 37 | 00191H7JR16471SZ34 | name, phone | Bellhaven of Sycamore Ridge · (419) 982-7764 | Bellhaven at Sycamore Ridge · (260) 365-6510 | $0 / $0 | med |
| 44 | 001RJ0D7Z5MAZN5HX5 | name, phone | Bellhaven Health Care Center of Ashland · (734) 319-7813 | Bellhaven Healthcare Centre of Ashland · (517) 314-5115 | $0 / $0 | med |
| 49 | 001RJU1X4NBWC1Q0G7 | name, phone | Riverbend Manor Care Center · (517) 457-9548 | Bellhaven of Chagrin Falls · (231) 283-7448 | $0 / $0 | med |
| 50 | 0013NUZQHQUEZ8DXEG | name | Chesterton Senior Commons | Bellhaven of Chesterton | $0 / $0 | med |
| 63 | 001TZCSTBZFM6K5BGN | name | Bellhaven Rehab and Nursing of Grove City | Bellhaven Rehabilitation & Nursing of Grove City | $0 / $0 | med |
| 66 | 0017MN2JYAJBDS8WQZ | name, phone | Sunny Acres Retirement Home · (216) 898-7925 | Bellhaven Willow Creek · (419) 394-5494 | $0 / $0 | med |
| 67 | 0010KJFP601YNTZVDA | name, phone | Arbors at Bellhaven Dayton · (216) 659-9837 | The Arbors at Bellhaven - Dayton · (260) 254-7592 | $0 / $0 | med |
| 59 | 001CF3LDWVRGL09P4F | billing_zip | 45626 | 45662 (street and phone match; transposed digits) | $0 / $0 | med |
| 45 | 001UKEFGADQ8YCZ4YM | phone | (330) 975-2492 | (231) 533-2969 (**Findlay**: phone only, `parent_id` untouched) | $22,000 / $0 | low |
| 51 | 001R4PXTUD9R6FNN8V | phone | (231) 238-4862 | (330) 691-2711 (Defiance) | $66,000 / $9,500 | low |
| 52 | 001JQER1RMYKNRLNME | phone | (517) 409-8156 | (330) 405-6040 (Goshen) | $121,000 / $0 | low |
| 55 | 0015L38R1Z5947ZZP7 | phone | (330) 314-3109 | (517) 847-7948 (Marion) | $87,000 / $0 | low |
| 43 | 001U1750VLVJAGG1S5 | phone | (814) 291-2902 | (814) 412-2218 (Monroe survivor) | $0 / $0 | low |
| 58 | 001UELXDAKFRKB8932 | phone | (614) 512-8712 | (330) 733-6423 (Port Clinton survivor) | $0 / $0 | low |
| 65 | 001CVBBCSDM7YHN220 | phone | (419) 495-1741 | (614) 792-9343 (Erie survivor) | $0 / $0 | low |

Defiance has AR, but only `phone` changes. A parent change on Defiance would have triggered CHOW.

### 1b. Direct re-parents (SOP permits: AR = $0)

| # | Account ID | Field | Before | After | Revenue / AR | Evidence |
|---|---|---|---|---|---|---|
| 39 | 001LGFPBJY4N9MB6KL Bellhaven Crossings of Lima | parent_id | Harborview Care Group `001FJZYHR7MLFMNPLL` | Bellhaven `0015QAPLGS3FVYEEEM` | $47,000 / **$0** | exact address; About page: Harborview joined 2025 |
| 61 | 001H1JMVZWP46D5VUF Cedar Trail of Zanesville | parent_id | Cedar Trail Communities `001FWSQ30SFW6S7604` | Bellhaven | **$0** / $0 | exact address; About page: Cedar Trail communities joined 2026 |

### 1c. Duplicate (same parent)

| # | Loser → Survivor | Loser before | Loser after | Why this survivor |
|---|---|---|---|---|
| 56 | 001QU150PM4Z15UA71 → 001EGU7BMJ942ZTRE6 (both Bellhaven of Owosso, 1120 W Main St 48867) | Active, dup="" | Inactive, `duplicate_of_account`=001EGU7BMJ942ZTRE6, note appended | survivor's phone (734) 503-1363 matches the website; loser has $0 / $0 |

Follow-up (not automated): the loser has a contact, Tricia Lindqvist (Admissions). It stays attached to the inactive record.

### 1d. New accounts (no CRM account at that ZIP or street)

| # | POST /accounts body |
|---|---|
| 47 | Bellhaven of Batavia · 2000 Hospital Dr, Batavia OH 45103 · (231) 698-3092 · care_type Skilled Nursing · parent Bellhaven · Active |
| 48 | Bellhaven of Carlisle · 640 Walnut Bottom Rd, Carlisle **PA** 17015 · (260) 386-7765 · Skilled Nursing · parent Bellhaven · Active (this is not the existing *New Carlisle, OH* account 001AQGPZ5G5VRES536) |

## Wave 2: 6 items, previewed only after their wave 1 sibling is VERIFIED (each `APPLY <id>`; optional `APPLY BATCH OF 6`)

| # | Account ID | Change | Before | After | Revenue / AR |
|---|---|---|---|---|---|
| 40 | 001LGFPBJY4N9MB6KL (Lima) | phone | (734) 872-9575 | (231) 539-3617 | $47,000 / $0 |
| 62 | 001H1JMVZWP46D5VUF (Zanesville) | name, phone | Cedar Trail of Zanesville · (517) 817-8191 | Bellhaven of Zanesville · (814) 599-2533 | $0 / $0 |
| 41 | 0011AB44D05WLA9HTX Cedar Trail of Monroe (Cedar Trail) | duplicate → 001U1750VLVJAGG1S5 | Active | Inactive + `duplicate_of_account` + note | $0 / $0 |
| 42 | 00159PL81N38KM4FHM Monroe Gardens Care Center (Harborview) | duplicate → 001U1750VLVJAGG1S5 | Active | Inactive + `duplicate_of_account` + note | $0 / $0 |
| 57 | 001JD2MWRA74LTSN24 Harborview N&R of Port Clinton | duplicate → 001UELXDAKFRKB8932 | Active | Inactive + `duplicate_of_account` + note | $0 / $0 |
| 64 | 001BLYF02K97SZLZHH Harborview Shores of Erie | duplicate → 001CVBBCSDM7YHN220 | Active | Inactive + `duplicate_of_account` + note | $0 / $0 |

**Duplicates: which account survives and why.**

| Facility | Survives (unchanged except its wave 1 phone fix) | Becomes Inactive |
|---|---|---|
| Monroe | `001U1750VLVJAGG1S5`: under the Bellhaven parent, at the website address | `0011AB44D05WLA9HTX` (Cedar Trail) and `00159PL81N38KM4FHM` (Harborview) |
| Port Clinton | `001UELXDAKFRKB8932` | `001JD2MWRA74LTSN24` (Harborview) |
| Erie | `001CVBBCSDM7YHN220` | `001BLYF02K97SZLZHH` (Harborview) |

- Every loser has $0 revenue, $0 AR, no CHOW link and no contacts (read-only contacts check, 2026-11-15).
- Each loser gets `duplicate_of_account` = the survivor, `status` Inactive and an explanatory note.
- Nothing is merged or deleted.

These rows are in wave 2 because each shares an account with a wave 1 item: #39 with #40, #61 with #62, and the survivor phone fixes with the duplicates.

## CHOW: one at a time (`APPLY 54`, `APPLY 60`). Batching is refused by design.

Each CHOW is **one** proposal with an ordered plan, approved and confirmed once:

0. Preserve the old account as the historical financial record. It gets no write: parent, name, status, revenue and AR are unchanged.
1. `POST` the successor under Bellhaven.
2. `PATCH` the old account's `chow_current_account` to the new id.
3. Read back both accounts.

Each step's state is saved. A failed or interrupted run resumes from the saved state after a new preview and confirmation, and never creates a second successor.

**Recommendation:** run CHOW only after one simple PATCH (#43) has been verified on the real API. Then execute #60 **alone** and inspect its read-back before #54. The real API has never received a successor `POST`, and it has **no DELETE endpoint**, so a wrongly created successor could only be marked Inactive, never removed.

| # | Old account (left exactly as is) | Revenue / AR | Step 1: POST successor | Step 2: PATCH old |
|---|---|---|---|---|
| 54 | 001A34WFSUYHCRBLFT Bellhaven of Marietta (Cedar Trail) | $51,250 / **$3,800** | Bellhaven of Marietta · 805 Colegate Dr, Marietta OH 45750 · (614) 337-1967 · Skilled Nursing · parent Bellhaven · Active | `chow_current_account`: "" → new id |
| 60 | 001U6RW32TY0WSXZZB Bellhaven of Tiffin (Cedar Trail) | $84,000 / **$12,400** | Bellhaven of Tiffin · 45 St Lawrence Dr, Tiffin OH 44883 · (260) 589-2589 · Skilled Nursing · parent Bellhaven · Active | `chow_current_account`: "" → new id |

---

## Prepared but recommended for HOLD or INVESTIGATE (4 items): do not approve yet

The operations are exact and executable, but the evidence or field meaning is insufficient. Full questions and consequences are in
[INVESTIGATION_QUESTIONS.md](INVESTIGATION_QUESTIONS.md).

| # | Exact operation | Why not now | Status |
|---|---|---|---|
| **70** | `PATCH 001SXSF4ELF0Z2LGDM` (Bellhaven of Sandusky, $130,000 / **$5,200 AR**) `chow_current_account`: "" → `0017JP8Z1UQ763BVK3` (Millstone Care of Sandusky) | The only evidence is absence from the website plus a same-address Millstone account. The About page never mentions a sale. The account has open AR and an active contact (Frank Dietz, DON) | **INVESTIGATE** |
| **46** | `PATCH 001NXP9X46CWEPSLSV` (Ashtabula) `billing_street`: "PO Box 517" → "3156 W Prospect Rd" | Identity is solid, but the field is a **billing** address, and a PO Box may be the invoicing address | **HOLD** until finance answers |
| **68** | `PATCH 00116ETS45BL7DTQP7` (Alliance) `status`: Active → "Needs Review" + note | "Needs Review" appears nowhere in the CRM (Active 112 / Inactive 9), and the API spec has no enums | **HOLD** unless the value is defined |
| **69** | `PATCH 0016PVXH4B25HWR7QE` (Coldwater), same change | Same as #68 | **HOLD** |

Nothing proposed is **redundant**. The pairs on Lima (#39/#40) and Zanesville (#61/#62) change different fields on purpose,
so each approval stays narrow. Duplicate losers and their survivor phone fixes also touch different accounts.

## Held identity cases (3): no operations exist until you answer

| Hold | Candidate accounts | Status | Recorded command once you decide (writes nothing; the next scan re-proposes, and each result still needs approval) |
|---|---|---|---|
| **#36 Amberly Manor** (Hudson OH) | `0015D74ZLRY810RGY5` (Colorado Springs CO, Juniper Point) | **INVESTIGATE**, leaning distinct | distinct: `./bh resolve 36 distinct --note "<your evidence>"` → `POST` Amberly Manor, 4390 Darrow Rd, Hudson OH 44236, (330) 228-4392, parent Bellhaven; the CO record untouched |
| **#38 Bellhaven at Union Square** (118 Union Square Dr) | `001GNU41AVXZRLLJ9P` (240 Market St, Juniper Point) | **INVESTIGATE**, leaning distinct | distinct: `./bh resolve 38 distinct --note "<your evidence>"` → `POST` Bellhaven at Union Square, 118 Union Square Dr, New Albany OH 43054, (330) 519-9639, parent Bellhaven |
| **#53 Bellhaven of Kettering** | `001WR41PYNWXCAE2X4`, `001B7XZAA3AFALS9GP`, `0016KTS1UAWBRXS09J` (all $0, same address) | **HOLD** | survivor: `./bh resolve 53 survivor <account_id> --note "<your evidence>"` → re-parent and rename the survivor; the other two set Inactive with `duplicate_of_account` |

The questions to answer first, and the consequences of each choice, are in [INVESTIGATION_QUESTIONS.md](INVESTIGATION_QUESTIONS.md).
These commands were dry-run on a **copy** of the ledger; the real ledger has no resolutions.

`./bh resolve <id> revoke --note …` withdraws a decision. Resolutions are append-only and audit-logged.

## Totals

- **28 operations** are ready for your individual authorization: 20 in wave 1, 6 in wave 2, and the 2 CHOW items.
- **4** are prepared but recommended for HOLD or INVESTIGATE: #46, #68, #69, #70.
- **3** identity holds have no operations: #36, #38, #53.

After executing, run `./bh scan`. It should report 0 new proposals, with only the held or investigated items still open. Every verified write appears in History and in `CRM_CHANGE_HISTORY.md`.
