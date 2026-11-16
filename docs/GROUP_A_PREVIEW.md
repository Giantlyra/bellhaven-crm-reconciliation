# Group A: consolidated validation preview (2026-11-16T04:17:39Z)

_Read-only. Live CRM re-read for every item; nothing written. **Not an authorization.** The CRM is unchanged and the server is in dry-run._

| # | Kind | App status | Pre-write validation (live) |
|---|---|---|---|
| #50 | FIELD_UPDATE | approved | ✅ clean |
| #59 | FIELD_UPDATE | approved | ✅ clean |
| #39 | WRONG_PARENT | pending | ✅ clean |
| #61 | WRONG_PARENT | pending | ✅ clean |
| #56 | DUPLICATE | pending | ✅ clean |
| #47 | WEBSITE_ONLY | pending | ✅ clean |
| #48 | WEBSITE_ONLY | pending | ✅ clean |
| #40 | FIELD_UPDATE | pending | ✅ clean |
| #62 | FIELD_UPDATE | pending | ✅ clean |

## Exact operations and checks

**#50** (FIELD_UPDATE): `PATCH /accounts/0013NUZQHQUEZ8DXEG` name: 'Chesterton Senior Commons' → 'Bellhaven of Chesterton'

**#59** (FIELD_UPDATE): `PATCH /accounts/001CF3LDWVRGL09P4F` billing_zip: '45626' → '45662'

**#39** (WRONG_PARENT): `PATCH /accounts/001LGFPBJY4N9MB6KL` parent_id: '001FJZYHR7MLFMNPLL' → '0015QAPLGS3FVYEEEM'
- Preview warnings: Direct re-parent allowed by SOP: outstanding AR is $0 (lifetime_revenue=$47,000, outstanding_ar=$0). Still requires explicit human approval.

**#61** (WRONG_PARENT): `PATCH /accounts/001H1JMVZWP46D5VUF` parent_id: '001FWSQ30SFW6S7604' → '0015QAPLGS3FVYEEEM'
- Preview warnings: Direct re-parent allowed by SOP: no revenue history (lifetime_revenue=$0, outstanding_ar=$0). Still requires explicit human approval. / CRM name 'Cedar Trail of Zanesville' differs from website 'Bellhaven of Zanesville' and the parent differs too: consistent with a rebrand/acquisition, but ownership is inferred from address only. Verify before approving.

**#56** (DUPLICATE): `PATCH /accounts/001QU150PM4Z15UA71` duplicate_of_account: '' → '001EGU7BMJ942ZTRE6'; status: 'Active' → 'Inactive'

**#47** (WEBSITE_ONLY): `POST /accounts` {"name": "Bellhaven of Batavia", "billing_street": "2000 Hospital Dr", "billing_city": "Batavia", "billing_state": "OH", "billing_zip": "45103", "phone": "(231) 698-3092", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"}
- Preview warnings: Creates a new CRM account. Verify the facility is not in the CRM under another name or address before approving.

**#48** (WEBSITE_ONLY): `POST /accounts` {"name": "Bellhaven of Carlisle", "billing_street": "640 Walnut Bottom Rd", "billing_city": "Carlisle", "billing_state": "PA", "billing_zip": "17015", "phone": "(260) 386-7765", "care_type": "Skilled Nursing", "parent_id": "0015QAPLGS3FVYEEEM", "status": "Active"}
- Preview warnings: Creates a new CRM account. Verify the facility is not in the CRM under another name or address before approving.

**#40** (FIELD_UPDATE): `PATCH /accounts/001LGFPBJY4N9MB6KL` phone: '(734) 872-9575' → '(231) 539-3617'

**#62** (FIELD_UPDATE): `PATCH /accounts/001H1JMVZWP46D5VUF` name: 'Cedar Trail of Zanesville' → 'Bellhaven of Zanesville'; phone: '(517) 817-8191' → '(814) 599-2533'

## Dependencies and execution stages (the batch refuses overlapping accounts by design)

- **Stage 1, one batch (no overlaps: none):** #50, #59, #39, #61, #56, #47, #48.
- **Stage 2, a separate batch after stage 1 is read-back verified:** #40 (same account as #39) and #62 (same account as #61). Their previews are taken after #39/#61 verify, and the drift check accepts only values this engine wrote and read back.
- Each item is individually approved, previewed, policy-checked, written, read back and audited. The batch stops at the first failure.
- #49 and #66 are **not** in Group A (see the plan note); they remain approved-not-executed until you confirm.
