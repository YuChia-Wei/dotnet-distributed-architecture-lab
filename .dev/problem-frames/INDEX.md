# Problem Frames Index

This index owns the file and directory catalog for `.dev/problem-frames/`.

## Entry Files

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.dev/problem-frames/`. |
| `INDEX.md` | File and directory catalog for problem-frame assets. |
| `SEMANTICS.md` | Problem-frame semantic guidance. |

## Authoring route

Use [problem-frame-author](../../.ai/core/skills/problem-frame-author/SKILL.md) with the requested target format and authentic sources. The removed generic CBF scaffold has no declared identical replacement. The existing layout below documents retained legacy target records; it does not force a new record format or migration.

## Minimum CBF Layout

```text
.dev/problem-frames/<domain>/cbf/<use-case>/
  frame.yaml
  acceptance.yaml
  machine/
    machine.yaml
    use-case.yaml
  controlled-domain/
    aggregate.yaml
```

Create target-repository problem frames from confirmed requirements, specs, code, and user-confirmed truth.

## Target-Repository Frames

| Path | Description |
| --- | --- |
| `orders/cbf/place-order/` | Commanded behavior frame for the current Orders place-order and Inventory reservation flow. |
| `inventory/cbf/reserve-inventory/` | Commanded behavior frame for durable, idempotent Inventory reservation and stable event publication. |

The previously copied Payments frame is not retained because no Payments bounded context exists in the current solution.
