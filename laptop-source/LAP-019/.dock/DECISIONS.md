# DECISIONS
<!-- Append-only; supersede entries rather than altering their history. -->

## 2026-10-08 — Approved laptop operator preflight
- Abhi approved the rollout and designated this laptop session as operator for this plan, with no other operator intended.
- Trusted Tailscale SSH preflight found an existing Import49R3Stage1 operator lock and recent electricity-import changelog activity. Stop before production changes; owner must release their lock. Do not infer a stale lock or delete it.
- Record notes locally on codex/approved-rollout-preflight; do not push or change exact approved PR heads while blocked.
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

## 2026-10-08 — Approved execution outcomes (supersedes pending preflight)
- Abhi supplied sole tick settings and verified deletion0; laptop operator exception explicitly approved, prior holder released, ContentRecovery20261008 lock acquired atomically. Original clocks frozen/drained and backed up before exact PR21/7/36/50 merges.
- All4daily recoveries succeeded, live pages/imagesHTTP200,31accepted IDs, Gemini skipped. Gandhi3brand delivery21accepted IDs onOct8; calendar-health remains degradedHTTP429 and two late captions require separately reviewed correction before social reuse.
- All5 originally-active GitHub workflows restored. Original-account primary tick and next normal execution remain pending. Preserve accepted receipts; no blind retries or silent paid-provider switch.
- Private backups retained; no services/DB/network changes. Full evidence: ../deliverables/rollout-execution-2026-10-08.md. New production changes need a separately reviewed exact-command plan and approval.
