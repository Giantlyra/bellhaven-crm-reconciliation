# Evidence-Based Decision Review: all 24 open proposals

> **PRE-EXECUTION SNAPSHOT (2026-11-16, before stage 1).** Kept unchanged as historical evidence. Recommendations before execution. #57/#64/#42 were later closed as predecessor records, not duplicates; #70 was executed by the user as a documented exception. **Final, authoritative outcome:** [FINAL_AUDIT.md](FINAL_AUDIT.md) · [FINAL_RECONCILIATION_REPORT.md](FINAL_RECONCILIATION_REPORT.md).

_Read-only review, 2026-11-16, by Claude Code, using the existing system only. **Nothing here approves or executes anything.**_

**Sources:**
- The live CRM: 121 accounts, 67 contacts, 6 parent accounts.
- The live website pages and the About page.
- Ledger proposals, decisions and audit history.
- Snapshots `snapshot.json` (pre-Findlay) and `run-0003` … `run-0011`.
- Earlier reports: `RECONCILIATION_DECISION_REPORT.md`, `WAVE_A_FINAL_VALIDATION.md`, `REMAINING_DECISIONS.md`.

## How each case was reviewed

| Step | Question asked | Done how |
|---|---|---|
| Evidence | What do the CRM, website, contacts, financials and audit history say right now? | Live GETs, website re-fetch, drift check against the proposal baseline (**none on all 24**) |
| Alternative explanations | Typo, rename, duplicate, predecessor record, ownership change, or a distinct facility? | Each plausible explanation tested against the evidence |
| Challenge | What would make the leading answer wrong, and what does a wrong write cost? | Contradictions, competing accounts, financial exposure, reversibility |
| Consistency | Does it fit the CRM's history, earlier decisions and how similar cases were treated? | Snapshots, precedent, prior verified writes |
| Recommendation | APPROVE · HOLD · REJECT · INVESTIGATE, with a confidence level | A case is re-examined only if new evidence could change the answer. **"Unresolved" is a valid result** |

**Findings that apply to every case:**
- No open-case account changed across any snapshot except this engine's verified writes. All are seed records (`updated_at` 2026-11-15 04:29:11Z), none created by the candidate.
- **Exactly 6 CRM addresses hold more than one account:** Monroe (3), Kettering (3), Erie, Owosso, Port Clinton and Sandusky. Every one is covered by a proposal below.
- **No website administrator appears as a contact on any competing account.** Contacts give no hidden identity links.
- **The CRM has no precedent for linked duplicate or predecessor records.** Its 9 inactive accounts have no `duplicate_of_account` or `chow_current_account`, and none shares an address with an active account.

## Decision table

| # | Case | Recommendation | Confidence | Status in app |
|---|---|---|---|---|
| 50 | Chesterton rename | APPROVE | high | approved, not executed |
| 59 | Portsmouth billing ZIP 45626 → 45662 | APPROVE | high | approved, not executed |
| 49 | Chagrin Falls rename + phone | APPROVE | medium-high | approved, not executed |
| 66 | Willow Creek rename + phone | APPROVE | medium | approved, not executed |
| 39 | Lima re-parent → Bellhaven | APPROVE | high | pending |
| 40 | Lima phone (after #39) | APPROVE | high | pending |
| 61 | Zanesville re-parent → Bellhaven | APPROVE | medium-high | pending |
| 62 | Zanesville rename + phone (after #61) | APPROVE | high | pending |
| 56 | Owosso duplicate | APPROVE | high | pending |
| 47 | Create Batavia OH | APPROVE | medium-high | pending |
| 48 | Create Carlisle PA | APPROVE | medium-high | pending |
| 60 | Tiffin CHOW | APPROVE (alone) | high | pending |
| 54 | Marietta CHOW (after #60) | APPROVE | high | pending |
| 57, 64 | Port Clinton / Erie predecessor-brand records | **POLICY P1** → then APPROVE | action safe: high · label: low | pending |
| 41, 42 | Monroe predecessor-brand records | **POLICY P1** → then APPROVE | action safe: high · label: low | pending (user hold) |
| 36 | Amberly Manor identity | RESOLVE DISTINCT (local; no CRM write) | high | held |
| 46 | Ashtabula PO Box → street | HOLD: one billing question | medium | pending |
| 38 | Union Square identity | INVESTIGATE: **unresolved** | low | held |
| 53 | Kettering (3 records) | INVESTIGATE: **unresolved** | low | held |
| 70 | Sandusky CHOW link to Millstone | INVESTIGATE: **unresolved** | low | pending |
| 68, 69 | Alliance / Coldwater "Needs Review" | REJECT as written | high | pending |

**Totals:**
- **APPROVE: 13.** 4 already approved in the app, 9 new.
- **Policy-dependent: 4.**
- **Resolve distinct: 1.**
- **HOLD: 1.**
- **Unresolved: 3.**
- **REJECT: 2.**

## Case notes

### APPROVE

**#50 Chesterton.** Rename only.
- Evidence: exact address (Northwest = NW); the phone **already matches** the website; the administrator contact (Karen Reyes) matches; Bellhaven parent; $0/$0; only account in the ZIP.
- Alternatives: a distinct facility is ruled out (single account, same phone and administrator).
- Challenge: the old name disappears; no note keeps it.
- History: consistent with the renames verified in queue run 1.

**#59 Portsmouth.** ZIP typo.
- Evidence: street, phone and administrator match.
- Alternatives: a separate valid mailing ZIP? No. 45626 is not a valid ZIP, Portsmouth OH has only 45662/45663, and the billing street *is* the facility street.
- Challenge: it is a billing field, but the account has $0 billing history.

**#49 Chagrin Falls.** Rebrand of a facility the CRM already records under Bellhaven.
- Evidence: only account in 44022; exact street; administrator (Dale Mabry) matches; $0/$0.
- Alternatives: a prior operator called "Riverbend Manor"? Undocumented, but the write leaves ownership fields untouched.
- Residual: no record of the old ownership.

**#66 Willow Creek.**
- Evidence: only account in Portage/49024; exact street, and the new name matches it; memory-only care type matches; $0/$0.
- Challenge: no CRM contacts at all, so no person corroborates. **The weakest approval.**
- Holding it is also defensible.

**#39 → #40 Lima.** Re-parent Harborview → Bellhaven, then the phone.
- Alternatives:
  - (a) Acquired via Harborview, which joined in 2025 per the About page. The CRM name is already "Bellhaven Crossings of Lima".
  - (b) A CRM parent error.
  - (c) Bellhaven only manages it. No evidence for (c).
- Challenge:
  - Revenue $47,000, AR $0. The SOP allows a direct re-parent only because AR = 0, and the preview re-checks this live.
  - The CRM administrator contact (Nadia Sandoval) ≠ the website (Tricia Fitch). That looks like a stale contact, not an identity conflict (exact address, only account).
- History: matches the verified Findlay re-parent ($22,000, AR $0).

**#61 → #62 Zanesville.** Re-parent Cedar Trail → Bellhaven, then rename and phone.
- Evidence: the administrator contact (Dale Amato) matches the website; the About page says Cedar Trail communities joined in 2026; $0/$0.
- Challenge: the CRM still uses the Cedar Trail name. Could Cedar Trail still operate it? The same administrator on both sides and the Bellhaven listing argue against that.
- History: Marietta and Tiffin (Cedar Trail with revenue) go to CHOW. Zanesville has $0, so a direct re-parent is consistent with the SOP.

**#56 Owosso.** Same-parent duplicate.
- Evidence: the survivor's phone **and** administrator contact (Gloria Lambert) match the website; the loser is $0/$0 with no links.
- Challenge: the loser's contact (Tricia Lindqvist, Admissions) stays on the inactive record. That's a follow-up, not a blocker.

**#47 Batavia / #48 Carlisle.** Create.
- Evidence: no account in the city, the ZIP or the ZIP area, or with the phone. The website administrators (Elaine Lindqvist, Ken Ashby) are not contacts anywhere in the CRM.
- Alternatives: recorded under another name? Not found. Carlisle PA ≠ New Carlisle OH, which is a separate clean match.
- Challenge: absence of evidence. The duplicate-successor guard re-checks right before the POST.

**#60 → #54 CHOW (Tiffin, then Marietta).**
- Evidence: Cedar Trail parent, Bellhaven name, About page confirms the acquisition. Revenue **and** AR are > 0 ($84,000 / $12,400 and $51,250 / $3,800).
- Alternatives: a plain parent error would still be forbidden from a direct re-parent while AR > 0.
- Challenge: a two-step write. Guards: an existing successor blocks the POST; a partial failure resumes using the saved id. By design the old account keeps its stale phone.
- Run Tiffin alone first.

### Policy decision P1 (#57, #64, #41, #42)

Facts: a $0, contact-less, predecessor-brand account (Harborview or Cedar Trail) sits at the address of a Bellhaven account.

- **Alternatives:**
  - (a) A leftover record from the previous operator.
  - (b) An accidental duplicate.
  - (c) A distinct facility. Ruled out: the website lists one community with one care type, and the loser has no contacts.
- **Challenge:** CRM data cannot separate (a) from (b), and no precedent exists. Either way the write is the same, has **no financial exposure**, and is reversible. Only the label "Duplicate of …" is at stake.
- **Survivor strength:** Port Clinton and Erie are strong (the administrator contact is on the Bellhaven account). Monroe is weaker: two competitors, and no record carries the website administrator (Phil Mabry).
- **Policy question for the user:** *"Treat $0 predecessor-brand records with no contacts as duplicates (link + Inactive + note)?"*
  - Yes → APPROVE #57 and #64; #41 and #42 can follow.
  - No → all four stay unresolved.

### HOLD / RESOLVE

**#36 Amberly Manor → resolve DISTINCT.**
- Alternatives: the same facility with a wrong address, or a different facility with a common name.
- Evidence: the CRM has four "Amberly" accounts, all under competitors, in MI, OH, PA and CO. The only "Amberly Manor" is in **Colorado**, with a different phone and parent. Bellhaven operates in OH, MI, IN and PA only. The administrator (Tom Trent) is in no contact record.
- Result: distinct is well supported. `./bh resolve` writes nothing; the next scan proposes a create for Hudson OH, which needs its own approval.

**#46 Ashtabula.**
- Identity is certain: name, phone, ZIP and the administrator contact (Ned Green) match.
- New point: the account has **$0 billing history**, which lowers the invoice risk. But overwriting `PO Box 517` erases a possibly valid mailing address, and no note is kept.
- Open question Q5: keep the PO Box as the billing address? One answer settles it.

### Unresolved (a valid result)

**#38 Union Square.**
- Alternatives:
  - (a) Two different New Albany communities: different street, phone and parent (Juniper Point, which the About page doesn't mention).
  - (b) The same campus with an old operator's mailing address on Market St.
- No contact links either way. It leans distinct, but the specific "Union Square" name in the same city keeps it open.
- Needs: confirmation that 240 Market St is a separate community.

**#53 Kettering.**
- Three $0, contact-less records: Harborview, Cedar Trail, and one with no parent. None is Bellhaven, none has the website phone, and the administrator (Priya Ashby) is in no contact record.
- Any survivor choice would be a guess.
- Needs: which record (if any) is live. Alternatively, a business rule such as "create a Bellhaven account and treat all three as predecessors"; that would be a new proposal.

**#70 Sandusky.**
- Alternatives:
  - (a) Bellhaven sold it to Millstone.
  - (b) The website omits a community Bellhaven still runs.
  - (c) Millstone manages it under contract.
- Evidence for (a): absent from the website; the Millstone parent exists for this one account only.
- Against: the About page is silent, and the Bellhaven account still has a DON contact.
- Challenge: the account has **$130,000 revenue and $5,200 open AR**. A wrong CHOW link asserts a sale and misdirects collections.
- Needs: Bellhaven finance or ownership confirmation.

### REJECT

**#68 Alliance / #69 Coldwater.**
- The proposals set status "Needs Review", which is never used in the CRM (121 accounts are Active or Inactive only), so the write could fail or break reports.
- The underlying finding is still valid: two Bellhaven-parented $0 accounts with no contacts are absent from the website.
- Report them as findings; ask whether they were sold or closed (Q6).

## What the human decides

1. **Lane A execution** (#50, #59, #49, #66): already approved. Running it needs a live-writes session and `APPLY BATCH OF 4`.
2. **Approve or hold** each of the 9 new APPROVE items. They run individually in the order shown.
3. **Policy P1:** yes or no (#57, #64, then #41, #42).
4. **#36:** resolve as distinct? Writes nothing.
5. **#46:** keep the PO Box?
6. **#68, #69:** reject?
7. **Unresolved:** #38, #53, #70 stay open until the business answers Q2–Q4.

Every approved change then goes through the existing flow: approve → fresh live preview → typed confirmation → write → read-back → audit receipt, plus Claude Code's independent snapshot diff.
