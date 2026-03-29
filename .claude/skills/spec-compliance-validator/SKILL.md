---
name: dotnet/spec-compliance-validator
description: |
  Validate .NET code and tests against problem frame specs with a 100% gate.
  Supports CBF (CommandedBehaviorFrame) and SWF (SimpleWorkpieceFrame).
  Use when: "validate spec dotnet", "check compliance dotnet", "spec-compliance-validator"
allowed-tools: Read, Glob, Grep, Bash, TodoWrite
---

# Spec Compliance Validator Skill (.NET)

## Overview
This skill verifies that generated .NET code and tests fully comply with problem frame specs.
It produces a compliance report and blocks completion if any category is below 100%.

Required references:
- `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md`
- `.ai/assets/skills/spec-compliance-validator/references/test-validation-steps.md`
- `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`

## Supported Frame Types

| Frame Type | Directory | Aggregate Path | Scenarios Source |
|-----------|-----------|----------------|------------------|
| CommandedBehaviorFrame (CBF) | `cbf/` | `controlled-domain/aggregate.yaml` | `acceptance.yaml` |
| SimpleWorkpieceFrame (SWF) | `swf/` | `workpiece/aggregate.yaml` | `requirements/*.yaml` |

## Trigger Conditions
Activate when user mentions:
- "validate spec dotnet" / "check spec compliance dotnet"
- "spec-compliance-validator"

## Input
```
Problem Frame Path: .dev/problem-frames/{domain}/{frame-type}/{use-case}/
```

---

## Mandatory Execution Steps

### Step 0.5: Detect Frame Type (MANDATORY)
Read `frame.yaml` and extract `frame_type`.

```yaml
frame_type: CommandedBehaviorFrame  # or SimpleWorkpieceFrame

# CBF uses controlled_domain:
controlled_domain:
  aggregate_spec: controlled-domain/aggregate.yaml

# SWF uses workpiece:
workpiece:
  aggregate_spec: workpiece/aggregate.yaml
```

Set working variables:

| Variable | CBF Value | SWF Value |
|----------|-----------|-----------|
| `AGGREGATE_PATH` | `controlled-domain/aggregate.yaml` | `workpiece/aggregate.yaml` |
| `SCENARIOS_SOURCE` | `acceptance.yaml` | `requirements/*.yaml` |
| `HAS_FRAME_CONCERNS` | `true` | `false` |
| `HAS_INVARIANTS_STRUCTURE` | `shared + local` | `flat` |

---

### Step 1: Read Problem Frame Specs (ALL REQUIRED)

#### 1.1 Read `frame.yaml`
- **CBF**: `frame_concerns`, `problem_world_facts`, `commanded_behavior`
- **SWF**: `constraints`, `commanded_behavior`

#### 1.2 Read `machine/machine.yaml`
Extract:
- `command_processing.steps`
- `error_handling`
- `constraint_enforcement`

#### 1.3 Read `machine/use-case.yaml`
Extract:
- `input` fields
- `preconditions`
- `postconditions`
- `output`
- `execution.method`

#### 1.4 Read `{AGGREGATE_PATH}`
- **SWF**: `behavior.signature`, `behavior.preconditions`, `behavior.postconditions`, `domain_events`, `entities[].methods[].postconditions`
- **CBF**: `contracts`, `invariants`, `behavior.signature`, `domain_events`

#### 1.5 Read `requirements/*.yaml` (SWF)
- `acceptance_criteria` and each `then` condition

#### 1.6 Read `acceptance.yaml` (CBF)
- `scenarios` with `given/when/then/and`
- `traces_to` for requirements and frame concerns
- `tests_anchor` mapping

---

### Step 2: Build the Compliance Checklist
Create a checklist (TodoWrite) for **all** required items.
Use the following sections:

**SWF Checklist**
1) Use case input fields
2) Service preconditions
3) Aggregate behavior signature
4) Domain event attributes
5) Constraints (C1–Cn)
6) Error handling
7) Acceptance criteria + then conditions
8) Entity contracts

**CBF Checklist**
1) Use case input fields
2) Service preconditions
3) Aggregate contracts (PRE/POST/INV) + L3 semantics
4) Aggregate invariants
5) Domain event attributes
6) Frame concerns (FC1–FC6) coverage
7) Error handling
8) Scenarios coverage + then assertions
9) Frame concerns coverage matrix
10) Gherkin GWT semantic alignment (L4)

---

### Step 3: Validate Production Code (.NET)

#### 3.1 Use Case Input
Locate command/query input models and verify all fields:
- `src/Application/<Aggregate>/UseCases/Commands/`
- `src/Application/<Aggregate>/UseCases/Queries/`

Rules:
- All input fields exist with correct type
- Required fields have validation

#### 3.2 Use Case Handler / Service
Validate that preconditions and error handling exist:
- `src/Application/<Aggregate>/UseCases/*/*.cs`

Rules:
- Each precondition has a corresponding guard/contract check
- Errors map to defined outcomes
- Use case calls aggregate behavior method

#### 3.3 Aggregate Contracts (L1 + L3)
Check aggregate behavior and DBC contracts:
- `src/Domain/<Aggregate>/Aggregates/<Aggregate>.cs`

Rules (L1 existence):
- Signature matches `behavior.signature`
- `Contract.Require` / `Contract.Ensure` / `Contract.Invariant` exists for each spec item

Rules (L3 semantics):
- Each PRE/POST/INV condition is semantically equivalent to the spec validation
- Mismatches or missing items are defects

#### 3.4 Domain Event Attributes
Verify event property coverage:
- `src/Domain/<Aggregate>/Events/*.cs`

Rules:
- Each event attribute in spec exists in the event type
- Metadata fields are preserved in event metadata (not entities)

---

### Step 4: Validate Test Code (.NET)

Test locations:
- Use case tests: `tests/Application.Tests/<Aggregate>/UseCases/`
- Contract tests: `tests/Domain.Tests/<Aggregate>/Contracts/`
- Reactor tests: `tests/Application.Tests/<Aggregate>/Reactors/`
- Controller tests: `tests/Api.Tests/Controllers/<Aggregate>/`

Rules:
- **xUnit + BDDfy (Gherkin-style naming only)**
- **No BaseTestClass**
- **NSubstitute** for mocks
- Each scenario/AC has a test method
- Each `then` condition has an explicit assertion
- Event publication checks are async-safe (no sleep)

Gherkin-style semantic alignment (L4):
- Given → test setup
- When → action execution
- Then/And → assertions
- Order and intent must match spec

Contract tests:
- `{Aggregate}ContractTests.cs` exists
- Preconditions validated with `UContract.PreconditionViolationException`
- Contracts use `UContract.Contract.Require/Ensure/Invariant`
- No framework bootstrapping in contract tests

---

### Step 5: Produce Compliance Report
Use the output format from `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`.
Include:
- Coverage per category
- Missing items with spec references
- Remediation actions (file + method + fix)

---

### Step 6: Remediation Guidance
If any category < 100%:
- List exact missing items
- Provide concrete edits for production and test code
- Re-run validation after fixes

---

## Failure Conditions (Any One Fails the Gate)
1. Any category coverage < 100%
2. Any scenario/AC missing a test
3. Any `then` missing an assertion
4. Any constraint/concern missing verification
5. Any PRE/POST/INV missing or semantically mismatched
6. GWT order mismatch
7. BaseTestClass usage or debug logging present

CBF-only:
- Any frame concern (FC1–FC6) not covered
- Any scenario missing `tests_anchor`

SWF-only:
- Any constraint (C1–Cn) not tested

Contract semantic mismatch:
- Spec validation differs from `Contract.*` condition
- Missing contract in spec or in implementation

---

## Integration with problem-frame-executor (Dotnet)
Insert before completion:

```
Step 10.5: Spec Compliance Validation (.NET)
  USE: dotnet/spec-compliance-validator
  If NOT COMPLIANT:
    - return to test generation
    - fix missing items
    - re-run validation
```

---

## Example Invocation
```
validate spec compliance dotnet for .dev/problem-frames/ezkanban/workflow/cbf/copy-lane
```

Expected output:
- Compliance report with 100% gate status
- Remediation list if any deficits exist


