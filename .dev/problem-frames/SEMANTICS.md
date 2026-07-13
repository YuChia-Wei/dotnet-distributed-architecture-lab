# Problem Frame Semantics Mapping

This document defines the minimum conventions for common semantic tags in `aggregate.yaml`. Use it as a reference during code review and subsequent problem-frame authoring.

## Purpose

- Make field semantics in `aggregate.yaml` consistently reusable.
- Provide a reference for the semantics mentioned in `.dev/standards/CODE-REVIEW-CHECKLIST.md`.
- Avoid using different terms in each project for the same invariant.

## Core Semantics

### `identity`

- Definition: The stable identifier of an Aggregate or Entity.
- Rules:
  - It must not change after creation.
  - No command or event should modify the identity.

### `value_immutable`

- Definition: A value that cannot be updated after creation.
- Rules:
  - It has no setter.
  - It should not have a corresponding update event.

### `collection_reference_immutable`

- Definition: A collection reference that is created once and cannot be replaced, while its contents can be changed safely.
- Rules:
  - The collection should be initialized once.
  - Its contents may be modified only through an Aggregate method.

### `soft_delete_flag`

- Definition: Indicates that a record is no longer active in the business domain but must be retained.
- Rules:
  - Behavior is restricted after deletion.
  - A corresponding event or explicit state transition should exist.

### `optimistic_concurrency_version`

- Definition: A version value used for concurrency control.
- Rules:
  - It is managed by infrastructure or the framework.
  - It is not specified directly by a business command.

### `external_authority`

- Definition: A field or state that this system cannot determine independently and must derive from an external system's result.
- Examples:
  - Payment authorization result
  - External customer status
  - Carrier shipment acceptance

### `idempotency_key`

- Definition: A stable key used to identify duplicate requests or retried callbacks.
- Rules:
  - Retrying with the same key must not cause duplicate side effects.
  - It should be traceable to a command or external callback.

## Usage Guidance

- When a field's semantics are covered here, prefer reusing these tags.
- When a project needs new semantics, define them here before referencing them in `aggregate.yaml`.
