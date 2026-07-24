# AI Scripts

This directory contains transitional AI workflow scripts, context governance checks, and local tool orchestration helpers.

It is no longer the long-term home for authoritative C# semantic validation. Rules that inspect C# syntax, symbols, type dependencies, attributes, or framework API usage should move to dotnet-native validation mechanisms such as Roslyn analyzers, `.editorconfig`, `dotnet format`, architecture tests, integration tests, or dotnet tools.

## Source Tooling Prerequisites

Repository-side Python tooling requires Python 3.11 or newer and the
checksum-stable dependency declared in the root `requirements.txt`:

```text
PyYAML==6.0.3
```

The repository's .NET validation tools require an SDK that satisfies
`global.json`; for v0.5.0 source work, install .NET SDK 10.0.300 or newer.
An older 10.0 feature band such as 10.0.203 does not satisfy the declared
10.0.300 baseline.

Create and activate a virtual environment using the conventions for the host,
then install the source dependency from the repository root:

```text
python -m venv .venv
python -m pip install -r requirements.txt
```

On POSIX hosts the interpreter may be named `python3`. `check-all.sh` discovers
`python` and then `python3` without changing its governed command inventory.
Set `AI_CONTEXT_PYTHON` to an executable name or path when an explicit
interpreter is required. Missing or failing required tools remain gate failures;
interpreter discovery does not convert them to skips.

Stock macOS installations may expose no `python` command and may provide a
`python3` older than the 3.11 floor. Install a supported interpreter, create the
environment with that interpreter, and set `AI_CONTEXT_PYTHON` to the resulting
executable when needed. The override is part of the supported runner contract;
synthetic fixture repositories remove inherited overrides before selecting
their deterministic PATH stubs, while fixture-owned explicit overrides remain
supported.

The extracted release package has its own checksum-governed envelope
`requirements.txt`; follow the package `INSTALL.md` rather than using this
source-repository bootstrap.

## Current Boundary

`shell-assets.yaml` is the machine-readable role, lifecycle, distribution, and
authority registry for shell assets plus the aggregate runner's literal required
script/command sets. `packaged` means shipped for execution or compatibility; it
does not endorse the script as a semantic source of truth.
`validate-shell-assets.py` enforces registry, Git mode, lifecycle requirements,
and set-based aggregate-runner parity without fixed expected counts. Current
standards, analyzers, compiled validators, and tests own semantic contracts;
packaged documentation must not depend on excluded source workflow history.

## Retention Policy

Shell or PowerShell scripts may remain when they are:

- AI workflow glue;
- prompt or context portability checks;
- repository file-system automation;
- local or CI orchestration over dotnet-native tools;
- non-C# semantic checks.

Shell or PowerShell scripts should be retired or replaced when they:

- use grep/find/plain-text matching to decide C# architecture correctness;
- duplicate `.editorconfig`, built-in analyzers, Roslyn analyzers, `dotnet format`, architecture tests, or dotnet tests;
- generate regex-based C# validation scripts from markdown and present them as formal gates.

## Script Classes

### Keep As AI Workflow Or Context Governance

- `check-prompt-portability.sh`
- `check-coding-standards.sh`
- `validate-ai-context.py`
- `validate-assessment-artifacts.py`
- `validate-ai-context-versions.py`
- `validate-ai-context-release-state.py`
- `prepare-ai-context-release.py`
- `validate-file-disposition-manifest.py`
- `validate-git-commits.py`
- `validate-workflow-handoff.py`
- `build-ai-context-package.py`
- `validate-ai-context-package.py`
- `plan-ai-context-package-apply.py`
- `render-ai-context-release-notes.py`

These scripts inspect AI context, markdown, prompt portability, or repository hygiene. They are not substitutes for dotnet C# validation.

`validate-ai-context.py` checks objective repository facts: active index paths, literal table corruption, declared runtime-root status, canonical/Agents/Claude skill inventory parity, case-safe `AGENTS.md` and thin `CLAUDE.md` root entries, canonical wrapper-metadata target/path integrity, sub-agent dynamic/native dispositions, exact adapter target/path/schema/canonical-link/package-profile parity, policy-scoped agent-facing language, root bilingual entry ownership/link/structural markers, rule ownership registry structure, canonical skill/sub-agent schema compliance, canonical template-family hygiene, and deterministic development capability routing. It scans both tracked and untracked non-ignored files so a new context file cannot bypass the gate before staging, while filtering tracked paths that are deleted in the working tree. Language lint uses exact path-and-line exceptions for deliberate routing triggers; other Han prose and selected non-ASCII punctuation fail with a file and line number. Script source, generated/example/archive/migration material, workflows, product `src`/`test` trees, and human-facing `.dev` documentation are outside that language scan; Markdown documentation under `.ai/scripts` remains in scope. Root bilingual validation checks reciprocal ownership links, headings, links, fences, inline-code identifiers, tables, lists, and ordered backtick table paths. These are structural drift guards, not proof of semantic equivalence; retained semantic review remains required when a bilingual entry changes materially.

`validate-workflow-artifacts.py` validates post-adoption workflow locator/task metadata, complete `.dev/workflows/INDEX.MD` directory coverage, locator-backed title/owner/status/timestamp/entrypoint parity, explicit legacy/no-locator rows, durable `.dev/backlog/items/*.yaml` identity/lifecycle/reference integrity, and fail-closed development implementation contracts for intent, execution mode, overlays, layered sources, subject revision, and acceptance criteria. Locators that opt into `lifecycle_contract: "1.0"` also enforce active-task cardinality, completed-workflow closure, and completed-task result semantics. Historical tasks and locators before their respective contract adoption remain compatible.

`validate-assessment-artifacts.py` validates `.dev/assessments/` locator and
index coverage, `ASM-YYYYMMDD-NNN` identity, template and report paths, assessed
Git revision metadata, branch and timestamp contracts, lifecycle sections,
resume safety, and assessment relationship integrity. It does not evaluate
report prose or replace the producing skill's evidence review.

`validate-ai-context-versions.py` validates governed release identity, SemVer,
immutable published tag-to-commit mappings, compatibility declarations, and an
optional target `.dev/AI-CONTEXT-SOURCE.yaml`. It automatically uses source mode
when release records exist and target mode when only the installed provenance
manifest exists. `compare-ai-context-versions.py`
is a read-only Git-tree comparison helper; it proposes an automatic candidate
only when a supplied target file is byte-identical to the recorded base. Target
truth, deletions, absent evidence, and source history remain reconciliation or
exclusion items.

`validate-ai-context-release-state.py` applies the REL-owned, version-specific
phase contract to one governed release. Candidate validation rejects unresolved
placeholders, copied lifecycle fields, impossible timestamps, unrelated or open
backlog references, dirty worktrees, package identity drift, and generated
provenance in authored notes while allowing prior versions in compatibility and
migration guidance. Tag validation requires an existing annotated tag and a
validated registry skeleton in the tagged tree. Hosted publication and
finalization use GET-only GitHub API calls to verify the successful
tag-triggered workflow, stable Release body, title, tag, and exact asset names.

`prepare-ai-context-release.py` is the pre-tag interface. It requires the merged
`main` candidate, reruns the candidate and critical gates, verifies the
worktree remains clean, reads exact AI provenance from the latest registered
handoff checkpoint, and prints a complete annotated-tag command for the
repository owner. It never executes the printed command or pushes a ref. The
printed command is valid only for the current `main` HEAD; any later merge to
`main`, including lifecycle-only closeout, requires rerunning preparation and
discarding every older printed command.

`validate-dependency-versions.py` is a deterministic offline gate. In the source
framework repository it enforces byte-identical pinned Python requirement
mirrors, requirements-file use and one Python version across GitHub workflows,
exact and consistent direct package versions in framework-managed
`tools/**/*.csproj`, and an exact `global.json` SDK new enough for those tools.
In initialized targets, source-only workflow and distribution checks become not
applicable while managed-tool checks remain active. It does not query package
registries or advisory databases and therefore makes no package-currency or
vulnerability claim. The normative boundary is
`.dev/standards/DEPENDENCY-VERSION-CONSISTENCY-POLICY.md`.

`validate-file-disposition-manifest.py` validates a supplied remediation
file-disposition manifest against repository Git facts. Legacy schema 1.0
enforces exact-case repository paths, the `kept` / `moved-to` / `merged-into` /
`retired` vocabulary, destination and base-presence rules, and complete
coverage of distributable framework paths changed since the recorded
remediation base commit. Schema 2.0 additionally pins the subject commit,
published-version path and blob history, portable-profile inclusion, lifecycle
registry agreement, evidence references, and downstream proof for relocation
or removal. The manifest describes incoming release intent only and does not
replace target-side three-way comparison.

`validate-git-commits.py` validates an explicitly selected commit or revision
range against `.dev/standards/GIT-COMMIT-POLICY.yaml`. It enforces the subject,
final AI signature, assessment ID trailer, and—when `--workflow-id` is
provided—ordered workflow body sections and matching workflow identity. The
aggregate gate invokes it only when `COMMIT_RANGE` is set, so ordinary working
tree checks do not guess whether a human-only commit used AI assistance.

`validate-workflow-handoff.py` validates a bounded receiving checkpoint for
cross-model, runtime, host, machine, and fresh-session continuation. It pins the
validated commit and containing checkpoint commit, records a real critical-gate
command and bounded output digest, blocks red gates outside an explicitly named
repair task, requires REL-owned phase evidence for release handoffs, separates
execution provenance from Git attribution, and preserves a generic
provider-compatible evidence union. Optional `--verify-repository` checks the
current branch, checkpoint-containing commit, worktree state, and pinned commit
metadata using an explicit read-only Git command allowlist. `--all` discovers
durable instances through `.dev/workflows/handoff-checkpoints.yaml`; source
repositories require that registry, while packaged targets without a checkpoint
registry report the check as not applicable.

`build-ai-context-package.py` reads an immutable Git commit tree and the
canonical distribution profile to produce normalized ZIP and tar.gz release
archives. `validate-ai-context-package.py` verifies the envelope, inventory,
member checksums, external archive checksum sidecars, and ZIP/tar member parity.
Their shared `ai_context_package.py` module rejects checkout-dependent bytes,
unsafe paths, output collisions, unsupported Git entry types, and existing
output files. These source-side packaging tools are excluded from the installed
target payload.

`plan-ai-context-package-apply.py` is the dry-run-first target-side package
entrypoint. It runs from the extracted envelope's `payload/.ai/scripts/`
directory, requires a clean committed target, and binds the package manifest,
target HEAD, and observed path hashes and modes into the plan. Existing target
templates and locally changed managed files become reconciliation items.
Acknowledging such an item skips it; acknowledgement never grants overwrite or
delete permission. `--apply` rechecks the complete binding, applies only safe
operations transactionally, and writes
`.dev/AI-CONTEXT-APPLY-PENDING.yaml`. It never updates validated source
provenance; `repo-structure-sync` or `ai-context-upgrader` owns validation and
provenance finalization.

`render-ai-context-release-notes.py` validates a governed release candidate and
renders the GitHub Release body from its canonical release notes, migration
guide, tag, and exact commit. Candidate mode can discover exactly one active
governed candidate; publish mode fails unless the tagged-tree record is
`validated`. The tag-triggered Action owns tag selection and Release mutation;
the renderer never creates or changes Git refs or remote releases.

Fail-closed validation and packaging regression tests use Given-When-Then
naming and comments and run entirely in disposable Git repositories:

```powershell
python .ai/scripts/tests/test_fail_closed_validation.py -v
python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v
python .ai/scripts/tests/test_ai_context_root_entries.py -v
python .ai/scripts/tests/test_ai_context_language_policy.py -v
python .ai/scripts/tests/test_workflow_implementation_contract.py -v
python .ai/scripts/tests/test_workflow_lifecycle_contract.py -v
python .ai/scripts/tests/test_assessment_artifacts.py -v
python .ai/scripts/tests/test_git_commit_policy.py -v
python .ai/scripts/tests/test_ai_context_version_governance.py -v
python .ai/scripts/tests/test_ai_context_package_apply.py -v
python .ai/scripts/tests/test_ai_context_packaging.py -v
python .ai/scripts/tests/test_ai_context_release_state.py -v
python .ai/scripts/tests/test_prepare_ai_context_release.py -v
python .ai/scripts/tests/test_release_notes_renderer.py -v
python .ai/scripts/tests/test_dependency_version_consistency.py -v
python .ai/scripts/tests/test_file_disposition_manifest.py -v
python .ai/scripts/tests/test_governance_workflow_contract.py -v
```

`test_ai_context_version_governance.py` and
`test_ai_context_packaging.py` are source-repository release/build tests.
`test_governance_workflow_contract.py` and the concrete v0.5.0 disposition
manifest validation are source-repository governance checks.
`validate-source-governance.py` discovers those manifests through the stable
source-only `.ai/distribution/governance-checks.yaml` registry so portable
scripts do not depend on dated workflow history. They remain required when
`check-all.sh` detects their exact source context, but the source-only
validators, test, registry, and workflow evidence are intentionally excluded
from public target packages. `test_ai_context_package_apply.py` and the
synthetic file-disposition fixture suite are downstream-supported and remain
packaged and required. A packaged `check-all.sh` reports the four source-only
checks as not applicable instead of requiring unavailable release history, Git
tags, builder modules, workflow evidence, or source CI configuration.

The shell fixture suite snapshots the real checkout before and after execution.
The wrapper-metadata fixture invokes only the bounded validator function against
temporary wrapper directories. Neither suite may source `check-all.sh` or
change files, modes, or index entries outside its temporary repository.

`shell-assets.yaml` classifies every tracked `.ai/scripts/**/*.sh` file with:

- `role`: active orchestrator, context validator, compatibility entrypoint,
  manual advisory, or transitional helper;
- `lifecycle`: active, compatibility, transitional, or retirement candidate;
- `distribution`: packaged or source-only;
- `authority`: orchestration-only, structural, context, or advisory.

Every non-active lifecycle requires an explicit replacement direction. Every
tracked shell asset must use Git index mode `100755`; required entrypoints and
required child scripts must be packaged and runnable under an active or
compatibility lifecycle. `validate-shell-assets.py` uses
`git ls-files --stage` instead of host filesystem executability, which is
unreliable under Windows Git Bash and `core.filemode=false`.

Required child-script calls in `check-all.sh` use the literal multiline form
`run_check "<script>"`, description, then `"required"` on the third line. The
shell asset validator compares those literal calls with
`check_all_required_scripts`; changing that call shape requires updating the
validator and its negative parity fixture in the same change.

### Active Orchestration And Context Validation

- `check-all.sh`
- `check-coding-standards.sh`
- `check-prompt-portability.sh`

`check-all.sh` orchestrates repository gates. The two context validators inspect
repository structure or prompt portability; neither claims C# semantic
compliance. `check-coding-standards.sh` checks required files, headings, catalog
routes, executable modes, and shell syntax, and explicitly excludes architecture
completeness, example correctness, and target technology adoption.

`check-all.sh` uses four enforcement classes:

- `required`: when selected by the active mode, the check must execute; missing,
  non-executable/unlaunchable, or non-zero outcomes fail the aggregate gate;
- `conditional-required`: absence of all applicability inputs is reported as not
  applicable, partial configuration fails, and an applicable check is required;
- `advisory`: execution problems and non-zero outcomes remain visible warnings
  but do not fail otherwise successful required checks;
- `deferred`: known future work is counted separately and is never described as
  a selected required check.

Mode-based omission is distinct from a selected required check being skipped.
Invalid modes or extra arguments return exit code `2`. A successful aggregate
result may contain explicit advisory warnings, deferred work, or not-applicable
conditional checks, but it cannot contain an unexecuted selected required check.

Future `check-all.sh` shape:

```bash
dotnet restore
dotnet build
dotnet test
dotnet format --verify-no-changes
dotnet tool run repo-context-lint
```

Current behavior:

- runs `dotnet test tools/DotnetBackendAnalyzers.Tests/DotnetBackendAnalyzers.Tests.csproj`;
- does not invoke the retired repository grep checks.

### Compatibility And Manual Entry Points

- `code-review.sh`
- `check-spec-compliance.sh`
- `check-mutation-coverage.sh`
- `test-profile-startup.sh`

These remain packaged for current manual or downstream invocation. Their output
is advisory or orchestration evidence and does not override the owning skill,
target configuration, analyzers, or tests.

### Deprecated Compatibility Helpers

- `check-test-di-compliance.sh`
- `check-data-class-annotations.sh`
- `check-domain-events-compliance.sh`
- `check-framework-api-compliance.sh`
- `check-dotnet-config.sh`
- `validate-dual-profile-config.sh`

- `check-test-compliance.sh`

These paths are deprecated in place. They remain packaged for compatibility and
are not endorsed as long-term semantic validators. Each registry record names
its analyzer, compiled validator, architecture-test, target-test, or CI
replacement direction. `check-test-compliance.sh` is no longer selected by
`check-all.sh`; downstream repositories should replace direct invocations with
their selected testing stack, analyzers, and executable test architecture
checks. Removal or relocation requires a later governed disposition with
downstream evidence.

Completed replacement:

- repository rules: `DBA1001` enforces canonical/compatibility inheritance,
  Aggregate Root constraints, aggregate method surface, query-port read-only
  behavior, and the generic writable CRUD prohibition; repository grep scripts
  have been removed.
- controller rules: `DBA1004`, `DBA1005`, and `DBA1006`; the controller grep scripts have been removed.
- mapper rules: `DBA1007` and `DBA1008`; the mapper grep scripts have been removed.
- aggregate rules: `DBA1003` and `DBA1009`; the aggregate grep scripts have been removed while invariant completeness remains test and AI review work.
- use case rules: `DBA1002` and `DBA1010` through `DBA1012`; the use case grep scripts have been removed while transaction and error-handling design remain AI review work.
- projection rules: `DBA1013` covers EF write operations and `DotnetBackendValidation` verifies marker-based EF model registration; the projection grep/config scripts have been removed.

Analyzer source template:

- `tools/DotnetBackendAnalyzers/`
- `tools/DotnetBackendAnalyzers.Tests/`

### Retired Generated Regex Checks

The markdown-to-shell generator, its parser and guide, and the `generated/`
outputs were removed under AIC-007. The root archive grep check was also removed
because its stale `HardDelete` text rule contradicted the active archive/purge
standard. Historical workflow evidence retains the original transition record.

## AI Reasoning Context

Do not remove software engineering reasoning context from `.ai`, `.dev`, or skills as part of this transition.

Analyzers and CI gates can enforce formalizable rules, but they do not replace design reasoning used by:

- `bdd-gwt-test-designer`;
- `code-reviewer`;
- `ddd-ca-hex-architect`;
- requirement/spec/problem-frame authoring skills.

The context remains useful even when executable validation moves to dotnet-native tooling.

## Related Files

- `.ai/scripts/shell-assets.yaml`
- `.ai/scripts/validate-shell-assets.py`
- `.ai/assets/tech-stacks/dotnet-backend/README.MD`
- `.dev/standards/AI-CONTEXT-BOUNDARY.md`
