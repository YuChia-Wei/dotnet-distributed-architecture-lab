# Document Targets

Rule IDs: `TECH-SELECT-001`.

This skill updates repo-specific architecture and repo-init entry areas only.

## Primary Targets

### `.dev/project-config.yaml`

Generate or update:

- repository identity and target mode
- detected languages and technology profiles
- target technology selections using the canonical generic selection record
- .NET SDK, target frameworks, solutions, and projects when present
- source/test roots and host/library classifications
- architecture, persistence, messaging, frontend, and deployment facts only when supported by evidence
- evidence paths and unresolved facts

Rules:

- start from `.ai/assets/skills/repo-structure-sync/templates/project-config.template.yaml`
- use `null` or empty collections for unknown facts
- never copy source-template credentials, connection strings, ports, domains, queues, or product names
- treat repository files as stronger evidence than copied `.dev/project-config.yaml`

### `AGENTS.md`

Update:

- quick-start wording if the repo's architecture entry docs changed
- stack rules that describe the current codebase
- file and directory index entries tied to actual repo structure
- skill/index references that help future agents navigate the copied repo

Preserve:

- collaboration precedence
- mandatory workflow rules unless the user explicitly changes them
- skill routing rules that are framework-level rather than target-project-specific

Use `.ai/assets/skills/repo-structure-sync/templates/public-root/AGENTS.md` only as the installation seed. After the target-specific English rewrite is final, optionally derive `AGENTS.zh-TW.md` through the low-cost `context-translator` role. Do not copy a pretranslated root template.

### `CLAUDE.md`

Preserve the thin Claude Code project-memory adapter. It must import
`@AGENTS.md` and must not duplicate or override the canonical collaboration
rules. If the target repository keeps this framework's runtime entries, verify
the adapter after updating `AGENTS.md`.

### Root `README.md` and `README.en.md`

Update:

- repository identity
- setup and run instructions when file-backed facts exist
- product or framework purpose
- directory layout that reflects the target repo
- links to target-relevant docs

Preserve:

- bilingual README convention when present
- framework usage notes when the repo is intentionally an AI context framework

For empty repos, keep README content minimal and do not invent product domains, services, endpoints, or stack versions.

### `.dev/ARCHITECTURE.md`

Update:

- architecture overview
- code organization description
- module or bounded-context breakdown
- host/runtime structure

### `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`

Update:

- runtime and language version
- persistence, messaging, testing, and hosting stack

### `.dev/README.MD`

Update:

- repo knowledge index entries that point to actual architecture and skill docs
- quick-start links if entry files changed

### `.ai/README.MD` and `.ai/INDEX.MD`

Update only when needed:

- statements about where repo-specific truth belongs
- links to packaging or sync workflow guidance
- references that help agents reorient after template transfer
