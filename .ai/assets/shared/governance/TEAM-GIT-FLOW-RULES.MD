# Portable Branch And Integration Policy

This target-facing policy defines a provider-neutral branch lifecycle. The
target repository owns its integration branch, review mechanism, merge method,
protection rules, and permissions.

## Branch-First Execution

- Start authorized workflow work from the target's configured integration
  branch.
- Create a bounded short-lived branch before workflow artifacts or material
  edits.
- Record the branch and base branch in the workflow locator and plan.
- Commit coherent validated stages; a push or integration event before
  completion is a checkpoint, not workflow closure.
- After integration, verify the target branch separately and do not claim
  publication or release completion from integration alone.

## Integration Gate And Merge Topology

The target selects its review or integration gate independently from Git
topology. A workflow does not inherently require a merge commit, and a linear
history does not inherently permit direct push.

Repository integration is the reviewed Git event that enters the target's
configured integration branch. It is not workflow completion, assessment
finality, release-source validation, hosted publication, or publication
finalization.

Choose linear integration when commits and the provider review record carry all
needed evidence and the branch has no durable checkpoint, approval, handoff,
external-lifecycle, or grouped rollback meaning. Direct-mode fixes, standalone
assessments, and non-normative documentation changes are common candidates.

Choose a merge commit when the branch is itself a meaningful review or rollback
unit, carries checkpoint or handoff state, reconciles release, publication,
migration, deployment, security, or another external lifecycle, or target
policy requires a merge node.

Issue count, task count, commit count, file count, and workflow mode are signals
only. The target records its positive topology choice and uses a provider-native
rebase, fast-forward, or merge-commit mechanism that does not bypass required
review, checks, permissions, or branch protection.

## Handoff And Customization

A push-only handoff resumes from the pushed workflow branch. A workflow that is
integrated before completion resumes on a new continuation branch from the
updated target. Cross-session or cross-runtime continuation must retain an
executable checkpoint.

The framework does not choose a branch name, hosted provider, review UI,
required reviewer, merge strategy, or automation for a target. Those settings
are target-owned customizations and must be preserved or reconciled during
installation and upgrade.
