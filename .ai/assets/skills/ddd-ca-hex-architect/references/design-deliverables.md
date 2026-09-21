# Design Deliverables

Use these shapes for `design`, scaled to the requested scope. Trace decisions to
requirement/AC IDs, record assumptions, alternatives, quality constraints and
observable acceptance. For `review`, use the shared artifact design/review
contract and `review-criteria.md`; leave the submitted design unchanged.

## New Bounded Context

Return:
1. Context purpose and ownership
2. Ubiquitous language and key aggregates
3. Inbound ports and primary use cases
4. Outbound ports and required adapters
5. BC contracts and integrations selected by the target
6. Project/folder placement
7. Docs to add or update

## New Aggregate or Major Refactor

Return:
1. Aggregate responsibility and invariant boundary
2. Entities and value objects
3. Commands/behaviors and emitted events
4. Repository and persistence strategy
5. Test strategy and review gates

## Command/Query/Reactor Design

Return:
1. Trigger and input DTO shape
2. Application port and handler responsibility
3. Domain calls or projection logic
4. Outbound ports and adapters
5. Result/error contract
6. Tests and validation steps

## MQ Integration Design

Return:
1. Producer BC and consumer BC
2. Event schema or contract payload
3. Delivery guarantees and idempotency notes
4. Outbox or transaction boundary
5. Failure handling and retry strategy

## Prompt or Skill Refactor

Return:
1. Existing prompt families and duplication hotspots
2. Stable shared rules to extract
3. Task-specific instructions to keep separate
4. Proposed skill/reference structure
5. Migration steps from old prompts to the new reusable skill

## Required Quality Checks

- Check the design against the target's supplied architecture, requirements and quality constraints; report missing authority explicitly.
- Load only applicable adopted rules through the source map and effective-rule contract.
- Apply the review criteria as an author self-check and label it accordingly; it does not satisfy independent review.
- Hand accepted decisions to the next owning skill with source IDs, open questions and existing authorization. Do not claim specification compliance or implementation completion.
- If the design affects code generation or review workflows, map the result back to `.ai/assets/` rather than inventing an isolated parallel standard.
