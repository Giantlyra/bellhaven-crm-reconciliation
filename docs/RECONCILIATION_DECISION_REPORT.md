# Bellhaven CRM Reconciliation: Consolidated Decision Report

_Read-only assessment, 2026-11-16 (UTC), by Claude Code. Nothing in this report is an approval. Each CRM write still needs the user's
in-app Approve → Live preview → typed `APPLY <id>`, followed by a read-back._

**Inputs:**
- Ledger `data/ledger.db`: 34 open proposals (31 PENDING, 3 HELD).
- Scan #11 (2026-11-16 01:24:55 UTC, complete, live): 35 website communities, 121 CRM accounts, snapshot `data/snapshots/run-0011-*.json`.
- A fresh live CRM read (all 121 accounts plus 67 contacts) and the website About page.

**Integrity checks:**
- No open proposal has drifted from its baseline.
- No account has an existing `chow_current_account`, `duplicate_of_account` or note.
- CRM status values in use: Active 112, Inactive 9.

> **Wave A status (2026-11-16 02:23 UTC):** all 14 field corrections were tentatively approved by the user and verified read-only (`WAVE_A_FINAL_VALIDATION.md`). Awaiting individual authorization. The 9 investigation and 2 not-recommended cases are unchanged.

> ## FINAL STATUS (2026-11-16, supersedes the counts below)
>
> **35 proposals reviewed: 23 VERIFIED (25 CRM operations) · 6 HOLD · 5 CLOSED/REJECTED without CRM write · #36 resolved and superseded by #71** (a new pending create for Amberly Manor, Hudson OH, from the follow-up scan; review only). Independent audit: 25 of 25 operations live-matched and receipted; protected fields and contacts intact; no unexplained CRM writes.
>
> | Disposition | Proposals |
> |---|---|
> | **Verified field updates** | #43, #58, #65, #52, #55, #45, #37, #44, #51, #63, #67, #50, #59, #40, #62 |
> | **Verified parent corrections** | #39 Lima, #61 Zanesville (AR $0, so direct re-parent under the SOP) |
> | **Verified duplicate** | #56 Owosso (same parent; loser inactivated and linked) |
> | **Verified new accounts** | #47 Batavia `00163AAEB690110611`, #48 Carlisle `00163ED66F49793F79` |
> | **Verified changes of ownership** | #60 Tiffin → `00164AE214A6588944`; #54 Marietta → `0014861C0619562203`. Historical accounts keep $84,000/$12,400 and $51,250/$3,800 |
> | **Verified CHOW link: documented exception** | #70 Sandusky → Millstone `0017JP8Z1UQ763BVK3`. Sale **not independently confirmed**; responsibility for the $5,200 AR unresolved |
> | **Closed: historical predecessor records, both accounts preserved, no CRM write** | #57 Port Clinton, #64 Erie, #42 Monroe (Harborview). Ownership history **inferred, not confirmed** |
> | **Closed: rejected as written** | #68 Alliance, #69 Coldwater (invalid status value "Needs Review") |
> | **HOLD: unresolved** | #41 Monroe (Cedar Trail), #53 Kettering, #38 Union Square, #46 Ashtabula, #49 Chagrin Falls, #66 Willow Creek |
> | **Identity resolved → new proposal** | #36 Amberly Manor resolved DISTINCT. Follow-up scan #12 created **#71** (create Amberly Manor, 4390 Darrow Rd, Hudson OH, under Bellhaven), **pending, not executed** |
>
> Legacy pre-engine change: Findlay `parent_id` → Bellhaven (verified, not part of the 35).
> Details: `EVALUATION_TABLE.md`, `CRM_CHANGE_HISTORY.md`, `CHOW_REVIEW.md`.

## 1. Executive summary

Bellhaven's website lists **35 communities**:
- **10** already match the CRM cleanly. This includes Monroe, which was fixed by verified write #43.
- **25** have one or more open proposals.

The CRM also holds **5 Bellhaven-parented accounts that are not at any website address**: Alliance, Coldwater and Sandusky, plus Ashtabula (PO Box) and Portsmouth (ZIP typo). All five are covered.

The CRM changes verified so far are the legacy Findlay re-parent and #43 (Monroe phone).

| Decision | Count | Proposals |
|---|---|---|
| **READY FOR APPROVAL** | **23** | #58, #65, #52, #55, #45, #51, #37, #44, #49, #50, #63, #66, #67, #59, #56, #39, #61, #40, #62, #47, #48, #60, #54 |
| **NEEDS INVESTIGATION** | **9** | #41, #42, #57, #64, #53, #36, #38, #70, #46 |
| **NOT RECOMMENDED** | **2** | #68, #69 |
| Total open | 34 | |

**What the 23 ready items would accomplish:**
- Fix phone, name or ZIP on 14 Bellhaven accounts.
- Re-parent Lima and Zanesville.
- Create the missing Batavia and Carlisle accounts.
- Perform the two CHOW successions (Tiffin, Marietta) under the billing SOP.
- Retire one same-parent duplicate (Owosso).

**What remains blocked:**
- Every case that depends on a business judgement about **historical ownership** (predecessor-brand records, Kettering, Sandusky).
- Identity of two website communities with **no CRM account** (Amberly Manor in Hudson, Union Square in New Albany).
- A billing-address policy (Ashtabula).
- Two status changes that use a value the CRM does not recognize.

## 2. Most important unresolved business questions

| # | Question | Blocks | Why it matters |
|---|---|---|---|
| Q1 | Are the $0 Harborview- and Cedar Trail-branded accounts at Monroe, Port Clinton and Erie **predecessor-operator records** (keep as history, or link) or **accidental duplicates** (inactivate as `duplicate_of_account`)? | #41, #42, #57, #64 | The write is the same either way and reversible. But the label ("Duplicate of …") becomes the permanent explanation in the CRM. One policy should apply to all four. |
| Q2 | Kettering: which of the three $0 accounts (Harborview, Cedar Trail, no-parent) is the live record for Bellhaven of Kettering? | #53 | Until answered, a Bellhaven community has no correctly parented account. The answer would also settle Q1 for Kettering. |
| Q3 | Did Bellhaven sell Sandusky to Millstone, and who owns the **$5,200 open AR**? | #70 | A CHOW link on a protected billing account with open AR has financial consequences if it is wrong. |
| Q4 | Are Amberly Manor (Hudson OH vs Colorado Springs CO) and Union Square (118 Union Square Dr vs 240 Market St) separate facilities? | #36, #38 | If yes, **two Bellhaven communities are missing from the CRM entirely**. Resolving them leads to create proposals. |
| Q5 | Should Ashtabula's billing address stay `PO Box 517` for invoicing? | #46 | The CRM has a single address field. Changing it could misroute invoices. |
| Q6 | Are Alliance and Coldwater still Bellhaven (closed, sold, or simply unlisted)? What status value should flag them? | #68, #69 | "Needs Review" is not a CRM status value. A note-only change or a decision to inactivate would need a new proposal. |

Out of scope, noted for completeness: the CRM **contacts are not reconciled**. The website administrator differs from the CRM contact at Sycamore Ridge, Lima, Grove City and Monroe, and the Owosso loser's contact will remain on the inactive record.

## 3. Recommended execution order and dependencies

Each step needs the server started with `CRM_WRITES_ENABLED=1 ./bh serve --port 8020`, then, per proposal: **Approve → Live preview → `APPLY <id>`**.
Non-CHOW items in the same wave may be confirmed together with `APPLY BATCH OF <n>`. Each item is still validated, executed and read back individually, and the batch stops at the first failure. Claude Code verifies each wave with an independent live read-back.

| Wave | Proposals | Depends on | Notes |
|---|---|---|---|
| A. Field fixes (14) | #58, #65, #52, #55, #45, #51, #37, #44, #49, #50, #63, #66, #67, #59 | none | Each writes a different account; there are no overlaps. #58 and #65 do not depend on #57 and #64 |
| B. Duplicate (1) | #56 Owosso | none | Writes only the loser account `001QU150PM4Z15UA71` |
| C. Re-parents (2) | #39 Lima, #61 Zanesville | none | SOP allows a direct re-parent (AR $0) |
| D. Dependents (2) | #40 Lima phone, #62 Zanesville name and phone | #39 and #61 **read-back verified** | Same account as the prerequisite; preview only after it verifies |
| E. Creates (2) | #47 Batavia, #48 Carlisle | none | One at a time; the duplicate-successor guard re-checks the address before POST |
| F. CHOW (2) | #60 Tiffin, **then** #54 Marietta | #60 verified before #54 | Never batched. Per `DEMO_SCRIPT.md`, #60 may be the item executed on camera |
| G. Re-scan | `./bh scan` | all of the above | Expected result: only the 11 items in sections 5 and 6 remain open |
| H. Investigation | Q1–Q6 | business answers | Then `./bh resolve` for #36, #38 and #53, and decisions on #41, #42, #57, #64, #70 and #46 |

## 4. READY FOR APPROVAL (23)

#### #58 · FIELD_UPDATE · Update phone: Bellhaven of Port Clinton
- **Recommendation: APPROVE**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Exact address and name; Bellhaven parent; the administrator contact (Brenda Whitfield) matches the website. Changes only the phone on the Bellhaven account. It is independent of duplicate #57: the #57 baseline excludes this phone.
- **Website:** Bellhaven of Port Clinton · 1420 Harbor Point Dr, Port Clinton OH 43452 · (330) 733-6423 · admin Brenda Whitfield · `/communities/bellhaven-of-port-clinton`
- **CRM (live GET):** `001UELXDAKFRKB8932` Bellhaven of Port Clinton · 1420 Harbor Point Dr, Port Clinton OH 43452 · (614) 512-8712 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001UELXDAKFRKB8932 {"phone": "(330) 733-6423"}
- **Sources:** ledger proposal #58 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/58`

#### #65 · FIELD_UPDATE · Update phone: Bellhaven Shores of Erie
- **Recommendation: APPROVE**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Exact address and name; Bellhaven parent; the administrator contact (Angela Quinn) matches the website. Changes only the phone. It is independent of duplicate #64.
- **Website:** Bellhaven Shores of Erie · 4930 W Lake Rd, Erie PA 16505 · (614) 792-9343 · admin Angela Quinn · `/communities/bellhaven-shores-of-erie`
- **CRM (live GET):** `001CVBBCSDM7YHN220` Bellhaven Shores of Erie · 4930 W Lake Rd, Erie PA 16505 · (419) 495-1741 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001CVBBCSDM7YHN220 {"phone": "(614) 792-9343"}
- **Sources:** ledger proposal #65 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/65`

#### #52 · FIELD_UPDATE · Update phone: Bellhaven of Goshen
- **Recommendation: APPROVE**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Exact address (Ave/Avenue normalized); the administrator contact matches. Phone only. Revenue is $121k but AR is $0, and a phone change triggers no SOP rule.
- **Website:** Bellhaven of Goshen · 1610 College Ave, Goshen IN 46526 · (330) 405-6040 · admin Tanya Castellano · `/communities/bellhaven-of-goshen`
- **CRM (live GET):** `001JQER1RMYKNRLNME` Bellhaven of Goshen · 1610 College Avenue, Goshen IN 46526 · (517) 409-8156 · parent Bellhaven Senior Living · $121,000 / AR $0
- **Operation:** PATCH /accounts/001JQER1RMYKNRLNME {"phone": "(330) 405-6040"}
- **Sources:** ledger proposal #52 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/52`

#### #55 · FIELD_UPDATE · Update phone: Bellhaven of Marion
- **Recommendation: APPROVE**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Exact address (Rd W / Road West normalized); the administrator contact matches. Phone only.
- **Website:** Bellhaven of Marion · 199 Barks Rd W, Marion OH 43302 · (517) 847-7948 · admin Doug Amato · `/communities/bellhaven-of-marion`
- **CRM (live GET):** `0015L38R1Z5947ZZP7` Bellhaven of Marion · 199 Barks Road West, Marion OH 43302 · (330) 314-3109 · parent Bellhaven Senior Living · $87,000 / AR $0
- **Operation:** PATCH /accounts/0015L38R1Z5947ZZP7 {"phone": "(517) 847-7948"}
- **Sources:** ledger proposal #55 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/55`

#### #45 · FIELD_UPDATE · Update phone: Bellhaven Meadows of Findlay
- **Recommendation: APPROVE**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Exact address; the administrator contact matches. Phone only. `parent_id`, set by the legacy Findlay write, is untouched; 'do not retry Findlay' refers to `parent_id` only.
- **Website:** Bellhaven Meadows of Findlay · 1800 N Blanchard St, Findlay OH 45840 · (231) 533-2969 · admin Sam Pruitt · `/communities/bellhaven-meadows-of-findlay`
- **CRM (live GET):** `001UKEFGADQ8YCZ4YM` Bellhaven Meadows of Findlay · 1800 N Blanchard St, Findlay OH 45840 · (330) 975-2492 · parent Bellhaven Senior Living · $22,000 / AR $0
- **Operation:** PATCH /accounts/001UKEFGADQ8YCZ4YM {"phone": "(231) 533-2969"}
- **Sources:** ledger proposal #45 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/45`

#### #51 · FIELD_UPDATE · Update phone: Bellhaven of Defiance
- **Recommendation: APPROVE**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Exact address; the administrator contact matches. Phone only. The account has AR of $9,500, but no parent or status change is involved, so the CHOW rules are not engaged.
- **Website:** Bellhaven of Defiance · 700 Carpenter Rd, Defiance OH 43512 · (330) 691-2711 · admin Victor Barros · `/communities/bellhaven-of-defiance`
- **CRM (live GET):** `001R4PXTUD9R6FNN8V` Bellhaven of Defiance · 700 Carpenter Road, Defiance OH 43512 · (231) 238-4862 · parent Bellhaven Senior Living · $66,000 / AR $9,500
- **Operation:** PATCH /accounts/001R4PXTUD9R6FNN8V {"phone": "(330) 691-2711"}
- **Sources:** ledger proposal #51 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/51`

#### #37 · FIELD_UPDATE · Update name, phone: Bellhaven of Sycamore Ridge
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** Exact address; Bellhaven parent; name differs only in 'of' → 'at'. Caveat: the CRM administrator contact (Sofia Castellano) differs from the website (Tom Bloom). Contacts are out of scope.
- **Website:** Bellhaven at Sycamore Ridge · 7420 Sycamore Ridge Dr, Miamisburg OH 45342 · (260) 365-6510 · admin Tom Bloom · `/communities/bellhaven-at-sycamore-ridge`
- **CRM (live GET):** `00191H7JR16471SZ34` Bellhaven of Sycamore Ridge · 7420 Sycamore Ridge Dr, Miamisburg OH 45342 · (419) 982-7764 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/00191H7JR16471SZ34 {"name": "Bellhaven at Sycamore Ridge", "phone": "(260) 365-6510"}
- **Sources:** ledger proposal #37 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/37`

#### #44 · FIELD_UPDATE · Update name, phone: Bellhaven Health Care Center of Ashland
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** Exact address; Bellhaven parent; the administrator contact (Carla Okafor) matches. The name change is a spelling normalization ('Healthcare Centre').
- **Website:** Bellhaven Healthcare Centre of Ashland · 1631 Claremont Ave, Ashland OH 44805 · (517) 314-5115 · admin Carla Okafor · `/communities/bellhaven-healthcare-centre-of-ashland`
- **CRM (live GET):** `001RJ0D7Z5MAZN5HX5` Bellhaven Health Care Center of Ashland · 1631 Claremont Ave, Ashland OH 44805 · (734) 319-7813 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001RJ0D7Z5MAZN5HX5 {"name": "Bellhaven Healthcare Centre of Ashland", "phone": "(517) 314-5115"}
- **Sources:** ledger proposal #44 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/44`

#### #49 · FIELD_UPDATE · Update name, phone: Riverbend Manor Care Center
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** A material rename (Riverbend Manor Care Center → Bellhaven of Chagrin Falls), but the address is exact, the parent is already Bellhaven, and the administrator contact (Dale Mabry) matches the website. Strong alias evidence.
- **Website:** Bellhaven of Chagrin Falls · 150 River St, Chagrin Falls OH 44022 · (231) 283-7448 · admin Dale Mabry · `/communities/bellhaven-of-chagrin-falls`
- **CRM (live GET):** `001RJU1X4NBWC1Q0G7` Riverbend Manor Care Center · 150 River St, Chagrin Falls OH 44022 · (517) 457-9548 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001RJU1X4NBWC1Q0G7 {"name": "Bellhaven of Chagrin Falls", "phone": "(231) 283-7448"}
- **Sources:** ledger proposal #49 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/49`

#### #50 · FIELD_UPDATE · Update name: Chesterton Senior Commons
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** Exact address (NW/Northwest normalized); the phone **already matches** the website; the administrator contact matches. Name only.
- **Website:** Bellhaven of Chesterton · 1250 NW Franklin Street, Chesterton IN 46304 · (216) 551-3978 · admin Karen Reyes · `/communities/bellhaven-of-chesterton`
- **CRM (live GET):** `0013NUZQHQUEZ8DXEG` Chesterton Senior Commons · 1250 Northwest Franklin St, Chesterton IN 46304 · (216) 551-3978 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/0013NUZQHQUEZ8DXEG {"name": "Bellhaven of Chesterton"}
- **Sources:** ledger proposal #50 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/50`

#### #63 · FIELD_UPDATE · Update name: Bellhaven Rehab and Nursing of Grove City
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** Exact address; the phone already matches; name formatting only ('Rehab and' → 'Rehabilitation &'). The CRM has no administrator contact (only a DON).
- **Website:** Bellhaven Rehabilitation & Nursing of Grove City · 3985 Broadway, Grove City OH 43123 · (614) 555-7729 · admin Marie Vogel · `/communities/bellhaven-rehabilitation-nursing-of-grove-city`
- **CRM (live GET):** `001TZCSTBZFM6K5BGN` Bellhaven Rehab and Nursing of Grove City · 3985 Broadway, Grove City OH 43123 · (614) 555-7729 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001TZCSTBZFM6K5BGN {"name": "Bellhaven Rehabilitation & Nursing of Grove City"}
- **Sources:** ledger proposal #63 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/63`

#### #66 · FIELD_UPDATE · Update name, phone: Sunny Acres Retirement Home
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** A material rename (Sunny Acres Retirement Home → Bellhaven Willow Creek). The address is exact, the parent is Bellhaven, and the care type matches (Memory). No contacts exist to corroborate, so this is the weakest of the renames, but no competing account exists.
- **Website:** Bellhaven Willow Creek · 8060 Willow Creek Ln, Portage MI 49024 · (419) 394-5494 · admin Walt Mabry · `/communities/bellhaven-willow-creek`
- **CRM (live GET):** `0017MN2JYAJBDS8WQZ` Sunny Acres Retirement Home · 8060 Willow Creek Lane, Portage MI 49024 · (216) 898-7925 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/0017MN2JYAJBDS8WQZ {"name": "Bellhaven Willow Creek", "phone": "(419) 394-5494"}
- **Sources:** ledger proposal #66 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/66`

#### #67 · FIELD_UPDATE · Update name, phone: Arbors at Bellhaven Dayton
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** Exact address; the administrator contact (Ray Novak) matches; name punctuation plus a phone fix.
- **Website:** The Arbors at Bellhaven - Dayton · 2210 Salem Ave, Dayton OH 45406 · (260) 254-7592 · admin Ray Novak · `/communities/the-arbors-at-bellhaven-dayton`
- **CRM (live GET):** `0010KJFP601YNTZVDA` Arbors at Bellhaven Dayton · 2210 Salem Ave, Dayton OH 45406 · (216) 659-9837 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/0010KJFP601YNTZVDA {"name": "The Arbors at Bellhaven - Dayton", "phone": "(260) 254-7592"}
- **Sources:** ledger proposal #67 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/67`

#### #59 · FIELD_UPDATE · Update billing_zip: Bellhaven of Portsmouth
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence medium. Live drift: none
- **Why:** Street, name, phone and administrator all match; the ZIP is transposed (45626 → 45662). Portsmouth OH is 45662. Low ambiguity.
- **Website:** Bellhaven of Portsmouth · 2222 Gallia St, Portsmouth OH 45662 · (330) 431-2495 · admin Tanya Quinn · `/communities/bellhaven-of-portsmouth`
- **CRM (live GET):** `001CF3LDWVRGL09P4F` Bellhaven of Portsmouth · 2222 Gallia St, Portsmouth OH 45626 · (330) 431-2495 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001CF3LDWVRGL09P4F {"billing_zip": "45662"}
- **Sources:** ledger proposal #59 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/59`

#### #56 · DUPLICATE · Duplicate: Bellhaven of Owosso (001QU150PM4Z15UA71) → Bellhaven of Owosso (001EGU7BMJ942ZTRE6)
- **Recommendation: APPROVE**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** A same-parent duplicate (both are Bellhaven of Owosso). The survivor wins decisively: its phone matches the website and its administrator contact (Gloria Lambert) matches. The loser has $0/$0, no links, and no billing history. Follow-up, not automated: the loser's contact Tricia Lindqvist (Admissions Director) stays attached to the inactive record.
- **Website:** Bellhaven of Owosso · 1120 W Main St, Owosso MI 48867 · (734) 503-1363 · admin Gloria Lambert · `/communities/bellhaven-of-owosso`
- **CRM (live GET):** `001QU150PM4Z15UA71` Bellhaven of Owosso · 1120 West Main Street, Owosso MI 48867 · (330) 383-5991 · parent Bellhaven Senior Living · $0 / AR $0<br>`001EGU7BMJ942ZTRE6` Bellhaven of Owosso · 1120 W Main St, Owosso MI 48867 · (734) 503-1363 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001QU150PM4Z15UA71 {"duplicate_of_account": "001EGU7BMJ942ZTRE6", "status": "Inactive", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #56 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/56`

#### #39 · WRONG_PARENT · Re-parent: Bellhaven Crossings of Lima (Harborview Care Group (Parent Account) → Bellhaven)
- **Recommendation: APPROVE**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** Direct re-parent Harborview → Bellhaven. The SOP allows this because AR is $0 (revenue $47k). The About page confirms Harborview joined Bellhaven in 2025. This is the only account at the address. Caveat: the CRM administrator contact (Nadia Sandoval) ≠ the website (Tricia Fitch).
- **Website:** Bellhaven Crossings of Lima · 3115 N Cole St, Lima OH 45801 · (231) 539-3617 · admin Tricia Fitch · `/communities/bellhaven-crossings-of-lima`
- **CRM (live GET):** `001LGFPBJY4N9MB6KL` Bellhaven Crossings of Lima · 3115 N Cole St, Lima OH 45801 · (734) 872-9575 · parent Harborview Care Group · $47,000 / AR $0
- **Operation:** PATCH /accounts/001LGFPBJY4N9MB6KL {"parent_id": "0015QAPLGS3FVYEEEM"}
- **Sources:** ledger proposal #39 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/39`

#### #61 · WRONG_PARENT · Re-parent: Cedar Trail of Zanesville (Cedar Trail Communities (Parent Account) → Bellhaven)
- **Recommendation: APPROVE**. Engine rating: risk high, confidence medium. Live drift: none
- **Why:** Direct re-parent Cedar Trail → Bellhaven. $0/$0, so the SOP allows it. The About page confirms Cedar Trail communities joined in 2026, and the administrator contact (Dale Amato) matches. This is the only account at the address.
- **Website:** Bellhaven of Zanesville · 2680 Maple Ave, Zanesville OH 43701 · (814) 599-2533 · admin Dale Amato · `/communities/bellhaven-of-zanesville`
- **CRM (live GET):** `001H1JMVZWP46D5VUF` Cedar Trail of Zanesville · 2680 Maple Avenue, Zanesville OH 43701 · (517) 817-8191 · parent Cedar Trail Communities · $0 / AR $0
- **Operation:** PATCH /accounts/001H1JMVZWP46D5VUF {"parent_id": "0015QAPLGS3FVYEEEM"}
- **Sources:** ledger proposal #61 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/61`

#### #40 · FIELD_UPDATE · Update phone: Bellhaven Crossings of Lima
- **Recommendation: APPROVE (after #39 verifies)**. Engine rating: risk low, confidence high. Live drift: none
- **Why:** Phone fix on the Lima account. It touches the same account as #39, so preview and execute it only after #39 is read-back verified; the drift guard accepts only #39's verified value.
- **Website:** Bellhaven Crossings of Lima · 3115 N Cole St, Lima OH 45801 · (231) 539-3617 · admin Tricia Fitch · `/communities/bellhaven-crossings-of-lima`
- **CRM (live GET):** `001LGFPBJY4N9MB6KL` Bellhaven Crossings of Lima · 3115 N Cole St, Lima OH 45801 · (734) 872-9575 · parent Harborview Care Group · $47,000 / AR $0
- **Operation:** PATCH /accounts/001LGFPBJY4N9MB6KL {"phone": "(231) 539-3617"}
- **Sources:** ledger proposal #40 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/40`

#### #62 · FIELD_UPDATE · Update name, phone: Cedar Trail of Zanesville
- **Recommendation: APPROVE (after #61 verifies)**. Engine rating: risk medium, confidence high. Live drift: none
- **Why:** Rename Cedar Trail of Zanesville → Bellhaven of Zanesville, plus a phone fix. The same account as #61, so it goes after #61 verifies.
- **Website:** Bellhaven of Zanesville · 2680 Maple Ave, Zanesville OH 43701 · (814) 599-2533 · admin Dale Amato · `/communities/bellhaven-of-zanesville`
- **CRM (live GET):** `001H1JMVZWP46D5VUF` Cedar Trail of Zanesville · 2680 Maple Avenue, Zanesville OH 43701 · (517) 817-8191 · parent Cedar Trail Communities · $0 / AR $0
- **Operation:** PATCH /accounts/001H1JMVZWP46D5VUF {"name": "Bellhaven of Zanesville", "phone": "(814) 599-2533"}
- **Sources:** ledger proposal #62 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/62`

#### #47 · WEBSITE_ONLY · Create account: Bellhaven of Batavia
- **Recommendation: APPROVE**. Engine rating: risk high, confidence medium. Live drift: none
- **Why:** No CRM account in that ZIP, city, name or phone, and none in the 451xx ZIP area. Creates a Bellhaven-parented account. The duplicate-successor guard re-checks for an account at the address right before the POST. Confidence is medium only because absence of evidence is the evidence.
- **Website:** Bellhaven of Batavia · 2000 Hospital Dr, Batavia OH 45103 · (231) 698-3092 · admin Elaine Lindqvist · `/communities/bellhaven-of-batavia`
- **CRM (live GET):** — (new account)
- **Operation:** POST /accounts {"name": "Bellhaven of Batavia", "billing_street": "2000 Hospital Dr", "billing_city": "Batavia", "billing_state": "OH", "billing_zip": "45103", "phone": "(231) 698-3092", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"} (+ provenance note)
- **Sources:** ledger proposal #47 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/47`

#### #48 · WEBSITE_ONLY · Create account: Bellhaven of Carlisle
- **Recommendation: APPROVE**. Engine rating: risk high, confidence medium. Live drift: none
- **Why:** Carlisle **PA** 17015 is distinct from Bellhaven of New Carlisle **OH** 45344, which is a separate website community and already a clean match. There is no CRM account in Carlisle, ZIP 170xx, or with this phone. Same create safeguards as #47.
- **Website:** Bellhaven of Carlisle · 640 Walnut Bottom Rd, Carlisle PA 17015 · (260) 386-7765 · admin Ken Ashby · `/communities/bellhaven-of-carlisle`
- **CRM (live GET):** — (new account)
- **Operation:** POST /accounts {"name": "Bellhaven of Carlisle", "billing_street": "640 Walnut Bottom Rd", "billing_city": "Carlisle", "billing_state": "PA", "billing_zip": "17015", "phone": "(260) 386-7765", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"} (+ provenance note)
- **Sources:** ledger proposal #48 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/48`

#### #60 · CHOW · CHOW successor: Bellhaven of Tiffin (Cedar Trail Communities (Parent Account) → Bellhaven)
- **Recommendation: APPROVE (alone, its own session)**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** CHOW: revenue $84,000 and AR $12,400, both > 0, so the old account must be preserved. This is the only account at the address; no existing successor and no existing `chow_current_account`. The About page confirms Cedar Trail joined in 2026. Two ordered operations: POST a successor, then PATCH the link. A partial failure resumes using the saved successor id. By SOP design, the old account keeps its stale phone and Cedar Trail parent.
- **Website:** Bellhaven of Tiffin · 45 St Lawrence Dr, Tiffin OH 44883 · (260) 589-2589 · admin Walt Osei · `/communities/bellhaven-of-tiffin`
- **CRM (live GET):** `001U6RW32TY0WSXZZB` Bellhaven of Tiffin · 45 St Lawrence Dr, Tiffin OH 44883 · (614) 829-9278 · parent Cedar Trail Communities · $84,000 / AR $12,400
- **Operation:** POST /accounts {"name": "Bellhaven of Tiffin", "billing_street": "45 St Lawrence Dr", "billing_city": "Tiffin", "billing_state": "OH", "billing_zip": "44883", "phone": "(260) 589-2589", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"} (+ provenance note)<br>PATCH /accounts/001U6RW32TY0WSXZZB {"chow_current_account": "$ref:new"}
- **Sources:** ledger proposal #60 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/60`

#### #54 · CHOW · CHOW successor: Bellhaven of Marietta (Cedar Trail Communities (Parent Account) → Bellhaven)
- **Recommendation: APPROVE (after #60 verifies)**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** CHOW, same analysis as Tiffin: $51,250 / $3,800. Only account at the address, no existing successor. Run it after #60 so the first CHOW is proven on the real API.
- **Website:** Bellhaven of Marietta · 805 Colegate Dr, Marietta OH 45750 · (614) 337-1967 · admin Rosa Dietz · `/communities/bellhaven-of-marietta`
- **CRM (live GET):** `001A34WFSUYHCRBLFT` Bellhaven of Marietta · 805 Colegate Drive, Marietta OH 45750 · (419) 353-5019 · parent Cedar Trail Communities · $51,250 / AR $3,800
- **Operation:** POST /accounts {"name": "Bellhaven of Marietta", "billing_street": "805 Colegate Dr", "billing_city": "Marietta", "billing_state": "OH", "billing_zip": "45750", "phone": "(614) 337-1967", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"} (+ provenance note)<br>PATCH /accounts/001A34WFSUYHCRBLFT {"chow_current_account": "$ref:new"}
- **Sources:** ledger proposal #54 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/54`

## 5. NEEDS INVESTIGATION (9): deeper analysis

These cases were reviewed from several angles: identity, ownership history, financial exposure, reversibility and consistency with other decisions.

**Predecessor-brand records (#41, #42, #57, #64; Kettering #53 is related).**
- **Facts:**
  - The About page says Harborview joined Bellhaven in 2025 and "select communities" from Cedar Trail joined in 2026.
  - Every Harborview and Cedar Trail account in the CRM sits at a Bellhaven website address.
  - At Monroe, Port Clinton and Erie a Bellhaven-parented account exists alongside them. At Kettering none does.
  - All the predecessor-brand records have $0 revenue and $0 AR, no contacts and no notes.
- **For "historical record":** branded names that follow their parent's naming style, and street-suffix variants such as "Road" and "Drive" that suggest a separate source system.
- **For "duplicate":** no billing ever ran through them, and nothing in the CRM records an ownership change.
- **Financial risk:** none ($0/$0).
- **Reversibility:** full (status and link can be reset).
- **Consistency:** decide all four together under one policy.
- **Recommendation:** once Q1 is answered, approve all four with the same treatment. If the answer is "historical", the note text ideally says so; that would require a new proposal fingerprint.

**Sandusky CHOW link (#70).**
- Identity is clear: the same address as Millstone Care of Sandusky.
- The direction of ownership is **inferred**, from absence on the website plus the Millstone account. It is not stated anywhere.
- Financial exposure: a protected account with $130,000 revenue and $5,200 open AR.
- The proposed write leaves the old account untouched apart from the link, which matches the SOP. But a wrong link would assert a sale that may not have happened.
- **Do not approve without confirmation of the Millstone transaction.**

**Identity holds (#36, #38, #53).**
- No CRM operation exists for these. The only action is a local `./bh resolve` decision, which writes nothing to the CRM. The next scan then turns it into normal proposals, each needing its own approval.
- Amberly Manor (#36) is the strongest candidate for "distinct", because the CRM's Amberly Manor is out of state, in a state where Bellhaven does not operate.

**Ashtabula billing street (#46).** Identity is certain. The open question is purely about billing policy (Q5).

#### #41 · DUPLICATE · Duplicate: Cedar Trail of Monroe (0011AB44D05WLA9HTX) → Bellhaven Gardens of Monroe (001U1750VLVJAGG1S5)
- **Recommendation: HOLD**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** A $0 Cedar Trail-branded record at Monroe's address. Predecessor-operator record or accidental duplicate? See business question Q1. The user has already kept it unapproved.
- **Website:** Bellhaven Gardens of Monroe · 750 Stewart Rd, Monroe MI 48162 · (814) 412-2218 · admin Phil Mabry · `/communities/bellhaven-gardens-of-monroe`
- **CRM (live GET):** `0011AB44D05WLA9HTX` Cedar Trail of Monroe · 750 Stewart Road, Monroe MI 48162 · (216) 748-7799 · parent Cedar Trail Communities · $0 / AR $0<br>`001U1750VLVJAGG1S5` Bellhaven Gardens of Monroe · 750 Stewart Rd, Monroe MI 48162 · (814) 412-2218 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/0011AB44D05WLA9HTX {"duplicate_of_account": "001U1750VLVJAGG1S5", "status": "Inactive", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #41 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/41`

#### #42 · DUPLICATE · Duplicate: Monroe Gardens Care Center (00159PL81N38KM4FHM) → Bellhaven Gardens of Monroe (001U1750VLVJAGG1S5)
- **Recommendation: HOLD**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** A $0 Harborview-branded record at Monroe's address. The same question as #41 (Q1).
- **Website:** Bellhaven Gardens of Monroe · 750 Stewart Rd, Monroe MI 48162 · (814) 412-2218 · admin Phil Mabry · `/communities/bellhaven-gardens-of-monroe`
- **CRM (live GET):** `00159PL81N38KM4FHM` Monroe Gardens Care Center · 750 Stewart Rd, Monroe MI 48162 · (330) 501-4496 · parent Harborview Care Group · $0 / AR $0<br>`001U1750VLVJAGG1S5` Bellhaven Gardens of Monroe · 750 Stewart Rd, Monroe MI 48162 · (814) 412-2218 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/00159PL81N38KM4FHM {"duplicate_of_account": "001U1750VLVJAGG1S5", "status": "Inactive", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #42 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/42`

#### #57 · DUPLICATE · Duplicate: Harborview Nursing & Rehab of Port Clinton (001JD2MWRA74LTSN24) → Bellhaven of Port Clinton (001UELXDAKFRKB8932)
- **Recommendation: HOLD**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** A $0 Harborview-branded record at Port Clinton's address. The same pattern and the same unanswered question as Monroe (Q1). Approving it while Monroe is held would decide Q1 inconsistently. #58, the phone fix on the survivor, does not depend on it.
- **Website:** Bellhaven of Port Clinton · 1420 Harbor Point Dr, Port Clinton OH 43452 · (330) 733-6423 · admin Brenda Whitfield · `/communities/bellhaven-of-port-clinton`
- **CRM (live GET):** `001JD2MWRA74LTSN24` Harborview Nursing & Rehab of Port Clinton · 1420 Harbor Point Drive, Port Clinton OH 43452 · (216) 314-1338 · parent Harborview Care Group · $0 / AR $0<br>`001UELXDAKFRKB8932` Bellhaven of Port Clinton · 1420 Harbor Point Dr, Port Clinton OH 43452 · (614) 512-8712 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001JD2MWRA74LTSN24 {"duplicate_of_account": "001UELXDAKFRKB8932", "status": "Inactive", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #57 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/57`

#### #64 · DUPLICATE · Duplicate: Harborview Shores of Erie (001BLYF02K97SZLZHH) → Bellhaven Shores of Erie (001CVBBCSDM7YHN220)
- **Recommendation: HOLD**. Engine rating: risk high, confidence high. Live drift: none
- **Why:** A $0 Harborview-branded record at Erie's address. Same as #57 (Q1). #65 does not depend on it.
- **Website:** Bellhaven Shores of Erie · 4930 W Lake Rd, Erie PA 16505 · (614) 792-9343 · admin Angela Quinn · `/communities/bellhaven-shores-of-erie`
- **CRM (live GET):** `001BLYF02K97SZLZHH` Harborview Shores of Erie · 4930 West Lake Road, Erie PA 16505 · (517) 775-8456 · parent Harborview Care Group · $0 / AR $0<br>`001CVBBCSDM7YHN220` Bellhaven Shores of Erie · 4930 W Lake Rd, Erie PA 16505 · (419) 495-1741 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001BLYF02K97SZLZHH {"duplicate_of_account": "001CVBBCSDM7YHN220", "status": "Inactive", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #64 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/64`

#### #53 · HOLD · HOLD — 3 indistinguishable accounts: Bellhaven of Kettering
- **Recommendation: HOLD (keep)**. Engine rating: risk hold, confidence low. Live drift: none
- **Why:** Three $0 accounts at Kettering's address: Harborview, Cedar Trail, and one with **no parent**. None is Bellhaven-parented, no phone matches, and there are no contacts. Picking a survivor would be a guess (Q2). Until resolved, the Bellhaven website community has no correctly parented CRM account.
- **Website:** Bellhaven of Kettering · 3313 Wilmington Pike, Kettering OH 45429 · (231) 269-5449 · admin Priya Ashby · `/communities/bellhaven-of-kettering`
- **CRM (live GET):** `001WR41PYNWXCAE2X4` Kettering Care Centre · 3313 Wilmington Pike, Kettering OH 45429 · (419) 600-2603 · parent Harborview Care Group · $0 / AR $0<br>`001B7XZAA3AFALS9GP` Kettering Senior Campus · 3313 Wilmington Pk, Kettering OH 45429 · (517) 646-8751 · parent Cedar Trail Communities · $0 / AR $0<br>`0016KTS1UAWBRXS09J` Kettering Nursing & Rehabilitation · 3313 Wilmington Pike, Kettering OH 45429 · (216) 345-3441 · parent (none) · $0 / AR $0
- **Operation:** none (HOLD: no CRM operation)
- **Sources:** ledger proposal #53 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/53`

#### #36 · HOLD · HOLD — same name, different address: Amberly Manor
- **Recommendation: Resolve as DISTINCT (user decision via `./bh resolve`)**. Engine rating: risk hold, confidence low. Live drift: none
- **Why:** The only 'Amberly Manor' in the CRM is in Colorado Springs CO under Juniper Point. Bellhaven operates in OH, MI, IN and PA only (About page). The phone differs; no Hudson OH account exists. The evidence strongly favours two different facilities. That means **Bellhaven's Hudson community is missing from the CRM**. Resolving it as distinct makes the next scan propose a create, which then needs its own approval (Q4).
- **Website:** Amberly Manor · 4390 Darrow Rd, Hudson OH 44236 · (330) 228-4392 · admin Tom Trent · `/communities/amberly-manor`
- **CRM (live GET):** — (new account)
- **Operation:** none (HOLD: no CRM operation)
- **Sources:** ledger proposal #36 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/36`

#### #38 · HOLD · HOLD — identity unresolved: Bellhaven at Union Square
- **Recommendation: Investigate, leaning DISTINCT**. Engine rating: risk hold, confidence low. Live drift: none
- **Why:** 'Union Square Senior Living' (Juniper Point) is at 240 Market St in the same city, with a different street, phone and parent. It may be a separate facility or a mailing address. Same-city ambiguity is higher than Amberly's, so confirm before resolving (Q4). Until then, Bellhaven's New Albany community has no CRM account.
- **Website:** Bellhaven at Union Square · 118 Union Square Dr, New Albany OH 43054 · (330) 519-9639 · admin Phil Holloway · `/communities/bellhaven-at-union-square`
- **CRM (live GET):** — (new account)
- **Operation:** none (HOLD: no CRM operation)
- **Sources:** ledger proposal #38 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/38`

#### #70 · CHOW · CHOW link: Bellhaven of Sandusky → Millstone Care of Sandusky (Millstone Health Partners (Parent Account))
- **Recommendation: HOLD**. Engine rating: risk high, confidence medium. Live drift: none
- **Why:** Speculative CHOW link. Bellhaven of Sandusky ($130,000 revenue, **$5,200 AR open**) is not on the website, and a $0 Millstone account sits at the same address. Millstone is **not** mentioned on the About page. A sale away from Bellhaven is inferred only from absence. A wrong link would misdirect AR collection history (Q3).
- **Website:** — (not on the website)
- **CRM (live GET):** `001SXSF4ELF0Z2LGDM` Bellhaven of Sandusky · 2715 Columbus Ave, Sandusky OH 44870 · (260) 212-1086 · parent Bellhaven Senior Living · $130,000 / AR $5,200<br>`0017JP8Z1UQ763BVK3` Millstone Care of Sandusky · 2715 Columbus Ave, Sandusky OH 44870 · (614) 307-3608 · parent Millstone Health Partners · $0 / AR $0
- **Operation:** PATCH /accounts/001SXSF4ELF0Z2LGDM {"chow_current_account": "0017JP8Z1UQ763BVK3"}
- **Sources:** ledger proposal #70 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/70`

#### #46 · FIELD_UPDATE · Update billing_street: Bellhaven of Ashtabula
- **Recommendation: HOLD**. Engine rating: risk medium, confidence medium. Live drift: none
- **Why:** The CRM's only address field is `billing_street`, and it holds `PO Box 517`. Name, phone, ZIP and administrator all match, so identity is certain. But replacing a PO Box in the **billing** address could break invoice delivery. It needs a billing or finance decision (Q5), not more matching.
- **Website:** Bellhaven of Ashtabula · 3156 W Prospect Rd, Ashtabula OH 44004 · (260) 440-4975 · admin Ned Green · `/communities/bellhaven-of-ashtabula`
- **CRM (live GET):** `001NXP9X46CWEPSLSV` Bellhaven of Ashtabula · PO Box 517, Ashtabula OH 44004 · (260) 440-4975 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/001NXP9X46CWEPSLSV {"billing_street": "3156 W Prospect Rd"}
- **Sources:** ledger proposal #46 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/46`

## 6. NOT RECOMMENDED (2)

#### #68 · CRM_ONLY · Flag for review: Bellhaven Care Center of Alliance not on website
- **Recommendation: REJECT as written**. Engine rating: risk medium, confidence medium. Live drift: none
- **Why:** Sets `status` to 'Needs Review', which is not a value used anywhere in the CRM (121 accounts: 112 Active, 9 Inactive), and the API publishes no enum. That risks a rejected write or breaking downstream reports. The underlying question remains valid (Q6): Alliance is Bellhaven-parented, $0/$0, and absent from the website.
- **Website:** — (not on the website)
- **CRM (live GET):** `00116ETS45BL7DTQP7` Bellhaven Care Center of Alliance · 1785 Freshley Ave, Alliance OH 44601 · (734) 358-4538 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/00116ETS45BL7DTQP7 {"status": "Needs Review", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #68 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/68`

#### #69 · CRM_ONLY · Flag for review: Bellhaven of Coldwater not on website
- **Recommendation: REJECT as written**. Engine rating: risk medium, confidence medium. Live drift: none
- **Why:** Same as #68, for Coldwater MI (Bellhaven parent, $0/$0, absent from the website). Track it as investigation question Q6 instead.
- **Website:** — (not on the website)
- **CRM (live GET):** `0016PVXH4B25HWR7QE` Bellhaven of Coldwater · 90 N Michigan Ave, Coldwater MI 49036 · (814) 581-1138 · parent Bellhaven Senior Living · $0 / AR $0
- **Operation:** PATCH /accounts/0016PVXH4B25HWR7QE {"status": "Needs Review", "note": "\u2026(appended note)"}
- **Sources:** ledger proposal #69 (payload and evidence) · scan #11 snapshot · live `GET /api/v1/accounts/<id>` 2026-11-16 · app page `/proposal/69`

## 7. What still requires the user's explicit approval

- **Every one of the 23 READY items, individually.** Approve on `/proposal/<id>`, run the Live preview, then type `APPLY <id>` (or `APPLY BATCH OF <n>` for a non-CHOW wave).
- **Starting the server with live writes:** `CRM_WRITES_ENABLED=1 ./bh serve --port 8020`. It currently runs in dry-run.
- **Identity resolutions** (`./bh resolve 36|38|53 …`). These are local decisions only, but they are yours to make.
- **Rejecting #68 and #69** in the app, if you agree. Rejecting writes nothing to the CRM.
- Nothing here, and no ChatGPT recommendation, authorizes a write.
