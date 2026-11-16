# CHOW Review: #60 Tiffin and #54 Marietta (2026-11-16T04:20:44Z)

_Read-only. Reviewed under the existing change-of-ownership SOP and financial rules. **Not an authorization.** Both stay pending; nothing is executed._

**SOP (from `app/policy.py`):** an account that must change parent AND has revenue > 0 AND outstanding AR > 0 is never re-parented. The old account is left exactly as it is.
A new account is created under the correct parent, and the old account's `chow_current_account` is set to it. Missing or malformed financials block the item.

## #60: Bellhaven of Tiffin

| Check | Result |
|---|---|
| Old account | `001U6RW32TY0WSXZZB` Bellhaven of Tiffin, 45 St Lawrence Dr, Tiffin OH 44883 |
| Old parent → required parent | Cedar Trail Communities (Parent Account) → Bellhaven Senior Living (Parent Account) |
| Revenue / outstanding AR | **$84,000 / $12,400**: both > 0, so the SOP requires CHOW (`chow_required` = True) |
| Old account state | Active; `chow_current_account` = (blank); `duplicate_of_account` = (blank); no note |
| Existing successor at this address | none |
| Website | Bellhaven of Tiffin · 45 St Lawrence Dr, Tiffin OH 44883 · (260) 589-2589 · administrator Walt Osei · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-tiffin |
| Old account contacts | none (no contact moves with a CHOW) |
| Live pre-write validation | ✅ clean (no drift, SOP and successor guard pass) |
| Drift vs proposal baseline | none |

**Exact operations, in order (one proposal, two writes, recoverable):**
1. `POST /accounts` {"name": "Bellhaven of Tiffin", "billing_street": "45 St Lawrence Dr", "billing_city": "Tiffin", "billing_state": "OH", "billing_zip": "44883", "phone": "(260) 589-2589", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"}
2. `PATCH /accounts/001U6RW32TY0WSXZZB` `{"chow_current_account": "<new successor id>"}`: the only field written on the old account

**Safeguards:**
- The duplicate-successor guard re-checks for an existing account at the address right before the POST.
- If the POST succeeds and the PATCH fails, a retry reuses the saved successor id and never creates a second account.
- An unknown POST outcome (timeout) is resolved by lookup, never by blind retry.
- The write is read back and compared. CHOW always runs alone, never in a batch.

## #54: Bellhaven of Marietta

| Check | Result |
|---|---|
| Old account | `001A34WFSUYHCRBLFT` Bellhaven of Marietta, 805 Colegate Drive, Marietta OH 45750 |
| Old parent → required parent | Cedar Trail Communities (Parent Account) → Bellhaven Senior Living (Parent Account) |
| Revenue / outstanding AR | **$51,250 / $3,800**: both > 0, so the SOP requires CHOW (`chow_required` = True) |
| Old account state | Active; `chow_current_account` = (blank); `duplicate_of_account` = (blank); no note |
| Existing successor at this address | none |
| Website | Bellhaven of Marietta · 805 Colegate Dr, Marietta OH 45750 · (614) 337-1967 · administrator Rosa Dietz · https://analyst-assessment-production.up.railway.app/communities/bellhaven-of-marietta |
| Old account contacts | none (no contact moves with a CHOW) |
| Live pre-write validation | ✅ clean (no drift, SOP and successor guard pass) |
| Drift vs proposal baseline | none |

**Exact operations, in order (one proposal, two writes, recoverable):**
1. `POST /accounts` {"name": "Bellhaven of Marietta", "billing_street": "805 Colegate Dr", "billing_city": "Marietta", "billing_state": "OH", "billing_zip": "45750", "phone": "(614) 337-1967", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"}
2. `PATCH /accounts/001A34WFSUYHCRBLFT` `{"chow_current_account": "<new successor id>"}`: the only field written on the old account

**Safeguards:**
- The duplicate-successor guard re-checks for an existing account at the address right before the POST.
- If the POST succeeds and the PATCH fails, a retry reuses the saved successor id and never creates a second account.
- An unknown POST outcome (timeout) is resolved by lookup, never by blind retry.
- The write is read back and compared. CHOW always runs alone, never in a batch.

## Explicit financial and ownership questions the user should answer before authorizing

1. **Ownership:** is the move from Cedar Trail to Bellhaven final for both communities? The only independent source is the website listing plus the About page ("select communities joining us from Cedar Trail" in 2026). Neither Tiffin nor Marietta is named there, and no CRM field records a transfer date.
2. **Outstanding AR stays on the OLD (Cedar Trail-parented) account:** Tiffin **$12,400** and Marietta **$3,800**. The new Bellhaven successor starts at $0 / $0. Who is responsible for collecting that AR after the change?
3. **The old accounts keep their stale phone and Cedar Trail parent by design.** The SOP leaves the old account untouched apart from the link. Is that the intended end state?
4. **Contacts:** neither old account has contacts, so nothing is orphaned. The successors are created without contacts.
5. **Order:** execute #60 Tiffin alone first, verify the CHOW on the live API, then #54.

## Assessment
- **Both pass every automated rule today.** The SOP, successor, drift and policy checks are clean, and nothing is blocked.
- **Confidence in ownership: high for the facility identity, medium for the transfer itself** (inferred from the website listing and the About page, not from a CRM or contract record).
- **Recommendation: APPROVE #60 first, alone, and #54 only after #60 verifies, on the condition that the user answers question 2.** Otherwise hold.


## Direction and successor verification (2026-11-16, read-only, before execution)

| Check | #60 Tiffin | #54 Marietta |
|---|---|---|
| Historical (old) account | `001U6RW32TY0WSXZZB` "Bellhaven of Tiffin", parent **Cedar Trail** | `001A34WFSUYHCRBLFT` "Bellhaven of Marietta", parent **Cedar Trail** |
| Direction | **Cedar Trail → Bellhaven** | **Cedar Trail → Bellhaven** |
| Evidence for direction | The website lists the community under Bellhaven; the About page says "select communities joining us from Cedar Trail" (2026); the CRM account already carries the Bellhaven name under the old parent | same |
| Evidence against | none found (no other account in the city or ZIP; no link, note or contact pointing elsewhere) | none found |
| Rule check | `chow_required` = True: revenue $84,000 **and** AR $12,400 > 0 | True: $51,250 and $3,800 > 0 |
| Successor vs website | name, street, city, state, ZIP and phone all equal the live website; parent Bellhaven; Active; care type Skilled Nursing (= Short-Term Rehab & Nursing) | same |
| Successor financials | **No revenue or AR fields are sent.** New accounts start at $0 / $0 (confirmed by the Batavia and Carlisle creates) | same |
| What changes on the old account | **Only** `chow_current_account` → new successor id. Parent, name, phone, revenue, AR, status, contacts (none) and audit history are preserved | same |
| Guards | Live preview clean: no drift, no existing successor, no existing CHOW link | same |
| Limitation | The direction rests on public website evidence, not a transaction record or transfer date | same |

### Unanswered: responsibility for the historical balances
The CHOW leaves the **$12,400 (Tiffin)** and **$3,800 (Marietta)** outstanding AR on the historical Cedar Trail-parented accounts, exactly as the SOP requires.
- **Who is legally or operationally responsible for collecting these balances is not known from the data.**
- This evaluation does **not** assume or change that responsibility, and the CHOW writes nothing about it.
- It is recorded as an open business question for Bellhaven/Cedar Trail (Q8).

### Execution plan
1. #60 alone: the user approves it in the app, runs the live preview, and types `APPLY 60`.
2. Claude Code independently verifies the result.
3. Only then is #54 presented, the same way.

Nothing is approved on the user's behalf.
