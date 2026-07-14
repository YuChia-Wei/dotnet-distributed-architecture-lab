# AI Context Remediation Report

## Metadata

- Workflow: `2026-07-15-ai-context-v0-1-downstream-feedback`
- Task: `AICG-V01-001`
- Owner skill: `ai-context-governance`
- Updated: `2026-07-15T07:22:28+08:00`
- Status: reopened for artifact-retention correction

## Remediation Summary

- Reframed the downstream installation as a known v0.1.0 raw-overlay baseline.
- Retained the full source-project feedback as the workflow-owned input and deliverable at `../ai-context-v0.1.0-downstream-feedback.md`.
- Removed five blob-confirmed source lifecycle requirements from target active requirements.
- Removed `.ai/scripts/README.md` backlinks to the excluded source transition workflow.
- Corrected 20 active architecture path references and 11 additional guide path case mismatches.
- Added a Git-path-based exact-case reference validator and two regression tests.
- Preserved historical workflow records without rewriting their old references.

## Validation Evidence

| Check | Result |
| --- | --- |
| `python .ai/scripts/tests/test_ai_context_exact_case_paths.py -v` | passed, 5 tests |
| `python .ai/scripts/validate-ai-context.py` | passed |
| `python .ai/scripts/validate-workflow-artifacts.py` | passed |
| `python .ai/scripts/validate-shell-assets.py` | passed |
| `git diff --check` | passed; Windows line-ending conversion warnings only |
| full `.ai/scripts/tests` discovery | 35/36 passed; one pre-existing fixed-count assertion failed |

## Finding Resolution Matrix

| Finding | Resolution | Evidence | Remaining action |
| --- | --- | --- | --- |
| AICG-V01-PROVENANCE | addressed | feedback records source tag and commit as known base | source project may adopt the recommendation |
| AICG-V01-LEAKS | addressed | five source lifecycle requirements deleted | none in target |
| AICG-V01-SCRIPT-BACKLINKS | addressed | excluded workflow links removed from script README | source package needs equivalent sanitation |
| AICG-V01-EXACT-CASE | addressed | active references corrected; validator and tests added | independent post-audit |
| AICG-V01-ARTIFACT-RETENTION | correction in progress | feedback restored under the workflow artifact root | validate, commit, and record evidence through AICG-V01-002 |

## Residual Risk

`test_fail_closed_validation.py` still expects `Required Failed: 2`, while the current critical runner selects three dotnet commands in its unavailable-command fixture. This is independent of the exact-case remediation and is documented as source framework feedback rather than silently broadened into this task.

## Commit Evidence

- Implementation: `8a5fef979ca1ce9804c722a5c9acae1d8532341c`
- Closeout metadata: committed separately after this artifact records the implementation hash.

## Closure Decision

The original remediation remains complete. The workflow is temporarily reopened to retain the feedback artifact, repair its relationships, and record correction commit evidence.
