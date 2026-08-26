# .ai Index

This index owns the file and directory catalog for `.ai/`. The `.ai/README.MD` file explains the folder purpose and boundary.

## Entry Documents

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.ai/`. |
| `INDEX.MD` | File and directory catalog for `.ai/`. |
| `DIRECTORY-RULES.MD` | Operational placement rules that point to canonical boundary and language policies. |
| `SUB-AGENT-SYSTEM.MD` | Active sub-agent routing and artifact handoff rules. |
| `distribution/` | Source-side package profiles, ownership rules, and generated metadata schemas. |
| `evaluation/` | Source-side deterministic behavior corpus, exact baseline, and result schemas. |

## Canonical Assets

| Path | Description |
| --- | --- |
| `assets/` | Canonical source root for reusable AI assets. |
| `assets/README.MD` | Purpose and boundary of `.ai/assets/`. |
| `assets/shared/` | Universal shared prompt fragments, rules, and supporting materials, including the canonical universal engineering-rule catalog. |
| `assets/tech-stacks/` | Tech-stack-specific reusable AI context. |
| `assets/tech-stacks/dotnet-backend/` | .NET backend-only agent context, including the resolver-ready profile rule catalog and its Markdown owners. |
| `assets/tech-stacks/dotnet-backend/engineering-rule-catalog.yaml` | Resolver-ready exact projection for registered .NET backend rules. |
| `assets/tech-stacks/dotnet-backend/standards/` | Canonical Markdown owners for migrated .NET backend profile rules. |
| `assets/tech-stacks/dotnet-backend/examples/` | Canonical landing path for migrated .NET backend profile examples. |
| `assets/tech-stacks/dotnet-backend/templates/` | Canonical landing path for migrated .NET backend profile templates. |
| `assets/tech-stacks/dotnet-backend/references/` | .NET backend reference indexes, pitfalls, failure cases, and templates. |
| `assets/skills/` | Canonical top-level skill specs. |
| `assets/skills/README.MD` | Canonical skill registry entry. |
| `assets/sub-agent-role-prompts/` | Canonical delegated sub-agent role prompts. |
| `assets/templates/` | Reusable prompt, command, and skill templates. |

## Scripts

| Path | Description |
| --- | --- |
| `scripts/` | Transitional local workflow scripts and orchestration helpers. |
| `scripts/README.md` | Script transition policy and inventory. |
| `scripts/validate-ai-context.py` | Active index, runtime-root, table-integrity, and skill-wrapper parity validation. |
| `scripts/python-entrypoints.json` | Registry for supported Python CLI prerequisite contracts. |
| `scripts/run-python-entrypoint.sh` | POSIX interpreter-discovery launcher for registered Python CLIs. |
| `scripts/run-python-entrypoint.ps1` | PowerShell interpreter-discovery launcher for registered Python CLIs. |

## Related Human-Facing Docs

| Path | Description |
| --- | --- |
| `../.dev/guides/README.MD` | Human-facing guide root. |
| `../.dev/guides/ai-collaboration-guides/INDEX.MD` | AI collaboration guide index. |
| `../.dev/guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md` | Human-facing strategy for AI asset placement. |
| `../.dev/guides/ai-collaboration-guides/AI-CONTEXT-INIT-SKILL-GUIDE.md` | Repo initialization and context sync guide. |
| `../.dev/guides/ai-collaboration-guides/PYTHON-PREREQUISITE-DIAGNOSTICS-GUIDE.zh-TW.md` | Human recovery and target-local validation-selection guide. |
| `../.dev/standards/AI-CONTEXT-BOUNDARY.md` | Canonical context boundary policy. |
| `../.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` | Canonical language policy. |
