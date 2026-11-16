# Final Reconciliation Audit (2026-11-16T22:58:35Z)

_Read-only: live website scrape, live CRM read, ledger and receipts. No CRM write is possible from this script._

## 1. Website vs CRM (all communities)

- Website: **35** communities (scrape complete: True). CRM: **125** accounts, **67** contacts.
- Result: **DIFFERS: 2** · **EXISTING ACCOUNT (alternate evidence): 1** · **MATCH: 23** · **MULTIPLE ACCOUNTS: 7** · **NO ACCOUNT AT PHYSICAL ADDRESS: 2**

| Community | Result | Detail |
|---|---|---|
| Amberly Manor | NO ACCOUNT AT PHYSICAL ADDRESS | create proposal #71 HOLD, awaiting explicit authorization |
| Bellhaven Gardens of Monroe | MULTIPLE ACCOUNTS | Bellhaven Gardens of Monroe (Bellhaven Senior Living), Cedar Trail of Monroe (Cedar Trail Communities), Monroe Gardens Care Center (Harborview Care Group) |
| Bellhaven Shores of Erie | MULTIPLE ACCOUNTS | Bellhaven Shores of Erie (Bellhaven Senior Living), Harborview Shores of Erie (Harborview Care Group) |
| Bellhaven Willow Creek | DIFFERS | differs: name, phone |
| Bellhaven at Union Square | NO ACCOUNT AT PHYSICAL ADDRESS | identity HOLD #38: a look-alike CRM account exists elsewhere; unresolved |
| Bellhaven of Ashtabula | EXISTING ACCOUNT (alternate evidence) | `001NXP9X46CWEPSLSV` matched by name + city/state match supported by: phone matches, CRM street is a PO Box (mailing address, not the facility), ZIP matches; CRM billing address 'PO Box 517' differs from the physical address; #46 HOLD, so the billing address is preserved pending a finance decision |
| Bellhaven of Chagrin Falls | DIFFERS | differs: name, phone |
| Bellhaven of Kettering | MULTIPLE ACCOUNTS | Kettering Care Centre (Harborview Care Group), Kettering Nursing & Rehabilitation (), Kettering Senior Campus (Cedar Trail Communities) |
| Bellhaven of Marietta | MULTIPLE ACCOUNTS | Bellhaven of Marietta (Bellhaven Senior Living), Bellhaven of Marietta (Cedar Trail Communities) |
| Bellhaven of Owosso | MULTIPLE ACCOUNTS | Bellhaven of Owosso (Bellhaven Senior Living), Bellhaven of Owosso (Bellhaven Senior Living) |
| Bellhaven of Port Clinton | MULTIPLE ACCOUNTS | Bellhaven of Port Clinton (Bellhaven Senior Living), Harborview Nursing & Rehab of Port Clinton (Harborview Care Group) |
| Bellhaven of Tiffin | MULTIPLE ACCOUNTS | Bellhaven of Tiffin (Bellhaven Senior Living), Bellhaven of Tiffin (Cedar Trail Communities) |
| _23 communities match exactly (name, address, phone, Bellhaven parent)_ | | |

- Bellhaven-parented CRM accounts at no website address: Bellhaven Care Center of Alliance (`00116ETS45BL7DTQP7`), Bellhaven of Ashtabula (`001NXP9X46CWEPSLSV`), Bellhaven of Coldwater (`0016PVXH4B25HWR7QE`), Bellhaven of Sandusky (`001SXSF4ELF0Z2LGDM`)

## 2. Verified ledger operations vs live CRM and audit receipts

| Op | Proposal | Account | Wrote | Status | Live CRM matches | Receipt |
|---|---|---|---|---|---|---|
| 1 | #43 | `001U1750VLVJAGG1S5` | phone | verified | ✅ | ✅ |
| 2 | #58 | `001UELXDAKFRKB8932` | phone | verified | ✅ | ✅ |
| 3 | #65 | `001CVBBCSDM7YHN220` | phone | verified | ✅ | ✅ |
| 4 | #52 | `001JQER1RMYKNRLNME` | phone | verified | ✅ | ✅ |
| 5 | #55 | `0015L38R1Z5947ZZP7` | phone | verified | ✅ | ✅ |
| 6 | #45 | `001UKEFGADQ8YCZ4YM` | phone | verified | ✅ | ✅ |
| 7 | #37 | `00191H7JR16471SZ34` | name, phone | verified | ✅ | ✅ |
| 8 | #44 | `001RJ0D7Z5MAZN5HX5` | name, phone | verified | ✅ | ✅ |
| 9 | #51 | `001R4PXTUD9R6FNN8V` | phone | verified | ✅ | ✅ |
| 10 | #63 | `001TZCSTBZFM6K5BGN` | name | verified | ✅ | ✅ |
| 11 | #67 | `0010KJFP601YNTZVDA` | name, phone | verified | ✅ | ✅ |
| 12 | #39 | `001LGFPBJY4N9MB6KL` | parent_id | verified | ✅ | ✅ |
| 13 | #47 | `00163AAEB690110611` | name, billing_street, billing_city, billing_state, billing_zip, phone, care_type, parent_id, status, note | verified | ✅ | ✅ |
| 14 | #48 | `00163ED66F49793F79` | name, billing_street, billing_city, billing_state, billing_zip, phone, care_type, parent_id, status, note | verified | ✅ | ✅ |
| 15 | #50 | `0013NUZQHQUEZ8DXEG` | name | verified | ✅ | ✅ |
| 16 | #56 | `001QU150PM4Z15UA71` | duplicate_of_account, status, note | verified | ✅ | ✅ |
| 17 | #59 | `001CF3LDWVRGL09P4F` | billing_zip | verified | ✅ | ✅ |
| 18 | #61 | `001H1JMVZWP46D5VUF` | parent_id | verified | ✅ | ✅ |
| 19 | #40 | `001LGFPBJY4N9MB6KL` | phone | verified | ✅ | ✅ |
| 20 | #62 | `001H1JMVZWP46D5VUF` | name, phone | verified | ✅ | ✅ |
| 21 | #60 | `00164AE214A6588944` | name, billing_street, billing_city, billing_state, billing_zip, phone, care_type, parent_id, status, note | verified | ✅ | ✅ |
| 22 | #60 | `001U6RW32TY0WSXZZB` | chow_current_account | verified | ✅ | ✅ |
| 23 | #70 | `001SXSF4ELF0Z2LGDM` | chow_current_account | verified | ✅ | ✅ |
| 24 | #54 | `0014861C0619562203` | name, billing_street, billing_city, billing_state, billing_zip, phone, care_type, parent_id, status, note | verified | ✅ | ✅ |
| 25 | #54 | `001A34WFSUYHCRBLFT` | chow_current_account | verified | ✅ | ✅ |

- **25 of 25** operations verified, live-matched and receipted.
- Queue receipt file: `queue-20261116T032655Z.json`

## 3. Protected fields and contacts vs pre-write snapshots

- 23 account snapshots compared. Protected fields (financials, parent, status, links, address, care type) changed only where the engine wrote them; contacts unchanged.
- Violations: **none**

## 4. Duplicate and CHOW links in the CRM

- `001A34WFSUYHCRBLFT` Bellhaven of Marietta: duplicate_of=- chow=0014861C0619562203 → ✅ matches a verified proposal
- `001QU150PM4Z15UA71` Bellhaven of Owosso: duplicate_of=001EGU7BMJ942ZTRE6 chow=- → ✅ matches a verified proposal
- `001SXSF4ELF0Z2LGDM` Bellhaven of Sandusky: duplicate_of=- chow=0017JP8Z1UQ763BVK3 → ✅ matches a verified proposal
- `001U6RW32TY0WSXZZB` Bellhaven of Tiffin: duplicate_of=- chow=00164AE214A6588944 → ✅ matches a verified proposal
- No account is Inactive because of this engine except where a verified duplicate proposal says so.
- Verified inactivations: 1

## 5. Proposal statuses and unresolved exceptions

- Open ledger: **hold: 7** · **rejected: 5** · **verified: 23**
- Resolved or superseded by later scans (not open): 36

| # | Kind | Status | Case | Open question |
|---|---|---|---|---|
| #38 | HOLD | hold | HOLD — identity unresolved: Bellhaven at Union Square | Is Union Square Senior Living (240 Market St) a different community from Bellhaven at Union Square? (#38) |
| #41 | DUPLICATE | hold | Duplicate: Cedar Trail of Monroe (0011AB44D05WLA9HTX) → Bellhaven Gard | Did 750 Stewart Rd ever operate under Cedar Trail, or is 'Cedar Trail of Monroe' an erroneous record? (#41) |
| #42 | DUPLICATE | rejected | Duplicate: Monroe Gardens Care Center (00159PL81N38KM4FHM) → Bellhaven | Predecessor-brand records preserved; ownership history inferred, not confirmed (#42, #57, #64: closed, no write) |
| #46 | FIELD_UPDATE | hold | Update billing_street: Bellhaven of Ashtabula | Keep PO Box 517 as Ashtabula's billing address? (#46) |
| #49 | FIELD_UPDATE | hold | Update name, phone: Riverbend Manor Care Center | Chagrin Falls / Willow Creek: rename or ownership change? (#49, #66) |
| #53 | HOLD | hold | HOLD — 3 indistinguishable accounts: Bellhaven of Kettering | Which Kettering account is live? (#53) |
| #54 | CHOW | verified | CHOW successor: Bellhaven of Marietta (Cedar Trail Communities (Parent | Who collects the historical Tiffin ($12,400) and Marietta ($3,800) balances? (#60, #54: CHOW verified) |
| #57 | DUPLICATE | rejected | Duplicate: Harborview Nursing & Rehab of Port Clinton (001JD2MWRA74LTS | Predecessor-brand records preserved; ownership history inferred, not confirmed (#42, #57, #64: closed, no write) |
| #60 | CHOW | verified | CHOW successor: Bellhaven of Tiffin (Cedar Trail Communities (Parent A | Who collects the historical Tiffin ($12,400) and Marietta ($3,800) balances? (#60, #54: CHOW verified) |
| #64 | DUPLICATE | rejected | Duplicate: Harborview Shores of Erie (001BLYF02K97SZLZHH) → Bellhaven  | Predecessor-brand records preserved; ownership history inferred, not confirmed (#42, #57, #64: closed, no write) |
| #66 | FIELD_UPDATE | hold | Update name, phone: Sunny Acres Retirement Home | Chagrin Falls / Willow Creek: rename or ownership change? (#49, #66) |
| #68 | CRM_ONLY | rejected | Flag for review: Bellhaven Care Center of Alliance not on website | Are Alliance and Coldwater still Bellhaven communities? (#68, #69: rejected as written) |
| #69 | CRM_ONLY | rejected | Flag for review: Bellhaven of Coldwater not on website | Are Alliance and Coldwater still Bellhaven communities? (#68, #69: rejected as written) |
| #70 | CHOW | verified | CHOW link: Bellhaven of Sandusky → Millstone Care of Sandusky (Millsto | Was the Sandusky sale to Millstone confirmed, and who collects the $5,200 AR? (#70: link verified, exception documented) |
| #71 | WEBSITE_ONLY | hold | Create account: Amberly Manor | Confirm Bellhaven's Hudson OH community before creating Amberly Manor (#71) |

### Open business questions

- **Q1:** Did 750 Stewart Rd ever operate under Cedar Trail, or is 'Cedar Trail of Monroe' an erroneous record? (#41)
- **Q1b:** Predecessor-brand records preserved; ownership history inferred, not confirmed (#42, #57, #64: closed, no write)
- **Q2:** Which Kettering account is live? (#53)
- **Q3:** Was the Sandusky sale to Millstone confirmed, and who collects the $5,200 AR? (#70: link verified, exception documented)
- **Q4:** Is Union Square Senior Living (240 Market St) a different community from Bellhaven at Union Square? (#38)
- **Q5:** Keep PO Box 517 as Ashtabula's billing address? (#46)
- **Q6:** Are Alliance and Coldwater still Bellhaven communities? (#68, #69: rejected as written)
- **Q7:** Chagrin Falls / Willow Creek: rename or ownership change? (#49, #66)
- **Q8:** Who collects the historical Tiffin ($12,400) and Marietta ($3,800) balances? (#60, #54: CHOW verified)
- **Q9:** Confirm Bellhaven's Hudson OH community before creating Amberly Manor (#71)

- Identity resolutions recorded (local decisions, no CRM write): 1
- Audit log: 412 events; append-only (SQLite triggers). Writes attempted by this engine: **25**.

## Result

**INTEGRITY: PASS.** Every executed change is live-matched, receipted and within its approved fields; protected fields and contacts are intact.
