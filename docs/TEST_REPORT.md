# Automated test report

Generated from `data/test_report.json`, written by `./bh test` at **2026-11-15T23:02:10+00:00**: **112 passed in 0.77s**, exit code 0. _Latest run 2026-11-16: **130 passed** (adds `tests/test_queue.py`)._

Environment: Python 3.9.6 (`.venv`), pytest. Every test uses an in-memory fake CRM (`tests/conftest.py::FakeCRM`) and an in-memory or temporary SQLite database. Live writes are forced off unless a test explicitly opts in, and then only on the fake. **No test contacts the live CRM.** The one subprocess test (`test_daily_job_refuses_to_start_with_writes_enabled`) checks that `scripts/run_daily.py` exits before it imports the CRM client.

Re-run with `./bh test`, or the **Test** tab ("Run test suite now"). Both rewrite `data/test_report.json`; this file is a snapshot of it.

## Required scenarios and where they are tested

| Scenario | Tests (all passing) |
|---|---|
| Incomplete ingestion | `test_failed_scrape_page_marks_incomplete_and_skips_crm_only`, `test_incomplete_scrape_creates_no_proposals`, `test_fewer_facilities_than_homepage_count_fails_closed`, `test_incomplete_scan_never_resolves_open_items`, `test_crm_listing_failure_fails_run`, `test_failed_scrape_never_flags_crm_only` |
| Duplicate survivor selection | `test_owosso_survivor`, `test_duplicates_survivor_is_bellhaven_parented`, `test_duplicate_survivor_needs_decisive_evidence`, `test_indistinguishable_same_address_accounts_are_held_not_guessed`, `test_duplicate_loser_with_billing_history_is_held`, `test_duplicate_inactivation` |
| Changed or missing financial data | `test_recheck_blocks_reparent_if_account_became_protected`, `test_direct_reparent_blocked_when_account_became_chow_protected`, `test_chow_blocks_when_financials_change_after_proposal`, `test_chow_blocks_when_financials_become_missing`, `test_missing_or_malformed_financials_block`, `test_sibling_tolerance_does_not_bypass_financial_policy` |
| CHOW partial failure and recovery | `test_chow_partial_failure_retry_does_not_recreate`, `test_chow_partial_failure_resume_needs_fresh_confirmation_and_reuses_successor`, `test_uncertain_create_is_resolved_by_lookup_not_blind_retry`, `test_chow_blocked_when_successor_already_exists`, `test_chow_preserves_all_financials_and_parent`, `test_interrupted_chow_execution_resumes_without_second_create`, `test_second_concurrent_execution_is_refused` |
| Repeated approvals and re-execution | `test_repeated_approval_is_refused_and_recorded_once`, `test_verified_proposal_cannot_be_executed_again`, `test_approval_from_another_proposal_version_does_not_authorize`, `test_superseded_approval_cannot_execute`, `test_reverted_proposal_reopens_pending_never_approved`, `test_nine_card_decisions_are_not_execution_approvals` |
| Idempotency and safe reruns | `test_rerun_does_not_repropose_decided_items`, `test_rerun_unchanged_is_noop`, `test_material_change_creates_new_proposal_and_supersedes_pending`, `test_website_fingerprint_ignores_fetch_timestamps`, `test_findlay_receipt_marks_stale_proposal_resolved` |
| Rejected proposals | `test_rejected_never_writes`, `test_rejected_via_ui_never_executes` |
| Read-back verification | `test_readback_mismatch_marks_failed`, `test_readback_failure_never_reports_success`, `test_approved_field_update_writes_and_verifies`, `test_sibling_proposals_on_one_account_both_verify` |
| Zero writes from scans, GETs and the scheduler | `test_pipeline_never_writes`, `test_scan_and_every_get_route_never_write`, `test_scheduled_scan_makes_zero_writes_and_is_reported`, `test_failed_scheduled_scan_is_shown_as_failure`, `test_daily_job_refuses_to_start_with_writes_enabled` |
| Authorization gates | `test_approval_alone_never_writes`, `test_writes_disabled_by_default_blocks_execution`, `test_wrong_confirmation_phrase_refused`, `test_state_change_between_preview_and_confirm_is_refused`, `test_dry_run_server_refuses_confirmed_write`, `test_post_without_csrf_is_refused`, `test_cross_origin_post_refused`, `test_legacy_findlay_route_refuses_in_dry_run` |

## All cases

### test_bellhaven_snapshot: 7/7 passed (Case expectations on the private snapshot (skips if absent))

- PASS `test_holds`
- PASS `test_chow_marietta_tiffin_never_direct_reparent`
- PASS `test_lima_direct_reparent`
- PASS `test_owosso_survivor`
- PASS `test_aliases_are_reviewable_renames`
- PASS `test_carlisle_and_batavia_not_conflated`
- PASS `test_findlay_pre_fix_snapshot_proposal_is_exactly_the_applied_change`

### test_executor: 9/9 passed (CHOW, duplicate, read-back, rejection, stale data)

- PASS `test_chow_creates_and_links_and_preserves_original`
- PASS `test_chow_partial_failure_retry_does_not_recreate`
- PASS `test_uncertain_create_is_resolved_by_lookup_not_blind_retry`
- PASS `test_duplicate_inactivation`
- PASS `test_rejected_never_writes`
- PASS `test_pending_cannot_execute_without_approval`
- PASS `test_approved_field_update_writes_and_verifies`
- PASS `test_readback_mismatch_marks_failed`
- PASS `test_stale_record_conflict_stops_write`

### test_finalization: 15/15 passed (Sibling drift, batch overlap, content fingerprint, legacy route gate, identity resolutions)

- PASS `test_sibling_proposals_on_one_account_both_verify`
- PASS `test_unexplained_drift_still_blocks`
- PASS `test_drift_to_a_value_we_did_not_write_still_blocks`
- PASS `test_sibling_tolerance_does_not_bypass_financial_policy`
- PASS `test_batch_with_shared_account_is_refused_before_any_write`
- PASS `test_batch_overlaps_reports_duplicate_survivor_shared_with_phone_fix`
- PASS `test_website_fingerprint_ignores_fetch_timestamps`
- PASS `test_legacy_findlay_route_refuses_in_dry_run`
- PASS `test_distinct_resolution_turns_identity_hold_into_create_and_leaves_lookalike_alone`
- PASS `test_survivor_resolution_produces_normal_proposals`
- PASS `test_resolution_only_for_open_web_holds`
- PASS `test_revoked_resolution_restores_hold_and_resolutions_are_append_only`
- PASS `test_stale_survivor_resolution_is_ignored_and_hold_returns`
- PASS `test_reverted_proposal_reopens_pending_never_approved`
- PASS `test_batch_items_that_only_read_the_same_survivor_do_not_conflict`

### test_idempotency: 7/7 passed (Re-runs, supersede, pagination, scrape failure)

- PASS `test_rerun_does_not_repropose_decided_items`
- PASS `test_rerun_unchanged_is_noop`
- PASS `test_material_change_creates_new_proposal_and_supersedes_pending`
- PASS `test_pipeline_never_writes`
- PASS `test_crm_pagination_fetches_all_pages`
- PASS `test_website_pagination_and_homepage_only_listing`
- PASS `test_failed_scrape_page_marks_incomplete_and_skips_crm_only`

### test_matching: 10/10 passed (Matching tiers and false-positive guards)

- PASS `test_exact_match_ok`
- PASS `test_field_update_outdated_name_same_address`
- PASS `test_similar_name_different_address_is_not_matched`
- PASS `test_ambiguous_same_city_similar_name_conflicting_address`
- PASS `test_po_box_name_match_supported_by_phone`
- PASS `test_website_only`
- PASS `test_duplicates_survivor_is_bellhaven_parented`
- PASS `test_crm_only_flagged_not_deactivated`
- PASS `test_failed_scrape_never_flags_crm_only`
- PASS `test_superseded_accounts_are_not_candidates`

### test_policy: 9/9 passed (Billing SOP and financial parsing)

- PASS `test_revenue_and_ar_requires_chow`
- PASS `test_direct_reparent_when_not_protected[40000-0]`
- PASS `test_direct_reparent_when_not_protected[0-2000]`
- PASS `test_direct_reparent_when_not_protected[0-0]`
- PASS `test_missing_or_malformed_financials_block[None-0]`
- PASS `test_missing_or_malformed_financials_block[-5]`
- PASS `test_missing_or_malformed_financials_block[100-n/a]`
- PASS `test_missing_or_malformed_financials_block[True-5]`
- PASS `test_recheck_blocks_reparent_if_account_became_protected`

### test_requirements: 14/14 passed (Repeated approvals, re-execution, CHOW financial change/missing, CHOW resume, scheduler, UI states)

- PASS `test_repeated_approval_is_refused_and_recorded_once`
- PASS `test_verified_proposal_cannot_be_executed_again`
- PASS `test_approval_from_another_proposal_version_does_not_authorize`
- PASS `test_chow_blocks_when_financials_become_missing`
- PASS `test_chow_blocks_when_financials_change_after_proposal`
- PASS `test_chow_partial_failure_resume_needs_fresh_confirmation_and_reuses_successor`
- PASS `test_scheduled_scan_makes_zero_writes_and_is_reported`
- PASS `test_failed_scheduled_scan_is_shown_as_failure`
- PASS `test_daily_job_refuses_to_start_with_writes_enabled`
- PASS `test_dashboard_shows_lifecycle_states_completeness_and_schedule`
- PASS `test_executing_state_is_labelled_and_never_called_applied`
- PASS `test_chat_and_ask_routes_are_not_part_of_the_app`
- PASS `test_interrupted_chow_execution_resumes_without_second_create`
- PASS `test_second_concurrent_execution_is_refused`

### test_safety: 34/34 passed (Risk & validation, executor gates, audit/state, fail-closed ingestion, Findlay receipt)

- PASS `test_indistinguishable_same_address_accounts_are_held_not_guessed`
- PASS `test_duplicate_survivor_needs_decisive_evidence`
- PASS `test_duplicate_loser_with_billing_history_is_held`
- PASS `test_chow_predecessor_is_not_field_edited`
- PASS `test_reparent_is_separate_from_field_edits`
- PASS `test_hold_cannot_be_approved`
- PASS `test_approval_alone_never_writes`
- PASS `test_writes_disabled_by_default_blocks_execution`
- PASS `test_wrong_confirmation_phrase_refused[]`
- PASS `test_wrong_confirmation_phrase_refused[apply 1]`
- PASS `test_wrong_confirmation_phrase_refused[APPLY 999]`
- PASS `test_wrong_confirmation_phrase_refused[yes]`
- PASS `test_state_change_between_preview_and_confirm_is_refused`
- PASS `test_superseded_approval_cannot_execute`
- PASS `test_direct_reparent_blocked_when_account_became_chow_protected`
- PASS `test_chow_blocked_when_successor_already_exists`
- PASS `test_chow_preserves_all_financials_and_parent`
- PASS `test_already_in_desired_state_is_resolved_without_write`
- PASS `test_drift_to_a_different_value_is_a_conflict`
- PASS `test_noop_proposal_resolves_without_write`
- PASS `test_readback_failure_never_reports_success`
- PASS `test_batch_excludes_chow_and_requires_phrase`
- PASS `test_batch_executes_each_individually`
- PASS `test_audit_log_is_append_only`
- PASS `test_migrates_old_ledger_in_place`
- PASS `test_findlay_receipt_marks_stale_proposal_resolved`
- PASS `test_unverified_legacy_attempt_is_not_a_receipt`
- PASS `test_findlay_live_state_produces_no_proposal`
- PASS `test_nine_card_decisions_are_not_execution_approvals`
- PASS `test_incomplete_scrape_creates_no_proposals`
- PASS `test_fewer_facilities_than_homepage_count_fails_closed`
- PASS `test_incomplete_scan_never_resolves_open_items`
- PASS `test_crm_listing_failure_fails_run`
- PASS `test_pipeline_saves_fingerprinted_snapshot`

### test_web: 7/7 passed (Web layer: no writes on GET, CSRF, origin, dry-run, token)

- PASS `test_scan_and_every_get_route_never_write`
- PASS `test_post_without_csrf_is_refused`
- PASS `test_cross_origin_post_refused`
- PASS `test_dry_run_server_refuses_confirmed_write`
- PASS `test_full_ui_flow_with_writes_enabled`
- PASS `test_rejected_via_ui_never_executes`
- PASS `test_removed_token_bearing_redirect`

## Live (non-test) verification in this review

- `./bh scan`: live read-only scan #9 completed. 35 facilities, 121 accounts, 0 new and 35 known proposals, 0 write calls.
- Read-only diff of `data/snapshot.json`, the ledger baselines and scan #9. The only difference is the verified Findlay parent write; there is 0 baseline drift across the 35 open proposals.
- `./bh serve --port 8020` (dry-run): 14 pages returned HTTP 200 with the DRY-RUN banner. The server was stopped afterwards, and ledger operations stayed at 0.
