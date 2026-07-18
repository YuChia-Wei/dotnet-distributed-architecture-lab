# Remediation Overlay

Apply this overlay when a bounded slice is authorized to resolve one or more
review findings or validation failures. It augments, and never replaces, the
selected command, query, reactor, or generic execution mode.

## Required Inputs

- `authorization_source`: user request or workflow task defining authorized
  scope, acceptance criteria, non-goals, and required validation;
- `normative_truth`: applicable requirements, specs, standards, and ADRs;
- `finding_evidence`: stable finding references and their evidence;
- `subject_revision`: reviewed or validated revision when applicable;
- `execution_mode`: exactly one mode reference.

Prefer durable references such as `<assessment-id>#<finding-id>` or a
workflow-qualified finding/task reference. If a finding is conversational only,
quote the bounded finding text in the authorization source rather than inventing
a durable identifier.

Follow the target repository's workflow gate. When durable assessment findings
are selected for remediation and repository policy requires workflow mode, the
owning workflow task is the authorization source and must reference the selected
findings.

## Execution Rules

1. Map every selected finding to an acceptance criterion and intended
   disposition before editing.
2. Load the selected execution mode and preserve all of its architecture rules.
3. Implement only the authorized findings; record adjacent issues as deferred.
4. Do not infer a new architecture direction from a recommendation. Stop and
   hand off when the normative source or architecture boundary is unclear.
5. Add or update regression protection when the finding concerns observable
   behavior and testing is within scope.
6. Record before/after evidence and the narrowest meaningful validation for
   each finding.

## Finding Dispositions

Use one of:

- `resolved`: acceptance criteria and validation pass;
- `partially-resolved`: an explicitly bounded portion is complete and the
  remainder is deferred with a reference;
- `not-reproduced`: current evidence cannot reproduce the finding; do not make a
  speculative change;
- `deferred`: authorization, normative truth, dependency, or scope is missing;
- `rejected`: evidence shows the finding is invalid, with rationale recorded by
  the workflow or review owner.

The implementer records evidence but does not silently close or rewrite the
original assessment or review report.

## Expected Output

- selected intent, execution mode, and overlay;
- finding-to-disposition mapping;
- touched files and bounded implementation result;
- validation and before/after evidence;
- unresolved or newly discovered findings;
- handoff to `code-reviewer`, `spec-compliance-validator`, or the workflow owner
  when independent verification is required.
