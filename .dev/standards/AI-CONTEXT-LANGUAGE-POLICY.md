# AI Context Language Policy

This policy defines the default language for AI-facing and human-facing documentation.

## Goals

- Keep agent-facing execution context concise and cheap to read.
- Keep human-facing project knowledge approachable for Traditional Chinese Taiwan readers.
- Avoid translation sprawl by limiting bilingual files to stable entry points.

## Defaults

| Document Class | Default Language | Reason |
| --- | --- | --- |
| `.ai/**` | English | Agent-facing context should minimize token cost and ambiguity. |
| `.agents/**` | English | Runtime wrappers are agent-facing. |
| `.claude/**` | English | Runtime wrappers are agent-facing. |
| `.dev/specs/**` | English | Specs are structured execution truth used heavily by agents. |
| `.dev/problem-frames/**` | English | Problem frames are machine-readable validation artifacts. |
| `.dev/standards/**` | English | Standards are execution contracts for agents and reviewers. |
| `**/INDEX.md`, `**/INDEX.MD`, `**/index.md` | English | Index files are navigation surfaces for agents. |
| `.dev/requirement/**` | Traditional Chinese Taiwan or English | Requirements are human-facing project truth unless a file is machine-readable. |
| `.dev/guides/**` | Traditional Chinese Taiwan or English | Human-facing guides may use zh-TW; execution contracts should link to English standards. |
| `.dev/operations/**` | Traditional Chinese Taiwan or English | Operations docs are human-facing project truth, but schemas and tables may use English terms. |
| `.dev/workflows/**/tasks/*.json` | English | Task JSON is machine-readable workflow state. |
| `.dev/workflows/**/workflow-plan.md` | English preferred | Plans are handoff artifacts used by agents and humans. |

## Bilingual Entry Files

Bilingual variants are allowed for stable entry points only:

- `README.md`
- `README.en.md`
- `README.zh-tw.md`
- `AGENTS.md`
- `agents.en.md`
- `agents.zh-tw.md`

`CLAUDE.md` is an English runtime-specific entry, not a bilingual content
owner. Keep it thin and import the canonical `AGENTS.md` instead of translating
or duplicating the collaboration rules.

Do not create bilingual variants for every guide or standard by default. Add a translation only when the file is a stable entry point or a user explicitly needs the translated document.

## Translation Ownership

When bilingual variants exist:

- English files are the preferred source for agent-facing execution rules.
- zh-TW files are the preferred source for human onboarding and project explanation.
- One file must state whether it is canonical or translated.
- Translation work should be tracked as a separate task when it affects more than one entry file.

## Mixed-Language Files

Mixed-language files are allowed only when:

- code identifiers, package names, or domain terms are naturally English;
- a zh-TW human-facing file references English commands or paths;
- a legacy file is being migrated and full rewrite is out of scope.

Do not mix languages in new agent-facing execution rules.

## Practical Rule

If an agent must read the file to execute work, prefer English. If a human maintainer must read the file to understand project intent, zh-TW is acceptable. If both are equally important, create a bilingual entry file rather than mixing full paragraphs in one file.
