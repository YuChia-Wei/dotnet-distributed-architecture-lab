# Low-Dependency Development Workflow (.NET)

## Applicability

This optional .NET reference applies only to the target-selected architecture,
providers and adopted test rules. Examples do not install packages, select an ORM,
broker or Event Sourcing, create fixed project paths, or prove execution. Preserve
per-domain persistence decisions and the target-selected GWT contract; BDDfy and
mocking packages remain separately selected.

## Develop with a small toolset

Start with the target's required .NET SDK, Git, an existing AI CLI with permitted
file access, and the project's own prerequisites. Read `global.json`, project
files, package sources and existing build/test instructions; SDK availability
alone does not prove that restore, native dependencies or external services work.
An IDE, MCP server, LSP, Codebase Memory index or Framework generation bundle is
optional. Install or change tools only within the target's authorization.

### Start from the task and existing project

Use a short request such as: "Implement the accepted behavior in `<spec path>`,
starting at `<entry or interface>`, with `<observable result>`; preserve
`<constraint>`." Reuse an existing requirement instead of rewriting it into a
form. Obtain project rules, accepted architecture, writable scope, relevant
commands and current Git state from the target. Ask only for missing information
that affects the work. An unclear business outcome needs its owner; a tool's
sample behavior cannot supply it.

Locate the relevant symbols and signatures before expanding their bodies.
Read immediate callers, implementations and tests only as needed to answer the
task's questions. Prefer the target-selected graph or IDE query when available;
verify its source identity and coverage. If unavailable or incomplete, disclose
that limit and use permitted tracked-file search and bounded reads. Never infer
symbol absence or complete references from an empty or stale index. This order
limits unnecessary context; it is not measured token savings.

### Choose the implementation path

| Starting point | Work to perform |
| --- | --- |
| An accepted interface | Read its signatures, nullability, error/cancellation behavior and relevant callers. Implement that actual contract and the specified business behavior; preserve compatibility and target registrations where applicable. |
| An accepted specification | Locate the existing entry and responsibility, then implement the behavior within the accepted design. Introduce an interface only when that design needs one; no default interface, CQRS or Use Case structure is required. |

Use a slice for coordinated behavior or contract changes, and a local operation
for a bounded technical change preserving accepted contracts. The number of files
or methods does not decide the scope. Stop dependent edits for an unresolved
contract or architecture decision; continue unaffected authorized work.

Choose a tool separately for each operation:

| Need | Applicable capability |
| --- | --- |
| Locate symbols or inspect code | Available, permitted IDE/MCP or graph queries; otherwise the target's permitted search and file reads. |
| Create repeatable project or item structure | SDK templates, or explicitly available Framework templates whose output fits the task. Inspect options, preview paths and resolve collisions first. |
| Implement an arbitrary interface or business rule | A suitable IDE operation, or AI editing of the actual target code followed by compiler and behavior checks. A fixed template does not interpret arbitrary interfaces. |
| Perform a supported refactoring | Prefer an applicable permitted IDE/MCP operation. If a needed capability is missing, inspect the selected Framework tool's actual support and safety contract before using it. |
| Format, build or test | The target-selected SDK commands, configuration, scope and gates. Use an additional tool only when the operation needs its capability. |

Honor explicit tool/provider selections. Report a missing capability before using
an available alternative within existing authorization; return a required provider
or permission change to its owner. Do not silently substitute tools, require all
operations to share one interface, or bypass a refactoring safety check with text
replacement. Optional knowledge and tools do not adopt project rules.

The [generation guide](generation/README.md) owns Framework template and snippet
details. When a matching template is installed, inspect `dotnet new <template>
--help` and preview the selected output with `--dry-run` before creation. Resolve
the target SDK/TFM, namespace and output paths; do not overwrite existing files to
force a fit. See [the SDK template command](https://learn.microsoft.com/dotnet/core/tools/dotnet-new).

For example, suppose an accepted specification says `IShippingQuote.Calculate`
returns zero delivery cost at or above 100 currency units and 5 below it. The
interface supplies types and the callable contract; the specification supplies
the threshold, units and expected results. A class template can provide a skeleton,
while AI editing supplies the contract-compatible implementation. Relevant checks
include 99 yielding 5 and 100 yielding 0, derived from that specification. If the
specification omits currency or negative-value behavior needed by the task, resolve
it instead of inventing it. This illustration is neither a required domain model
nor a new template or fixed test count.

### Validate and deliver a reviewable change

1. Capture initial `git status --short --untracked-files=all`, unstaged and staged differences, and
   existing untracked files. Preserve changes outside the task, including edits
   within a file this task also changes. Do not reset, clean or stage them merely
   to obtain a clean starting point.
2. Select checks from the actual changed behavior, contracts, dependencies and
   target gates. Build the affected project when compiler evidence is needed;
   use relevant tests with expected outcomes from the specification or accepted
   contract. A service/SDK/artifact interaction justifies its own check only when
   that interaction is part of the claim. No universal test count or matrix is
   added here; mandatory target gates remain required.
3. For formatting, name the project/solution, working directory, affected files
   and selected `whitespace`, `style` or `analyzers` mode. Follow the target's
   `.editorconfig` and adopted style. Resolve `--include` paths against the actual
   invocation and confirm project membership and selected-file diagnostics;
   exit 0 with zero selected files is not formatting evidence. Use the installed
   SDK's help and [format command reference](https://learn.microsoft.com/dotnet/core/tools/dotnet-format).
   Inspect any resulting code changes before final affected checks.
4. Inspect final `git diff` and `git diff --cached` from the repository root,
   plus `git status --short --untracked-files=all`. Ordinary diffs omit untracked content: read every
   newly created task file and review its complete contents, including intended
   generated output. Compare with the initial state to distinguish the task's
   changes. Staging or committing follows separate target authorization.
5. Report acceptance coverage, changed paths and scope, actual commands and
   results, remaining failures or unknowns, and the reviewable diff/new files.
   Compilation or the first passing test run does not prove all requirements.
   Preserve failures, isolate the affected cause and rerun relevant checks after
   repair; do not weaken requirements or assertions to obtain a pass. Missing
   environment evidence remains blocked or not run.

For an explicitly selected real-task trial, record the outcome, elapsed time,
available token measurements, correction attempts and user-observed obstacles.
The first task establishes a baseline; do not promise a savings percentage or
infer usability from source checks. Trial, installation and release are separate
operations under their own authorization.

## Git and change authority

Use the target project's actual commit grammar, branch/PR topology and authorized
integration operations. `git status`, `git diff` and `git log` help inspect state;
a command example does not authorize staging, pushing, merging or changing main.
For cross-machine continuation, preserve a durable checkpoint under the target's
selected workflow and provider rules. This package has no source Git-policy path
or mandatory workflow branch convention.

## Related resources

- Target-owned Git flow and commit policy (caller-supplied authority).
- [Database migration guide](../integration/persistence/database-migrations.md)
- [Microsoft .NET documentation](https://learn.microsoft.com/dotnet)
- [Microsoft EF Core documentation](https://learn.microsoft.com/ef/core)
