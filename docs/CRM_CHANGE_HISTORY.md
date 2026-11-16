# Verified CRM change history

A change is listed here only if a **read-back from the CRM API** confirmed it. Approvals, previews and proposals are
not changes.

As of 2026-11-16 03:27 UTC there are **twelve** verified CRM changes:

1. The Findlay re-parent, made before this engine existed.
2. Proposal #43, the Monroe phone fix.
3. Proposal #58, the Port Clinton phone fix (Wave A).
4. Proposal #65, the Erie phone fix (Wave A).
5. Proposal #52, the Goshen phone fix (Wave A).
6. Proposal #55, the Marion phone fix (Wave A).
7. Proposal #45, the Findlay phone fix (Wave A).
8–12. Proposals #37, #44, #51, #63 and #67: Wave A field fixes run through the controlled execution queue.

The engine has made 11 write calls in total.

## 1. Findlay parent correction (verified)

| Field | Value |
|---|---|
| Account | `001UKEFGADQ8YCZ4YM` Bellhaven Meadows of Findlay, 1800 N Blanchard St, Findlay OH 45840 |
| Change | `parent_id`: "" (blank) → `0015QAPLGS3FVYEEEM` (Bellhaven Senior Living (Parent Account)) |
| Financial context | lifetime revenue $22,000, outstanding AR $0, so the SOP allows a direct re-parent. Financial fields were not sent |
| Request | `PATCH /api/v1/accounts/001UKEFGADQ8YCZ4YM` via the guarded Findlay page (`app/proposals.py`), with an explicit operator confirmation |
| Audit events (`data/execution_audit.db`, read-only) | `2026-11-15T10:14:01.324005Z STARTED` "PATCH parent_id to Bellhaven parent"; `2026-11-15T10:14:01.482342Z VERIFIED` "Read-back parent_id matches target; financial fields were not sent" |
| Imported receipt (`data/ledger.db`, `legacy_receipts`) | `001UKEFGADQ8YCZ4YM.parent_id = 0015QAPLGS3FVYEEEM`, verified_at 2026-11-15T10:14:01.482342Z |
| Live confirmation since | Every live scan from #3 to #9 shows `parent_id = 0015QAPLGS3FVYEEEM` and CRM `updated_at = 2026-11-15 10:14:01Z`. The pre-Findlay `data/snapshot.json` differs from live data **only** in this account's `parent_id`, `parent_name` and `updated_at` |
| Status | **Verified. Do not retry.** On stale data the engine marks a re-derived proposal RESOLVED; on live data Findlay is a clean match. The legacy route now refuses in dry-run |

## 2. Engine-executed changes

### 2.1 #43 Monroe phone correction (verified 2026-11-16 01:17:47 UTC)

| Field | Value |
|---|---|
| Account | `001U1750VLVJAGG1S5` Bellhaven Gardens of Monroe, 750 Stewart Rd, Monroe MI 48162 (Bellhaven parent, $0 / $0) |
| Change | `phone`: (814) 291-2902 → (814) 412-2218, the live website value |
| Authorization | Approved 01:17:13 UTC; preview token `9294078faccde24d69d2d791`; confirmed by typing `APPLY 43` at 01:17:47 UTC (actor `local-reviewer`) |
| Request | `PATCH /api/v1/accounts/001U1750VLVJAGG1S5` `{"phone": "(814) 412-2218"}`. Only this field was sent |
| Ledger | `decisions` #1–#2, `operations` #1 (verified), `audit_log` #88–#97, read-back receipt ok |
| Pre-write snapshot | `data/pre_43_001U1750VLVJAGG1S5.json` |
| Independent live re-check | A later GET in the same session showed phone = (814) 412-2218 and `updated_at` 2026-11-16 01:17:47Z. Parent, status and financials were unchanged |

### 2.2 #58 Port Clinton phone correction, Wave A (verified 2026-11-16 02:47:11 UTC)

| Field | Value |
|---|---|
| Account | `001UELXDAKFRKB8932` Bellhaven of Port Clinton, 1420 Harbor Point Dr, Port Clinton OH 43452 (Bellhaven parent, $0 / $0) |
| Change | `phone`: (614) 512-8712 → (330) 733-6423, the live website value |
| Authorization | User authorized in chat ("Authorize #58"). In-app Approve at 02:46:43 UTC, preview token `0db421a14d4ab471178ee7d4` at 02:46:57, `APPLY 58` typed at 02:47:11 (actor `local-reviewer`) |
| Request | `PATCH /api/v1/accounts/001UELXDAKFRKB8932` `{"phone": "(330) 733-6423"}`. Only this field was sent |
| Ledger | `decisions` #3–#4, `operations` #2 (verified), `audit_log` #100–#109, app read-back ok |
| Independent read-back | Full-record diff against `data/wave_a_pre_execution_snapshot.json`: **only** `phone` and `updated_at` (→ 2026-11-16 02:47:11Z) changed. Parent, status, revenue, AR, links, note, name and address are unchanged; contacts are unchanged |
| Related record | Harborview account `001JD2MWRA74LTSN24`, held as #57, is untouched: (216) 314-1338, Active, `updated_at` 2026-11-15 04:29:11Z |
| Backup | `data/ledger.pre-58.db` |

### 2.3 #65 Erie phone correction, Wave A (verified 2026-11-16 02:52:27 UTC)

| Field | Value |
|---|---|
| Account | `001CVBBCSDM7YHN220` Bellhaven Shores of Erie, 4930 W Lake Rd, Erie PA 16505 (Bellhaven parent, $0 / $0) |
| Change | `phone`: (419) 495-1741 → (614) 792-9343, the live website value |
| Authorization | User authorized in chat ("Authorize #65"). In-app Approve at 02:51:53 UTC, preview token `2739c3488cc548221cb18b5d` at 02:52:18, `APPLY 65` typed at 02:52:27 (actor `local-reviewer`) |
| Request | `PATCH /api/v1/accounts/001CVBBCSDM7YHN220` `{"phone": "(614) 792-9343"}`. Only this field was sent |
| Ledger | `decisions` #5–#6, `operations` #3 (verified), `audit_log` #110–#119, app read-back ok |
| Independent read-back | Full-record diff against `data/wave_a_pre_execution_snapshot.json`: **only** `phone` and `updated_at` (→ 2026-11-16 02:52:27Z) changed. Contacts are unchanged |
| Related record | Harborview account `001BLYF02K97SZLZHH`, held as #64, is untouched: (517) 775-8456, Active, `updated_at` 2026-11-15 04:29:11Z |
| Backup | `data/ledger.pre-65.db` |

### 2.4 #52 Goshen phone correction, Wave A (verified 2026-11-16 02:58:21 UTC)

| Field | Value |
|---|---|
| Account | `001JQER1RMYKNRLNME` Bellhaven of Goshen, 1610 College Avenue, Goshen IN 46526 (Bellhaven parent, $121,000 / AR $0) |
| Change | `phone`: (517) 409-8156 → (330) 405-6040, the live website value |
| Authorization | User authorized in chat. In-app Approve at 02:53:34 UTC; preview token `07996dc1101a4104401543d3`; `APPLY 52` at 02:58:21 (actor `local-reviewer`). An earlier `APPLY 52` was **refused** by the dry-run gate (audit #123); nothing was written by it |
| Request | `PATCH /api/v1/accounts/001JQER1RMYKNRLNME` `{"phone": "(330) 405-6040"}`. Only this field was sent |
| Ledger | `decisions` #7–#8, `operations` #4 (verified), `audit_log` #120–#131, app read-back ok |
| Independent read-back | Full-record diff against `data/wave_a_pre_execution_snapshot.json`: **only** `phone` and `updated_at` (→ 2026-11-16 02:58:21Z) changed. Revenue $121,000 and AR $0 are unchanged; contacts are unchanged |
| Backup | `data/ledger.pre-52.db` |

### 2.5 #55 Marion phone correction, Wave A (verified 2026-11-16 03:00:50 UTC)

| Field | Value |
|---|---|
| Account | `0015L38R1Z5947ZZP7` Bellhaven of Marion, 199 Barks Road West, Marion OH 43302 (Bellhaven parent, $87,000 / AR $0) |
| Change | `phone`: (330) 314-3109 → (517) 847-7948, the live website value |
| Authorization | User authorized in chat. In-app Approve at 03:00:30 UTC; preview token `78c5e0ede640f7916f28c141`; `APPLY 55` at 03:00:50 (actor `local-reviewer`) |
| Request | `PATCH /api/v1/accounts/0015L38R1Z5947ZZP7` `{"phone": "(517) 847-7948"}`. Only this field was sent |
| Ledger | `decisions` #9–#10, `operations` #5 (verified), `audit_log` #132–#141 |
| Independent read-back | Full-record diff against `data/wave_a_pre_execution_snapshot.json`: **only** `phone` and `updated_at` (→ 2026-11-16 03:00:50Z) changed. Revenue, AR and contacts unchanged |
| Backup | `data/ledger.pre-55.db` |

### 2.6 #45 Findlay phone correction, Wave A (verified 2026-11-16 03:05:33 UTC)

| Field | Value |
|---|---|
| Account | `001UKEFGADQ8YCZ4YM` Bellhaven Meadows of Findlay, 1800 N Blanchard St, Findlay OH 45840 (Bellhaven parent, $22,000 / AR $0) |
| Change | `phone`: (330) 975-2492 → (231) 533-2969, the live website value. This is separate from the legacy `parent_id` correction (§1) |
| Authorization | In-app Approve at 03:01:56 UTC; the first execute attempts (audit #145 and #147) were **refused** by the dry-run gate and wrote nothing. After the server was restarted with live writes, preview token `5edfe56639bd9ce89c259943` and `APPLY 45` at 03:05:33 (actor `local-reviewer`) |
| Request | `PATCH /api/v1/accounts/001UKEFGADQ8YCZ4YM` `{"phone": "(231) 533-2969"}`. Only this field was sent |
| Ledger | `decisions` #11–#12, `operations` #6 (verified), `audit_log` #142–#155 |
| Independent read-back | Full-record diff against `data/wave_a_pre_execution_snapshot.json`: **only** `phone` and `updated_at` (→ 2026-11-16 03:05:33Z) changed. `parent_id` is still Bellhaven; revenue $22,000 and AR $0 are unchanged; contacts unchanged |
| Backup | `data/ledger.pre-45.db` |

### 2.7 Controlled execution queue run 1: #37, #44, #51, #63, #67 (verified 2026-11-16 03:26:52–03:26:55 UTC)

| Field | Value |
|---|---|
| Authorization | Each record was approved by the user in the app (03:20 UTC). The read-only queue validation showed 5 of 5 ready. The user typed `APPLY QUEUE OF 5`; one earlier attempt with a mismatched phrase was refused before any write. |
| Receipt | `data/queue_receipts/queue-20261116T032655Z.json`. Audit `queue_started` #176 · `queue_item` #184, #192, #200, #208, #216 · `queue_finished` #217 (stopped=false) |
| Independent read-back | Live GET of each account diffed against `data/wave_a_pre_execution_snapshot.json`: only the approved fields plus `updated_at` changed. Parent (Bellhaven), status, revenue, AR, links and note are unchanged; contacts are unchanged. Each receipt's after-values equal the live CRM |
| Backup | `data/ledger.pre-queue2.db` |

| # | Account | Change | Revenue / AR | Ledger |
|---|---|---|---|---|
| #37 | `00191H7JR16471SZ34` Bellhaven at Sycamore Ridge (Sycamore Ridge) | name: Bellhaven of Sycamore Ridge → Bellhaven at Sycamore Ridge; phone: (419) 982-7764 → (260) 365-6510 | $0 / $0 | decision #18, op #7, queue_item #184, 03:26:52 UTC |
| #44 | `001RJ0D7Z5MAZN5HX5` Bellhaven Healthcare Centre of Ashland | name: Bellhaven Health Care Center of Ashland → Bellhaven Healthcare Centre of Ashland; phone: (734) 319-7813 → (517) 314-5115 | $0 / $0 | decision #19, op #8, queue_item #192, 03:26:53 UTC |
| #51 | `001R4PXTUD9R6FNN8V` Bellhaven of Defiance | phone: (231) 238-4862 → (330) 691-2711 | $66,000 / AR $9,500 (unchanged) | decision #20, op #9, queue_item #200, 03:26:54 UTC |
| #63 | `001TZCSTBZFM6K5BGN` Bellhaven Rehabilitation & Nursing of Grove City | name: Bellhaven Rehab and Nursing of Grove City → Bellhaven Rehabilitation & Nursing of Grove City | $0 / $0 | decision #21, op #10, queue_item #208, 03:26:54 UTC |
| #67 | `0010KJFP601YNTZVDA` The Arbors at Bellhaven - Dayton | name: Arbors at Bellhaven Dayton → The Arbors at Bellhaven - Dayton; phone: (216) 659-9837 → (260) 254-7592 | $0 / $0 | decision #22, op #11, queue_item #216, 03:26:55 UTC |

The other proposals are not affected by these changes. As of queue run 1 there are 21 PENDING, 3 HELD and 11 VERIFIED (#43, #58, #65, #52, #55, #45, #37, #44, #51, #63, #67). Earlier local
approvals, including the nine-card console's "APPROVE Marietta", are not authorizations.

When you execute approved items, each verified change appears automatically:

- **History** tab: "CRM write attempts by this engine", with per-operation `started → succeeded → verified`, the returned ids and the read-back receipt in the audit log.
- `./bh status`: the "CRM write calls ever" count.
- `sqlite3 data/ledger.db "select proposal_id, op_type, account_id, status, returned_id, updated_at from operations"`.

After the session, add each VERIFIED item to this file, or point reviewers to the History tab. Don't list FAILED or
BLOCKED items as changes.
