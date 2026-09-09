# Slide renderers

Layout code for the daily Metal Dock and Dockfinity briefs.

| Brand | Script | Output |
|---|---|---|
| Metal Dock | `metaldock/render-slides.py` | five 1080×1350 slides + a ZIP |
| Dockfinity | `dockfinity/render-slides.py` | one 1080×1350 image, or a 3–5 slide carousel |

## Why this repository is public

Two scheduled tasks fetch these files over plain HTTPS, unauthenticated, at
04:30 and 05:30 UTC every day:

```
https://raw.githubusercontent.com/jain13abhi/slide-renderers/main/metaldock/render-slides.py
https://raw.githubusercontent.com/jain13abhi/slide-renderers/main/dockfinity/render-slides.py
```

A private repository answers those URLs with 404, and the tasks are written to
produce nothing rather than guess at a layout. **Making this repository
private stops both brands from posting.** The `raw-url-reachable` workflow
checks both URLs on every push and once a day before either run, so the repo
going private surfaces as a failed run rather than as a silent empty morning.

The website repositories stay private. Only the layout has to be readable.

## How a run uses them

The task fills the `BRIEF` dictionary at the top of the file and changes
nothing else. Everything below `BRIEF` is fixed: geometry, colour, type scale,
spacing arithmetic, footer and safe margins.

```
python render-slides.py --logo /path/to/logo.png --out-dir ./out   # dockfinity
```

Both scripts measure rather than assert. Card heights come from wrapped text,
never from an estimate made before wrapping. Vertical distribution is
arithmetic per column against a 24px minimum and a 160px maximum. When content
will not fit, the script raises and names the offending block — it never clips.
The task's response to a raise is to shorten the text in `BRIEF` and run again,
never to edit the script.

Each run prints its own clearance and spacing figures, measured off the
rendered PNG. Those figures are what the task reports; nothing is restated
from memory.

## Changing a layout

Change it here, in a pull request. The next morning's run picks it up, because
the task re-fetches on every run and is forbidden from using a cached copy.
Nothing in the scheduled tasks needs editing.
