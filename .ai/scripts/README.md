# AI Scripts

This directory contains transitional AI workflow scripts, context governance checks, and local tool orchestration helpers.

Python implementations and contract tests owned by exactly one canonical skill
belong under `.ai/assets/skills/<skill-id>/scripts/`. This directory retains
shared, multi-skill, provider, release, package, workflow, and source-wide
automation plus explicit compatibility entrypoints for already published
commands.

It is not the home for authoritative C# semantic validation. A target may
explicitly select its own Roslyn analyzers, `.editorconfig`, `dotnet format`,
architecture tests, integration tests, or tools; those choices are not
framework release prerequisites.

## Source Tooling Prerequisites

Repository-side Python tooling requires Python 3.11 or newer and the
checksum-stable dependency declared in the root `requirements.txt`:

```text
PyYAML==6.0.3
```

The source framework has no .NET SDK prerequisite. A target that explicitly
creates a managed project owns its SDK and package prerequisites.

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

## Governed Python Entrypoints

The supported Python-command registry is
`.ai/scripts/python-entrypoints.json`. Use a registered CLI directly when the
selected interpreter is already ready, or use a launcher when the invoking
shell needs deterministic interpreter discovery:

```text
python .ai/scripts/validate-ai-context.py --help
sh .ai/scripts/run-python-entrypoint.sh .ai/scripts/validate-ai-context.py --help
pwsh -File .ai/scripts/run-python-entrypoint.ps1 .ai/scripts/validate-ai-context.py --help
```

Direct CLIs and both launchers accept `--diagnostic-format=json`; without it,
blocked prerequisites are emitted as a human-readable stderr diagnostic. A
blocked diagnostic reports `blocked-by-environment`, the required Python floor,
the selected candidate when available, missing requirements, and a recovery
command. The recovery command is advice only: the preflight never installs
Python, packages, or other dependencies.

`.dev/validation.local.conf` is an ignored target-local selection file, never a
package member. When a target enables it, it must contain exactly one line,
`validation.routine.local=<approved-mode>`; it may only strengthen the checked
in selection and is never an environment-variable override. See the human
guide at
`.dev/guides/ai-collaboration-guides/PYTHON-PREREQUISITE-DIAGNOSTICS-GUIDE.zh-TW.md`
for the approved modes and recovery process.

`.dev/ai-context/local/cli-execution-routing.yaml` is an optional,
per-clone CLI execution-route binding covered by the tracked
`/.dev/ai-context/local/` ignore rule. `validate-ai-context.py` validates the
portable schema and, when the local file exists, rejects tracked, staged,
unignored, symlinked, sensitive, ambiguous, or implicitly consented records.
Agents never create or update the file implicitly; after a successful reusable
recovery they must ask first under the canonical CLI execution-routing
contract.

Source-only registered CLIs remain source-framework tooling. Their presence or
absence in an extracted target is not a prerequisite failure, and release
publication is outside this diagnostic contract.

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
- `validate-ai-context-target.py`
- `resolve-effective-rule-packet.py`
- `validate-source-dispositions.py`
- `validate-source-work-management.py`
- `validate-file-disposition-manifest.py`
- `validate-git-commits.py`
- `validate-workflow-handoff.py`
- `plan-ai-context-package-apply.py`

These scripts inspect AI context, markdown, prompt portability, or repository hygiene. They are not substitutes for dotnet C# validation.

`validate-source-work-management.py` checks the source repository's live GitHub
authority boundary, the frozen `.dev/backlog` path-and-byte identity, historical
v0.5.0-v0.9.0 `backlog_refs`, v0.10.0+ online Issue scope, and prospective
workflow rejection of retired local planning bindings. It is deterministic and
does not use GitHub credentials or network access.

Source-maintainer release validation, tag handoff, hosted publication,
provider reconciliation, release rendering, package building, immutable source
history, and source load/evaluation entrypoints are intentionally excluded from
target packages. Their names and commands belong to upstream source policy and
runbooks; this portable instruction path does not make them target actions.

`resolve-effective-rule-packet.py` is the shared, read-only action-time resolver for one exact
`capability` / `execution_mode` / `technology_profile` / `file_type` tuple. Every invocation must
select `--applicability-mode framework-source` or `--applicability-mode initialized-target`.
Framework-source mode requires explicit `--source-rule-id` and `--selection-evidence` inputs,
reads its policy, resolver, schema, and catalogs from the exact Git `HEAD`, verifies corresponding
working-tree bytes, and emits transient source-only evidence. It neither requires nor creates
`.dev/ai-context/provenance.yaml`, and it never persists evidence into a downstream package or
target authority. Initialized-target mode preserves the pinned `.dev/ai-context/provenance.yaml`,
`customizations.yaml`, freshness-validated `.dev/ai-context/effective-rules.yaml`, and selected
packet contract. Neither mode scans Markdown, ADRs, directories, remembered defaults, or alternate
skills for nearby semantics. Missing applicability, source selection, downstream provenance,
stale state, unresolved semantics, or digest-invalid evidence stops the action with a distinct
diagnostic. In initialized-target mode, `--emit-candidate` remains an explicit reconciliation aid:
it prints a packet candidate with complete effective normative statements but neither writes nor
activates it. Reconciliation publication stages all packets first and the state index last, with
rollback for in-process exceptions. It does not claim cross-file crash atomicity; a crash-mixed
candidate remains unusable because freshness and digest validation fails closed.

`validate-ai-context.py` checks objective repository facts: active index paths, literal table corruption, declared runtime-root status, canonical/Agents/Claude skill inventory parity, case-safe `AGENTS.md` and thin `CLAUDE.md` root entries, canonical wrapper-metadata target/path integrity, sub-agent dynamic/native dispositions, exact adapter target/path/schema/canonical-link/package-profile parity, policy-scoped agent-facing language, root bilingual entry ownership/link/structural markers, rule ownership registry structure, qualified governance-term namespace/owner/shorthand/machine-binding routes, canonical skill/sub-agent schema compliance, canonical template-family hygiene, and deterministic development capability routing. It scans both tracked and untracked non-ignored files so a new context file cannot bypass the gate before staging, while filtering tracked paths that are deleted in the working tree. Language lint uses exact path-and-line exceptions for deliberate routing triggers; other Han prose and selected non-ASCII punctuation fail with a file and line number. Script source, generated/example/archive/migration material, workflows, product `src`/`test` trees, and human-facing `.dev` documentation are outside that language scan; Markdown documentation under `.ai/scripts` remains in scope. Root bilingual validation checks reciprocal ownership links, headings, links, fences, inline-code identifiers, tables, lists, and ordered backtick table paths. These are structural drift guards, not proof of semantic equivalence; retained semantic review remains required when a bilingual entry changes materially.

`validate-workflow-artifacts.py` validates post-adoption workflow locator/task metadata, complete `.dev/workflows/INDEX.MD` directory coverage, locator-backed title/owner/status/timestamp/entrypoint parity, explicit legacy/no-locator rows, durable `.dev/backlog/items/*.yaml` identity/lifecycle/reference integrity, and fail-closed development implementation contracts for intent, execution mode, overlays, layered sources, subject revision, and acceptance criteria. Locators that opt into `lifecycle_contract: "1.0"` also enforce active-task cardinality, completed-workflow closure, and completed-task result semantics. An explicit `terminal_anchor_contract` binds lifecycle effects to tracked evidence: a satisfied `complete` anchor rejects active workflow/task state, while a satisfied `continue` anchor requires a reason and the exact unfinished task IDs. The error names the workflow, anchor, task, and conflicting state. The validator never infers anchors from names, paths, dates, or versions and performs no live provider access. Historical tasks and locators before their respective contract adoption remain compatible. The development implementation-contract and orchestrator acceptance tests live with `software-development-orchestrator`; the old `.ai/scripts/tests/` paths are thin compatibility entrypoints only.

`validate-assessment-artifacts.py` validates `.dev/assessments/` locator and
index coverage, `ASM-YYYYMMDD-NNN` identity, template and report paths, assessed
Git revision metadata, branch and timestamp contracts, lifecycle sections,
resume safety, and assessment relationship integrity. It does not evaluate
report prose or replace the producing skill's evidence review.

`validate-ai-context-target.py` validates only downstream
`.dev/ai-context/provenance.yaml` and `customizations.yaml`. It requires stable
semantic identities, safe paths, base and decision evidence, owner
reconciliation, active-context baseline audit, post-upgrade audit, and
fail-closed finalization without requiring source release records, Git tags, or
publication workflows.
`.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py`
is a read-only Git-tree comparison helper; it proposes an automatic candidate
only when a supplied target file is byte-identical to the recorded base. Target
truth, deletions, absent evidence, and source history remain reconciliation or
exclusion items.

`validate-dependency-versions.py` is a deterministic offline gate. In the source
framework repository it enforces byte-identical pinned Python requirement
mirrors, requirements-file use and one Python version across GitHub workflows,
and the Python entrypoint registry. The framework contains no managed .NET
project and selects no `global.json`. If an initialized target explicitly adds
target-owned `tools/**/*.csproj`, the same validator conditionally requires
exact and consistent direct package versions plus a target `global.json` whose
SDK can build the selected target frameworks. It does not scan unrelated
`.ai/` assets or require an SDK when no managed project exists. It does not
query package registries or advisory databases and therefore makes no
package-currency or vulnerability claim. The normative boundary is
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

The distribution profile assigns every projected path to exactly one component.
Broad entries may use non-overlapping `component_overrides` to classify
AI-context lifecycle skills, wrappers, target validators, and human guides
without duplicating package paths. Multiple matching overrides fail closed.

`plan-ai-context-package-apply.py` is the dry-run-first target-side package
entrypoint. It runs from the extracted envelope's `payload/.ai/scripts/`
directory, requires a clean committed target, and binds the package manifest,
target HEAD, effective component selection, selection authority evidence, and
observed path hashes and modes into the plan. Clean installation uses the
package default and accepts an explicit `--enable-provider repo-backlog`;
upgrades preserve component-aware provenance or derive the legacy backlog
provider only from a schema-1 previous inventory. Schema-2 previous inventory
without component-aware provenance and dual provenance authorities fail
closed. Incoming, previous, and operation sets are filtered together so a
disabled provider never generates removal work. Existing target
templates and locally changed managed files become reconciliation items.
Acknowledging such an item skips it; acknowledgement never grants overwrite or
delete permission. `--apply` rechecks the complete binding, rejects drift in
unchanged selected managed paths, and seals a schema-2 plan. Raw bytes are the
authority; a clean tracked Git projection may satisfy the previous identity
only when its index bytes and LF-normalized UTF-8 bytes match and no content
transform attribute is configured. The transaction ID is the plan SHA-256.
Before the first target mutation, the tool durably stores the plan, ordered
operation boundary, exact prestates, and recovery bytes under the target Git
administrative `ai-context-package-apply/<transaction-id>/` directory. Atomic
same-directory writes (including Windows `MoveFileExW` write-through namespace
transitions) and a durable state machine (`planned`, `applying`,
`interrupted`, `rolling-back`, `rolled-back`, `finalized`) make process-death
recovery explicit. Rollback seals its starting target surface and persists an
ordered reverse-prestate path prefix, so a retry can distinguish the one
in-flight restore from completed and untouched rollback paths.
Resume the exact sealed package with `--resume <transaction-id>`; restore the
exact prestate without package availability with `--rollback <transaction-id>`.
Both terminal operations are idempotent, while ambiguous state and unrelated
worktree changes fail closed.

An apply publishes `.dev/AI-CONTEXT-APPLY-PENDING.yaml` immediately before its
final journal transition. The receipt is non-authoritative until the durable
`finalized` journal binds its exact SHA-256; interruption at that boundary must
be resumed or rolled back. Target validation additionally requires the sealed
target root and starting commit to match the current target and `HEAD`. Its
schema-2 receipt binds the plan and selected-input proof identities, operation order,
every applied artifact's raw SHA-256 and intended Git mode, removed paths, the
complete selected framework-managed identity, resolved/default selection, and
applied/skipped counts by component. It never updates validated source
provenance. `ai-context-init` or `ai-context-upgrader` owns validation and
provenance finalization; reconciliation-preserved managed paths remain an
explicit target-validation failure until owner resolution.

For every selected framework-managed path, dry run also records an exact target
Git ignore match (`source`, line, and pattern). An ignored path is an explicit
unresolved item with its path, component, ownership, and the only permitted
owner dispositions: preserve the target rule, add a narrow exception, disable
the component, or keep a pending owner decision. The planner never rewrites
target-owned ignore configuration and apply refuses unresolved ignored paths
before any target byte or pending receipt is written. A successful receipt
binds every selected framework-managed path to its component, ownership, and
expected bytes; target validation and provenance finalization reject the same
missing, changed, or ignored path. This keeps plan preflight, post-install
validation, and the target critical gate on one identity without treating a
skipped path as a pass.

`measure-ai-context-load.py` is the source-only deterministic measurement
interface for representative repository-backed context traces. It requires a
clean repository at the full declared `HEAD`, exactly the `runtime`,
`skill-routing`, `release`, `handoff`, and `development` trace families, safe
unique repository-relative paths within each family, and exact Git blob, byte,
and whitespace-word evidence for every `runtime` or `full-file` load event. Its
normalized result keeps the tracked UTF-8 `repository_corpus` separate from
the actual `repository_loaded` events. A provider may report
`total_prompt_tokens`; otherwise that value is null. The deterministic
bytes-divided-by-four value is marked as a repository-loaded heuristic and is
never treated as total prompt usage.

Source-repository fail-closed and packaging regression tests use
Given-When-Then naming and disposable Git repositories. All test trees under
`.ai/scripts/tests/` and skill-owned `scripts/tests/` are explicitly
source-only, are excluded from the portable payload, and cannot contribute to
portable validation success. A freshly extracted package instead runs the
candidate-owned `.ai/scripts/validate-ai-context-payload.py` command documented
by the envelope `INSTALL.md`; its exact identity and arguments are recorded in
`metadata/validation.json`.

`test_ai_context_load_measurement.py` proves the source-only context-load
measurement contract in disposable synthetic Git repositories; it creates no
official trace or release evidence.
`test_governance_workflow_contract.py`, the concrete v0.5.0 disposition
manifest validation, the exhaustive source-disposition coverage gate, and the repository identity drift gate are
source-repository governance checks. `validate-source-governance.py` discovers
the manifest, `.ai/distribution/repository-identity-policy.yaml`, and
`.ai/distribution/source-dispositions.yaml` through the
stable source-only `.ai/distribution/governance-checks.yaml` registry so
portable scripts do not depend on dated workflow history. The identity
validator scans Git-tracked plus untracked non-ignored files and fails on
unclassified retired names, overlapping rules, stale rules, or any attempted
`current-operational` exception. These checks remain required when
`check-all.sh` detects their exact source context, but the source-only
validators, tests, registry, and workflow evidence are intentionally excluded
from public target packages. The package apply and file-disposition runtime
capabilities remain downstream-supported, while their source test modules stay
excluded. A packaged `check-all.sh` reports source-only checks as
not applicable instead of requiring unavailable release history, Git tags,
builder modules, workflow evidence, or source CI configuration.

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
- `validation-profile-registry.sh`
- `check-coding-standards.sh`
- `check-prompt-portability.sh`

`check-all.sh` executes the canonical profile membership declared in
`validation-profile-registry.sh`; CI never maintains a second copied check
list. The registry declares each stable check ID, owner, tags, profile
membership, input paths, dependencies, environment capability, timeout,
resource class, cache policy, source/downstream disposition, and callable. The
two context validators inspect repository structure or prompt portability;
neither claims C# semantic compliance. `check-coding-standards.sh` checks
required files, headings, catalog routes, executable modes, and shell syntax,
and explicitly excludes architecture completeness, example correctness, and
target technology adoption.

Use `--profile fast`, `pr`, `release`, `closeout`, or `nightly-full`. The
legacy `--quick`, `--critical`, and `--full` flags remain explicit compatibility
aliases for `pr`, `release`, and `nightly-full`. Successful runs print one line
per selected check plus a concise summary; full stdout/stderr is retained under
the ignored `artifacts/validation/` path. `--verbose` additionally prints the
retained child output and slowest-check list.

Each selected check also receives a retained `evidence.jsonl` record with its
stable validator ID/version, profile, selected-input fingerprint, environment
class, timing, output counts, log reference, outcome, and execution
disposition. The record stores hashes and counts rather than output content,
prompts, host identity, or provider token data. A prior eligible `executed`
pass with the same validator/profile/input/environment identity may be reported
as `reused`; that remains distinct from a new execution in both the compact
summary and evidence record.

Before any validation command is launched, the runner retains a repository
admission snapshot. `release` and `nightly-full` require a clean, operation-free
commit; `fast` and `pr` may use a stable dirty snapshot, but any subsequent
HEAD, index, tracked/untracked content, or Git-operation drift aborts the
remaining command chain. Admission failure retains a private failure artifact
and launches no check.

Launched checks run through `validation_process_supervisor.py`. Windows uses a
Job Object and supported Linux hosts use subreaper-aware descendant tracking;
unsupported POSIX containment is rejected before launch. A passing execution
requires a sealed log, complete descendant cleanup, exact effective-argv and
duration binding, a privacy-safe persisted argv, and matching raw plus adapter
receipts. The raw receipt treats monotonic elapsed time as the authoritative
duration and records any UTC wall-clock adjustment explicitly; the adapter
authenticates that adjustment before deriving internally consistent timing.
Legacy receipts without an adjustment retain the strict wall-clock equality
contract. Timeout, cancellation, snapshot drift, launch failure, and unproven
cleanup are never reusable passes. Selected checks that never launch are
recorded explicitly as `not-executed` and cannot impersonate supervised
execution.

The aggregate shell runner also derives every evidence timestamp from one
wall-clock origin plus monotonic elapsed time. A hosted NTP or VM clock
adjustment therefore cannot create a negative per-check duration or invalidate
otherwise authentic finalization evidence. The wall origin preserves an
epoch-compatible `started_at`; subsequent timing never re-reads wall time.

Per-check timeouts are execution ceilings, not profile budgets. The
`multi-hop-upgrade-transaction`, `package-apply`, and
`aggregate-runner-contract` ceilings include measured Windows full-suite
duration plus bounded headroom; profile membership and required enforcement
remain unchanged when those ceilings are calibrated.

After every selected ID has exactly one event, the runner verifies the final
repository snapshot, atomically writes summaries, and seals their canonical
digests with the selection, logs, receipts, and evidence records. Cache reads
and writes are disabled for terminal profiles. For eligible non-terminal
profiles, a new pass becomes reusable only after the complete invocation seal
has succeeded; failed finalization or sealing publishes neither a passing
manifest nor new reusable cache state.

For the source-only immutable-history checks, `fast` and `pr` may also report
`reused` from the tracked full-validation receipt. This path does not consume a
host-local cache and does not rescan unchanged historical blobs. The receipt
decision is itself a supervised preparation: its exact selected Python
interpreter and verifier argument vector are authenticated without persisting
the interpreter's host path, and its wrapper, raw receipt, log, snapshot, and
tracked receipt are included in the final invocation seal. A release,
scheduled full run, protected-path change, validator/schema change, unknown
diff path, or invalid receipt forces fresh native execution. Downstream runs do
not load this source receipt.

`check-all.sh` uses four enforcement classes:

- `required`: when selected by the active mode, the check must execute or carry
  an authenticated eligible reuse source; missing, non-executable/unlaunchable,
  or non-zero outcomes fail the aggregate gate;
- `conditional-required`: absence of all applicability inputs is reported as not
  applicable, partial configuration fails, and an applicable check is required;
- `advisory`: execution problems and non-zero outcomes remain visible warnings
  but do not fail otherwise successful required checks;
- `deferred`: known future work is counted separately and is never described as
  a selected required check.

Profile non-selection is distinct from a selected required check being skipped.
Invalid profiles or extra arguments return exit code `2`. A successful aggregate
result may contain explicit advisory warnings, deferred work, or not-applicable
conditional checks, but it cannot contain a selected required check that has
neither a supervised execution nor an authenticated eligible reuse source.

Current source-framework behavior is SDK-free: required profiles use Python and
shell contracts and do not install or invoke `dotnet`. A target may separately
select its own `dotnet restore`, build, test, format, analyzer, or architecture
test commands; those commands and prerequisites remain target evidence and are
not framework release gates. Retired repository grep checks remain retired.

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

Retained target-enforcement mapping:

- repository rules: `DBA1001` enforces canonical/compatibility inheritance,
  Aggregate Root constraints, aggregate method surface, query-port read-only
  behavior, and the generic writable CRUD prohibition; repository grep scripts
  have been removed.
- controller rules: `DBA1004`, `DBA1005`, and `DBA1006`; the controller grep scripts have been removed.
- mapper rules: `DBA1007` and `DBA1008`; the mapper grep scripts have been removed.
- aggregate rules: `DBA1003` and `DBA1009`; the aggregate grep scripts have been removed while invariant completeness remains test and AI review work.
- use case rules: `DBA1002` and `DBA1010` through `DBA1012`; the use case grep scripts have been removed while transaction and error-handling design remain AI review work.
- projection rules: `DBA1013` maps EF write-operation checks, while a target-owned configuration-test recipe covers marker-based EF model registration; the projection grep/config scripts have been removed.

Reference-only creation guidance is available at:

- `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/`

The framework supplies no analyzer project or test project. A target that
selects a mapping owns implementation, SDK/package versions, wiring, severity,
tests, CI, compatibility, and fresh evidence.

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
