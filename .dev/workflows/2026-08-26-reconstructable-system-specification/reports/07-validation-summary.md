# Validation Summary

## Passed

| Check | Outcome |
| --- | --- |
| Parse every JSON under `.dev/specs/` and this workflow | passed; 31 files |
| Parse every problem-frame and workflow-evidence YAML | passed; 17 files |
| `python -B .ai/scripts/validate-workflow-artifacts.py` | passed; 7 post-adoption workflows, 9 indexed directories, 1 backlog item |
| Local Markdown-link resolution for current changed and new Markdown | passed; 12 files |
| Effective rule packets for requirements, specs, architecture, framing, test design, and compliance | resolved with freshness verified |
| Inventory project build | passed; 0 errors, 1 pre-existing nullable warning |
| Inventory default test profile | passed; 19 passed, 1 external PostgreSQL test skipped, 0 failed |
| Orders regression test profile | passed; 11 passed, 0 skipped, 0 failed |
| Local checkpoint | `a4b0f09f06bdfca9d8ea4e3e7e57ad68102fb15e`; no push, PR, merge, or Issue mutation |

## Failed Closed Or Interrupted

| Check | Outcome | Meaning |
| --- | --- | --- |
| ReserveInventory CBF compliance | failed-closed at 94% | Real PostgreSQL FC3/POST1/INV1 execution remains; 100% is mandatory. |
| Inventory PostgreSQL external profile | blocked-by-environment | Docker Desktop was not running; the checked-in test was correctly skipped and is not passing evidence. |
| `python -B .ai/scripts/validate-ai-context.py` | failed on pre-existing active catalog references to absent `.ai/scripts`, `distribution/`, `evaluation/`, and one guide | The reported paths are outside this workflow's changed surfaces; no repair was inferred. |

## Scope Verification

- No production file under `src/` was modified. Test ownership and coverage under `tests/` were intentionally changed by RECON-007.
- No source deletion or disposable reconstruction exercise occurred.
- No push, pull request, merge, Issue closure, release, or publication occurred.
- The workflow remains active at RECON-007; RECON-006 cannot close until the 100% compliance and reconstruction gates pass.
