# Wave A Final Validation Report

_Read-only verification completed 2026-11-16T02:23:11Z by Claude Code. **CRM writes: DISABLED.** The server on :8020 (PID 76147) runs in dry-run, with no `CRM_WRITES_ENABLED` in its environment._

The 14 tentative approvals in this report came from the user's conversation with ChatGPT. **They are not authorizations.**
- "Verified" below means the proposal passed technical and evidence checks and is ready for **individual** in-app authorization.
- Nothing has been approved in the app, and nothing has been written.
- Wave A authorizes nothing outside these 14 proposals.

## Result

| Status | Count |
|---|---|
| ✅ Verified, ready for individual authorization | **14** |
| ⏸ Held for investigation | 0 |
| ✖ Rejected or revised | 0 |

## Checks applied to all 14
1. **Register vs ledger vs CRM:** every account ID in the PRD equals the proposal's single target account. Every PRD before-value equals the live CRM value. Every PRD after-value equals the ledger operation. The field sets are identical, with no extra fields.
2. **Drift:** the live CRM equals each proposal's baseline (parent, financials, status, CHOW and duplicate links, name, address, phone). Every account's `updated_at` is unchanged since the original seed, except Findlay's, which is the legacy parent write at 2026-11-15 10:14:01Z.
3. **Website re-fetched live, not from the snapshot:** every proposed value is still published, and no website address changed since the proposal.
4. **Competing records:** no other account shares the address, ZIP, city or either phone number, except the two held Harborview records (Port Clinton, Erie), which are not touched.
5. **Scope:** each operation is one `PATCH` on one Bellhaven-parented account with only the listed fields. None touches a parent, status, revenue, AR, CHOW link, duplicate link, note or contact.
6. **Pre-execution snapshot:** the full live record and contacts for all 14 accounts are saved to `data/wave_a_pre_execution_snapshot.json`. After each write, Claude Code diffs every field against it, so protected fields are proven unchanged rather than assumed.

## Verified proposals (recommended order for separate, individual authorization)

| Order | Proposal | Account | Exact change (live before → after) | Status | Protection / note |
|---|---|---|---|---|---|
| 1 | #58 Port Clinton | `001UELXDAKFRKB8932` | phone: (614) 512-8712 → **(330) 733-6423** | ✅ VERIFIED | The Harborview record at the same address (`001JD2MWRA74LTSN24`, held as #57) is not touched. |
| 2 | #65 Erie | `001CVBBCSDM7YHN220` | phone: (419) 495-1741 → **(614) 792-9343** | ✅ VERIFIED | The Harborview record at the same address (`001BLYF02K97SZLZHH`, held as #64) is not touched. |
| 3 | #52 Goshen | `001JQER1RMYKNRLNME` | phone: (517) 409-8156 → **(330) 405-6040** | ✅ VERIFIED | Revenue $121,000 / AR $0 unaffected. |
| 4 | #55 Marion | `0015L38R1Z5947ZZP7` | phone: (330) 314-3109 → **(517) 847-7948** | ✅ VERIFIED | Revenue $87,000 / AR $0 unaffected. |
| 5 | #45 Findlay | `001UKEFGADQ8YCZ4YM` | phone: (330) 975-2492 → **(231) 533-2969** | ✅ VERIFIED | The verified legacy `parent_id` = Bellhaven is not in the request and stays as is. |
| 6 | #51 Defiance | `001R4PXTUD9R6FNN8V` | phone: (231) 238-4862 → **(330) 691-2711** | ✅ VERIFIED | **AR $9,500** and revenue $66,000 are not in the request and stay as is. |
| 7 | #44 Ashland | `001RJ0D7Z5MAZN5HX5` | name: Bellhaven Health Care Center of Ashland → **Bellhaven Healthcare Centre of Ashland**; phone: (734) 319-7813 → **(517) 314-5115** | ✅ VERIFIED | The administrator contact Carla Okafor matches the website. |
| 8 | #63 Grove City | `001TZCSTBZFM6K5BGN` | name: Bellhaven Rehab and Nursing of Grove City → **Bellhaven Rehabilitation & Nursing of Grove City** | ✅ VERIFIED | The phone already matches; the contact (Janet Krueger, DON) is not touched. |
| 9 | #67 Dayton | `0010KJFP601YNTZVDA` | name: Arbors at Bellhaven Dayton → **The Arbors at Bellhaven - Dayton**; phone: (216) 659-9837 → **(260) 254-7592** | ✅ VERIFIED | The administrator contact Ray Novak matches the website. |
| 10 | #37 Sycamore Ridge | `00191H7JR16471SZ34` | name: Bellhaven of Sycamore Ridge → **Bellhaven at Sycamore Ridge**; phone: (419) 982-7764 → **(260) 365-6510** | ✅ VERIFIED | Contacts (Ingrid Pruitt, Sofia Castellano) are not touched; an account PATCH does not affect contacts. |
| 11 | #50 Chesterton | `0013NUZQHQUEZ8DXEG` | name: Chesterton Senior Commons → **Bellhaven of Chesterton** | ✅ VERIFIED | The phone already matches the website; only the name changes. |
| 12 | #59 Portsmouth | `001CF3LDWVRGL09P4F` | billing_zip: 45626 → **45662** | ✅ VERIFIED | Conditional check ★, see below. |
| 13 | #49 Chagrin Falls | `001RJU1X4NBWC1Q0G7` | name: Riverbend Manor Care Center → **Bellhaven of Chagrin Falls**; phone: (517) 457-9548 → **(231) 283-7448** | ✅ VERIFIED | Conditional check ★, see below. |
| 14 | #66 Willow Creek | `0017MN2JYAJBDS8WQZ` | name: Sunny Acres Retirement Home → **Bellhaven Willow Creek**; phone: (216) 898-7925 → **(419) 394-5494** | ✅ VERIFIED | Conditional check ★, see below. |

The order runs from simplest to most nuanced: phone-only items first, then name normalizations, then the three conditional items. Each item is still authorized, previewed, confirmed and read back on its own. No batching.

## ★ Conditional checks

### #49 Chagrin Falls (`001RJU1X4NBWC1Q0G7`): Riverbend Manor Care Center → Bellhaven of Chagrin Falls. **VERIFIED: a rebrand of a facility the CRM already records under Bellhaven.**
- **Identity:**
  - This is the only CRM account in ZIP 44022 or in Chagrin Falls.
  - "Riverbend" appears on no other account.
  - The street is exact: 150 River St.
  - Care type matches (Assisted Living).
  - The administrator contact (Dale Mabry) matches the website.
  - The old phone, (517) 457-9548, is used nowhere else.
- **Ownership:** both sources agree that the **current** owner is Bellhaven: the CRM parent is already Bellhaven, and the website lists it under Bellhaven. No CHOW link, duplicate link or note records an earlier owner, and the About page does not mention Riverbend. So we **cannot prove** whether "Riverbend Manor" was an earlier operator or just an earlier name. But nothing **contradicts** the current ownership.
- **Why that does not block this write:**
  - Only `name` and `phone` change. Ownership fields (`parent_id`) are untouched.
  - The account has $0 revenue and $0 AR. If an ownership change ever happened, there is no billing history the CHOW SOP would protect; that applies only when revenue > 0 and AR > 0.
- **Residual:** if the business requires prior ownership to be documented before renaming, hold this item. The evidence does not support classifying it as an ownership transition.

### #66 Willow Creek (`0017MN2JYAJBDS8WQZ`): Sunny Acres Retirement Home → Bellhaven Willow Creek. **VERIFIED, with the lowest corroboration in Wave A.**
- **Identity:**
  - This is the only CRM account in ZIP 49024 or in Portage.
  - "Sunny Acres" appears on no other account.
  - The street number and street are exact: 8060 Willow Creek Lane/Ln.
  - The new name matches the street the building is on.
  - Care type matches and is distinctive: memory-only. Only 2 of 35 website communities are memory-only.
  - The old phone is used nowhere else.
- **Missing:** no CRM contacts at all, so the administrator (Walt Mabry) cannot be cross-checked.
- **Ownership:** same as #49. The current owner is Bellhaven in both sources, and nothing records an earlier owner. The account has $0/$0, and only `name` and `phone` change.
- **Residual:** identity rests on a unique exact address plus care type, not on a person. If a human confirmation such as a call or the regional director is required, hold this item.

### #59 Portsmouth (`001CF3LDWVRGL09P4F`): billing_zip 45626 → 45662. **VERIFIED: the existing billing ZIP is not independently valid.**
- **The CRM has a single address**, the `billing_*` fields; there is no separate physical address. Its billing street `2222 Gallia St, Portsmouth OH` is **identical to the facility's street**. So this is not a separate invoice mailing address, unlike Ashtabula's PO Box (#46, held).
- **Is 45626 valid?**
  - Public ZIP references list only **45662 and 45663** for Portsmouth OH, both standard street ZIPs with no PO-box ZIP. Sources: [zip-codes.com, Portsmouth OH](https://www.zip-codes.com/city/oh-portsmouth.asp) and [uszip.com, 45662](https://www.uszip.com/zip/45662).
  - Gallia St addresses near 2222 (2201, 2624) are in 45662.
  - No reference to **45626** as a ZIP code could be found: zip-codes.com returns 404 for it.
- **Other corroboration:** the phone and administrator already match the website, and the contact's email domain is `bellhavenliving.com`. 45662 is the transposition of 45626.
- **Residual:** the ZIP lists come from public third-party sources, not a USPS API call. The current value is very likely a typo, and the correction makes the billing address internally consistent.

## Differences between the original proposals and fresh data
**None.** All 14 are byte-for-byte unchanged in the ledger, CRM and website since scan #3. Ledger status is PENDING for all 14, with no approvals recorded.

## Newly discovered risks
1. **The app's read-back checks only the fields it wrote.** Mitigation: Claude Code's independent full-record diff against the pre-execution snapshot, described above. No code change needed.
2. **Name changes affect search and reporting.** For #49, #50 and #66 the old names disappear from the CRM. Nothing preserves them unless a note is added, and the proposals send no note. **Business decision:** is losing the old name acceptable? The account ID is unchanged.
3. **No new conflicts, drift or website changes were found.**

## What still requires the user
For **each** item, individually: a decision in chat, then the in-app **Approve**, a **fresh Live preview** (Claude Code checks the request body equals the "Exact change" column), and the typed **`APPLY <id>`**.
- The server must first be restarted with `CRM_WRITES_ENABLED=1 ./bh serve --port 8020`.
- Afterwards it goes back to dry-run.
- No batch confirmation will be used.

## Execution log (individual authorizations only)

| Proposal | Authorized | Executed (UTC) | Ledger receipt | Independent read-back |
|---|---|---|---|---|
| #58 Port Clinton | user, in chat + in-app Approve + `APPLY 58` | 2026-11-16 02:47:11 | decisions #3–4 · op #2 · audit #100–109 · token `0db421a1…` | ✅ only `phone` (+`updated_at`) changed; contacts and the Harborview account untouched |
| #65 Erie | user, in chat + in-app Approve + `APPLY 65` | 2026-11-16 02:52:27 | decisions #5–6 · op #3 · audit #110–119 · token `2739c348…` | ✅ only `phone` (+`updated_at`) changed; contacts and the Harborview account untouched |
| #52 Goshen | user, in chat + in-app Approve + `APPLY 52` | 2026-11-16 02:58:21 | decisions #7–8 · op #4 · audit #120–131 · token `07996dc1…` | ✅ only `phone` (+`updated_at`) changed; $121,000 / AR $0 and contacts untouched. Earlier dry-run refusal at audit #123 |
| #55 Marion | user, in chat + in-app Approve + `APPLY 55` | 2026-11-16 03:00:50 | decisions #9–10 · op #5 · audit #132–141 · token `78c5e0ed…` | ✅ only `phone` (+`updated_at`) changed; $87,000 / AR $0 and contacts untouched |
| #45 Findlay | user, in-app Approve + `APPLY 45` | 2026-11-16 03:05:33 | decisions #11–12 · op #6 · audit #142–155 · token `5edfe566…` | ✅ only `phone` (+`updated_at`) changed; `parent_id` still Bellhaven; $22,000 / AR $0 and contacts untouched. Earlier dry-run refusals at audit #145/#147 |
