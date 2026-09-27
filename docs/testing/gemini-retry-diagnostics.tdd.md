# Gemini retry and quota diagnostics — TDD evidence

## Source and user journey

This task was derived from production run `36292121762`, where both Dussehra jobs received HTTP 429 before image generation.

As the content operator, I want transient Gemini rate limits to retry within a strict bound and permanent quota failures to report the API's reason, so that occasion production neither fails silently nor loops indefinitely.

## RED evidence

- Production run `36292121762` failed both jobs with the opaque message `HTTP Error 429: Too Many Requests`.
- `python -m unittest occasion.tests.test_providers.GeminiTests` ran the three new transport tests and failed because retry configuration did not exist.
- RED checkpoint: `32c2f97 test: reproduce Gemini 429 retry gap`.

## GREEN evidence

- Gemini HTTP requests retry only status codes 408, 429, 500, 502, 503 and 504.
- Retry count is bounded to three attempts by default.
- Backoff respects `Retry-After`, otherwise uses capped exponential delay.
- Non-transient 400 responses fail immediately.
- Final failures include the safe Google API error message without exposing the API key.
- Targeted provider tests pass: 5/5.
- Full occasion suite passes: 42/42.
- Python compilation and `git diff --check` pass.

## Test specification

| # | What is guaranteed | Test | Type | Result |
|---|---|---|---|---|
| 1 | A transient 429 is retried and a later successful response is returned | `test_http_transport_retries_429_then_returns_text` | unit | PASS |
| 2 | Repeated 429 responses stop after three attempts and include the quota reason | `test_http_transport_reports_quota_detail_after_bounded_retries` | unit | PASS |
| 3 | A non-transient 400 response is not retried | `test_http_transport_does_not_retry_non_transient_400` | unit | PASS |

## Coverage and known gaps

The full occasion suite contains 42 passing tests. The next production retry is the end-to-end acceptance check against the live Gemini service.
