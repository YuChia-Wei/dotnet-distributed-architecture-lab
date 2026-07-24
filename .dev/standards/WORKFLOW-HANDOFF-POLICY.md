# Workflow Handoff Policy

This policy defines the fail-closed checkpoint required when an active workflow
is transferred across a model, runtime, host, machine, or fresh session.

## Purpose

A receiving agent must be able to continue from repository evidence alone. A
handoff must not depend on hidden conversation history, the previous executor's
memory, or an assumption that the next executor will infer the intended state.
Design the checkpoint for the weakest credible executor that is authorized to
perform the next action.

The machine-readable contract is
`WORKFLOW-HANDOFF-POLICY.yaml`. Use the skill-owned template at
`.ai/assets/skills/ai-context-governance/templates/workflow-handoff-checkpoint-template.yaml`.
Register every durable instance in
`.dev/workflows/handoff-checkpoints.yaml`; aggregate and hosted governance
checks validate every registered checkpoint.

## When A Checkpoint Is Required

Create or refresh a checkpoint before:

- changing the model, runtime, host, or machine that owns an active workflow;
- continuing an active workflow in a fresh session;
- delegating continuation to a lower-cost or otherwise less-contextual
  executor;
- pushing or merging an incomplete workflow as a transport boundary;
- handing off release candidate, tag, publication, or finalization work.

The checkpoint is not workflow completion. Keep the workflow and unfinished
task active unless their own completion contracts are satisfied.

## Repository And Resume Pins

The checkpoint must record:

- repository root, branch, and the fully validated subject commit;
- `checkpoint_commit_source: containing-commit`, which tells the receiver to
  resolve the exact checkpoint transport commit from the latest commit that
  contains the checkpoint file;
- observed dirty state and the SHA-256 of `git status --porcelain=v1`;
- workflow ID, current task ID, last completed action, and exact next action;
- `hidden_context_required: false`.

This two-commit shape avoids an impossible self-reference: the checkpoint file
can pin the validated parent commit while its own containing commit is resolved
deterministically from Git. The receiver must run:

```text
python .ai/scripts/validate-workflow-handoff.py --checkpoint <path> --verify-repository
```

Repository verification is read-only. It rejects a stale branch tip, wrong
branch, missing commit, mismatched dirty state, or attribution observation that
does not match the pinned commit.

## Critical Gate

Before creating the checkpoint, run the repository critical gate. Record the
exact command, exit code, observation time, SHA-256 of normalized complete
output, total line count, and no more than the bounded tail allowed by the
machine policy.

The portable command is:

```text
bash .ai/scripts/check-all.sh --critical
```

An environment-specific Bash executable is permitted when the recorded command
still invokes the same repository path and `--critical` mode.

A successful gate permits normal continuation. A failed gate blocks
continuation unless all of the following are true:

- continuation mode is `repair-only`;
- the checkpoint names the current workflow task as the repair task;
- one or more stable failure IDs are recorded;
- the exact next action is limited to repairing those failures.

The repair exception does not authorize unrelated work.

## Release Handoffs

Set `release_handoff: true` for candidate, tag, publication, or finalization
handoffs. In addition to the critical gate, record the REL-owned phase-specific
state command and bounded observed result. A release phase check must pass
before release work continues; a failed phase check has no general
continuation exception.

HANDOFF owns this interface. REL owns the allowed phase vocabulary, the
sanctioned command, and its release-state semantics.

Until the REL-owned contract declared by
`WORKFLOW-HANDOFF-POLICY.yaml:release_phase_contract_path` exists, every
`release_handoff: true` checkpoint fails closed. An arbitrary command string or
synthetic successful result is not a release phase contract.

## Validation Evidence

A handoff validation claim is not free-text success prose. Each claim records a
runnable command and its observed result. The checkpoint applies this rule to
the aggregate critical gate, any release phase check, and validation claims
needed by the current task or its handoff commit.

The full output remains outside the repository when it contains transient
runner detail. The checkpoint retains a normalized digest, line count, and
bounded tail so a receiver can identify the observation without copying an
unbounded log into AI context.

## Execution Provenance

Execution provenance is supplemental to Git attribution. Record `model_source`
as exactly one of:

- `runtime-reported`;
- `provider-reported`;
- `user-declared`;
- `unavailable`.

Preserve user-declared model and reasoning labels verbatim. Never describe a
user-declared value as runtime-verified. When the source is `unavailable`, do
not invent a model or reasoning label.

## Provider-Compatible Attribution

Never amend, rebase, recreate, or otherwise rewrite a commit solely to
normalize AI attribution. Preserve provider-native Author, Committer,
cryptographic signature, trailers, human co-author, and session-log metadata.

The checkpoint records one observed attribution evidence path:

- `repository-created-local-ai-trailer`;
- `provider-native-coauthor-trailer`;
- `provider-native-authorship-or-signed-session`.

This is an evidence union, not a provider identity registry. Provider-specific
rules may be activated only after a real provider-generated commit object is
captured verbatim as a golden fixture. Missing Copilot CLI, Copilot cloud
agent, Claude, or Codex evidence remains `blocked` with a reason; it is not
replaced by an invented name or email.

The four path identifiers are stable fixture categories, not prescribed
provider identities. Every checkpoint must record each category as `captured`
or `blocked`. The selected attribution evidence must reference a captured
fixture whose commit equals the selected and validated commit.

The existing `GIT-COMMIT-POLICY` and `validate-git-commits.py` continue to
govern repository-created local workflow commits. Do not broaden that validator
to provider-native shapes until the required real fixtures exist. A
provider-native commit that cannot satisfy the local validator must remain
outside that validator's selected local-workflow range rather than be amended
for normalization.

Repository-owned Copilot, Claude, or other provider settings must not disable,
replace, or pin native attribution behavior without explicit owner approval and
a provider fixture proving preservation.

## Security And Mutation Boundary

`validate-workflow-handoff.py` is read-only. Its Git command allowlist excludes
`commit`, `amend`, `rebase`, `reset`, `tag`, `push`, and all other
history-writing commands. Validation proves evidence; it never repairs or
normalizes Git history.
