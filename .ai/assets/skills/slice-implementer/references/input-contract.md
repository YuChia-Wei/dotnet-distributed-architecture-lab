# Slice Implementer Input Contract

Before implementing, confirm these fields:

- `intent`: feature, bug-fix, review-remediation, validation-failure-remediation, behavior-correction, refactor, or cleanup.
- `scope`: one bounded implementation slice.
- `execution_mode`: exactly one of command, query, reactor, or generic.
- `overlays`: zero or more applicable overlays; use `remediation` for review-finding or validation-failure remediation.
- `authorization_source`: the user request or workflow task that authorizes scope, acceptance criteria, non-goals, and validation.
- `normative_truth`: the applicable requirements, specs, standards, and ADRs that define correct behavior and architecture.
- `finding_evidence`: stable assessment, code-review, or validation finding references when remediation is requested.
- `subject_revision`: the reviewed or validated revision when the finding is revision-specific.
- `non_goals`: work explicitly excluded from this slice.
- `validation`: tests, reference checks, build checks, or stated skipped validation.

Do not collapse these source layers into a single `source_truth` field. A workflow
task authorizes work but does not replace normative truth. A finding records an
observed defect and evidence but does not independently redefine correct behavior.

When an informal defect is reported without a formal finding, use `bug-fix` or
`behavior-correction` intent without the remediation overlay. Ordinary feature,
refactor, and cleanup intents do not require findings. Do not manufacture a
finding identifier.

If the slice boundary, aggregate boundary, dependency direction, or domain language is unclear, stop and hand off to `ddd-ca-hex-architect` or `software-development-orchestrator`.
