# Assessment Artifact Policy

This policy defines durable assessment identity, storage, metadata, lifecycle,
Git lookup, and handoff boundaries. An assessment records what was observed at a
specific repository revision; it does not authorize remediation.

## Assessment Versus Workflow

| Mode | Use | Durable artifact |
| --- | --- | --- |
| Transient analysis | Read-only analysis that remains in the conversation. | none |
| Standalone assessment | A persisted audit, large code review, architecture assessment, or technical-debt inventory without authorized remediation. | `.dev/assessments/<assessment-id>/` |
| Workflow execution | Authorized multi-stage work, remediation, or source-of-truth change. | `.dev/workflows/<workflow-id>/` |

Persistence alone does not turn an observation into a workflow. If the user asks
to assess and remediate in one request, store the assessment under
`.dev/assessments/` and store execution state under the owning workflow. The
workflow references the assessment; it does not copy the report.

## Ownership Boundary

- The repository owns this policy, the assessment locator template, the index,
  ID rules, and structural validation.
- Each assessment-producing skill owns its report template, finding format,
  methodology, and domain-specific evidence contract.
- `.dev/assessments/INDEX.MD` owns assessment discovery and current lifecycle
  state; `assessment.yaml` owns one assessment's identity and relationships.
- `.dev/backlog/` owns candidate work selected from assessments.
- `.dev/workflows/` owns authorized execution plans, tasks, remediation evidence,
  and checkpoints.
- ADRs and standards own adopted decisions and normative truth.

## Storage Contract

Use this shape for every new durable assessment:

```text
.dev/assessments/<assessment-id>/
  assessment.yaml
  report.md
  evidence/                 # optional assessment-owned evidence
```

Do not store assessment instances under skill packages, runtime wrappers,
workflow directories, ignored paths, generated output, or external caches.
Evidence files must remain bounded to the assessment and must not duplicate
large repository content.

## Assessment Identity

Use:

```text
ASM-YYYYMMDD-NNN
```

- `YYYYMMDD` is the local calendar date when the assessment locator is created.
- `NNN` is the next unused three-digit sequence for that date, starting at
  `001` and determined from tracked assessment locators and the index.
- The directory name, `assessment_id`, and `commit_search_id` must match exactly.
- IDs are globally unique within the repository and path-safe.
- Do not reuse an ID from a final, superseded, withdrawn, merged, or published
  assessment.
- Before allocation, refresh the intended integration branch and inspect current
  assessment IDs. If an unpublished branch collides, reallocate and update the
  unpublished artifact and commit message before sharing it.
- After an assessment is pushed or merged, its ID is immutable. Corrections use
  an addendum or successor assessment.

## Locator Contract

Every `assessment.yaml` must contain:

- `schema_version`;
- `assessment_id` and matching `commit_search_id`;
- `assessment_type`, `title`, `owner_skill`, and `status`;
- `report`, which resolves to `report.md` inside the assessment directory;
- `artifact_branch` and `base_branch`, distinguishing the artifact branch from
  the assessed subject branch;
- `created_at` and `updated_at` with seconds and an explicit UTC offset;
- `template_source` and `template_version`;
- `report_template_source` and `report_template_version`, owned by the
  assessment-producing skill;
- `subject_ref.repository`, `subject_ref.branch`, and
  `subject_ref.commit` identifying the revision assessed;
- `scope.included` and `scope.excluded` lists;
- relationship lists for `supersedes`, `superseded_by`,
  `related_assessments`, `workflow_refs`, `backlog_refs`, and `adr_refs`;
- `resume.last_completed_action`, `resume.next_action`, and `resume.blockers`.

The assessment commit SHA is not required inside the initial locator because it
does not exist until after the locator is committed. Find artifact commits by
the stable assessment ID in Git history.

## Lifecycle

Use these states:

```text
draft -> final -> superseded
               -> withdrawn
```

- `draft` may be updated while evidence is gathered. Keep `resume` current
  before a budget, session, approval, or tool-limit stop.
- `final` freezes report conclusions and finding IDs.
- `superseded` retains the report and points to one or more successor
  assessments. The successor records the reciprocal `supersedes` link.
- `withdrawn` retains the report and records a reason in the report and locator
  resume/blocker or relationship context; do not delete the record.
- Updating only locator lifecycle relationships does not rewrite the final
  report. Do not silently edit final report conclusions.
- Use `<assessment-id>#<finding-id>` for durable finding references.

## Branch Contract

A standalone assessment uses a dedicated short-lived branch without creating a
workflow locator solely because the report is persisted:

```text
codex/assessment/<lowercase-assessment-id>
claude/assessment/<lowercase-assessment-id>
```

Create the branch before the locator or report. Commit only assessment-owned
artifacts and required index updates; do not remediate the assessed surface on
that branch. When an assessment is produced inside an already-authorized
workflow, use that workflow branch and do not create a competing assessment
branch.

## Git Search Contract

Assessment creation and material assessment-update commit subjects must contain
the stable ID immediately after the normal commit prefix:

```text
docs(assessment): [ASM-20260713-001] add AI context health assessment
```

Add this trailer before any required `Co-Authored-By` trailers:

```text
Assessment-Id: ASM-20260713-001
Co-Authored-By: <AI runtime/model> <noreply@provider-domain>
```

Downstream workflow, backlog, ADR, remediation, or verification commits may
reference one or more assessments with repeatable `Assessment-Id` trailers even
when the subject does not contain the ID. Search history with:

```text
git log --all --grep='ASM-20260713-001'
```

The ID remains stable across amend, rebase, cherry-pick, or repository migration
when the commit message and assessment artifact are preserved.

## Handoff Contract

- A backlog item references the assessment and selected finding IDs in
  `origin_refs`; it does not duplicate the full report.
- A workflow records source assessment IDs in its plan or task metadata and
  maps each selected finding to an execution disposition.
- A post-remediation verification is a new assessment related to the baseline
  and workflow. It does not overwrite the baseline.
- An adopted decision may reference an assessment from an ADR or standard, but
  the assessment remains evidence rather than normative truth.

## Template And Time Metadata

- The repository locator template records `template_id`, `template_version`,
  `template_created_at`, and `template_updated_at`.
- Skill-owned report templates carry equivalent template metadata.
- `created_at` is immutable. Update `updated_at` when content, status,
  relationships, scope, or resume state changes materially.
- Derived translations have their own timestamps and `derived_from` relation;
  they do not replace `report.md` as the canonical report.

## Validation And Legacy Boundary

- Validate new assessments with
  `.ai/scripts/validate-assessment-artifacts.py`.
- Structural validation does not claim that report prose, evidence quality, or
  every Markdown link is semantically correct.
- Existing reports under `.dev/workflows/**` remain historical workflow
  artifacts. Do not relocate or assign synthetic IDs unless a separate migration
  is explicitly authorized.
- This contract applies prospectively to assessments created after adoption.
