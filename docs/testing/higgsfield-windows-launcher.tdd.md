# Higgsfield Windows launcher — TDD evidence

## Source and user journey

The journey was derived from controlled production run `36293080273`: the persistent Windows
runner must launch the installed Higgsfield npm command shim from Python just as PowerShell does.

## RED evidence

- Commit: `0a155b1 test: reproduce Windows Higgsfield launcher failure`
- Command: `python -m unittest occasion.tests.test_providers.HiggsfieldTests.test_default_runner_resolves_windows_command_shim_before_launch`
- Result: the test errored because the provider did not resolve the command through `shutil.which`.
  In production this surfaced as `[WinError 2]` even though preflight found `higgsfield.cmd`.

## GREEN evidence

- The default command runner now resolves the first command through the operating system's PATH
  and PATHEXT rules before launching it, preserving all remaining arguments.
- Targeted result: 1/1 passed.
- Full command: `python -m unittest discover -s occasion/tests -p 'test_*.py'`
- Full result: 45/45 passed in 1.020 seconds.
- `python -m compileall -q occasion` passed.
- `git diff --check` passed.

## Test specification

| # | What is guaranteed | Test | Type | Result |
|---|---|---|---|---|
| 1 | The Windows `higgsfield.cmd` shim is resolved before subprocess launch and receives unchanged arguments | `test_default_runner_resolves_windows_command_shim_before_launch` | Unit/platform integration | PASS |
| 2 | Existing planning, Gemini, Higgsfield, rendering, and validation behavior remains intact | Full occasion suite | Regression | PASS (45/45) |

## Coverage and known gaps

The bundled Python runtime does not include the optional `coverage` package, so a numeric report
was unavailable. The platform-specific launch branch is directly executed by the new test. A
controlled self-hosted Windows production run is the final acceptance check.
