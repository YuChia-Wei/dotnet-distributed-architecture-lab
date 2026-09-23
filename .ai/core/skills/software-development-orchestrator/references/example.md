# Inert workflow examples

These are synthetic instructions and data, not execution evidence. Replace root
paths with actual authorized existing roots and select the installed package.
No files, hashes, approval or runtime results are created by reading this page.

## Tracked-intent store

Project JSON can be:
```json
{
  "config_version": 2,
  "skills": {
    "software-development-orchestrator": {
      "store": {"kind": "filesystem", "root": "notes/workflows", "tracking": "tracked"},
      "retention": {"compact_after_days": 30, "archive_after_days": 90, "purge_after_days": null}
    }
  },
  "constraints": {
    "software-development-orchestrator": {
      "write_roots": ["notes/workflows"],
      "locked_fields": ["store.root", "store.tracking", "retention"]
    }
  }
}
```

Provision notes before an authorized create, or explicitly grant its creation.
Tracking intent does not stage/commit these records or prove backup/shared durability.

## Minimal semantic creation

A complete request shape uses explicit roots:
```json
{
  "operation": "create",
  "project_root": "/absolute/project",
  "package_root": "/absolute/installed/software-development-orchestrator",
  "content": {
    "title": "Keep one repair resumable",
    "intent": "Preserve the selected failure, repair progress and next action.",
    "scope": {"included": ["One selected worker"], "excluded": ["Global retry policy"]},
    "acceptance": [{"id": "A1", "criterion": "The selected failure and actual result remain inspectable."}],
    "first_action": {
      "action": "Inspect the selected failure and record its exact subject.",
      "completion_condition": "A retained attributed observation identifies that subject.",
      "owner": "Project maintainer"
    }
  }
}
```

The tool mechanically creates one planned workflow and pending T001; it does not
invent a plan, execute an inspection or report a pass. Save the actual returned ID,
digest and store binding. Invoke inspect/resume with that reference. Never invent
expected_sha256: use the digest from the actual read.

Transition planned to active with actual expected state/digest and a reason.
Checkpoint a complete content replacement to record actual progress. Add evidence
and reference objects before using their IDs; all claims are caller-supplied.
A failed attempt remains in immutable evidence even after a later success.
Task T002 depending on failed/deferred T001 cannot become active/completed.

An explicit deferral object has reason, owner, trigger, next_action, authority_ref:
```json
{
  "reason": "The selected environment is unavailable.",
  "owner": "Project validation owner",
  "trigger": "Environment becomes available",
  "next_action": "Run the selected check against the actual subject and retain output.",
  "authority_ref": "An actual already-existing owner decision reference"
}
```
The final field is attribution, not a generated approval or authorization service.
A workflow may complete with such deferrals only under all completion conditions;
its derived result is with-deferrals, not passed. Failed required acceptance remains
open unless actually resolved or explicitly deferred with retained history.

## Ignored-intent store

Select store.root=scratch/private-workflows and store.tracking=ignored in the
same namespace, with a matching explicit project write_roots constraint. Establish
ignore/tracking and a durable shared copy separately. The tool does not choose a
RAM disk, ignore files, set global temporary directories or infer a teammate can
read an ignored local record. Local config in a Git project must already be ignored
and untracked.

## No new knowledge and candidate handoff

A retrospect authored value may be:
```json
{
  "outcome": "no-new-knowledge",
  "reflection": {
    "actual_outcome": "Describe the actual bounded outcome.",
    "observations": "Existing workflow evidence is sufficient for this local result.",
    "limitations": "No wider applicability was established."
  },
  "rationale": "A new Lesson or ADR would duplicate the retained local observation.",
  "candidates": []
}
```
Supply it with the actual workflow reference and expected_sha256. It is bound to
current content; a later checkpoint invalidates it while preserving its history.

For a Lesson candidate, include the useful observation, applicability and missing
actual related query/decision evidence. Do not create executable foreign JSON with a
placeholder hash. Inspect the selected Lesson public contract and obtain its actual
inputs independently. An unavailable package leaves the candidate intact.

## Retention

An explicit retention-preview request names mode and a nonempty selection of actual
workflow IDs. A planned workflow is protected. An old closed workflow still needs
reference/evidence analysis; unknown external inbound links never become absence.
Compact can return a summary with original retained; archive/purge returns missing
owner/copy/reader/reference evidence, never deletion authority. Terminal open
knowledge candidates require a separately reconciled successor; the original stays
immutable and protected.
