# Dev Workflow Output Contract

Use this output shape when reporting software-development workflow decisions, stage status, or final results.

## Planning Output

```text
Workflow Mode:
- direct | workflow

Reason:
- <why the mode applies>

Selected Skills:
- <skill>: <why>

Artifacts:
- <path or none>

Stages:
- <stage id>: <goal, owner skill, validation>

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
```

## Final Output

```text
Completed:
- <concise summary>

Changed:
- <important files or boundaries>

Validation:
- <commands/checks run>

Commits:
- <commit hash and title, if committed>

Open Decisions:
- <remaining decisions, or none>
```
