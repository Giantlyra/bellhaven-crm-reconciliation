# Comprehensive Evaluation: all 35 proposals (read-only)

_2026-11-16, Claude Code. **No CRM changes were made by this evaluation.** Server: dry-run. Sources: live CRM (123 accounts, 67 contacts), live website, the ledger and audit log, all snapshots, and receipts._

**Method.** Each case was examined for (1) plausible explanations, (2) what could make the proposed change unsafe, and (3) consistency with CRM history, contacts, parent relationships, financials and prior decisions. Categories follow the business taxonomy: FIELD UPDATE · PARENT CORRECTION · CHANGE OF OWNERSHIP · DUPLICATE · NEW ACCOUNT · INSUFFICIENT/CONFLICTING EVIDENCE.

## Headline facts

- **Stage 1 HAS run.** All 7 were written 04:25:02–04:25:04 UTC, and the batch logged `batch_finished` with all 7 verified. This evaluation did not interrupt it.
- **Completed work:** 18 verified operations plus the legacy Findlay parent write. A fresh audit shows **18 of 18 live-matched and receipted, and integrity PASS.** Protected fields and contacts are intact.
- **Ledger:** 18 verified · 4 pending (#40, #62, #60, #54) · 11 held · 2 rejected = 35.
- **Server:** dry-run.

**Historical pattern in the CRM (new evidence).**
- Every Harborview and Cedar Trail account sits at a Bellhaven website address, which matches the About page: Harborview joined in 2025, select Cedar Trail communities in 2026.
- The acquired accounts take two forms:
  - **Renamed in place under the old parent:** Lima, Marietta, Tiffin, Zanesville. These are single records, and each carries or carried a Bellhaven-style name. Lima and Zanesville are now re-parented.
  - **A second, old-brand record beside a separate Bellhaven record:** Port Clinton, Erie, Monroe (two of them) and Kettering. **All of these old-brand records are $0 / $0 with no contacts.**
- No old-brand record anywhere has billing history while a Bellhaven duplicate also exists. That is consistent with stale import records, but the CRM cannot prove it.
- No website administrator appears as a contact on any competing record, so contacts give no hidden identity link.
- Competing records for the two identity cases carry **different administrators**: Union Square Senior Living has Dale Croft (website says Phil Holloway), and the Colorado Amberly Manor has Ned Duval (website says Tom Trent). Both lean toward distinct facilities.

## Consolidated table

| ID | Category | Evidence | Recommended action | Confidence and limitations | Execution state | Missing information |
|---|---|---|---|---|---|---|
| #43 | FIELD UPDATE | Monroe phone; exact address; matches website | Done | High. Website the only phone source | ✅ VERIFIED (op 1) | none |
| #58 | FIELD UPDATE | Port Clinton phone; admin contact matches | Done | High | ✅ VERIFIED (op 2) | none |
| #65 | FIELD UPDATE | Erie phone; admin contact matches | Done | High | ✅ VERIFIED (op 3) | none |
| #52 | FIELD UPDATE | Goshen phone; admin matches; $121k/AR $0 untouched | Done | High | ✅ VERIFIED (op 4) | none |
| #55 | FIELD UPDATE | Marion phone; admin matches | Done | High | ✅ VERIFIED (op 5) | none |
| #45 | FIELD UPDATE | Findlay phone; parent from the legacy write intact | Done | High | ✅ VERIFIED (op 6) | none |
| #37 | FIELD UPDATE | Sycamore Ridge "of"→"at" + phone; exact address | Done | High; CRM admin contact ≠ website | ✅ VERIFIED (op 7) | contact reconciliation |
| #44 | FIELD UPDATE | Ashland spelling + phone; admin matches | Done | High | ✅ VERIFIED (op 8) | none |
| #51 | FIELD UPDATE | Defiance phone; $66k / **AR $9,500 intact** | Done | High | ✅ VERIFIED (op 9) | none |
| #63 | FIELD UPDATE | Grove City name format; phone already matched | Done | High | ✅ VERIFIED (op 10) | none |
| #67 | FIELD UPDATE | Dayton name + phone; admin matches | Done | High | ✅ VERIFIED (op 11) | none |
| #50 | FIELD UPDATE | Chesterton rename; phone and admin already match; only account in ZIP | Done | High. Old name not preserved | ✅ VERIFIED (op 15, stage 1) | none |
| #59 | FIELD UPDATE | Portsmouth billing ZIP 45626→45662. 45626 is not a valid Portsmouth ZIP; billing street = facility street | Done | High. ZIP validity from public references, not USPS | ✅ VERIFIED (op 17, stage 1) | none |
| #39 | PARENT CORRECTION | Lima: Harborview→Bellhaven; exact address; About: Harborview joined 2025; **revenue $47k, AR $0** | Done | High on identity. See "potentially misclassified" | ✅ VERIFIED (op 12, stage 1) | whether the $47k history should stay attributed to Harborview |
| #61 | PARENT CORRECTION | Zanesville: Cedar Trail→Bellhaven; admin matches; $0/$0 | Done | Medium-high; ownership inferred from About page | ✅ VERIFIED (op 18, stage 1) | transfer date |
| #56 | DUPLICATE (same parent) | Owosso: survivor holds website phone and admin; loser $0/$0, no links | Done | High | ✅ VERIFIED (op 16, stage 1) | loser's Admissions contact (Tricia Lindqvist) now sits on an inactive record |
| #47 | NEW ACCOUNT | Batavia OH. No name, street, phone, ZIP-area or alternate-name match in the CRM | Done | Medium-high; absence of evidence | ✅ VERIFIED (op 13), created `00163AAEB690110611`, exists once | none |
| #48 | NEW ACCOUNT | Carlisle PA. Distinct from New Carlisle OH; nothing in Carlisle/170xx | Done | Medium-high | ✅ VERIFIED (op 14), created `00163ED66F49793F79`, exists once | none |
| #40 | FIELD UPDATE | Lima phone to the website value; **unblocked now that #39 is verified**; preview clean | **READY: approve** | High | PENDING; preview clean (drift explained by #39) | none |
| #62 | FIELD UPDATE | Zanesville rename + phone; **unblocked by #61**; preview clean; admin matches | **READY: approve** | High | PENDING; preview clean | none |
| #60 | CHANGE OF OWNERSHIP | Tiffin: $84,000 / **AR $12,400** → SOP requires CHOW. Account already carries the Bellhaven name under Cedar Trail. No existing successor | **Approve alone, after the AR question is answered** | High on identity; **medium on the transfer** (website + About page only) | PENDING; preview clean | who collects the $12,400; transfer date |
| #54 | CHANGE OF OWNERSHIP | Marietta: $51,250 / **AR $3,800**; same pattern | **Approve after #60 verifies** | same as #60 | PENDING; preview clean | who collects the $3,800; transfer date |
| #49 | FIELD UPDATE (rename) | Chagrin Falls: exact address; only account in the ZIP; **already under Bellhaven**; admin matches; $0/$0 | Release when the user is ready; evidence supports | Medium-high. Prior ownership undocumented, but no ownership field is written | HOLD (user) | whether "Riverbend Manor" was a prior operator |
| #66 | FIELD UPDATE (rename) | Willow Creek: exact address; new name matches the street; memory-only care type; already under Bellhaven | Release when ready; weakest of the renames | Medium. **No CRM contacts** | HOLD (user) | any person or record corroborating the identity |
| #57 | DUPLICATE vs historical | Port Clinton: Harborview-brand $0 record. Survivor holds the website admin | HOLD pending policy P1 | Action is reversible; **label** unsupported. High on survivor, low on label | HOLD | Q1: predecessor record or duplicate? |
| #64 | DUPLICATE vs historical | Erie: same pattern; survivor holds the website admin | HOLD pending P1 | same | HOLD | Q1 |
| #41 | DUPLICATE vs historical | Monroe Cedar Trail-brand $0 record; "Road" spelling | HOLD pending P1 | Survivor weaker: no record holds the admin (Phil Mabry) | HOLD | Q1 |
| #42 | DUPLICATE vs historical | Monroe Harborview-brand $0 record | HOLD pending P1 | same | HOLD | Q1 |
| #53 | INSUFFICIENT / CONFLICTING | Kettering: **3** $0 records (Harborview, Cedar Trail, no parent), none Bellhaven, no contacts, no phone match | Keep HOLD | Low: any survivor is a guess | HOLD | Q2: which record is live? Possibly one should be re-parented like Lima |
| #38 | INSUFFICIENT / CONFLICTING | Union Square: look-alike at 240 Market St differs on street, phone, parent **and administrator** (Dale Croft vs Phil Holloway) | Leans DISTINCT; resolve as #36 once confirmed | Medium. Same city and similar name | HOLD | one confirmation that 240 Market St is a separate community |
| #70 | CHANGE OF OWNERSHIP (inferred) | Sandusky: Bellhaven account ($130,000 / **AR $5,200**) off the website; $0 Millstone account at the same address. **The structure matches a CHOW**: old account with history, new-parent account with none | Keep HOLD | Low-medium: sale inferred from absence | HOLD | Q3: sale confirmed? who owns the AR? |
| #46 | FIELD UPDATE (billing) | Ashtabula: identity certain; billing street is PO Box 517; **$0 billing history** | Keep HOLD | High on identity; the open point is policy | HOLD | Q5: keep PO Box as billing address? |
| #36 | NEW ACCOUNT (identity) | Amberly: CRM's only "Amberly Manor" is in Colorado, with a different administrator (Ned Duval) and parent; Bellhaven doesn't operate in CO | Closed: resolved DISTINCT. A scan will then propose creating Hudson OH | High | CLOSED (resolution #1, no CRM write); the create is not yet proposed | confirm Hudson OH is a real Bellhaven community |
| #68 | INSUFFICIENT EVIDENCE | Alliance: Bellhaven-parented $0 account not on the website. **Proposal sets status "Needs Review", a value the CRM never uses** | Closed: REJECT | High that the status is unsafe | REJECTED | Q6: is Alliance still Bellhaven? |
| #69 | INSUFFICIENT EVIDENCE | Coldwater: same | Closed: REJECT | same | REJECTED | Q6 |

## Completed correctly

- All **18 executed operations plus the legacy Findlay re-parent**, independently re-checked: live values match, protected fields are untouched, contacts are unchanged and each write has a read-back receipt.
- The new `parent_name` values on #39 and #61 are just the display name following the new `parent_id`, not extra changes.
- #47 and #48 each exist exactly once, with Bellhaven as parent, $0 / $0, and a provenance note.
- #56 inactivated only the loser, with the link and note. The survivor is unchanged.

## Potentially misclassified or unsafe

1. **#39 Lima (executed).** Treated as a PARENT CORRECTION, but business-wise it is an ownership transition with $47k of Harborview-era revenue. The SOP allows it because AR is $0. This follows the Findlay precedent, but the history is now attributed to Bellhaven.
2. **#60 / #54 (pending).** They are parent corrections forced into CHOW by the AR rule. After execution the old Cedar Trail-parented account stays Active under the same name as the new successor, so there will be two active "Bellhaven of Tiffin" and two "Bellhaven of Marietta" accounts. Reports must follow `chow_current_account`.
3. **#57, #64, #41, #42.** The DUPLICATE label may be wrong (historical import records). The action is reversible, but the note would state the wrong reason.
4. **#46.** Presented as a FIELD UPDATE; it is really a billing-address policy question.
5. **#68, #69.** Unsafe as written (an invalid status value). Correctly rejected; the exceptions remain as findings.
6. **#56.** A same-parent duplicate, so low risk. One side effect: an active contact now sits on an inactive account.
7. **#49 and #66** are not unsafe. They were held conservatively, and their evidence is stronger than the other held cases.

## Ready for final authorization

- **#40 and #62** (stage 2). Unblocked and clean in a live preview.
- **#60, then #54** (CHOW), after the user answers the unpaid-balance question.
- **#49 and #66**, if the user chooses to release the holds.

## Requiring Bellhaven confirmation

| Question | Cases |
|---|---|
| **Q1** Are $0 old-brand records historical operators or duplicates? | #57, #64, #41, #42 |
| **Q2** Which Kettering record is live? | #53 |
| **Q3** Was Sandusky sold to Millstone; who owns the $5,200 AR? | #70 |
| **Q4** Is 240 Market St a separate community from Union Square? Is Amberly Hudson OH a real Bellhaven community? | #38, #36 |
| **Q5** Keep the PO Box as Ashtabula's billing address? | #46 |
| **Q6** Are Alliance and Coldwater still Bellhaven communities? | #68, #69 |
| **Q8** Who collects the Tiffin and Marietta unpaid balances after the CHOW? | #60, #54 |

## Still missing from the assessment

- **Final deliverables:** the final reconciliation report, the monitoring demonstration and the submission walkthrough.
- **A check against the original assessment brief.** The brief isn't in this session, so I have only the project's own `docs/REQUIREMENTS_MATRIX.md`. Please supply the brief or confirm the deliverables list.
- **Items the project's own report lists as not done:** the demo video, the public repository, the time-spent figure and the form submission. A repository commit exists locally (branch `bellhaven-assessment`).
- **A follow-up scan** so the #36 resolution turns into a Hudson OH create proposal for review.
- **Doc refresh.** Some documents still quote old counts: 112 tests, 32 pending, the pre-queue lifecycle.
- **Contacts aren't reconciled** (the website administrators differ from CRM contacts at several communities), and the daily cron schedule isn't installed. Both are outside the agreed scope.

## Final action plan, in batches

| Batch | What | Gate |
|---|---|---|
| **1. Stage 2** | #40 and #62 together (2 items, no overlap, clean preview) | The user's authorization; the batch preview and typed phrase in the app |
| **2. CHOW** | #60 alone, verify, then #54 alone, verify | The user answers Q8 first |
| **3. Optional release** | #49 and #66 | The user's call |
| **4. Business answers** | Q1–Q6 → then the policy P1 batch (#57, #64, #41, #42), #38, #53, #70, #46 | Bellhaven's confirmation. Unresolved is a valid documented result if no answers come |
| **5. Wrap-up** | Follow-up scan, final audit run, final report, monitoring demo, walkthrough, and a check against the original brief | After batches 1–2, whichever of 3–4 are done |
