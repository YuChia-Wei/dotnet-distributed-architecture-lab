# Validation Summary

## Passed

| Check | Outcome |
| --- | --- |
| Parse every JSON under `.dev/specs/` and this workflow | passed; 30 files |
| Parse every problem-frame YAML | passed; 15 files |
| `python -B .ai/scripts/validate-workflow-artifacts.py` | passed; 7 post-adoption workflows, 9 indexed directories, 1 backlog item |
| Local Markdown-link resolution for all changed and new Markdown | passed; 31 files |
| Effective rule packets for requirements, specs, architecture, framing, test design, and compliance | resolved with freshness verified |

## Failed Closed Or Interrupted

| Check | Outcome | Meaning |
| --- | --- | --- |
| ReserveInventory CBF compliance | failed-closed at 68% | Missing executable tests remain; 100% is mandatory. |
| Focused `SaleOrders.Tests` Inventory command | interrupted during restore | No passing test evidence was produced. |
| `python -B .ai/scripts/validate-ai-context.py` | failed on pre-existing active catalog references to absent `.ai/scripts`, `distribution/`, `evaluation/`, and one guide | The reported paths are outside this workflow's changed surfaces; no repair was inferred. |

## Scope Verification

- No file under `src/` or `tests/` was modified.
- No source deletion or disposable reconstruction exercise occurred.
- No push, pull request, merge, Issue closure, release, or publication occurred.
- The workflow remains active at RECON-005; RECON-006 cannot close until the 100% compliance and reconstruction gates pass.
