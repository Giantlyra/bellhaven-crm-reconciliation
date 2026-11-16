# Final Decision Review (read-only, for human sign-off)

_2026-11-16. Built from a fresh live read of the CRM (125 accounts) and the website, plus the ledger and the final audit. **No CRM writes, no holds released, no approvals, no ledger changes.** Earlier conversational agreement is **not** treated as permission to write. Server: dry-run._

## 1. The six held proposals

| # | Website (physical) | CRM record(s) | Supports a match | Conflicts / gaps | Financial and contact implications | Recommended disposition |
|---|---|---|---|---|---|---|
| **#53 Kettering** (identity HOLD, no CRM operation) | Bellhaven of Kettering, 3313 Wilmington Pike 45429, (231) 269-5449, admin Priya Ashby | `001WR41PYNWXCAE2X4` Kettering Care Centre (Harborview) · `001B7XZAA3AFALS9GP` Kettering Senior Campus (Cedar Trail, "Wilmington **Pk**") · `0016KTS1UAWBRXS09J` Kettering Nursing & Rehabilitation (**no parent**). All $0/$0, Active, no contacts | All three are at the same address | None is under Bellhaven; none has the website phone; the administrator appears nowhere; no record is decisive | No billing at risk. Picking a survivor would be a guess | **Keep HOLD.** Question: which record is live, or should a Bellhaven account be designated and the rest treated as predecessors? |
| **#38 Union Square** (identity HOLD, no CRM operation) | Bellhaven at Union Square, **118 Union Square Dr**, New Albany OH 43054, (330) 519-9639, admin **Phil Holloway** | `001GNU41AVXZRLLJ9P` Union Square Senior Living, **240 Market St**, New Albany 43054, **Juniper Point**, (260) 782-4620, admin **Dale Croft**, $0/$0. The only account in the ZIP | Same city and ZIP; similar name | Different street, phone, parent and administrator | No billing at risk. Creating a Bellhaven account could duplicate a facility if 240 Market St is actually the same campus | **Keep HOLD**, leaning *distinct*. Question: is 240 Market St a separate community? |
| **#41 Monroe / Cedar Trail** (actionable, held) | Bellhaven Gardens of Monroe, 750 Stewart Rd 48162, (814) 412-2218, admin Phil Mabry | Existing **Bellhaven Gardens of Monroe** `001U1750VLVJAGG1S5` (Bellhaven; phone fixed by #43; contact Elaine Vogel, Billing). Disputed: **Cedar Trail of Monroe** `0011AB44D05WLA9HTX`, "750 Stewart **Road**", Cedar Trail, (216) 748-7799, $0/$0, no contacts | Same building | A Cedar Trail record at a building with Harborview lineage (#42) is unexplained; nothing ties it to the community | No billing; no contacts to orphan | **Keep HOLD.** Question: did 750 Stewart Rd ever operate under Cedar Trail, or is this record an error? |
| **#46 Ashtabula** (actionable, held) | Bellhaven of Ashtabula, **3156 W Prospect Rd** 44004, (260) 440-4975, admin Ned Green | **Existing** `001NXP9X46CWEPSLSV` Bellhaven of Ashtabula, billing **PO Box 517** 44004, Bellhaven, same phone; contacts Ned Green (Admin), Marie Bianchi (DON) | Name, phone, ZIP and administrator all match; **not a missing account** | The proposal would overwrite the billing PO box with the street address | $0/$0 billing history, but the PO box may be the real invoice mailing address | **Keep HOLD: Needs verification** (mailing vs physical; purpose unverified). Briefly released to pending at 22:04 UTC with no note; re-held 22:16 UTC with the reviewer note. Release or approval now requires an evidence note. Finance question: is PO Box 517 the mailing address, and where should the physical street be recorded? |
| **#49 Chagrin Falls** (actionable, held) | Bellhaven of Chagrin Falls, 150 River St 44022, (231) 283-7448, admin Dale Mabry | `001RJU1X4NBWC1Q0G7` **Riverbend Manor Care Center**, 150 River St 44022, already under Bellhaven, $0/$0; contact **Dale Mabry (Administrator)** | Exact address; the administrator matches; the only account in the ZIP | Was "Riverbend Manor" a former name or a former operator? | No ownership field would change; no billing at risk | **Keep HOLD** (your decision). The evidence would support release if you confirm the former name |
| **#66 Willow Creek** (actionable, held) | Bellhaven Willow Creek, 8060 Willow Creek Ln 49024, (419) 394-5494, admin Walt Mabry | `0017MN2JYAJBDS8WQZ` **Sunny Acres Retirement Home**, 8060 Willow Creek Lane 49024, under Bellhaven, Memory Care, $0/$0, **no contacts** | Exact address; memory-only care type; the only account in the ZIP | No person or record corroborates the identity | No billing at risk | **Keep HOLD.** Question: is Sunny Acres the same facility under a former name? |

**The three kinds of "not done":**
- An **identity HOLD** (#38, #53) has *no* CRM operation at all.
- An **actionable proposal held by a human** (#41, #46, #49, #66) has a concrete operation that could be released later.
- A **rejected** proposal (below) will never run.

## 2. #71 Amberly Manor, Hudson OH (not held; approved 2026-11-16 22:21:51 UTC, not executed)

- **Website:** Amberly Manor, 4390 Darrow Rd, Hudson OH 44236, (330) 228-4392, admin Tom Trent.
- **No CRM account in Hudson.**
- **Why the Colorado Amberly Manor is distinct.** `0015D74ZLRY810RGY5` is at 918 S Nevada Ave, Colorado Springs CO, under Juniper Point, phone (734) 358-9267, administrator Ned Duval. Bellhaven operates only in OH, MI, IN and PA. Every identity attribute differs except the name, and matching never relies on name alone.
- **Proposed:** create Amberly Manor (Hudson OH) under Bellhaven, starting at $0/$0.
- **Status: APPROVED in the app (22:21:51 UTC, empty note), not executed.** Creating it still needs a typed `APPLY 71` on a writes-enabled server. Nothing is created.

## 2a. Investigation categories (display only, shown in the app)

Each open case carries a descriptive category so a reviewer can see why it isn't finished and what the business must confirm. **Categories are labels, not statuses or permissions:** nothing in the executor, batch or queue reads them. Statuses come live from the ledger.

| Category | Cases (status at 2026-11-16 ~22:40 UTC) | What the business team must confirm |
|---|---|---|
| Possible change of ownership / rebrand (none confirmed) | #41 Monroe HELD · #49 Chagrin Falls HELD · #66 Portage HELD | Did 750 Stewart Rd operate under Cedar Trail? Is Riverbend Manor a former name? Is Sunny Acres a former name? |
| Address verification | #46 Ashtabula HELD | Should PO Box 517 remain the billing address? |
| Identity verification | #38 Union Square HELD · #53 Kettering HELD | Is 240 Market St a separate community? Which of the three Kettering records is current? |
| New account confirmation (not an ownership change) | #71 Amberly Manor APPROVED, not executed | Is Amberly Manor (Hudson OH) a Bellhaven community that needs its own account? |

## 3. Closed without CRM write

| # | Record (live) | Disposition |
|---|---|---|
| #42 | `00159PL81N38KM4FHM` Monroe Gardens Care Center (Harborview), $0/$0, Active, no contacts | Preserved as a likely **historical predecessor**, not inactivated (history inferred) |
| #57 | `001JD2MWRA74LTSN24` Harborview Nursing & Rehab of Port Clinton, $0/$0, Active, no contacts | Same |
| #64 | `001BLYF02K97SZLZHH` Harborview Shores of Erie, $0/$0, Active, no contacts | Same |
| #68 | `00116ETS45BL7DTQP7` Bellhaven Care Center of Alliance, $0/$0, Active | **Rejected:** "Needs Review" is not a CRM status. Question: still a Bellhaven community? |
| #69 | `0016PVXH4B25HWR7QE` Bellhaven of Coldwater, $0/$0, Active | Same |

## 4. Sandusky #70: TECHNICALLY VERIFIED, BUSINESS UNCONFIRMED

- **Live:** `001SXSF4ELF0Z2LGDM` Bellhaven of Sandusky (Bellhaven parent, $130,000 / **$5,200 AR**, contact Frank Dietz, DON) has `chow_current_account` = `0017JP8Z1UQ763BVK3`, Millstone Care of Sandusky (Millstone, $0/$0).
- **Technically verified:** the link exists and matches the operation you authorized (`APPLY 70`, op 23, read-back OK).
- **Business unconfirmed:**
  - The sale's direction and date are not independently documented. The evidence is the community's absence from the website plus a Millstone account at the same address.
  - Who collects the **$5,200** is unknown.
  - The original investigation recommended HOLD; you released and executed it.
- **This report does not describe the transfer as proven.**

## 5. Tiffin #60 and Marietta #54: balances preserved

| | Historical account (live) | Successor (live) |
|---|---|---|
| Tiffin | `001U6RW32TY0WSXZZB`, Cedar Trail, **$84,000 / $12,400**, Active, chow → `00164AE214A6588944` | `00164AE214A6588944`, Bellhaven, **$0 / $0**, website phone |
| Marietta | `001A34WFSUYHCRBLFT`, Cedar Trail, **$51,250 / $3,800**, Active, chow → `0014861C0619562203` | `0014861C0619562203`, Bellhaven, **$0 / $0** |

Unresolved: **who collects the $12,400 and $3,800** left on the historical accounts.

## 6. Lima #39 (and #40): $47,000 revenue, $0 AR

- **Live:** `001LGFPBJY4N9MB6KL` Bellhaven Crossings of Lima, now under **Bellhaven**, $47,000 revenue / **$0 AR**, phone (231) 539-3617 (#40), contact Nadia Sandoval.
- **Implication:** the billing SOP allows a direct re-parent only because AR is $0. Nothing is owed, so no collection responsibility moves.
- **But** the $47,000 of historical revenue, earned while under Harborview, is now attributed to an account under Bellhaven. This follows the earlier Findlay precedent ($22,000, AR $0).
- The CRM administrator contact (Nadia Sandoval) differs from the website's (Tricia Fitch). Contacts are out of scope.

## 7. Owosso #56: duplicate handled

- **Survivor:** `001EGU7BMJ942ZTRE6`, Active, Bellhaven, phone **(734) 503-1363 = website**, contact **Gloria Lambert (Administrator) = website administrator**.
- **Inactive record:** `001QU150PM4Z15UA71`, **Inactive**, `duplicate_of_account` = survivor, $0/$0.
- **Remaining contact on the inactive record:** **Tricia Lindqvist (Admissions Director)**. This is a follow-up to move or confirm; it isn't automated.

## Assessment readiness

- **CRM state matches the ledger:** 25 operations, all verified; 125 accounts; every account changed since the seed is explained by a verified operation. Final audit: **integrity PASS**.
- **Requirements (from the welcome page):** a schedule configuration is provided, and the cron job is also **installed and tested**; no hosting is needed; the public repo opens; the write-up and demo script are ready.
- **Docs:** stale "cron not installed" wording was corrected in the README, `OPERATIONS.md` and the 5-minute script. Historical reports stay marked as PRE-EXECUTION SNAPSHOTs.
- **Not yet done (yours):** the time-spent and AI-tools wording in `WRITEUP.md`, the video, the form.

## Material uncertainties (business, not technical)

1. Sandusky: the sale and the $5,200 AR owner.
2. Tiffin and Marietta: who collects $12,400 and $3,800.
3. Predecessor history for #42, #57 and #64 is **inferred**.
4. Monroe's Cedar Trail record (#41).
5. Kettering's live record (#53).
6. Union Square identity (#38).
7. Ashtabula billing address (#46).
8. Former names vs former operators (#49, #66).
9. Alliance and Coldwater status (#68, #69).
10. Hudson OH confirmation before #71.
