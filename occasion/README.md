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
VPS self-hosted runner
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
interactive step is the initial `higgsfield auth login` on the VPS, and again
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
python3 -m occasion.engine deliver
python3 -m occasion.engine notify-failure --stage preflight --detail "example"
```

The default lead time is 14 days. Production files are written beneath
`occasion/production/`; resumable markers live beneath `occasion/state/`.

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

Higgsfield authentication is stored by the CLI on the VPS and is deliberately
not copied into GitHub secrets or this repository.

## One-time deployment

1. Create a private GitHub repository for orchestration, for example
   `dock-content-engine`.
2. Copy `deployment/occasion-production.yml` into that private repository as
   `.github/workflows/occasion-production.yml`.
3. On the always-on VPS, install Python 3, Pillow, Git, Node.js, and the official
   Higgsfield CLI. Run `higgsfield auth login` and confirm
   `higgsfield account status --json` succeeds.
4. Register that VPS as a self-hosted runner for the private orchestration
   repository with labels `self-hosted`, `linux`, `x64`, and
   `dock-content-vps`. Run it as a service.
5. Add the four private-repository secrets listed below.
6. Deploy the updated Apps Script bridge and set the two optional occasion
   properties listed below.
7. Run a workflow dispatch using `--dry-run` first, then run one controlled
   production job and verify the resulting Telegram package.

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
  recoverable package on the VPS workspace.
- **Telegram failure:** the generated marker remains pending. The next run sends
  the same card and captions without another Gemini or Higgsfield generation.
- **Corrupt state:** execution fails closed instead of risking duplicate spend.

The existing `occasions.json`, `render-posts.py`, and manual assets remain a
legacy recovery path. Once this engine is deployed, `registry.json` is the
production source of truth.

