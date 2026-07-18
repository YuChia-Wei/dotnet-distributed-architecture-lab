# Context Translation Playbook

## Required Handoff

The delegating agent supplies exactly one finalized source path, one output path, and the selected low-cost runtime/model. If any value is missing, or if the output path is the English source, stop without writing.

For root collaboration context, translate `AGENTS.md` only after `repo-structure-sync` has completed its evidence-backed English rewrite. The derived output is `AGENTS.zh-TW.md`.

The translator does not edit the finalized English source. After translation, the main agent adds reciprocal language links to both files, reruns structural and semantic parity review, and records any resulting translation adjustment.

## Translation Rules

- Preserve Markdown structure and ordering. Do not add advice, examples, rules, or interpretations.
- Keep code, commands, paths, filenames, identifiers, frontmatter keys, URLs, and template tokens unchanged.
- Keep RFC 2119-like strength aligned: `must`, `must not`, `should`, `may`, and equivalent policy words must not be weakened or strengthened.
- Prefer Taiwan usage. Retain established repository terms such as AI context, workflow, skill, runtime wrapper, source of truth, commit, and repository when translating them would reduce precision.
- Preserve the source document's canonical/derived ownership statement.

## Parity Return

Return a compact summary containing:

1. source and output paths;
2. heading, link, code-fence, inline-code, table, and list counts for both files;
3. unresolved terminology or ambiguous normative wording;
4. confirmation that no other file was modified.

The main agent owns semantic review, validation, and any commit.
