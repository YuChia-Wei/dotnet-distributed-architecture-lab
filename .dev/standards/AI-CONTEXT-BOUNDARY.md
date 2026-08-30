# AI Context Boundary

This standard defines where AI collaboration context belongs and how to separate reusable context from .NET backend-specific context and repo-specific truth.

## Context Classes

| Class | Meaning | Primary Location |
| --- | --- | --- |
| Universal AI context | Canonical portable baseline concepts, rules, constraints, and abstract enforcement capabilities reusable across repositories and technology stacks. | `.ai/assets/shared/` |
| Skill context | Canonical top-level skill specs and skill references. | `.ai/assets/skills/` |
| Sub-agent context | Owning-skill bounded worker role prompts and references; they may execute direct inline or through genuine delegation. This category does not prove an invocation. | `.ai/assets/sub-agent-role-prompts/` |
| Tech-stack context | Canonical portable profile defaults, rules, constraints, bindings, bundled tooling, and execution context tied to a specific stack profile. | `.ai/assets/tech-stacks/<profile>/` |
| Runtime wrapper context | Thin runtime entries for a specific agent tool. | `.agents/skills/`, `.claude/skills/` |
| Source governance and ownership registry | Framework governance, ownership classification, and the registry that identifies each artifact's canonical owner. A current registry record whose legacy `canonical_path` is here is transitional-unmigrated until reclassified. | `.dev/standards/` |
| Target-effective AI-context truth | A target's adopted rule and constraint state, semantic deltas, tuning, waivers, provenance, and decision evidence. It is shared execution truth for humans and agents. | `.dev/ai-context/` |
| Other project truth | Requirements, domain language, specs, operations, architecture facts, workflows, and decisions that are not target-effective AI-context records. | `.dev/` |
| Human guide | Human-facing explanations, tutorials, and prompt usage guides. | `.dev/guides/` |

## Current Tech-Stack Profile

The current specialized profile is:

```text
dotnet-backend
```

It covers .NET backend systems using DDD, Clean Architecture, CQRS, repository patterns, persistence, message integration, testing, and backend host configuration.

It explicitly excludes Razor, Blazor, MAUI, ASP.NET MVC view rendering, and other .NET frontend UI frameworks. Those belong to a future full-stack or UI-specific template/profile.

## Placement Rules

- Put cross-technology portable baseline concepts, rules, constraints, and abstract enforcement capabilities in `.ai/assets/shared/`.
- Put .NET backend-only baseline defaults, rules, constraints, bindings, and bundled tooling in `.ai/assets/tech-stacks/dotnet-backend/`.
- Put source governance and the ownership registry in `.dev/standards/`. A current registry record with a legacy `canonical_path` under `.dev/standards/` is resolved as `transitional-unmigrated` until the migration matrix reclassifies it; `.dev/standards/` is not the blanket future owner for framework semantics.
- Put a downstream target's effective semantic state, deltas, tuning, waivers, provenance, and reconciliation evidence in `.dev/ai-context/`. `.dev/` is shared execution truth, not a human-only tree.
- Put canonical skill specs in `.ai/assets/skills/<skill-id>/`.
- Put owning-skill bounded worker role definitions in `.ai/assets/sub-agent-role-prompts/<role-id>/`; they may execute direct inline or through genuine delegation, and placement alone does not prove an invocation.
- Put Codex runtime wrappers in `.agents/skills/<skill-id>/`.
- Put Claude-compatible wrappers in `.claude/skills/<skill-id>/`.
- Put project requirements, domain language, specs, operations truth, workflow artifacts, and architecture facts under `.dev/`.
- Put human-facing guides under `.dev/guides/`.

## Folder First, Metadata Second

Folder placement is the primary classification mechanism. Metadata is useful only for machine-readable canonical assets such as:

- `skill.yaml`
- `sub-agent.yaml`
- prompt package YAML files
- workflow task JSON files
- registry or schema files

Do not add frontmatter or scope metadata to every Markdown file just to classify it. Prefer moving the file to the correct folder or linking it from a clear index.

## Tool-Neutral Evidence Boundary

Rule ID: `AICTX-EVIDENCE-001`

Optional repository indexes, code graphs, IDE indexes, MCP servers, semantic
search, and similar tools are discovery accelerators. They may identify candidate
files, sections, or relationships, but their output is not authoritative project
truth and must not be the sole evidence for an AI-context finding, absence claim,
inventory, or relationship conclusion.

- Keep AI-context skills usable when no optional discovery tool is installed.
- Do not require one vendor, graph schema, hook, cache, or persisted index.
- Verify material findings against direct repository files, Git-tracked paths,
  structured manifests, or repository-owned deterministic validators.
- Treat an empty search result as unknown until the declared scope is checked by
  a tool-independent fallback.
- Record tool name, index freshness, scope, exclusions, and skipped checks when
  tool output materially accelerated an assessment.
- Prefer the narrowest direct verification needed for a candidate finding; an
  accelerator may choose where to look, but it may not decide what is true.

### Quick Fallback Verification

Use these repository-native checks before accepting a discovery-tool conclusion:

| Risk | Fast verification |
| --- | --- |
| Hidden or skipped AI-context roots | Run `git ls-files -- .ai .dev .agents .claude .codex .github AGENTS.md CLAUDE.md AGENTS.zh-TW.md README.md README.en.md`, then inspect `git status --short --untracked-files=all` for untracked context. |
| Incomplete Markdown inventory | Run `git ls-files -- '*.md'` and compare the relevant paths with the tool result. |
| Missing Markdown relationship | Search the literal target or link text with `git grep -n -F -- '<target-or-link-text>' -- '*.md'`, open the source file, and resolve the target relative to that file. |
| Stale index or snapshot | Compare the tool's recorded revision, when available, with `git rev-parse HEAD`; directly reopen every file used by a material finding. |
| Tool-specific omissions | Run `python .ai/scripts/validate-ai-context.py` for registered context contracts and record any relationship class the validator does not cover. |

The 2026-07-13 Codebase Memory MCP probe is an example, not a permanent
product contract: its full index omitted `.claude/` and exposed Markdown files
and headings without Markdown link edges. Re-test current tool behavior when it
matters, and use the fallback checks above regardless of tool brand.

### Generated Inventory Contract

A generated inventory, index, graph export, or snapshot that is retained as a
repository artifact must identify its generator, generation time, source Git
revision or input digest, scope, and exclusions. It must also state how a user
can reproduce or validate it. If those fields are absent or its source revision
differs from the subject revision, treat it as a discovery hint rather than
primary evidence.

- Do not overwrite human-owned or file-backed truth with a generated view.
- Do not infer completeness from a generated artifact merely because it is committed.
- Prefer a repository-owned deterministic regeneration or parity check when the generated artifact is an active catalog.
- When no active generated inventory exists, record the check as not applicable instead of creating one solely for convenience.

## Decision Checklist

Before creating or moving an AI context file, answer these questions:

1. Can this file be reused across non-.NET repositories without rewrite?
   - Yes: use universal AI context.
2. Is it reusable only for .NET backend repositories?
   - Yes: use `tech-stacks/dotnet-backend`.
3. Does it describe this repo's actual domains, ubiquitous language, services, queues, specs, operations, or workflow state?
   - Yes: use `.dev/`.
4. Is it only a runtime entry for a specific agent?
   - Yes: use a thin wrapper under `.agents/` or `.claude/`.
5. Is it meant primarily for humans to learn or invoke a workflow?
   - Yes: use `.dev/guides/`.

## Anti-Patterns

- Do not hide .NET backend rules in universal shared context.
- Do not duplicate canonical skill instructions in runtime wrappers.
- Do not put project-specific requirements or specs under `.ai/`.
- Do not use a frontend or full-stack folder for the current .NET backend-only profile unless a separate profile is explicitly created.
- Do not rely on metadata when folder placement can express the boundary.
- Do not let a projection, wrapper, checklist, or example become a second normative owner through repeated `MUST` language.
- Do not infer that a file, directory, or Markdown relationship is absent solely because an optional index or graph omitted it.

## Engineering Identity And Semantic Ownership

Canonical portable universal baseline contract:
`.ai/assets/shared/governance/ENGINEERING-IDENTITY-CONTRACT.md`

Framework identity contract: `ENG-IDENTITY-001`

The framework distinguishes an engineering meaning from the mechanisms that
observe or enforce it. The machine-readable registry defines the exact record
shape; these identities are the common vocabulary for standards, portable
projections, target-effective records, migration matrices, and compatibility
records.

| Kind | Stable identity | Canonical owner | Not the owner |
| --- | --- | --- | --- |
| Engineering concept | `concept_id` (`CONCEPT-...`) | a cross-technology baseline record under `.ai/assets/shared/` | a profile, Diagnostic, package, target configuration, or registry alone |
| Normative rule | `rule_id` (existing registered IDs remain valid; new IDs may use `RULE-...`) | the classified baseline record under `.ai/assets/shared/` or `.ai/assets/tech-stacks/<profile>/` | a projection of another record, checklist, skill, or provider |
| Observable constraint | `constraint_id` (`CONSTRAINT-...`) | the classified baseline record under `.ai/assets/shared/` or `.ai/assets/tech-stacks/<profile>/` | a Diagnostic ID, command, or test name |
| Abstract enforcement capability | `capability_id` (`CAPABILITY-...`) | a cross-technology capability record under `.ai/assets/shared/` | a particular analyzer, validator, package, or runtime configuration |
| Technology binding | `binding_id` (`BINDING-...`) | the selected profile binding under `.ai/assets/tech-stacks/<profile>/` | the bound provider, Diagnostic ID, package version, or target configuration alone |

One concept may support several rules; one rule may yield several constraints;
and a constraint may use several abstract capabilities and technology bindings.
Bindings identify *how* a selected profile may enforce a constraint. They do
not redefine the concept, rule, or constraint that they reference.

Portable framework baselines are delivered under these distinct locations:

- cross-technology baseline semantics: `.ai/assets/shared/`;
- .NET-specific baseline defaults, bindings, and bundled tooling:
  `.ai/assets/tech-stacks/dotnet-backend/`;
- target-effective semantic state and target-selected enforcement disposition:
  `.dev/ai-context/`.

`.dev/standards/` owns the source-governance and registry records that classify
these owners; it does not become a second semantic owner. A current record
whose legacy `canonical_path` is under `.dev/standards/` is
`transitional-unmigrated` until the migration matrix assigns its portable
baseline location. The matrix must preserve each existing identity and name one
canonical statement; it must not invent a path-derived replacement ID.

### Reference Integrity And Ambiguity

- Every cross-artifact reference declares both its kind and stable ID, resolves
  to exactly one registered record, and is type-valid for the relationship.
- IDs are immutable while their engineering meaning is unchanged. A file move,
  rewritten projection, provider swap, diagnostic renumbering, or package
  upgrade retains the existing semantic ID. A changed meaning needs an
  explicit `supersedes` relationship and owner decision, not an alias silently
  chosen by a consumer.
- A missing, duplicate, path-first, type-invalid, or ambiguous reference is
  `unresolved`. Consumers must report that state and fail closed; they must not
  silently substitute a framework default, a similarly named Diagnostic, or a
  provider-specific rule.
- A provider, analyzer, runtime validator, test command, Diagnostic ID, or
  target `.slnx`, `Directory.Build.props`, `.editorconfig`, package, and
  configuration setting may implement, select, tune, or waive enforcement.
  None of them owns normative engineering semantics or may silently mutate
  target-owned configuration.

### Source-Repository Applicability

Framework-source action execution must select `framework-source` explicitly and
follow source-only policy `.dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml`.
It binds the exact source repository, commit, policy, resolver, schema, catalog
bytes, selectors, explicit rule IDs, selection evidence, and normative statement
digests. This transient evidence is source-only. It does not require, fabricate,
or satisfy downstream `.dev/ai-context/provenance.yaml`, target-effective state,
or packet authorities, and it must not enter a downstream package.

Applicability is never inferred from a missing provenance file, remembered
default, broad scan, or alternate skill. A source identity or execution-byte
mismatch is a source applicability failure, separate from downstream provenance,
staleness, unresolved-semantic, and digest failures.

### Initialized-Target Effective Consumption

Initialized-target routine action work consumes a freshness-validated,
task-scoped effective rule
packet rather than scanning all target documents or relying on remembered
framework defaults. The packet retains the selected rule and constraint's full
normative statement and records the baseline version, target-state digest, and
loaded IDs. Its resolver and packet format are implemented separately; until
then, an absent or stale effective state is unresolved rather than permission
to fall back silently.

## Rule Ownership

See [AI Context Rule Ownership](AI-CONTEXT-OWNERSHIP.md) and its machine-readable
[registry](AI-CONTEXT-OWNERSHIP.yaml). Folder placement classifies the context;
the registry resolves normative ownership when the same rule is consumed across
multiple surfaces.
