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

- start from `.ai/assets/skills/ai-context-init/templates/project-config.template.yaml`
- use `null` or empty collections for unknown facts
- never copy source-template credentials, connection strings, ports, domains, queues, or product names
- treat repository files as stronger evidence than copied `.dev/project-config.yaml`

### `AGENTS.md`

Use `.ai/assets/skills/ai-context-init/templates/public-root/AGENTS.md` only as the installation seed. In a target guide, `Repository-Specific Context` is the primary replacement zone. If an existing guide uses another structure, identify its equivalent target-owned area before editing; do not replace the whole guide with the seed.

Write concise, evidence-backed facts in that zone:

- repository identity and purpose;
- essential entry paths and constraints that affect work;
- applicable stack facts without copied source-repository assumptions;
- target-owned setup, build, test, and validation commands with their working directories and known prerequisites.

Leave unsupported facts unresolved. Distinguish commands discovered in configuration from commands actually executed successfully. Prefer stable entry links over a full directory, skill, or rule catalog.

Outside the replacement zone, make only minimal evidence-backed navigation or quick-start adjustments when target entry paths or applicable routes differ. Keep loading task- and phase-specific; do not introduce unconditional README, architecture, index, or policy preloading.

Preserve portable collaboration precedence, existing user authorization, workflow and validation safeguards, framework skill routing, and target-owned rules unless an explicit user decision changes them. Do not treat a seed rewrite as permission to weaken these boundaries. Reuse authorization already granted for the same action and scope; ordinary implementation choices are not new approval checkpoints.

Keep detailed workflow, CLI consent, and commit mechanics with their canonical owners and link to them only when applicable. Keep English canonical for consistent execution wording. After the target-specific English rewrite is final, optionally derive `AGENTS.zh-TW.md` through the low-cost `context-translator` role with structural and normative parity. Do not copy a pretranslated root template.

### `.gitignore`

Ensure the exact `/.dev/ai-context/local/` rule exists before any optional CLI
execution-routing binding can be created. This tracked rule is
framework collaboration infrastructure, not a personal value. Do not create
`.dev/ai-context/local/cli-execution-routing.yaml` during
initialization; that file requires a later successful recovery plus explicit
user consent under the CLI execution-routing contract.

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
