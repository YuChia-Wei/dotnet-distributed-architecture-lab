# Document Targets

This skill updates repo-specific architecture areas only.

## Primary Targets

### `agents.md`

Update:

- quick-start wording if the repo's architecture entry docs changed
- stack rules that describe the current codebase
- file and directory index entries tied to actual repo structure
- skill/index references that help future agents navigate the copied repo

Preserve:

- collaboration precedence
- mandatory workflow rules unless the user explicitly changes them

### `.dev/ARCHITECTURE.MD`

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
