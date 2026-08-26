# Portable Git Commit Policy

Use `<type>(<scope>): <summary>` with a scope that names the affected boundary.
Include an external work reference only when the target has a real provider
identifier; never fabricate one and never require a provider to create a
commit.

For workflow stages, record:

```text
Why:
- <reason>

What:
- <coherent change>

Validation:
- <exact command and outcome>

Workflow:
- <workflow-id>
- Stage: <stage-id>
- Task: <task-id>

Co-Authored-By: <AI runtime> (<model>, <reasoning_effort>) <provider address>
```

Commit one validated durable stage or coherent bounded batch. Preserve shared
history and approval, assessment, validation, checkpoint, and handoff
boundaries. The target owns its integration mechanism; a commit, push, or
integration event does not prove workflow completion or publication.
