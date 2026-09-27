# Occasion display separators — TDD evidence

## Source and user journey

The journey came from visual inspection of both controlled Dussehra cards: the locked renderer must
never show a missing-glyph box when LLM copy uses a bullet, middle dot, en dash, or em dash as a
date separator.

## RED evidence

- Commit: `e91060a test: reproduce unsupported occasion separator glyphs`
- Command: `python -m unittest occasion.tests.test_renderer.RendererTests.test_display_text_normalizes_unsupported_unicode_separators`
- Result: four subtests errored because the renderer had no display-safe normalization boundary.

## GREEN evidence

- The renderer now converts four common Unicode separators to an ASCII hyphen and normalizes
  whitespace before fit validation and drawing. Caption copy and stored draft content remain intact.
- Targeted result: 1/1 test passed with four separator subcases.
- Full command: `python -m unittest discover -s occasion/tests -p 'test_*.py'`
- Full result: 47/47 passed in 0.839 seconds.
- `python -m compileall -q occasion` passed.
- `git diff --check` passed.

## Test specification

| # | What is guaranteed | Test | Type | Result |
|---|---|---|---|---|
| 1 | Bullet, middle dot, en dash, and em dash render through an ASCII-safe separator | `test_display_text_normalizes_unsupported_unicode_separators` | Unit/render boundary | PASS |
| 2 | Existing occasion planning, providers, rendering, and delivery contracts remain intact | Full occasion suite | Regression | PASS (47/47) |

## Coverage and known gaps

The bundled Python runtime does not include the optional `coverage` package, so a numeric report
was unavailable. The affected text-normalization branch and every supported separator are directly
exercised. Existing Dussehra backgrounds will be rerendered without new provider calls.
