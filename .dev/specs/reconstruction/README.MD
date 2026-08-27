# Source-Independent Reconstruction Specification

This directory is the durable entry point for rebuilding the product after product source and test code are unavailable. It is written for a fresh AI session with no hidden context.

## Authority Order

When two artifacts disagree, use this order and record the conflict instead of guessing:

1. owner-approved requirements and Accepted ADRs;
2. production and adapter specs under `.dev/specs/`;
3. problem-frame acceptance oracles;
4. operations contracts and test specs;
5. `observed` evidence recorded in the coverage matrix.

The original source implementation is evidence for authoring this baseline, not an input to a future reconstruction. Implementation accidents must not override `required`, `compatibility`, `preserve`, or `quality-uplift` rules.

## Reconstruction Inputs

Read in this order:

1. `../../requirement/reconstructable-system-baseline.md`
2. `../../ARCHITECTURE.md` and Accepted ADRs
3. `system-blueprint.md`
4. `project-manifest.json`
5. `coverage-matrix.md`
6. `http-api-contracts.json`, `message-contracts.json`, `persistence-contracts.json`, and `runtime-contracts.json`
7. domain production specs under `../domains/`
8. problem frames under `../../problem-frames/`
9. test specs under `../tests/`
10. `reconstruction-procedure.md`

## Required Outputs

A reconstruction is complete only when it produces:

- `MQArchLab.slnx` with the project identities and logical groups in `project-manifest.json`;
- three bounded contexts (`Products`, `Orders`, `Inventory`) plus business-neutral BuildingBlocks and Published Language contract projects;
- six runtime hosts and three PostgreSQL schemas;
- all listed HTTP and message contracts;
- all domain/application/persistence/delivery semantics;
- the required test oracles and validation evidence.

## Evidence Status

- `required`, `compatibility`, `preserve`, and `quality-uplift` are normative.
- `observed` is non-normative evidence that may explain an existing behavior.
- `gap` and `deferred` are never passing states.

## Source Independence Rule

Do not require `src/`, `tests/`, `.git/`, `bin/`, `obj/`, a code knowledge graph, generated cache, archived conversation, uncommitted state, or workflow runtime state to understand these artifacts. Repository-native build metadata must be regenerated from `project-manifest.json` and the version selections recorded in the requirements/runtime contract.

## Validation

Use `reconstruction-procedure.md` and `coverage-matrix.md` as the final checklist. A green build alone is insufficient; contract, behavior, durability, idempotency, topology, and traceability gates must all pass.

## Current Deletion Gate

The baseline is ready to drive reconstruction attempts, but it is not yet evidence that they will pass. Do not remove product source except in isolated disposable copies until selected problem frames reach 100% compliance, required PostgreSQL and canonical Kafka gates pass, and two independent LUNA-class runs satisfy `../tests/e2e/reconstruction-acceptance.test-spec.md`. Even then, deleting the original source requires a separate explicit owner authorization.
