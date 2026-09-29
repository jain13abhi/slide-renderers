# Occasion portable paths — TDD evidence

## RED

- Commit: `800a602` (`test: reproduce cross-platform occasion state paths`)
- Command: `python -m unittest occasion.tests.test_state occasion.tests.test_pipeline occasion.tests.test_cli occasion.tests.test_telegram occasion.tests.test_migrate_paths`
- Result: 17 tests ran; one assertion failure and five errors reproduced the
  missing portable-path contract, legacy Windows separator handling, delivery
  output-root argument, and migration command.

## GREEN

- Schema-v2 markers and packages serialize production-relative POSIX paths.
- Schema-v1 readers normalize `\` to `/` and resolve against an explicit legacy
  repository root while enforcing the production-root boundary.
- Telegram delivery uses the same versioned resolver for card artifacts.
- `migrate-paths` is dry-run by default, opt-in with `--write`, atomic per JSON
  file, and idempotent.
- The production template passes the same output root to produce and deliver.
- Ubuntu and Windows CI run the complete engine test suite.

Verification command and result:

```text
python -m unittest discover -s occasion/tests -p "test_*.py"
Ran 52 tests in 0.927s
OK
```

The migration command was exercised only against temporary test fixtures. It
was not run against repository or production data.
