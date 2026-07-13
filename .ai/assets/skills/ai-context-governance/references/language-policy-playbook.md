# Language Policy Playbook

Use this playbook when deciding whether documentation should be English, Traditional Chinese Taiwan, or bilingual.

## Defaults

- Agent-facing context: English.
- Runtime wrappers: English.
- Machine-readable task/spec/frame artifacts: English.
- Human-facing requirements and guides: Traditional Chinese Taiwan is allowed.
- Entry files may have bilingual variants.

## Bilingual Limits

Allow bilingual variants for stable entry files:

- `README.md`
- `README.en.md`
- `README.zh-tw.md`
- `AGENTS.md`
- `agents.en.md`
- `agents.zh-tw.md`

Do not create translation pairs for every guide or standard unless the user explicitly asks for a translation workflow.

## Rewrite Guidance

When converting an agent-facing file to English:

- keep commands, paths, and identifiers exact;
- preserve canonical rule meaning;
- remove explanatory human tutorial tone where possible;
- link to human-facing zh-TW guides instead of embedding long translations.

When writing a human-facing zh-TW guide:

- use Traditional Chinese Taiwan wording;
- keep code identifiers and file paths in English;
- avoid duplicating canonical rule bodies that already live in English standards or skill references.
