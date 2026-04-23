# Team Git Flow Rules

> Status:
> working-branch governance draft
>
> Release rule:
> keep this document as a reusable framework file, but rewrite the branch rules and examples so they match the target project's actual git flow before publishing to `main`.

## Purpose

This document defines the expected git flow, branch responsibilities, and branch naming rules used while building and refining the portable AI prompts baseline.

This file is intended to remain as part of the reusable template baseline, but its branch model and naming examples should be replaced with the target project's own git flow rules during release preparation.

## Branch Model

### Long-lived branches

#### `main`

- role: release-quality output branch
- meaning: the content on `main` should already be in a state that can be imported into another git repository as a template baseline
- expectation:
  - no temporary workflow execution records
  - no team-only working governance notes
  - no branch-local cleanup leftovers

#### `baseline/portable-ai-prompts`

- role: primary working branch
- meaning: this is the day-to-day integration branch for ongoing prompt/framework cleanup and restructuring
- expectation:
  - may contain temporary workflow artifacts
  - may contain temporary team coordination notes
  - may contain branch-local working documents that must be removed before release back to `main`

### Short-lived working branches

#### `codex/<workflow-id>`

- role: Codex implementation branch
- use when:
  - Codex executes a bounded workflow or staged task
  - work should remain isolated until reviewed or integrated

#### `gemini/<workflow-id>`

- role: Gemini implementation branch
- use when:
  - Gemini participates in a bounded workflow
  - multi-agent collaboration requires branch isolation

#### `claude/<workflow-id>`

- role: Claude implementation branch
- use when:
  - Claude participates in a bounded workflow
  - multi-agent collaboration requires branch isolation

### Release branch

#### `release/portable-baseline`

- role: release cleanup and transition branch
- base expectation: created from `main`
- integration expectation: merge `baseline/portable-ai-prompts` into this branch, remove non-portable artifacts, then merge back to `main`
- purpose:
  - perform final cleanup before release
  - verify the branch contains only portable baseline content
  - keep release-oriented removal work out of the main working branch

## Expected Flow

### Normal working flow

1. Start from `baseline/portable-ai-prompts`
2. Create a short-lived agent branch such as `codex/<workflow-id>`
3. Complete the bounded workflow or staged work
4. Merge back into `baseline/portable-ai-prompts`

### Release preparation flow

1. Create or refresh `release/portable-baseline` from `main`
2. Merge `baseline/portable-ai-prompts` into `release/portable-baseline`
3. Remove non-release artifacts
4. Confirm the branch is suitable as a portable repo template
5. Merge `release/portable-baseline` back into `main`

## Cleanup Rules Before Merging To `main`

The following content should be removed or normalized before release is merged into `main`:

- workflow execution records under `.dev/workflows/`, keeping only reusable templates when appropriate
- temporary branch governance notes such as this file
- any team-only coordination notes that are not part of the portable baseline
- any project-specific operational truth that should not ship as repo template content

## Naming Rules

### Branch prefixes

- `baseline/`
  - long-lived working baseline branch
- `codex/`
  - Codex-owned workflow branch
- `gemini/`
  - Gemini-owned workflow branch
- `claude/`
  - Claude-owned workflow branch
- `release/`
  - release cleanup branch

### Workflow id rule

Use a branch suffix that is stable, human-readable, and traceable to the workflow or task theme.

Recommended format:

```text
<yyyy-mm-topic>
<yyyy-mm-dd-topic>
<workflow-id-from-.dev/workflows>
```

Examples:

- `codex/2026-04-legacy-script-rename`
- `codex/2026-04-14-legacy-script-rename`
- `gemini/problem-frame-validator-pilot`

## Responsibility Boundaries

### `baseline/portable-ai-prompts`

- can accumulate active work
- can carry temporary artifacts
- should remain the main integration line for ongoing restructuring

### `release/portable-baseline`

- should be focused on subtraction, cleanup, and release validation
- should not become a second long-term working branch
- should exist to produce a `main`-safe final state

### `main`

- should stay clean, portable, and publishable
- should represent the final reusable template shape

## Decision Notes

- `main` is treated as release output, not day-to-day integration
- `baseline/portable-ai-prompts` plays the role that many repositories would normally assign to `main`
- `release/portable-baseline` exists because the final release shape requires explicit cleanup and artifact removal

## Review Trigger

Revisit this document if any of the following change:

- the repository starts publishing versioned releases directly from the working branch
- `main` stops being the portable template output branch
- multi-agent collaboration introduces additional persistent branch types
- release cleanup becomes fully automated and no longer needs a dedicated branch
