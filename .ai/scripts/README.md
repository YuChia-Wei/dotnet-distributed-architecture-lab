# AI Scripts

This directory contains transitional AI workflow scripts, context governance checks, and local tool orchestration helpers.

It is no longer the long-term home for authoritative C# semantic validation. Rules that inspect C# syntax, symbols, type dependencies, attributes, or framework API usage should move to dotnet-native validation mechanisms such as Roslyn analyzers, `.editorconfig`, `dotnet format`, architecture tests, integration tests, or dotnet tools.

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

These scripts inspect AI context, markdown, prompt portability, or repository hygiene. They are not substitutes for dotnet C# validation.

`validate-ai-context.py` checks objective repository facts: active index paths, literal table corruption, exact Git path casing in active internal references, declared runtime-root status, canonical/Agents/Claude skill inventory parity, case-safe `AGENTS.md` and thin `CLAUDE.md` root entries, canonical wrapper-metadata target/path integrity, policy-scoped agent-facing language, root bilingual entry ownership/link/structural markers, rule ownership registry structure, canonical skill/sub-agent schema compliance, canonical template-family hygiene, and deterministic development capability routing. It scans both tracked and untracked non-ignored files so a new context file cannot bypass the gate before staging, while filtering tracked paths that are deleted in the working tree. Language lint uses exact path-and-line exceptions for deliberate routing triggers; other Han prose fails with a file and line number. Script source, generated/example/archive/migration material, workflows, product `src`/`test` trees, and human-facing `.dev` documentation are outside that language scan; Markdown documentation under `.ai/scripts` remains in scope. Root bilingual validation checks reciprocal ownership links, heading-level shape, and ordered backtick table paths, not full semantic parity. Canonical schema validation is structural and path-based; it does not claim semantic equivalence between projections.

`validate-workflow-artifacts.py` validates post-adoption workflow locator/task metadata, complete `.dev/workflows/INDEX.MD` directory coverage, locator-backed title/owner/status/timestamp/entrypoint parity, explicit legacy/no-locator rows, and durable `.dev/backlog/items/*.yaml` identity, lifecycle, timestamp, index, and reference integrity.

Fail-closed shell validation regression tests use Given-When-Then naming and
comments and run entirely in disposable Git repositories:

```powershell
python .ai/scripts/tests/test_fail_closed_validation.py -v
python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v
python .ai/scripts/tests/test_ai_context_root_entries.py -v
python .ai/scripts/tests/test_ai_context_exact_case_paths.py -v
```

The shell fixture suite snapshots the real checkout before and after execution.
The wrapper-metadata fixture invokes only the bounded validator function against
temporary wrapper directories. Neither suite may source `check-all.sh` or
change files, modes, or index entries outside its temporary repository.

`shell-assets.yaml` classifies every tracked `.ai/scripts/**/*.sh` file as
`retained` or `retirement_candidates`. Retained shell assets must use Git index
mode `100755`; required entrypoints and child scripts must be retained.
`validate-shell-assets.py` enforces this contract with `git ls-files --stage`
instead of host filesystem executability, which is unreliable under Windows
Git Bash and `core.filemode=false`.

Required child-script calls in `check-all.sh` use the literal multiline form
`run_check "<script>"`, description, then `"required"` on the third line. The
shell asset validator compares those literal calls with
`check_all_required_scripts`; changing that call shape requires updating the
validator and its negative parity fixture in the same change.

### Keep As Orchestrator Only

- `check-all.sh`
- `code-review.sh`

These may remain as local workflow entry points, but their future role is to invoke dotnet-native validation and summarize outputs. They should not remain regex-based C# validators.

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

- runs analyzer and runtime-validation self-tests;
- runs `dotnet build MQArchLab.slnx --no-restore`, which proves the source-included analyzer executes against production projects through `src/Directory.Build.props`;
- keeps `DBA1001`, `DBA1015`, and `DBA1017` as visible staged-adoption warnings linked to target-repository backlog items, with error severity restored after their migrations;
- does not invoke the retired repository grep checks.

### Replace With Roslyn Analyzer Or Architecture Tests

- `check-test-compliance.sh`
- `check-test-di-compliance.sh`
- `check-data-class-annotations.sh`
- `check-domain-events-compliance.sh`
- `check-framework-api-compliance.sh`

Completed replacement:

- repository rules: `DBA1001` enforces canonical/compatibility inheritance,
  Aggregate Root constraints, aggregate method surface, query-port read-only
  behavior, and the generic writable CRUD prohibition; repository grep scripts
  have been removed.
- controller rules: `DBA1004`, `DBA1005`, and `DBA1006`; the controller grep scripts have been removed.
- mapper rules: `DBA1007` and `DBA1008`; the mapper grep scripts have been removed.
- aggregate rules: `DBA1003` and `DBA1009`; the aggregate grep scripts have been removed while invariant completeness remains test and AI review work.
- use case and Handler rules: `DBA1002`, `DBA1010` through `DBA1012`, and `DBA1014` through `DBA1017`; the use case grep scripts have been removed while transaction and error-handling design remain AI review work.
- projection rules: `DBA1013` covers EF write operations and `DotnetBackendValidation` verifies marker-based EF model registration; the projection grep/config scripts have been removed.

Analyzer source template:

- `tools/DotnetBackendAnalyzers/`
- `tools/DotnetBackendAnalyzers.Tests/`

### Replace With Dotnet Tool Or Tests

- `check-dockerfile-csproj-copy-sync.ps1`
- `check-dotnet-config.sh`
- `check-spec-compliance.sh`
- `check-mutation-coverage.sh`
- `test-profile-startup.sh`
- `validate-dual-profile-config.sh`

These are not necessarily Roslyn analyzer rules. They belong in dotnet tools, integration tests, config tests, Stryker.NET configuration, or CI orchestration.

### Retired Generated Regex Checks

The markdown-to-shell generator, its parser and guide, and the `generated/`
outputs were removed under AIC-007. The root archive grep check was also removed
because its stale `HardDelete` text rule contradicted the active archive/purge
standard. Historical workflow evidence retains the original transition record.

`check-test-compliance.sh` remains temporarily as an explicitly advisory helper
until its rules are split across `.editorconfig`, analyzers, and test architecture
checks. It is manually maintained and cannot be regenerated from Markdown.

## AI Reasoning Context

Do not remove software engineering reasoning context from `.ai`, `.dev`, or skills as part of this transition.

Analyzers and CI gates can enforce formalizable rules, but they do not replace design reasoning used by:

- `bdd-gwt-test-designer`;
- `code-reviewer`;
- `ddd-ca-hex-architect`;
- requirement/spec/problem-frame authoring skills.

The context remains useful even when executable validation moves to dotnet-native tooling.

## Related Files

- `.ai/assets/tech-stacks/dotnet-backend/README.MD`
- `.dev/standards/AI-CONTEXT-BOUNDARY.md`
