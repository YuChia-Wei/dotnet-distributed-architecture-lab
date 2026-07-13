# Git Commit Policy

This policy defines commit title format, commit body structure, and commit timing for agent-assisted work.

## Title Format

When an issue number exists:

```text
<type>(#<issue-number>|<scope>): <summary>
```

When there is no issue number:

```text
<type>(<scope>): <summary>
```

For multiple issue numbers:

```text
<type>(#<issue-number>,#<issue-number>|<scope>): <summary>
```

Examples:

```text
docs(#123|ai-context): define language policy
workflow(#124|governance): add workflow gate
refactor(#125,#128|dotnet-backend): split backend-specific prompt rules
docs(ai-context): inventory context boundaries
```

## Types

Use these commit types:

| Type | Use |
| --- | --- |
| `docs` | Documentation, policy, standards, guides, specs, requirements. |
| `workflow` | Workflow artifacts, task status, review reports, process tracking. |
| `feat` | User-facing or externally visible behavior. |
| `fix` | Bug fixes. |
| `refactor` | Structure changes without intended behavior change. |
| `test` | Test additions or corrections. |
| `chore` | Tooling, housekeeping, generated metadata, or repository maintenance. |

## Scope

The scope should name the affected boundary, not the file extension. Prefer:

- `ai-context`
- `governance`
- `dotnet-backend`
- `repo-structure-sync`
- `skills`
- `workflow`
- `testing`
- `architecture`

## Body Format

Workflow-stage commits should include this body:

```text
Why:
- <why this change exists>

What:
- <main change>
- <main change>

Validation:
- <command or check>
- <skipped validation and reason, if any>

Workflow:
- <workflow-id>
- Stage: <stage-id>
- Task: <task-id>

Co-Authored-By: <AI runtime/model> <noreply@provider-domain>
```

Small direct-mode commits may omit the body when the title is sufficient and the user did not ask for detailed traceability.

Transient read-only analysis has no repository artifacts and therefore requires no branch, workflow, or commit. A durable report-only audit commits only auditor-owned workflow and report artifacts; read-only evidence gathering does not authorize changes to the audited context. Remediation commits belong to the governance workflow that owns those changes.

## AI Model Signature Trailer

Every commit authored with material AI assistance, including workflow commits
and AI-created merge commits, must end with a Git `Co-Authored-By` trailer that
identifies the AI runtime or model:

```text
Co-Authored-By: <AI runtime/model> <noreply@provider-domain>
```

Examples:

```text
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
Co-Authored-By: OpenAI Codex (GPT-5) <noreply@openai.com>
```

Rules:

- place the trailer after all body sections, separated from the body by one blank line;
- keep the trailer as the final non-empty line, or use one final trailer per materially contributing AI runtime/model;
- use the runtime/model identity actually reported by the active environment; when the exact model is unavailable, use the known runtime name without inventing a model version;
- do not add an AI trailer to a human-only commit;
- apply this rule prospectively; do not rewrite existing history solely to add missing trailers.

## Commit Timing

Create a commit when:

- a workflow stage is completed and validated;
- a task JSON status is updated to `completed`;
- a policy or source-of-truth document is introduced;
- a file move or large rename is completed and references are checked;
- the user explicitly asks for a commit.

Do not commit when:

- the working tree includes unrelated user changes;
- validation is still running or unresolved;
- a task is halfway through a file move;
- the next immediate step may invalidate the current diff;
- the user asked not to commit.

## Workflow Commit Rule

For workflow mode, commit at these boundaries:

1. workflow bootstrap;
2. inventory completed;
3. each policy completed;
4. each skill or wrapper sync completed;
5. each file move batch completed;
6. final validation completed.

If several small policy tasks are completed together and validated together, they may share one commit.

## Workflow Branch And Merge Rule

Branch naming, branch-first creation, push, checkpoint merge, continuation, and default `--no-ff` behavior are owned by `.dev/TEAM-GIT-FLOW-RULES.MD`.

For commit-policy purposes:

- create workflow commits only on the dedicated workflow or continuation branch;
- include checkpoint state in the commit body when the workflow will be handed off or merged before completion;
- do not treat a commit, push, or merge as evidence that the workflow is complete;
- verify the workflow closing checklist separately from Git transport state.

## Validation Notes

Before commit, run the narrowest meaningful validation:

- Markdown or documentation-only changes: `git diff --check` and reference search when links changed.
- JSON task changes: parse changed JSON files.
- Code changes: run the relevant test command or state why tests were not run.

The commit body must mention skipped validation when the skipped check would normally apply.
AI-assisted commits must also satisfy the AI model signature trailer contract above.
