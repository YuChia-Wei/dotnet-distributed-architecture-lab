# Software Development Orchestrator Output Contract

Use this output shape when reporting software-development workflow decisions, stage status, or final results.

## Planning Output

```text
Workflow Mode:
- direct | workflow

Reason:
- <why the mode applies>

Activation:
- <high-level intent and repository evidence; no skill name required>

Selected Skills:
- <skill>: <why>

Artifacts:
- <path or none>

Stages:
- <stage id>: <goal, owner skill, validation>

Approval State:
- approved | awaiting-approval
- <decision boundary or none>

Open Decisions:
- <decision needed from user, or none>
```

## Stage Handoff Output

```text
Workflow:
- <workflow id>

Task:
- <task id>

Owner Skill:
- <skill>

Inputs:
- <source files, policies, constraints>

Expected Output:
- <files or sections>

Validation:
- <checks required before return>

Test Execution:
- Level: <unit | integration | e2e | browser | playwright | environment-dependent>
- Provider: <target-profile-commands | evaluated-external-skill | fallback-contract>
- Command / Working Directory / Prerequisites / Policy: <target-owned values>
- Outcome: <passed | failed | blocked-by-environment | not-applicable | deferred-with-owner>

Spec Compliance:
- Selected: <yes | no>
- Outcome: <100-percent-pass | failed-closed | not-applicable>
```

## Final Output

```text
Completed:
- <concise summary>

Changed:
- <important files or boundaries>

Validation:
- <commands/checks run>

Test Outcomes:
- <level>: <exact outcome and evidence>

Spec Compliance:
- <not-applicable when unselected, or selected 100-percent gate evidence>

Review And Task State:
- <review disposition, workflow status, and unfinished/deferred items>

Commits:
- <durable stage or coherent-batch commit hash and title, if committed>

Branch / Handoff:
- <active branch, merge/checkpoint state, and continuation evidence>

Open Decisions:
- <remaining decisions, or none>
```

Do not collapse closeout into one generic success flag. Verify approved
requirements and specs, implementation completion, each required test outcome,
selected compliance gates, review disposition, validation evidence, workflow
task state, commit evidence, and branch or handoff state separately.
