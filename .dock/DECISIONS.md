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

## 2026-10-21 — Reviewed repair, not a production rollout
- Context: Abhi requested fixes for daily/occasion failures and the existing original brand logos; resumed after October19.
- Decision: Implement regression-tested minimal changes on laptop/content-reliability-20261019 and push reviewed PRs; preserve main, locked visuals, accepted Telegram receipts and owner approval holds.
- Boundary: Fresh exact-command rollout/operator approval is required before new production merges, dispatches, backfills or VPS changes. The October8 exception is not reused.
- Evidence: Local tests/review do not prove live provider acceptance or complete global/China/regional calendar coverage. Keep degraded health visible; no paid switch or account rotation.
- Decided by: Abhi's repair/resume request and Dock rules; recorded by Codex on BOOK-4AFVC139C5.

## 2026-10-21 — Stage A operator approval and preview gate
- Abhi explicitly approved Stage A and designated this laptop session sole VPS operator for this rollout. Exact target heads remain renderer22 e5b9ad1, Metal40 27cd14a and Dock53 81d6316; engine8 remains excluded.
- Read-only Tailscale preflight found no operator lock; roles/runbook/changelog read. All approved heads are mergeable with passing Ubuntu/Windows CI. Website exact-head Vercel Preview deployments succeeded, but direct page/image acceptance is blocked by Vercel SSO.
- No existing automation-bypass token on either project; do not invoke CLI token auto-creation, weaken deployment protection or call old production a preview. Ask owner to open signed-in previews and verify page/image rendering.
- Pause before all rollout mutations until preview acceptance; no backups/merges/dispatches/VPS writes yet. Publish this handoff on its own laptop branch, never change the approved PR head for a status note.
