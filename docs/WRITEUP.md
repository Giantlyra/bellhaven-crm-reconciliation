# Write-up: Bellhaven CRM Reconciliation

_Clipboard Health · Sales Operations Analyst assessment. Submission deadline: Nov 16 2026, 11:29 PM EST._

## The problem

Bellhaven Senior Living's public website lists **35 communities**. The assessment CRM had **121 accounts** with several problems:
- stale names, phones and ZIPs;
- communities under the wrong parent company, including acquisitions from Harborview (2025) and Cedar Trail (2026);
- duplicates, and two facilities missing entirely;
- accounts carrying billing history that the change-of-ownership rules require us to preserve.

The goal: reconcile the CRM to the website, change only what is justified, never damage financial history, and keep running daily.

## Matching approach

1. **Ingest everything, or nothing.**
   - Scrape the directory's pagination **and** every `/communities/<slug>` link on the homepage. One community, Findlay, is linked only from the homepage: 35 found, 34 in the directory.
   - Read every CRM page.
   - If any page fails or counts don't add up, the run is marked incomplete and **no proposals are made**.
2. **Normalize:** street suffixes and directions (Rd/Road, NW/Northwest), 5-digit ZIP, 10-digit phone, and a name "core".
3. **Identity is decided by location, not by name.**
   - Exact street+ZIP first; then same street number + ZIP with ≥ 0.8 street similarity.
   - Last, a same-city similar name, but only if supported by a matching phone or a PO-box address.
   - **A name alone never decides identity.** Amberly Manor exists in the CRM, but in Colorado; "Carlisle PA" is not "New Carlisle OH".
4. **Classify each case** as one of:
   - **field update** (identity unchanged; the website's name, phone or ZIP wins);
   - **parent correction**;
   - **change of ownership (CHOW)**: revenue > 0 **and** AR > 0, so the old account is preserved, a successor is created under Bellhaven at $0/$0, and the two are linked;
   - **duplicate**: a survivor must win on decisive evidence, otherwise the case is held;
   - **new account**, after searching for alternative names;
   - **HOLD**: insufficient or conflicting evidence, which becomes a business question instead of a guess.
5. **Human-in-the-loop execution.** Every write requires all of:
   - an approval bound to the proposal's fingerprint;
   - a fresh live preview, which re-reads the CRM, re-checks the rules, detects drift and blocks duplicate successors;
   - a typed `APPLY <id>`;
   - a server explicitly started with writes enabled.

   Every write is then **read back** and compared before it counts as VERIFIED. All decisions and writes go to an append-only SQLite audit log.
6. **Daily monitoring:** a read-only scheduled scan (`scripts/run_daily.py`). It refuses to run if writes are enabled. Configured as a cron line (`scripts/crontab.txt`), **installed and tested on the author's Mac** (06:00 daily, logs to `data/daily.log`), and as a GitHub Actions workflow (`.github/workflows/daily-reconcile.yml`, which has no token secret on GitHub). A read-only `scripts/final_audit.py` re-verifies every write against the live CRM.

## Results

- **25 CRM operations on 23 proposals, all read-back VERIFIED.** The final audit shows integrity PASS: protected fields and contacts intact, and no change outside the ledger.
  - 15 field updates. Five of them ran through a controlled low-risk queue with stop-on-error.
  - 2 parent corrections (Lima, Zanesville; AR $0).
  - 1 same-parent duplicate (Owosso).
  - 2 new accounts (Batavia OH, Carlisle PA).
  - 3 changes of ownership. Tiffin and Marietta: the historical accounts keep $84,000/$12,400 and $51,250/$3,800. Sandusky is linked to Millstone.
- **Closed without a write:**
  - Three old-operator records were preserved as likely predecessor records, not labelled duplicates.
  - Two proposals were rejected because they would have set a status value the CRM doesn't use.
- **Left open on purpose, with a business question each:** Kettering (3 records), Union Square, Monroe/Cedar Trail, the Ashtabula PO box, two renames, and Hudson OH (#71, pending).
  - Documented exceptions: the Sandusky sale and its $5,200 AR, and who collects the Tiffin and Marietta balances.
- **23 of 35** communities now match the CRM exactly; every remaining difference is a documented case.
- **130 automated tests** run on a mocked CRM and temporary SQLite.

Details: `docs/FINAL_RECONCILIATION_REPORT.md`, `docs/FINAL_AUDIT.md`, `docs/CRM_CHANGE_HISTORY.md`.

## AI tools used

- **The application itself uses no AI at runtime.** Matching, classification, policy and execution are deterministic Python, so every decision is reproducible and testable.
- **Claude Code (Anthropic):** implementation, refactoring and tests; read-only CRM and website verification; evidence tables; independent read-back checks after each authorized write; documentation.
- **ChatGPT (OpenAI):** business reasoning and second opinions. It drafted the review prompts (evidence → alternative explanations → risk challenge → historical consistency → recommendation) and challenged recommendations before decisions.
- **Every CRM write was approved and confirmed by me personally in the app.** The AI tools prepared evidence and code; they never authorized changes.
- _Confirm or edit this list before submitting._

## What we'd build next

1. **Contacts reconciliation.** Compare website administrators with CRM contacts, and move or flag contacts left on inactivated or historical accounts (for example the Owosso Admissions contact).
2. **A first-class "predecessor record" relationship.** Mark old-operator records as history with accurate wording, instead of forcing them into "duplicate" or leaving them unlabelled.
3. **Ownership confirmation inputs.** Capture the transfer date, a source document and the AR-collection owner on each change of ownership, so the inferred cases (Sandusky, Tiffin, Marietta) become confirmed.
4. **Identity-resolution UI and survivor tooling** for multi-record sites like Kettering. Today this is a CLI command.
5. **Production scheduling:** turn on the GitHub Actions workflow with the secret, persist the ledger, alert on failed or incomplete scans, and send a daily diff of new discrepancies to the owner.
6. **Read-back tolerance and idempotency:** normalized comparisons (such as phone formats) and API idempotency keys for creates.
7. **Multi-user auth and roles,** so approvals record a real reviewer identity instead of `local-reviewer`.

## Time spent

_Fill in your honest total before submitting._
