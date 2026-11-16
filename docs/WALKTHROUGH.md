# Assessment Walkthrough

_For the reviewer. Every step is read-only unless stated otherwise._

## Setup (1 minute)
```
cd ~/clipboard-assessment
./bh test          # 134 tests, mocked CRM, about 1 s
./bh status        # last scan, proposal counts, write calls (25)
./bh serve         # http://127.0.0.1:8000, DRY-RUN
```

## 5-minute walkthrough script

| Time | Screen | Say / show |
|---|---|---|
| **0:00–0:40 · Problem** | Website homepage → **Start Here** | "Bellhaven's public website lists **35 communities**. The CRM had **121 accounts** with wrong names, phones, ZIPs and parents, duplicates, missing facilities, and acquired communities still under their old operator. The website is the source of truth for identity and contact data; the CRM holds financial history that must not be damaged." |
| **0:40–1:30 · Reconciliation engine** | **Start Here**: completeness card, source fingerprints | "One read-only scan pages through the whole website, including the homepage-only listing, and every CRM page. If anything is incomplete it fails closed and proposes nothing. It matches on exact address+ZIP, then classifies each case: field update, parent correction, change of ownership, duplicate, new account, or insufficient evidence. No LLM, no guessing." |
| **1:30–2:15 · Evidence** | **Build/Modify** → #60 Tiffin | "Every proposal shows website vs CRM side by side, the sources and timestamps, and what's still missing. Tiffin sits under Cedar Trail with **$84,000 revenue and $12,400 unpaid**. The billing rules forbid simply re-parenting it, so the engine proposes a **change of ownership**: keep the historical account untouched, create a $0 Bellhaven successor, and link them." |
| **2:15–3:00 · Human approval** | #60 page: Approve → **Live preview & confirm** | "Nothing writes without a human. Approval records a decision bound to this exact proposal version. The live preview re-reads the CRM, re-checks the rules, blocks if a successor already exists, and shows the exact POST and PATCH. Then I type `APPLY 60`. The server must also have been started with writes enabled; in dry-run, everything is refused." |
| **3:00–3:45 · Verified execution** | **History** tab; **Queue** run 1 | "Every write is persisted, then read back and compared, and only then marked VERIFIED. **25 operations on 23 proposals**, all verified. Low-risk phone and name fixes ran through a controlled queue with a website re-check, a protected-field diff and stop-on-first-error. The audit also logs the refusals: wrong phrase, stale page, a held proposal." |
| **3:45–4:20 · Exceptions** | `docs/FINAL_RECONCILIATION_REPORT.md` §4–5 | "Not everything should be forced. Three old-operator records were **closed and preserved** rather than mislabelled as duplicates. Six cases stay on **HOLD** with a specific question for Bellhaven, for example Kettering's three records. Sandusky's link is verified, but the sale and the **$5,200** remain a documented exception. An unresolved case with its evidence is a valid result." |
| **4:20–5:00 · Monitoring** | Terminal: `scripts/run_daily.py` (with and without the flag) → Start Here schedule card → `docs/FINAL_AUDIT.md` | "The daily job is read-only and **refuses to run if writes are enabled**. Re-running finds **0 new** items. The dashboard shows the last scheduled run and failures. The 6 AM cron job is **installed and tested** on this Mac (configuration alone would satisfy the brief). The final audit re-checks every write against the live CRM: **integrity PASS**." |

## 2-minute demo video: BEFORE → WHAT I FOUND → HOW I DECIDED → AFTER

**Presentation view and teleprompter:** `docs/teleprompter.html`. Double-click it in Finder; it works offline.
- Each of the 7 beats has a visual panel built from authentic data, with its source shown.
- **S** = slide view (show it on screen) · **C** = narration only · ←/→ move between beats · **T** = 2:00 timer.
- The narration is **about 260 words, about 2:00** at roughly 130 words per minute. It's built around **three judgment moments**: Owosso's survivor, the predecessor realization, and Tiffin's financial protection.

| # | Time | Screen | Narration |
|---|---|---|---|
| 1 BEFORE | 0:00–0:18 | Slide 1 ("Before" panel) | Bellhaven's website lists thirty-five communities. The CRM had a hundred and twenty-one accounts, and only nine matched cleanly. The first full scan found thirty-five issues: wrong phones and names, wrong parent companies, duplicates, missing communities, and accounts with unpaid balances. |
| 2 Judgment 1 | 0:18–0:36 | Slide 2, or app `/proposal/56` (Owosso) | Here's what I noticed first: six addresses had more than one account. At Owosso, both belonged to Bellhaven, but one matched the website's phone and administrator. That gave me a defensible survivor, so the other was inactivated and linked. |
| 3 Judgment 2 | 0:36–0:58 | Slide 3, or app `/proposal/57` (Port Clinton) | But when I double-checked Monroe, Port Clinton and Erie, the extra records belonged to other parent companies. That's when I realized a previous operator's account isn't necessarily a duplicate. So I preserved them and documented what still needs confirming. Stricter identity checks also stopped two unsafe account creations. |
| 4 Judgment 3 | 0:58–1:19 | App **`/proposal/60`**, financial table | Tiffin was the third judgment call. It sat under Cedar Trail with eighty-four thousand dollars of revenue and twelve thousand four hundred still owed. Re-parenting it would break the billing rules, so I kept that history, created a new Bellhaven account at zero, and linked them. |
| 5 Approval | 1:19–1:34 | `/proposal/60` Decisions and Write log → **`/history`** | The system is deterministic Python; AI helped me build and review it, never to change the CRM. I approve, the live preview re-checks everything, I type APPLY, and the result is read back. |
| 6 Rejection | 1:34–1:41 | App **`/proposal/68`** (REJECTED) | Alliance's proposed status doesn't exist in the CRM, so I rejected it. Nothing was written. |
| 7 AFTER | 1:41–2:00 | Slide 7 (Before/After table) → Start Here | Now: twenty-five verified operations, twenty-three exact matches, an audit that passes, and a daily read-only scan. I didn't just build a system that finds differences. The business context decides what should actually change, and when a change shouldn't be made. |

**Before recording:**
- Run the app in **dry-run** at http://127.0.0.1:8020.
- Use two windows: the presentation in slide view, and the app.
- Crop the address bar.
- **No CRM write on camera.**
- Speak it as *your* investigation ("I noticed… I double-checked… I realized… I decided"), not as documentation.

## Live 45-minute walkthrough: preparation for the "small modification"

- **Run tests first and last:** `./bh test` (134 tests, about 1 s). Keep the server in dry-run while changing code.
- **Where common changes go:**
  - *Compare a new field* (e.g. care type): `app/normalize.py` (normalizer), `app/reconcile.py` (`_website_fields` and the field-diff block), then a test in `tests/test_matching.py`.
  - *Change matching strictness*: the street-similarity threshold and match tiers in `app/reconcile.py`.
  - *Add or tighten a safety rule*: `app/policy.py` (`check_ops`), then a test in `tests/test_policy.py`. The rule runs automatically at preview and execute time.
  - *Change queue eligibility*: `app/exec_queue.py` (`ALLOWED_FIELDS`, `MIN_NAME_SIMILARITY`), tests in `tests/test_queue.py`.
  - *Add a column or page*: route in `app/main.py`, template in `app/templates/`.
  - *Schedule*: `scripts/crontab.txt` or `.github/workflows/daily-reconcile.yml`.
- **Show the safety model while modifying:** only `executor.execute` writes; anything else, such as scans, GETs, tests and the scheduler, is proven write-free by tests.

## 45-minute live walkthrough: talking points

**The extended duplicates story (about 45–55 seconds, for the live session):**
> "One thing I noticed while double-checking the duplicates was that having two accounts at the same address didn't necessarily mean one needed to be inactivated. Take Owosso. Both accounts belonged to Bellhaven, but one matched the website's phone and administrator. That gave us a defensible survivor, so we linked and inactivated the duplicate. But then I looked at Monroe, Port Clinton and Erie. Those records had different parent companies, which suggested they might be previous operators rather than simple duplicates. That changed my approach. Instead of automatically inactivating them, I preserved the records and documented what we still needed to confirm. That's why I built human approval into the workflow. The system can find discrepancies, but the business context determines what we should actually change."

*Accuracy note:* the predecessor history is **possible, not proven**. The parents, names and $0 billing are consistent with it, but nothing in the CRM confirms it. Say you recognized the possibility and held back. Don't say you proved it.

**Investigations to walk through, each as *noticed → checked → realized → decided*:**

1. **Duplicates vs predecessors:** Owosso (inactivated) vs Monroe, Port Clinton and Erie (preserved). Alternatives considered: accidental duplicate, predecessor record, distinct facility. Why preserve: $0 billing means no financial risk either way, but a "Duplicate of" note would mislabel history.
2. **Tiffin and Marietta (change of ownership):** revenue and unpaid balance both above $0, so no direct re-parent. The old account keeps $84,000 / $12,400 and $51,250 / $3,800; the successors start at $0. Open question: who collects those balances?
3. **Lima (parent correction):** allowed because the unpaid balance was $0. Disclose that the $47,000 earned under Harborview now sits under Bellhaven, the same as the Findlay precedent.
4. **The unsafe creates the matching caught:** the first scan would have created Amberly Manor and Union Square. Stricter identity checks found look-alike records. Amberly turned out to be distinct (Colorado; Bellhaven isn't there), so #71 is pending. Union Square stays held.
5. **Technical vs business verification (Sandusky):** the link to Millstone is verified, but the sale and the $5,200 are not proven. The original investigation recommended holding it.
6. **"No account at this address" ≠ "no account" (Ashtabula):** the account exists under PO Box 517, kept pending a finance decision.
7. **Why six cases stay held:** each needs a fact that isn't in the data. Name the question for each (`FINAL_DECISION_REVIEW.md`).

**Likely questions, short answers:**
- *Why not just inactivate the Harborview records?* "Without billing or contacts, there was no financial reason to act, and labelling history as a duplicate would be wrong if they're predecessors."
- *Why did Sandusky run if it was uncertain?* "I authorized it. The write is verified, but I document the sale as unconfirmed rather than claim it's proven."
- *What would you build next?* Contacts reconciliation, a 'predecessor record' relationship type, transfer-date and AR-owner inputs for changes of ownership, and an identity-resolution UI (see `WRITEUP.md`).
- *How do you know nothing else changed?* The final audit compares every account changed since the original data load against the ledger: 25 writes, all verified, 0 unexplained.
- *Small modification on the spot?* See the code map below. Run `./bh test` before and after.

## Technical walkthrough (on request)
1. `app/scrape.py`, `app/reconcile.py`: website + CRM ingestion (fail-closed), address+ZIP matching, classification.
2. `app/policy.py`: billing / CHOW SOP and financial invariants.
3. `app/executor.py`: the **only** write path: approval bound to a fingerprint, live preview with plan token, typed confirmation, per-op persistence, read-back.
4. `app/exec_queue.py`: controlled queue (eligibility gate, website re-check, protected-field diff, stop-on-error).
5. `app/ledger.py`: SQLite ledger and append-only audit log.
6. `scripts/run_daily.py` (read-only schedule), `scripts/final_audit.py` (integrity audit).

## How a write would be made (not needed for the demo)
1. `CRM_WRITES_ENABLED=1 ./bh serve`.
2. Approve the proposal.
3. **Live preview & confirm**.
4. Type `APPLY <id>`.
5. Read-back. In dry-run every write is refused.

## Submission checklist
- [x] All 35 communities and all CRM accounts reconciled; evidence for every proposal
- [x] 25 CRM operations human-approved, executed and verified; integrity audit PASS
- [x] Unresolved cases documented with business questions (report §5)
- [x] 134 tests passing
- [x] Read-only daily schedule **installed** as a local cron job (06:00 daily, idempotent) and tested: run #14 PASS, failure capture PASS, 0 CRM writes
- [x] Code committed locally on branch `bellhaven-assessment`
- [x] Cross-checked against the original brief (welcome page): deadline Nov 16 2026 11:29 PM EST; schedule config only (no live cron needed); no hosting
- [x] Public GitHub repository: https://github.com/Giantlyra/bellhaven-crm-reconciliation (`.env`, `data/`, `investigation.txt` are gitignored; `docs/` contains assessment account IDs and phones)
- [ ] ~2-minute video showing evidence, approval, **rejection** and a verified CRM change (script above)
- [x] Honest actual time spent: approximately 5.5 hours of active work, excluding breaks and idle waiting (`docs/WRITEUP.md`, README)
- [x] Write-up: matching approach, AI tools used, what we'd build next (`docs/WRITEUP.md`). Confirm the AI-tools list
- [ ] Submit before **Nov 16 2026, 11:29 PM EST**
