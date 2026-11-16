# Remaining Decisions: all 24 open proposals

_Read-only review 2026-11-16T03:37:33Z by Claude Code: live CRM (121 accounts), live website pages and the ledger. **Nothing here authorizes a write.** Server: dry-run._

**Checks run on all 24:**
- No baseline drift on any of them.
- Every website value is unchanged since the proposal.
- **None** qualifies for the low-risk queue (phone/name, exact match, similar name). Each is a rename, billing, ownership, duplicate, CHOW or create change.
- Pre-execution snapshot of every touched account and its contacts: `data/remaining_pre_execution_snapshot.json`.

| Lane | Count |
|---|---|
| A. Controlled batch: verified Wave A items (existing `/batch` path, `APPLY BATCH OF n`) | 4 |
| B. Ready: individual execution (`APPLY <id>`), in this order | 9 |
| C. Blocked: needs a business answer (no write possible yet) | 9 |
| D. Recommend REJECT (writes nothing) | 2 |

## A. Controlled batch: verified Wave A items (existing `/batch` path, `APPLY BATCH OF n`)

| # | Kind | Exact change | Evidence | Risk | Recommended | Caveat |
|---|---|---|---|---|---|---|
| #50 | FIELD_UPDATE | `0013NUZQHQUEZ8DXEG` name: Chesterton Senior Commons → Bellhaven of Chesterton | Exact address (NW/Northwest); phone and administrator (Karen Reyes) already match the website; Bellhaven parent; $0/$0; only account in ZIP. | medium | **APPROVE** | Old name disappears from the CRM (no note kept) |
| #59 | FIELD_UPDATE | `001CF3LDWVRGL09P4F` billing_zip: 45626 → 45662 | Street, phone and administrator match. 45626 is not a valid ZIP; Portsmouth OH has only 45662/45663. The billing street *is* the facility street, not a separate mailing address. | medium | **APPROVE** | Changes a billing field |
| #49 | FIELD_UPDATE | `001RJU1X4NBWC1Q0G7` name: Riverbend Manor Care Center → Bellhaven of Chagrin Falls; phone: (517) 457-9548 → (231) 283-7448 | Only account in Chagrin Falls/44022. Exact street; administrator (Dale Mabry) matches; already under Bellhaven; $0/$0. Current ownership is consistent in both sources. | medium | **APPROVE** | Material rename; prior ownership undocumented (no billing to protect) |
| #66 | FIELD_UPDATE | `0017MN2JYAJBDS8WQZ` name: Sunny Acres Retirement Home → Bellhaven Willow Creek; phone: (216) 898-7925 → (419) 394-5494 | Only account in Portage/49024. Exact street (Willow Creek Ln matches the new name); memory-only care type matches; already under Bellhaven; $0/$0. | medium | **APPROVE or HOLD** | No CRM contacts to corroborate: the weakest of the four |

## B. Ready: individual execution (`APPLY <id>`), in this order

| # | Kind | Exact change | Evidence | Risk | Recommended | Caveat |
|---|---|---|---|---|---|---|
| #39 | WRONG_PARENT | `001LGFPBJY4N9MB6KL` parent_id: 001FJZYHR7MLFMNPLL → 0015QAPLGS3FVYEEEM | Exact address; About page: Harborview joined Bellhaven in 2025; only account at address. Revenue $47k, AR $0 → the SOP allows a direct re-parent. | high | **APPROVE (alone)** | Ownership field; CRM admin contact ≠ website |
| #40 | FIELD_UPDATE | `001LGFPBJY4N9MB6KL` phone: (734) 872-9575 → (231) 539-3617 | Phone fix on the Lima account; website match. | low | **APPROVE after #39 verifies** | Same account as #39 |
| #61 | WRONG_PARENT | `001H1JMVZWP46D5VUF` parent_id: 001FWSQ30SFW6S7604 → 0015QAPLGS3FVYEEEM | Exact address; About page: Cedar Trail communities joined in 2026; administrator (Dale Amato) matches; $0/$0 → direct re-parent. | high | **APPROVE (alone)** | Ownership field; inferred rebrand |
| #62 | FIELD_UPDATE | `001H1JMVZWP46D5VUF` name: Cedar Trail of Zanesville → Bellhaven of Zanesville; phone: (517) 817-8191 → (814) 599-2533 | Rename Cedar Trail of Zanesville → Bellhaven of Zanesville, plus a phone fix. | medium | **APPROVE after #61 verifies** | Same account as #61 |
| #56 | DUPLICATE | `001QU150PM4Z15UA71` duplicate_of_account: ∅ → 001EGU7BMJ942ZTRE6; status: Active → Inactive | Same-parent duplicate. The survivor wins decisively: website phone and administrator (Gloria Lambert) match. The loser is $0/$0 with no links. | medium | **APPROVE (alone)** | Loser's contact (Tricia Lindqvist) stays on the inactive record |
| #47 | WEBSITE_ONLY | POST new account: Bellhaven of Batavia, 2000 Hospital Dr, Batavia OH 45103, (231) 698-3092, parent Bellhaven | No CRM account in that city, ZIP or ZIP area, or with that phone. The duplicate-successor guard re-checks right before the POST. | high | **APPROVE (alone)** | Creates an account; confidence medium (absence of evidence) |
| #48 | WEBSITE_ONLY | POST new account: Bellhaven of Carlisle, 640 Walnut Bottom Rd, Carlisle PA 17015, (260) 386-7765, parent Bellhaven | Carlisle PA ≠ Bellhaven of New Carlisle OH (a separate clean match). No CRM account in Carlisle/170xx or with that phone. | high | **APPROVE (alone)** | Creates an account |
| #60 | CHOW | POST new account: Bellhaven of Tiffin, 45 St Lawrence Dr, Tiffin OH 44883, (260) 589-2589, parent Bellhaven<br>`001U6RW32TY0WSXZZB` chow_current_account: ∅ → <new successor id> | $84,000 / AR $12,400 → CHOW: the old account is preserved, a successor is POSTed, then linked. Only account at the address; no existing successor; About page confirms Cedar Trail joined. | high | **APPROVE (alone, first CHOW)** | Two-step write; partial failure resumes using the saved id |
| #54 | CHOW | POST new account: Bellhaven of Marietta, 805 Colegate Dr, Marietta OH 45750, (614) 337-1967, parent Bellhaven<br>`001A34WFSUYHCRBLFT` chow_current_account: ∅ → <new successor id> | CHOW, same as Tiffin: $51,250 / AR $3,800. | high | **APPROVE after #60 verifies** | Run after #60 proves CHOW on the live API |

## C. Blocked: needs a business answer (no write possible yet)

| # | Kind | Exact change | Evidence | Risk | Recommended | Caveat |
|---|---|---|---|---|---|---|
| #70 | CHOW | `001SXSF4ELF0Z2LGDM` chow_current_account: ∅ → 0017JP8Z1UQ763BVK3 | Sandusky: $130,000 / **AR $5,200**; the sale to Millstone is inferred only. | high | **HOLD (Q3)** | Financial risk if wrong |
| #36 | HOLD | — (no CRM operation) | The CRM's Amberly Manor is in Colorado; Bellhaven operates in OH/MI/IN/PA only. | hold | **Resolve DISTINCT (Q4)** | Then a create proposal is needed for Hudson OH |
| #38 | HOLD | — (no CRM operation) | 'Union Square Senior Living' is at 240 Market St, same city, different phone and parent. | hold | **HOLD (Q4)** | Distinct, or a mailing address? |
| #41 | DUPLICATE | `0011AB44D05WLA9HTX` duplicate_of_account: ∅ → 001U1750VLVJAGG1S5; status: Active → Inactive | $0 Cedar Trail-branded record at Monroe. | high | **HOLD (Q1)** | Predecessor record or duplicate? |
| #42 | DUPLICATE | `00159PL81N38KM4FHM` duplicate_of_account: ∅ → 001U1750VLVJAGG1S5; status: Active → Inactive | $0 Harborview-branded record at Monroe. | high | **HOLD (Q1)** | Same |
| #57 | DUPLICATE | `001JD2MWRA74LTSN24` duplicate_of_account: ∅ → 001UELXDAKFRKB8932; status: Active → Inactive | $0 Harborview record at Port Clinton. | high | **HOLD (Q1)** | Same |
| #64 | DUPLICATE | `001BLYF02K97SZLZHH` duplicate_of_account: ∅ → 001CVBBCSDM7YHN220; status: Active → Inactive | $0 Harborview record at Erie. | high | **HOLD (Q1)** | Same |
| #53 | HOLD | — (no CRM operation) | 3 $0 accounts at Kettering: Harborview, Cedar Trail, and one with no parent. No Bellhaven record. | hold | **HOLD (Q2)** | Which one is live? |
| #46 | FIELD_UPDATE | `001NXP9X46CWEPSLSV` billing_street: PO Box 517 → 3156 W Prospect Rd | Ashtabula billing street is PO Box 517; identity is certain. | medium | **HOLD (Q5)** | Could break invoice delivery |

## D. Recommend REJECT (writes nothing)

| # | Kind | Exact change | Evidence | Risk | Recommended | Caveat |
|---|---|---|---|---|---|---|
| #68 | CRM_ONLY | `00116ETS45BL7DTQP7` status: Active → Needs Review | Sets status 'Needs Review', which the CRM never uses (only Active/Inactive). | medium | **REJECT** | Q6: is Alliance still Bellhaven? |
| #69 | CRM_ONLY | `0016PVXH4B25HWR7QE` status: Active → Needs Review | Same as #68, for Coldwater MI. | medium | **REJECT** | Q6 |

## Business questions (lane C)
- **Q1:** Are the $0 Harborview and Cedar Trail records at Monroe, Port Clinton and Erie predecessor-operator records, or duplicates? (#41, #42, #57, #64)
- **Q2:** Which Kettering account is live? (#53)
- **Q3:** Did Bellhaven sell Sandusky to Millstone, and who owns the $5,200 AR? (#70)
- **Q4:** Are Amberly (Hudson OH) and Union Square (New Albany OH) distinct from the look-alike CRM accounts? (#36, #38)
- **Q5:** Should Ashtabula's billing address stay PO Box 517? (#46)
- **Q6:** Are Alliance and Coldwater still Bellhaven communities? (#68, #69)

## Execution path after the user's approvals
1. Lane A uses the existing batch path. Approve the items, then open **Build / Modify → approved → Preview batch**, type `APPLY BATCH OF n`.
   Each item is approved and fingerprint-checked, re-previewed with a plan token, policy-checked, written, read back and audited; the batch stops at the first failure.
   Claude Code then diffs every account against `data/remaining_pre_execution_snapshot.json`, including contacts.
2. Lane B goes one at a time, `APPLY <id>`, in the order shown. The CHOW items are never batched.
3. Lane C: nothing can execute until the business question is answered.
4. Lane D: rejecting in the app writes nothing.
