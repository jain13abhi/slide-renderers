# Higgsfield CLI contract — TDD evidence

## Source and user journey

The journey was derived from controlled production run `36293348775` and the installed Higgsfield
CLI 1.1.26 behavior. The Windows runner must preserve multiline image prompts and 4:5 arguments,
then accept the CLI's separate create and wait JSON responses while still requiring a completed
HTTPS image result.

## RED evidence

- Commit: `c9ddda6 test: reproduce Higgsfield Windows argument and JSON failures`
- Targeted command: `python -m unittest occasion.tests.test_providers.HiggsfieldTests.test_default_runner_invokes_windows_npm_cli_through_node occasion.tests.test_engine.HiggsfieldContractTests.test_result_parser_accepts_create_and_wait_json_responses`
- Result: 2 tests ran; the launcher assertion failed because Python called the npm `.cmd` wrapper
  directly, and parsing errored with `Extra data` when a queued JSON response preceded the completed
  JSON response.

## GREEN evidence

- A Windows npm shim is now resolved to its installed Higgsfield JavaScript entry point and invoked
  through Node, preserving each argument as a distinct process argument.
- The parser now decodes one or more whitespace-separated JSON values, but continues to accept only
  a completed status with an HTTPS result URL.
- Targeted result: 2/2 passed.
- Full command: `python -m unittest discover -s occasion/tests -p 'test_*.py'`
- Full result: 46/46 passed in 2.730 seconds.
- `python -m compileall -q occasion` passed.
- `git diff --check` passed.

## Test specification

| # | What is guaranteed | Test | Type | Result |
|---|---|---|---|---|
| 1 | The Windows npm shim is bypassed safely so multiline prompt and later flags remain separate arguments | `test_default_runner_invokes_windows_npm_cli_through_node` | Unit/platform integration | PASS |
| 2 | A queued create response followed by a completed wait response yields the final HTTPS image URL | `test_result_parser_accepts_create_and_wait_json_responses` | Unit/provider contract | PASS |
| 3 | Existing unsafe/incomplete URL rejection and all occasion contracts remain intact | Full occasion suite | Regression | PASS (46/46) |

## Coverage and known gaps

The bundled Python runtime does not include the optional `coverage` package, so a numeric report
was unavailable. Both corrected provider branches are directly exercised. The self-hosted Windows
production run is the remaining acceptance check.
