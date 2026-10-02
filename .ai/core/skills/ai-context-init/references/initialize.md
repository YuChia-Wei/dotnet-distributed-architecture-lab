# Initialization and refresh

## Establish the target and authority

Resolve the target root and the requested output before inspecting project files.
Read its applicable AGENTS files, current Git/worktree state when available, and
explicitly selected requirements or decisions. A non-Git or empty directory is
valid; do not create Git history or a remote as a side effect. Project instructions
and explicit owner choices govern layout, language, workflow and validation.

Inspect only enough to establish languages, manifests, solution/workspace entry,
source/test roots, executable hosts, dependency direction, selected runtimes and
commands. Prefer target discovery tools when available, then verify material facts
against current files. Existing directory names alone do not establish architecture
or adoption. Record source paths for facts, and distinguish observed implementation
from intended requirements and accepted decisions. Report conflicts instead of
silently choosing one. Do not read secret values; configuration key names and safe
examples normally suffice. Do not copy credentials into context or evidence.

For an empty target, establish purpose and stack constraints with the owner when
they affect the output. Useful generic AGENTS guidance can be drafted while those
choices remain unresolved. Unknowns are explicit, not invented projects, business
contexts, commands, CI providers or dependency versions.

## Select a small output set

Use [structure guidance](project-structure.md) to map existing paths. The normal
minimum is a root collaboration entry and a concise navigation entry when multiple
project documents warrant one. An existing satisfactory file may require no edit.
Add inventories, architecture or technology requirements only when they serve an
identified need; do not manufacture empty documents or directories for every row.

Use [AGENTS](../templates/public-root/AGENTS.md) as the baseline for a missing root.
Retain its scope, progressive loading, authorization and truthful validation rules.
Fill Repository-Specific Context with evidence-backed facts, command working
directories and selected navigation. Resolve actual installed runtime entry names
(original or prefixed) rather than assuming either. A missing skill installation
does not block project context and must not produce a link to a nonexistent route.

Optional resources are [CLAUDE](../templates/public-root/CLAUDE.md),
[README](../templates/public-root/README.md),
[development overview](../templates/public-catalogs/dev/README.MD),
[development index](../templates/public-catalogs/dev/INDEX.md),
[project inventory](../templates/project-config.template.yaml),
[architecture](../templates/architecture.md) and
[technology requirements](../templates/technology-requirements.md).
Their prompts are authoring instructions: remove those prompts from output, resolve
placeholders, or write an explicit unknown. Do not present unconfigured commands as
quick-start instructions. Inventory YAML is an optional project-owned format, not
framework configuration, a validated universal schema or a new precedence source.

## Preserve existing content

Before writing, capture the expected bytes/hash for each existing selected file or
its expected absence. Treat path aliases, symlinks, case collisions, generated
files and ownership uncertainty as conflicts to resolve before touching that path.
Do not follow an unexpected link outside the selected target. A selected file with
unrelated local edits needs a narrowly composed diff, never reset or regeneration.

For an existing AGENTS, the repository-specific section is the primary fact update
zone. Keep its current heading when equivalent. Outside it, make only requested or
necessary navigation corrections supported by actual target paths. Preserve all
other custom rules and sections. If there is no clear fact zone, append a concise
section or propose the structural change instead of replacing the document.
Refresh uses the same rule; provenance alone never authorizes a whole-file rewrite.
Do not overwrite an existing Claude adapter, README or project inventory with a
seed. Preserve comments, custom keys, language and formatting where possible.

English is the default canonical language for a new agent entry unless target
instructions select otherwise. Derive any requested Traditional Chinese (Taiwan)
translation only after the canonical facts and rules are final, preserving their
structure and normative meaning. Preserve existing language ownership. A new
CLAUDE entry is thin and imports the actual canonical file; it needs no copied
rules. Other runtimes need their own selected adapter, not an invented equivalent.

## Apply and verify

Prepare the exact file/directory changes and preserve the evidence for material
facts. Reuse the user's existing write authorization. If authority is missing,
show the concrete proposal before asking; do not perform dependent mutations.
Immediately before a write, recheck its expected preimage/absence. If it drifted,
re-read and reconcile the affected diff; do not overwrite concurrent work.

Apply with ordinary permitted file tools. When the caller explicitly selects the
installer's existing project-edit transaction, hand it exact desired bytes and
preimage constraints under that API's contract. Do not implement a new transaction,
edit managed `.ai/core/` or runtime skill entries, forge an installation lock, or
change installation selection as part of document initialization. Context authoring
does not migrate or recover a legacy published package format.

Read back actual changed files and review the diff. Check local links against real
destinations, parse authored YAML/JSON where applicable, and ensure no unresolved
seed prompts, copied source-project facts or unintended changes remain. Confirm
unchanged custom sections and files against their captured bytes/diff. For commands,
record source, working directory, prerequisites and `discovered`, `executed-passed`,
`executed-failed`, `blocked` or `not-configured`. Run only selected authorized checks;
do not run installation, deployment or a broad suite merely to fill a table.

Return the actual files, meaningful changes, unresolved decisions and verification
limits. Installing this skill is not initialization; initialized documentation is
not proof that an agent follows it, that the product runs, or that CI passed.
