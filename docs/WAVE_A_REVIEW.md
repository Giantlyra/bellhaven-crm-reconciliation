# Wave A Review: 14 field corrections (for the user's decision)

> **Update 2026-11-16 02:23 UTC:** all 14 were tentatively approved in the user–ChatGPT review and then **verified** read-only. See `WAVE_A_FINAL_VALIDATION.md`. None is authorized or executed yet.

_Prepared read-only on 2026-11-16 from a fresh live read of the CRM (121 accounts, 67 contacts), scan #11 and the ledger.
CRM writes are **disabled**: the server on :8020 runs in dry-run. "Ready for approval" is **not** authorization.
Each item is executed only after the user's own decision, individually, with Approve → fresh Live preview → typed `APPLY <id>` → read-back. **No batch execution.**_

Every item writes **one field set on one Bellhaven-parented account**. None changes a parent, status, financials, CHOW link or duplicate link,
and no two items touch the same account. Rejecting or holding any item does not affect the others.

## Decision sheet

| # | Proposal | Account | Change (before → after) | Other accounts at address | Your decision |
|---|---|---|---|---|---|
| 1 | #58 | `001UELXDAKFRKB8932` | Bellhaven of Port Clinton | phone: (614) 512-8712 → **(330) 733-6423** | ⚠ 1 other at address (held) | ☐ Approve ☐ Hold ☐ Reject |
| 2 | #65 | `001CVBBCSDM7YHN220` | Bellhaven Shores of Erie | phone: (419) 495-1741 → **(614) 792-9343** | ⚠ 1 other at address (held) | ☐ Approve ☐ Hold ☐ Reject |
| 3 | #52 | `001JQER1RMYKNRLNME` | Bellhaven of Goshen | phone: (517) 409-8156 → **(330) 405-6040** | none | ☐ Approve ☐ Hold ☐ Reject |
| 4 | #55 | `0015L38R1Z5947ZZP7` | Bellhaven of Marion | phone: (330) 314-3109 → **(517) 847-7948** | none | ☐ Approve ☐ Hold ☐ Reject |
| 5 | #45 | `001UKEFGADQ8YCZ4YM` | Bellhaven Meadows of Findlay | phone: (330) 975-2492 → **(231) 533-2969** | none | ☐ Approve ☐ Hold ☐ Reject |
| 6 | #51 | `001R4PXTUD9R6FNN8V` | Bellhaven of Defiance | phone: (231) 238-4862 → **(330) 691-2711** | none | ☐ Approve ☐ Hold ☐ Reject |
| 7 | #37 | `00191H7JR16471SZ34` | Bellhaven of Sycamore Ridge | name: Bellhaven of Sycamore Ridge → **Bellhaven at Sycamore Ridge**; phone: (419) 982-7764 → **(260) 365-6510** | none | ☐ Approve ☐ Hold ☐ Reject |
| 8 | #44 | `001RJ0D7Z5MAZN5HX5` | Bellhaven Health Care Center of Ashland | name: Bellhaven Health Care Center of Ashland → **Bellhaven Healthcare Centre of Ashland**; phone: (734) 319-7813 → **(517) 314-5115** | none | ☐ Approve ☐ Hold ☐ Reject |
| 9 | #49 | `001RJU1X4NBWC1Q0G7` | Riverbend Manor Care Center | name: Riverbend Manor Care Center → **Bellhaven of Chagrin Falls**; phone: (517) 457-9548 → **(231) 283-7448** | none | ☐ Approve ☐ Hold ☐ Reject |
| 10 | #50 | `0013NUZQHQUEZ8DXEG` | Chesterton Senior Commons | name: Chesterton Senior Commons → **Bellhaven of Chesterton** | none | ☐ Approve ☐ Hold ☐ Reject |
| 11 | #63 | `001TZCSTBZFM6K5BGN` | Bellhaven Rehab and Nursing of Grove City | name: Bellhaven Rehab and Nursing of Grove City → **Bellhaven Rehabilitation & Nursing of Grove City** | none | ☐ Approve ☐ Hold ☐ Reject |
| 12 | #66 | `0017MN2JYAJBDS8WQZ` | Sunny Acres Retirement Home | name: Sunny Acres Retirement Home → **Bellhaven Willow Creek**; phone: (216) 898-7925 → **(419) 394-5494** | none | ☐ Approve ☐ Hold ☐ Reject |
| 13 | #67 | `0010KJFP601YNTZVDA` | Arbors at Bellhaven Dayton | name: Arbors at Bellhaven Dayton → **The Arbors at Bellhaven - Dayton**; phone: (216) 659-9837 → **(260) 254-7592** | none | ☐ Approve ☐ Hold ☐ Reject |
| 14 | #59 | `001CF3LDWVRGL09P4F` | Bellhaven of Portsmouth | billing_zip: 45626 → **45662** | none | ☐ Approve ☐ Hold ☐ Reject |

To decide, reply with the list, e.g. "Approve 58, 65, 52; hold 66". In the app (http://127.0.0.1:8020/proposal/&lt;id&gt;) these items are PENDING.

## Evidence per item

### 1. #58: Bellhaven of Port Clinton (`001UELXDAKFRKB8932`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| phone | (614) 512-8712 | **(330) 733-6423** | (330) 733-6423 |
- **Website evidence:** Bellhaven of Port Clinton · 1420 Harbor Point Dr, Port Clinton OH 43452 · (330) 733-6423 · administrator Brenda Whitfield · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-port-clinton (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name match, phone differs, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ✅ Brenda Whitfield. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001UELXDAKFRKB8932` `{"phone": "(330) 733-6423"}`. No other field is sent.
- **Uncertainty:** Low. The website is the only source for the phone. A Harborview record at the same address is held under #57; it is not changed here.
- **Conflicting CRM candidates:** same address: `001JD2MWRA74LTSN24` Harborview Nursing & Rehab of Port Clinton (Harborview Care Group, (216) 314-1338, $0/$0). Not touched by this item
- **Drift since proposal:** none (live read 2026-11-16)

### 2. #65: Bellhaven Shores of Erie (`001CVBBCSDM7YHN220`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| phone | (419) 495-1741 | **(614) 792-9343** | (614) 792-9343 |
- **Website evidence:** Bellhaven Shores of Erie · 4930 W Lake Rd, Erie PA 16505 · (614) 792-9343 · administrator Angela Quinn · https://analyst-assessment-production.up.railway.app/communities/bellhaven-shores-of-erie (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name match, phone differs, parent Bellhaven Senior Living, care Assisted Living vs Assisted Living, Memory Support, administrator ✅ Angela Quinn. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001CVBBCSDM7YHN220` `{"phone": "(614) 792-9343"}`. No other field is sent.
- **Uncertainty:** Low. The website is the only source for the phone. A Harborview record at the same address is held under #64; it is not changed here.
- **Conflicting CRM candidates:** same address: `001BLYF02K97SZLZHH` Harborview Shores of Erie (Harborview Care Group, (517) 775-8456, $0/$0). Not touched by this item
- **Drift since proposal:** none (live read 2026-11-16)

### 3. #52: Bellhaven of Goshen (`001JQER1RMYKNRLNME`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| phone | (517) 409-8156 | **(330) 405-6040** | (330) 405-6040 |
- **Website evidence:** Bellhaven of Goshen · 1610 College Ave, Goshen IN 46526 · (330) 405-6040 · administrator Tanya Castellano · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-goshen (scan #11, unchanged since #3)
- **Identity match:** street normalized (1610 College Avenue ≈ 1610 College Ave), ZIP match, name match, phone differs, parent Bellhaven Senior Living, care Assisted Living vs Assisted Living, administrator ✅ Tanya Castellano. Financials: $121,000 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001JQER1RMYKNRLNME` `{"phone": "(330) 405-6040"}`. No other field is sent.
- **Uncertainty:** Low. The website is the only source for the phone.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 4. #55: Bellhaven of Marion (`0015L38R1Z5947ZZP7`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| phone | (330) 314-3109 | **(517) 847-7948** | (517) 847-7948 |
- **Website evidence:** Bellhaven of Marion · 199 Barks Rd W, Marion OH 43302 · (517) 847-7948 · administrator Doug Amato · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-marion (scan #11, unchanged since #3)
- **Identity match:** street normalized (199 Barks Road West ≈ 199 Barks Rd W), ZIP match, name match, phone differs, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ✅ Doug Amato. Financials: $87,000 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/0015L38R1Z5947ZZP7` `{"phone": "(517) 847-7948"}`. No other field is sent.
- **Uncertainty:** Low. The website is the only source for the phone.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 5. #45: Bellhaven Meadows of Findlay (`001UKEFGADQ8YCZ4YM`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| phone | (330) 975-2492 | **(231) 533-2969** | (231) 533-2969 |
- **Website evidence:** Bellhaven Meadows of Findlay · 1800 N Blanchard St, Findlay OH 45840 · (231) 533-2969 · administrator Sam Pruitt · https://analyst-assessment-production.up.railway.app/communities/bellhaven-meadows-of-findlay (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name match, phone differs, parent Bellhaven Senior Living, care Assisted Living vs Assisted Living, Memory Support, administrator ✅ Sam Pruitt. Financials: $22,000 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001UKEFGADQ8YCZ4YM` `{"phone": "(231) 533-2969"}`. No other field is sent.
- **Uncertainty:** Low. This is the account with the legacy Findlay parent write; only the phone changes here. Findlay is linked only from the homepage.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 6. #51: Bellhaven of Defiance (`001R4PXTUD9R6FNN8V`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| phone | (231) 238-4862 | **(330) 691-2711** | (330) 691-2711 |
- **Website evidence:** Bellhaven of Defiance · 700 Carpenter Rd, Defiance OH 43512 · (330) 691-2711 · administrator Victor Barros · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-defiance (scan #11, unchanged since #3)
- **Identity match:** street normalized (700 Carpenter Road ≈ 700 Carpenter Rd), ZIP match, name match, phone differs, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ✅ Victor Barros. Financials: $66,000 / AR $9,500, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001R4PXTUD9R6FNN8V` `{"phone": "(330) 691-2711"}`. No other field is sent.
- **Uncertainty:** Low. The website is the only source for the phone. The account has $9,500 AR, but a phone change engages no SOP rule.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 7. #37: Bellhaven of Sycamore Ridge (`00191H7JR16471SZ34`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Bellhaven of Sycamore Ridge | **Bellhaven at Sycamore Ridge** | Bellhaven at Sycamore Ridge |
| phone | (419) 982-7764 | **(260) 365-6510** | (260) 365-6510 |
- **Website evidence:** Bellhaven at Sycamore Ridge · 7420 Sycamore Ridge Dr, Miamisburg OH 45342 · (260) 365-6510 · administrator Tom Bloom · https://analyst-assessment-production.up.railway.app/communities/bellhaven-at-sycamore-ridge (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name differs, phone differs, parent Bellhaven Senior Living, care Assisted Living vs Assisted Living, administrator ❌ website Tom Bloom vs CRM Ingrid Pruitt, Sofia Castellano. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/00191H7JR16471SZ34` `{"name": "Bellhaven at Sycamore Ridge", "phone": "(260) 365-6510"}`. No other field is sent.
- **Uncertainty:** Low–medium. A small name change ('of' → 'at') plus the phone. The CRM administrator contact (Sofia Castellano) ≠ the website (Tom Bloom); contacts are out of scope.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 8. #44: Bellhaven Health Care Center of Ashland (`001RJ0D7Z5MAZN5HX5`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Bellhaven Health Care Center of Ashland | **Bellhaven Healthcare Centre of Ashland** | Bellhaven Healthcare Centre of Ashland |
| phone | (734) 319-7813 | **(517) 314-5115** | (517) 314-5115 |
- **Website evidence:** Bellhaven Healthcare Centre of Ashland · 1631 Claremont Ave, Ashland OH 44805 · (517) 314-5115 · administrator Carla Okafor · https://analyst-assessment-production.up.railway.app/communities/bellhaven-healthcare-centre-of-ashland (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name differs, phone differs, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ✅ Carla Okafor. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001RJ0D7Z5MAZN5HX5` `{"name": "Bellhaven Healthcare Centre of Ashland", "phone": "(517) 314-5115"}`. No other field is sent.
- **Uncertainty:** Low. A spelling normalization ('Health Care Center' → 'Healthcare Centre') plus the phone.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 9. #49: Riverbend Manor Care Center (`001RJU1X4NBWC1Q0G7`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Riverbend Manor Care Center | **Bellhaven of Chagrin Falls** | Bellhaven of Chagrin Falls |
| phone | (517) 457-9548 | **(231) 283-7448** | (231) 283-7448 |
- **Website evidence:** Bellhaven of Chagrin Falls · 150 River St, Chagrin Falls OH 44022 · (231) 283-7448 · administrator Dale Mabry · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-chagrin-falls (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name differs, phone differs, parent Bellhaven Senior Living, care Assisted Living vs Assisted Living, administrator ✅ Dale Mabry. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001RJU1X4NBWC1Q0G7` `{"name": "Bellhaven of Chagrin Falls", "phone": "(231) 283-7448"}`. No other field is sent.
- **Uncertainty:** Medium. A material rename (Riverbend Manor Care Center → Bellhaven of Chagrin Falls). It is supported by the exact address, the Bellhaven parent and the administrator contact.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 10. #50: Chesterton Senior Commons (`0013NUZQHQUEZ8DXEG`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Chesterton Senior Commons | **Bellhaven of Chesterton** | Bellhaven of Chesterton |
- **Website evidence:** Bellhaven of Chesterton · 1250 NW Franklin Street, Chesterton IN 46304 · (216) 551-3978 · administrator Karen Reyes · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-chesterton (scan #11, unchanged since #3)
- **Identity match:** street normalized (1250 Northwest Franklin St ≈ 1250 NW Franklin Street), ZIP match, name differs, phone match, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ✅ Karen Reyes. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/0013NUZQHQUEZ8DXEG` `{"name": "Bellhaven of Chesterton"}`. No other field is sent.
- **Uncertainty:** Low. A material rename, but the phone **already matches** the website and the administrator contact matches.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 11. #63: Bellhaven Rehab and Nursing of Grove City (`001TZCSTBZFM6K5BGN`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Bellhaven Rehab and Nursing of Grove City | **Bellhaven Rehabilitation & Nursing of Grove City** | Bellhaven Rehabilitation & Nursing of Grove City |
- **Website evidence:** Bellhaven Rehabilitation & Nursing of Grove City · 3985 Broadway, Grove City OH 43123 · (614) 555-7729 · administrator Marie Vogel · https://analyst-assessment-production.up.railway.app/communities/bellhaven-rehabilitation-nursing-of-grove-city (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name differs, phone match, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ❌ website Marie Vogel vs CRM Janet Krueger. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001TZCSTBZFM6K5BGN` `{"name": "Bellhaven Rehabilitation & Nursing of Grove City"}`. No other field is sent.
- **Uncertainty:** Low. Name formatting only ('Rehab and' → 'Rehabilitation &'). The phone already matches.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 12. #66: Sunny Acres Retirement Home (`0017MN2JYAJBDS8WQZ`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Sunny Acres Retirement Home | **Bellhaven Willow Creek** | Bellhaven Willow Creek |
| phone | (216) 898-7925 | **(419) 394-5494** | (419) 394-5494 |
- **Website evidence:** Bellhaven Willow Creek · 8060 Willow Creek Ln, Portage MI 49024 · (419) 394-5494 · administrator Walt Mabry · https://analyst-assessment-production.up.railway.app/communities/bellhaven-willow-creek (scan #11, unchanged since #3)
- **Identity match:** street normalized (8060 Willow Creek Lane ≈ 8060 Willow Creek Ln), ZIP match, name differs, phone differs, parent Bellhaven Senior Living, care Memory Care vs Memory Support, administrator — no CRM contacts. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/0017MN2JYAJBDS8WQZ` `{"name": "Bellhaven Willow Creek", "phone": "(419) 394-5494"}`. No other field is sent.
- **Uncertainty:** Medium. A material rename (Sunny Acres Retirement Home → Bellhaven Willow Creek). There are no CRM contacts to corroborate it; identity rests on the exact address, the Bellhaven parent and the matching care type (Memory).
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 13. #67: Arbors at Bellhaven Dayton (`0010KJFP601YNTZVDA`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| name | Arbors at Bellhaven Dayton | **The Arbors at Bellhaven - Dayton** | The Arbors at Bellhaven - Dayton |
| phone | (216) 659-9837 | **(260) 254-7592** | (260) 254-7592 |
- **Website evidence:** The Arbors at Bellhaven - Dayton · 2210 Salem Ave, Dayton OH 45406 · (260) 254-7592 · administrator Ray Novak · https://analyst-assessment-production.up.railway.app/communities/the-arbors-at-bellhaven-dayton (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP match, name differs, phone differs, parent Bellhaven Senior Living, care Memory Care vs Memory Support, administrator ✅ Ray Novak. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/0010KJFP601YNTZVDA` `{"name": "The Arbors at Bellhaven - Dayton", "phone": "(260) 254-7592"}`. No other field is sent.
- **Uncertainty:** Low. Punctuation in the name ('The', ' - ') plus the phone.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

### 14. #59: Bellhaven of Portsmouth (`001CF3LDWVRGL09P4F`)
| Field | CRM now (live) | Proposed | Website |
|---|---|---|---|
| billing_zip | 45626 | **45662** | 45662 |
- **Website evidence:** Bellhaven of Portsmouth · 2222 Gallia St, Portsmouth OH 45662 · (330) 431-2495 · administrator Tanya Quinn · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-portsmouth (scan #11, unchanged since #3)
- **Identity match:** street exact, ZIP DIFFERS (45626 vs 45662), name match, phone match, parent Bellhaven Senior Living, care Skilled Nursing vs Short-Term Rehabilitation & Nursing, administrator ✅ Tanya Quinn. Financials: $0 / AR $0, not changed.
- **Exact operation:** `PATCH /api/v1/accounts/001CF3LDWVRGL09P4F` `{"billing_zip": "45662"}`. No other field is sent.
- **Uncertainty:** Low. The ZIP digits are transposed (45626 → 45662). The phone and administrator already match, and 45662 is Portsmouth OH.
- **Conflicting CRM candidates:** none (no other account at the address, ZIP or city, and neither phone is used elsewhere)
- **Drift since proposal:** none (live read 2026-11-16)

## Not part of Wave A (preserved, no CRM changes)
- Needs investigation: #41, #42, #57, #64, #53, #36, #38, #70, #46
- Not recommended: #68, #69

## Execution protocol after the user's decisions
1. The user restarts with writes enabled: `CRM_WRITES_ENABLED=1 ./bh serve --port 8020`.
2. For **one** authorized item at a time: Approve → Live preview, where Claude Code checks the preview body is exactly the operation above → user types `APPLY <id>`.
3. Claude Code does an independent live GET read-back and records the ledger receipt (decision, operation and audit ids) in `ASSESSMENT_HANDOFF.md` and `docs/CRM_CHANGE_HISTORY.md`.
4. Repeat for the next item, then restart in dry-run.
