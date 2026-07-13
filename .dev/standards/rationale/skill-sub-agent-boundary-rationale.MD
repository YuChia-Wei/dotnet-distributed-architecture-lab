# Skill and Sub-Agent Boundary Rationale

## Decision Pattern

Distinguish between two kinds of AI assets:

- top-level skill
- delegated sub-agent role

## Why

### 1. Different Entry Levels

A skill is a high-level capability that a human or main agent can invoke directly.
A sub-agent role is delegated to a worker inside a workflow.

### 2. Avoid Taxonomy Confusion

Promoting every executable prompt to a skill would blur the distinction between:

- top-level capability
- worker role
- shared prompt material

### 3. Support Portable Knowledge-Base Organization

When skills and sub-agents are clearly separated, `.ai/` can retain a stable, portable structure instead of being reorganized whenever runtime wrappers change.

## Why Not

### Make Every Executable Prompt a Skill

Drawbacks:

- Too many runtime entries.
- An unclear boundary with delegated workers.
- A wrapper strategy that is difficult to maintain.

## Practical Rule

- top-level capability -> skill
- delegated bounded worker -> sub-agent role prompt
- checklist / template / shared rules -> supporting materials
