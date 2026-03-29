---
name: bdd-gwt-test-designer
description: Design Given-When-Then tests for this repository. Use when Codex needs to turn requirements, specs, acceptance criteria, or existing behavior into BDD/Gherkin-style test scenarios, scenario matrices, assertion points, or test design notes without directly implementing the tests yet.
---

# BDD GWT Test Designer

## Overview

Use this skill to design tests in Given-When-Then form.
It is for test design and scenario decomposition, not for implementing test code.

## Quick Start

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Read [references/scope-rules.md](references/scope-rules.md) to confirm the task is about test design.
3. Read [references/scenario-design-playbook.md](references/scenario-design-playbook.md) before drafting scenarios.
4. Read [references/output-contract.md](references/output-contract.md) before returning results.

## Workflow

### 1. Identify the source of truth
Prefer these inputs in order:
- `.dev/requirement/`
- `.dev/specs/`
- ADR or architecture constraints
- existing code behavior if the design task is reverse-engineering

### 2. Extract behaviors
Turn the input into explicit behaviors:
- preconditions
- trigger action
- observable outcomes
- negative paths
- domain rule variants

### 3. Draft GWT scenarios
For each behavior:
- one clear Given section
- one main When action
- one or more Then assertions
- And only when it improves clarity

### 4. Map scenarios to test intent
State whether each scenario is best suited for:
- aggregate test
- use case test
- reactor test
- controller test
- integration test

### 5. Stop before implementation
Do not write final xUnit test code unless the user explicitly asks for implementation.
If implementation is needed, hand off to the relevant test generation workflow or implementer.

## Scope Rules

### What This Skill Owns
- scenario discovery
- Given-When-Then decomposition
- acceptance criteria to scenario mapping
- assertion planning
- edge case and negative path coverage planning

### What This Skill Does Not Own
- final test code implementation
- choosing architecture boundaries
- changing production code
- broad test refactoring execution

## Output Expectations

Return:
1. source inputs used
2. scenario list in Given-When-Then form
3. recommended test level for each scenario
4. assertion points and important data setup notes
5. missing information or ambiguous rules

## References

- [references/scope-rules.md](references/scope-rules.md)
- [references/scenario-design-playbook.md](references/scenario-design-playbook.md)
- [references/output-contract.md](references/output-contract.md)
