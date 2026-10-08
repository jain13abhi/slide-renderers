# DECISIONS
<!-- Append-only; supersede entries rather than altering their history. -->
## 2026-10-08 — Status audit boundary
- Context: Abhi requested status since the previous check through today.
- Decision: Inspect production read-only; do not merge, push, dispatch, backfill, generate, or change VPS state. Save and commit local handoff notes under the standing session-state rule.
- Alternatives: Automatic repair was not authorized by this status request.
- Decided by: Abhi via current request and global Dock rules; recorded by Codex on BOOK-4AFVC139C5.

## 2026-10-08 — Reliability repair boundary
- Context: Abhi subsequently requested fixes for daily/occasion and Telegram failures.
- Decision: Implement minimal branch changes and regression tests; preserve locked visuals, source/session validation, approval-sensitive holds and bounded model calls. Prepare reviewed PRs.
- Production: Standing operator rules require a fresh exact-command plan approval before production merges, dispatches, backfills or VPS writes. The previous audit entry remains historical.
- Delivery: Persist confirmed per-message receipts; do not claim exactly-once delivery after ambiguous provider acceptance. Distinguish publication, delivery and calendar coverage.
- Decided by: Abhi's repair request and global Dock rules; recorded by Codex on BOOK-4AFVC139C5.
