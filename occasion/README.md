# Occasion production engine

This directory contains the reusable, multi-brand pipeline for festival,
national-day, industry-day, and other occasion posts. It is separate from the
Metal Dock and Dockfinity daily briefs, so a failure here cannot stop either
daily brief.

## Production architecture

```text
Apps Script (primary IST clock)
        |
        v
private GitHub orchestration repository
        |
        v
private self-hosted runner (Linux VPS; Windows fallback)
  Gemini: grounded research + structured copy
  Higgsfield CLI: text-free 4:5 background image
  deterministic renderer: locked logo, colour, type, spacing
        |
        +--> private versioned package and resumable state
        |
        v
Telegram: final card + separately copyable captions
```

GitHub's daily schedule is a backup clock. Apps Script is the primary clock.
The persistent runner must be registered only with the private orchestration
repository; never attach it to this public repository.

This design uses the Higgsfield account subscription through its official CLI.
It does not use the separately billed Higgsfield API. The only unavoidable
interactive step is the initial `higgsfield auth login` for the runner account, and again
if that account session expires.

## Safety and autonomy rules

- Only an occurrence with `status: "locked"` and verified HTTPS sources can run.
- Approval-sensitive events never run unattended.
- All registry data is validated before any Gemini or Higgsfield call.
- One research call and at most two drafting calls are allowed per job.
- At most two image attempts are allowed per job; the production default is one.
- A failed or ambiguous Higgsfield command is not automatically repeated, which
  prevents accidental duplicate credit use.
- Generated and delivered are separate states. A Telegram retry reuses the
  existing package and never regenerates its image.
- The generated background is immutable. The deterministic renderer alone adds
  the locked brand logo, colour treatment, typography, and spacing.
- X copy is URL-free and length-limited. Every configured platform receives its
  own caption in Telegram.
- Failures return a non-zero exit and the workflow sends the captured stage and
  error to Telegram. Nothing fails silently.

## Registry

[`registry.json`](registry.json) is the source of truth. It contains:

- brands, channel lists, logos, and renderer profiles;
- the reusable event catalogue;
- dated occurrences and their official sources;
- sensitivity and activation status.

Enabled brands currently are Metal Dock, Dockfinity, and Paatra. Disabled
company entries are retained as onboarding templates and cannot produce work.

An occasion without a locked occurrence is intentionally inactive. Add dates
only after checking authoritative government, UN, or official institutional
sources. Do not ask Gemini to decide a religious calendar date.

## Commands

Run these from the repository root:

```bash
python3 -m occasion.engine produce --date 2026-10-06 --dry-run
python3 -m occasion.engine produce --date 2026-10-06
python3 -m occasion.engine deliver --output-root occasion/production
python3 -m occasion.engine notify-failure --stage preflight --detail "example"
```

The default lead time is 14 days. Production files are written beneath
`occasion/production/`; resumable markers live beneath `occasion/state/`.

Generated schema-v2 markers and packages store paths relative to the production
root with `/` separators, regardless of the runner operating system. Readers
remain compatible with schema-v1 desktop markers containing `\` separators.
Both `produce` and `deliver` must receive the same `--output-root` whenever a
non-default production directory is used.

The optional path migration is dry-run only unless `--write` is supplied:

```bash
python3 -m occasion.engine migrate-paths \
  --state-root ../data/occasion/state \
  --output-root ../data/occasion/production
```

Review the preview before explicitly adding `--write`. Normal production does
not require migration because legacy paths are read tolerantly.

Required production environment variables:

```text
GEMINI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Optional model overrides:

```text
GEMINI_MODEL=gemini-3.5-flash-lite
HIGGSFIELD_MODEL=nano_banana_2
HIGGSFIELD_RESOLUTION=2k
```

Higgsfield authentication is stored by the CLI in the runner account and is deliberately
not copied into GitHub secrets or this repository.

## One-time deployment

1. Create a private GitHub repository for orchestration, for example
   `dock-content-engine`.
2. Use the dispatcher and platform-specific reusable workflows maintained in
   `dock-content-engine`. Its engine checkout must pin the reviewed commit SHA.
3. Prepare the approved non-root Linux runner account, its pinned dependencies,
   and Higgsfield login using the operator runbook. Verify
   `higgsfield account status --json` without displaying credentials.
4. Register the repo-scoped runner with `self-hosted`, `linux`, `x64`, and
   `dock-content-vps`. Keep the existing `dock-content-desktop` runner as a
   rollback option until an explicitly approved cutover succeeds.
5. Add the three private-repository secrets listed below.
6. Deploy the updated Apps Script bridge and set the two optional occasion
   properties listed below.
7. Run the CLI's `produce --dry-run` locally with fixtures first. The production
   workflow has no dry-run input: a manual dispatch is a real production run
   and needs separate approval. Verify a controlled run's archive and Telegram
   acceptance before declaring deployment complete.

Private orchestration repository secrets:

```text
GEMINI_API_KEY          Google AI Studio key
TELEGRAM_BOT_TOKEN      existing bot token
TELEGRAM_CHAT_ID        existing destination
```

Generated images, copy packages, and delivery state are committed to the
private orchestration repository under `data/occasion`. The public renderer
repository is checked out read-only, so no cross-repository write token is
needed.

Apps Script properties:

```text
OCCASION_ENABLED=true
OCCASION_REPO=jain13abhi/dock-content-engine
```

The Apps Script route stays disabled unless both properties are present. This
makes deployment fail-safe and leaves the existing daily briefs untouched.

## Recovery

- **Gemini failure:** no image call occurs unless a valid draft exists. The
  workflow alerts Telegram and the next clock can retry.
- **Higgsfield auth/credit/CLI failure:** the job stops and alerts Telegram.
  Ambiguous commands are not retried automatically.
- **Render/package failure:** no generated marker is written.
- **Git archive failure:** Telegram delivery does not begin, preserving the
  recoverable package on the runner workspace.
- **Telegram failure:** the generated marker remains pending. The next run sends
  the same package without another Gemini or Higgsfield generation. Confirmed
  photo/caption message IDs are archived in a private per-package receipt and
  skipped on retry. An ambiguous timeout before receipt persistence still
  requires checking Telegram; this is not an exactly-once guarantee.
- **Corrupt state:** execution fails closed instead of risking duplicate spend.

The existing `occasions.json`, `render-posts.py`, and manual assets remain a
legacy recovery path. Once this engine is deployed, `registry.json` is the
production source of truth.

## Calendar discovery and health

The discovery integration is staged in renderer PR #21 and private-engine
PR #7; these changes are not live merely because this branch documents them.
Before production, merge the reviewed renderer commit and pin that exact SHA
in both reusable workflows.

Discovery checks today through the next 14 days, verifies candidate dates
against approved official sources, and binds names/source evidence to canonical
event IDs before applying brand and approval policies. Legacy generated calendar
rows are rebuilt from verified sources rather than trusted across policy changes.
Calendar warnings return a nonzero health result after verified packages have
been produced/delivered; incomplete coverage cannot appear as a clean zero-job
success. Source availability and complete worldwide coverage are not guaranteed.

