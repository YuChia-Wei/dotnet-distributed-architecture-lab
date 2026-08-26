# Skill and Sub-Agent Boundary Rationale

## Decision Pattern

Distinguish between two kinds of AI assets:

- top-level skill
- delegated sub-agent role

## Why

### 1. Different Entry Levels

A skill is a high-level capability that a human or main agent can invoke directly.
A sub-agent role is a bounded worker contract owned by a skill; the owning
skill may apply that same contract inline or, when justified and supported,
delegate it to a worker.

### 2. Avoid Taxonomy Confusion

Promoting every executable prompt to a skill would blur the distinction between:

- top-level capability
- worker role
- shared prompt material

Treating a role prompt as a child invocation by default would create a second
confusion: a loaded role contract is not evidence that a runtime worker ran.

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
- bounded worker contract -> sub-agent role prompt
- checklist / template / shared rules -> supporting materials

## Execution Boundary

Role mapping and applicability stay with the owning skill. Runtime selection
uses the provider-neutral
[Role Execution Contract](../../../.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md):

- `direct` is the default and applies the same role contract inline without
  inventing a child invocation;
- `delegated` requires a justified, genuine worker invocation with execution
  evidence;
- `unavailable` and `not-applicable` are explicit dispositions, not silent
  skips; and
- an orchestrator may aggregate owner-produced role execution records and
  retain or surface the named final integration owner's decision. It may make
  that decision only when explicitly named as that owner, and never replaces
  the owning skill's domain responsibility.

Runtime adapters remain selective execution integrations. Their presence does
not promote a role to a skill or prove delegation support in the current
session.
