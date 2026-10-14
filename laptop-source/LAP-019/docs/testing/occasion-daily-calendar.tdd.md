# Daily occasion calendar — TDD evidence

User journey: the owner never needs to name today's festival. Daily automation
identifies upcoming occasions, verifies dates, retains the calendar, generates
bounded batches and reports incomplete discovery instead of a false zero-event success.

## RED

- `88ae717`: `python -m unittest occasion.tests.test_discovery` failed because
  the discovery module did not exist.
- `b413413`: CLI tests failed on missing `discover`, `calendar-health`, `--batch`;
  day-persistence and disabled-brand tests failed on their intended behavior.

## GREEN

`python -m unittest discover -s occasion/tests -p "test_*.py"` passed 75 tests
on Windows Python 3.12.
Coverage of discovery: 92%; combined discovery/CLI: 85%; full engine: 82%.
Ubuntu/Windows CI exercises the same suite.

| Guarantee | Test |
| --- | --- |
| Gandhi identified without daily owner input, even when AI fails | test_gandhi_is_identified_without_owner_input_or_ai_success |
| Verified dates persist between days | test_discovered_occurrences_survive_next_day_without_reidentification |
| One reserved model HTTP attempt per IST date, including failures | test_api_attempt_is_persisted_before_call_and_failure_cannot_reburn_quota |
| Exact official excerpt proves the date, not model memory | test_ai_invented_quote_or_date_cannot_be_locked |
| Government table year and weekday reject stale/OCR dates | test_weekday_checks_reject_ocr_wrong_dates_and_stale_calendar_year |
| Existing dates, brand visuals and sensitivity are not overwritten | test_conflict_with_locked_occurrence_is_held_not_overwritten; test_existing_brand_visuals_and_sensitive_policy_cannot_be_overridden |
| Source failure is degraded, not healthy zero | test_zero_sources_and_ai_failure_is_alert_not_healthy_zero |
| Extra jobs defer, not abort everything | test_batch_mode_defers_excess_jobs_instead_of_aborting_all |
| One calendar warning per day; receipt only after Telegram accepts | test_degraded_calendar_alert_is_sent_once_and_retained_on_failure |
| Official URL, redirect, response size/page limits | fetch/redirect tests in test_discovery.py |

Live read-only smoke test: the Survey of India government PDF supplied 13
weekday-validated gazetted rows, including Gandhi Jayanti on 2026-10-02.
This smoke test used no Gemini/Higgsfield credits and sent no Telegram message.

## Boundaries and known limitations

- Grounded discovery considers India/state/religious, China and global occasions
  over a rolling 14-day window. It is not a guarantee of exhaustive world coverage.
- Fetchable official evidence is required to auto-lock AI suggestions. Inaccessible,
  conflicting, partisan/sensitive or unproved candidates are held and reported.
- The deterministic PDF adapter is for 2026 Indian gazetted holidays, not every
  regional/restricted holiday. A future-year missing adapter emits a warning;
  grounded discovery can still verify year-specific official sources.
- At most 12 AI candidates/day; production caps six jobs per batch. Re-runs use
  the durable attempt/report and produced state, not repeated calendar API calls.
  The daily attempt guarantee depends on retaining the journal: catastrophic
  runner loss before Git archiving cannot preserve an uncommitted reservation.
- Existing approval-required events remain held. Social autopublishing remains
  deferred; Telegram receives copy-ready cards and captions.
- No real production migration or generation was used in unit tests.

Production dependencies pin patched Pillow 12.3.0 and pypdf 6.19.0. The initial
older versions failed pip-audit; patched versions were separately audited and
the renderer regressions rerun before the GREEN checkpoint.
