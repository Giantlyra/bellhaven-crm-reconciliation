# Ambiguous records: investigation questions

> **PRE-EXECUTION SNAPSHOT (2026-11-15).** Kept unchanged as historical evidence. The questions remain valid. Their current status is in the final report §5. **Final, authoritative outcome:** [FINAL_AUDIT.md](FINAL_AUDIT.md) · [FINAL_RECONCILIATION_REPORT.md](FINAL_RECONCILIATION_REPORT.md).

Source: live read-only scan **#9** (2026-11-15 22:51 UTC; 35 website facilities, 121 CRM accounts, CRM fingerprint
`5daed874…`). Bellhaven parent = `0015QAPLGS3FVYEEEM`.

The tool does not approve, reject, create or update any of these records. Seven cases need a human answer:

- **Three identity holds** (#36, #38, #53) have no operations at all.
- **Four proposals** (#70, #46, #68, #69) have operations, but the evidence for them is not strong enough. I recommend holding them.

How a held case gets unblocked:

1. Answer the questions for the case.
2. Record the outcome:
   - for an identity hold: `./bh resolve <hold#> distinct|survivor <account_id> --note "..."`, or keep it held
   - for a proposal: Hold or Reject it in the UI
3. Run the next scan. It turns a recorded resolution into ordinary **pending** proposals.
4. Those proposals still need approval, a live preview and a typed confirmation before anything is written.

| # | Case | Recommended status |
|---|---|---|
| 36 | Amberly Manor | **INVESTIGATE** (leaning: distinct facility) |
| 38 | Bellhaven at Union Square | **INVESTIGATE** (leaning: distinct facility) |
| 53 | Bellhaven of Kettering (3 CRM accounts) | **HOLD** |
| 70 | Sandusky CHOW link to Millstone | **INVESTIGATE** (do not approve yet) |
| 46 | Ashtabula billing street (PO Box) | **HOLD** pending a finance answer |
| 68, 69 | Alliance / Coldwater status "Needs Review" | **HOLD**; no write unless the status value is valid |

---

## #36 Amberly Manor (HOLD, no operations)

**Website facility.** Amberly Manor, 4390 Darrow Rd, Hudson **OH** 44236, (330) 228-4392. Administrator Tom Trent; Assisted Living.
Source: `/communities/amberly-manor`.

**Candidate CRM account.** `0015D74ZLRY810RGY5` Amberly Manor:

- 918 S Nevada Ave, Colorado Springs **CO** 80903, (734) 358-9267
- parent Juniper Point Healthcare; Active; $0 revenue / $0 AR
- contact Ned Duval (verified with a read-only contacts GET)

**Supporting evidence (same facility).** The name is identical, and the care type is the same (Assisted Living).

**Conflicting evidence.**

- Different state and street.
- Different phone.
- Different administrator or contact.
- The parent is Juniper Point, which the About page does not mention as an acquisition.
- No other CRM account exists at 4390 Darrow Rd or ZIP 44236.

**Missing information.** Whether the Colorado record was ever meant to represent the Hudson building, for example as a data-entry error, or is a separate Juniper Point community.

**Questions for the reviewer.**

1. Is the Colorado Springs Amberly Manor a real, separate community?
2. Should Bellhaven's Hudson, OH community get its own CRM account?
3. Is there any internal record (contracts, shifts, invoices) tied to `0015D74ZLRY810RGY5` for a Hudson, OH location?

**Consequences of each resolution.**

- **Distinct** (`./bh resolve 36 distinct`): the next scan proposes `POST /accounts` for Amberly Manor:
  - 4390 Darrow Rd, Hudson OH 44236, (330) 228-4392, Assisted Living, parent Bellhaven
  - the Colorado account is untouched
  - risk: if the CO record really was the Hudson facility, Bellhaven ends up with two accounts for one building, though no money is involved ($0 / $0)
- **Same facility**: correct the CO record's address, phone and parent instead. That needs evidence the tool doesn't have, and it would overwrite a record that looks valid.
- **Keep holding**: Bellhaven's Hudson community stays missing from the CRM.

---

## #38 Bellhaven at Union Square (HOLD, no operations)

**Website facility.** Bellhaven at Union Square, 118 Union Square Dr, New Albany OH 43054, (330) 519-9639. Administrator Phil Holloway; Assisted Living.

**Candidate CRM account.** `001GNU41AVXZRLLJ9P` Union Square Senior Living:

- 240 Market St, New Albany OH 43054, (260) 782-4620
- parent Juniper Point Healthcare; Active; $0 / $0
- contact Dale Croft

**Supporting evidence.** The same city and ZIP, and "Union Square" appears in both names. Same care type.

**Conflicting evidence.**

- Different street, phone and administrator.
- The About page names Harborview (2025) and "select communities" from Cedar Trail (2026) as acquisitions. Juniper Point isn't mentioned.

**Missing information.** Whether Juniper Point sold a Union Square community to Bellhaven, and whether 240 Market St and 118 Union Square Dr are two entrances of one campus.

**Questions for the reviewer.**

1. Are 240 Market St and 118 Union Square Dr the same building or campus?
2. Did Bellhaven acquire anything from Juniper Point?
3. Does `001GNU41AVXZRLLJ9P` have billing activity elsewhere that would make it CHOW-protected? The CRM shows $0 / $0 today.

**Consequences.**

- **Distinct**: the next scan proposes a create for Bellhaven at Union Square under Bellhaven, and the Juniper record is untouched. If they are really one campus, that creates a duplicate.
- **Same facility**: it would be a re-parent from Juniper Point. The SOP allows a direct re-parent at $0 AR, together with a rename. That is wrong if Juniper still operates the Market St community.
- **Keep holding**: Bellhaven's Union Square community stays missing from the CRM.

---

## #53 Bellhaven of Kettering (HOLD, no operations)

**Website facility.** Bellhaven of Kettering, 3313 Wilmington Pike, Kettering OH 45429, (231) 269-5449. Administrator Priya Ashby; Short-Term Rehabilitation & Nursing.

**Candidate CRM accounts** (all at the same address, Active, $0 revenue / $0 AR, Skilled Nursing, no contacts):

| Account | Name | Parent | Phone |
|---|---|---|---|
| `001WR41PYNWXCAE2X4` | Kettering Care Centre | Harborview Care Group | (419) 600-2603 |
| `001B7XZAA3AFALS9GP` | Kettering Senior Campus (street "Wilmington Pk") | Cedar Trail Communities | (517) 646-8751 |
| `0016KTS1UAWBRXS09J` | Kettering Nursing & Rehabilitation | none | (216) 345-3441 |

**Supporting evidence.** All three are at the website address, so the facility is almost certainly one of them, or all three.

**Conflicting evidence.**

- None of the phones matches the website.
- The parents differ.
- Nothing distinguishes the accounts: no revenue, no AR, no contacts and no Bellhaven name.

**Missing information.** Which record the business actually uses (shifts, contracts, contacts), and whether any of the three is a real separate entity at the same address, such as a distinct licensed unit.

**Questions for the reviewer.**

1. Which of the three accounts, if any, is used operationally?
2. Are any of them separate licensed units that should stay active?
3. Should the survivor be the Harborview record? Harborview is the documented 2025 acquisition.

**Consequences.**

- **Survivor `001WR41PYNWXCAE2X4`** (`./bh resolve 53 survivor 001WR41PYNWXCAE2X4`). The next scan proposes four items, each needing approval:
  - re-parent `001WR41PYNWXCAE2X4` from Harborview to Bellhaven ($0 AR, so the SOP allows a direct change)
  - rename it to "Bellhaven of Kettering" and set phone (231) 269-5449
  - set the other two Inactive, with `duplicate_of_account` pointing at `001WR41…` and a note

  If the wrong survivor is chosen, the record people actually use becomes Inactive. Nothing is deleted, so it can be reversed by hand.
- **Another survivor**: the same shape with different IDs.
- **Keep holding** (recommended until question 1 is answered): three conflicting records stay, and Kettering is not under Bellhaven.

---

## #70 Sandusky CHOW link (proposal with an operation; recommend INVESTIGATE, do not approve)

**Record.** `001SXSF4ELF0Z2LGDM` Bellhaven of Sandusky:

- 2715 Columbus Ave, Sandusky OH 44870; parent Bellhaven
- **$130,000 revenue / $5,200 AR** (CHOW-protected)
- contact Frank Dietz, Director of Nursing

**Proposed operation.** `PATCH /accounts/001SXSF4ELF0Z2LGDM {chow_current_account: "0017JP8Z1UQ763BVK3"}`. The target is Millstone Care of Sandusky, under Millstone Health Partners, at the same address, with $0 / $0.

**Supporting evidence.** The Bellhaven account is **not** on the website, and a different operator's account exists at the same address.

**Conflicting or absent evidence.**

- The About page never mentions Millstone or a sale.
- The direction and date of the sale are unknown; the Millstone record could predate Bellhaven.
- The Bellhaven account still has open AR and an active contact.

**Missing information.** Whether Bellhaven sold or closed Sandusky, and when.

**Questions for the reviewer.**

1. Did Sandusky change ownership from Bellhaven to Millstone?
2. Is the $5,200 AR still collectable by Bellhaven?
3. Should the old account stay Active while AR is open?

**Consequences.**

- **Approve**: Sandusky's revenue history is linked to Millstone as the current account. If the sale is wrong, billing history is linked to the wrong operator, and it has to be reversed by hand.
- **Hold**: no change; the account stays under Bellhaven with its AR.
- **Reject**: the proposal never executes. A later scan with the same evidence produces the same fingerprint, which stays rejected.

---

## #46 Ashtabula billing street (recommend HOLD)

**Record.** `001NXP9X46CWEPSLSV` Bellhaven of Ashtabula, `billing_street` = "PO Box 517", ZIP 44004, phone (260) 440-4975; $0 / $0.

**Proposed operation.** `billing_street`: "PO Box 517" → "3156 W Prospect Rd" (the website's street).

**Supporting evidence.** The name, city, ZIP and phone all match the website, so identity is solid.

**Conflicting evidence.** The field is a **billing** address, and a PO Box can be a deliberate invoicing address.

**Question for the reviewer.**

1. Does finance send invoices to PO Box 517?
2. Is `billing_*` the facility address or the invoicing address in this CRM?

**Consequences.**

- **Approve**: the PO Box is lost from the CRM. The note keeps no copy, because this proposal writes only the street.
- **Hold**: the facility address remains the PO Box.

---

## #68 Alliance and #69 Coldwater: "Needs Review" status (recommend HOLD)

**Records.**

- `00116ETS45BL7DTQP7` Bellhaven Care Center of Alliance, 1785 Freshley Ave, Alliance OH 44601
- `0016PVXH4B25HWR7QE` Bellhaven of Coldwater, 90 N Michigan Ave, Coldwater MI 49036

Both are under Bellhaven, Active, $0 / $0, and neither is on the website.

**Proposed operation.** `status`: Active → "Needs Review", plus an explanatory note.

**Supporting evidence.** Neither is listed on any website directory page or the homepage.

**Conflicting evidence.**

- The CRM contains only `Active` (112) and `Inactive` (9).
- The API spec lists no allowed status values, so "Needs Review" may be rejected or may create an orphan status.
- A missing listing doesn't establish a new owner.

**Questions for the reviewer.**

1. Does the assessment or CRM define "Needs Review" as a valid status?
2. Are Alliance and Coldwater closed, sold, or simply not marketed online?

**Consequences.**

- **Approve**: the write may fail validation, in which case it is recorded as FAILED and nothing is assumed. Otherwise it sets a status no report filters on.
- **Hold or reject**: report them as findings only; no CRM change.
