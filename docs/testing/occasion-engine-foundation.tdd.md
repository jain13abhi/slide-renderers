# Occasion engine TDD evidence

Date: 2026-09-21

The production foundation was implemented test-first in paired RED/GREEN
commits. Each contract test was committed while failing before its matching
implementation was added.

| Contract | RED commit | GREEN commit |
|---|---|---|
| Registry validation and job planning | `5fa6c90` | `ba79d38` |
| Verified multi-brand event registry | `92b5142` | `0a803bd` |
| Image-led locked renderer | `09485f6` | `4d79bc7` |
| Transactional production package | `e759776` | `11de765` |
| Bounded Gemini and Higgsfield providers | `9799e1c` | `0be5605` |
| Resumable two-phase state | `978bb45` | `1d9d918` |
| Telegram delivery | `18a949b` | `2ccbb63` |
| Credential-free scheduler preflight | `c3a5744` | `0067828` |
| Private VPS workflow security | `a52def7` | `f48fd7f` |
| Partial-success archive and delivery | `9815738` | `8c40b3a` |

Verification command:

```powershell
python -m unittest discover -s occasion/tests -v
```

The suite contains 35 tests covering validation, planning, source locking,
sensitivity gates, renderer geometry, content bounds, quota budgets, provider
failure modes, atomic state, resume behavior, Telegram payloads, CLI dry runs,
and workflow security constraints.

The bundled Python environment does not include the third-party `coverage`
package, so no numerical line-coverage percentage is asserted. Contract and
failure-path coverage is recorded by the test inventory above.
