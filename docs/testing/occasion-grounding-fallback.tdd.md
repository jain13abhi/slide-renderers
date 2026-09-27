# Occasion grounding fallback — TDD evidence

## Source and user journey

The journey was derived during this TDD run: when Gemini text generation is available but Google
Search grounding has exhausted its bounded free-tier quota, an occasion job should continue from
the already-validated calendar registry without changing the locked date, sources, visual system,
or publishing contract. Non-quota research failures must still stop the job.

## RED evidence

- Commit: `f78d91d test: reproduce grounded research quota failure`
- Command: `python -m unittest occasion.tests.test_providers.GeminiTests.test_grounding_quota_uses_locked_registry_packet_then_drafts occasion.tests.test_providers.GeminiTests.test_non_quota_research_failure_still_stops_before_drafting`
- Result: 2 tests ran; the quota-fallback test errored because the first HTTP 429 propagated from
  `GeminiDrafter.draft`, while the HTTP 400 fail-fast test passed.

## GREEN evidence

- The drafter now recognizes only a bounded HTTP 429 quota/resource-exhausted research failure and
  substitutes a deterministic packet built from the validated registry event, date, tradition,
  category, sensitivity, brand direction, and curated source URLs.
- The normal ungrounded structured drafting request then runs unchanged. Other research failures
  continue to propagate.
- Targeted command: same two-test command as RED.
- Targeted result: 2/2 passed.
- Full command: `python -m unittest discover -s occasion/tests -p 'test_*.py'`
- Full result: 44/44 passed in 1.767 seconds.
- Compile check: `python -m compileall -q occasion` passed.
- Diff check: `git diff --check` passed.

## Test specification

| # | What is guaranteed | Test | Type | Result |
|---|---|---|---|---|
| 1 | Exhausted Search-grounding quota uses locked registry facts and still makes exactly one structured drafting call | `test_grounding_quota_uses_locked_registry_packet_then_drafts` | Unit/integration boundary | PASS |
| 2 | The fallback packet preserves event name, confirmed date, and curated source attribution | `test_grounding_quota_uses_locked_registry_packet_then_drafts` | Unit | PASS |
| 3 | HTTP 400 research failures remain fail-fast and cannot silently enter fallback | `test_non_quota_research_failure_still_stops_before_drafting` | Error path | PASS |
| 4 | Existing research, correction, Higgsfield, planning, rendering, and validation contracts remain valid | Full occasion test suite | Regression | PASS (44/44) |

## Coverage and known gaps

The bundled Python runtime did not include the optional `coverage` package, so a numeric coverage
report was unavailable. Both new branches are directly executed by tests, and the complete existing
occasion suite passed. The controlled live production run is the remaining acceptance check.

## Merge evidence

RED is preserved in `f78d91d`. The subsequent fix commit records the GREEN implementation and this
report so the sequence remains reviewable even if the pull request is squash-merged.
