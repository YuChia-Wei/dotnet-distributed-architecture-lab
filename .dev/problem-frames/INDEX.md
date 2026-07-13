# Problem Frames Index

This index owns the file and directory catalog for `.dev/problem-frames/`.

## Entry Files

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.dev/problem-frames/`. |
| `INDEX.md` | File and directory catalog for problem-frame assets. |
| `SEMANTICS.md` | Problem-frame semantic guidance. |

## Templates

| Path | Description |
| --- | --- |
| `templates/cbf-external-system/` | Reusable CommandedBehaviorFrame template for external-system integration cases. |
| `templates/cbf-external-system/frame.yaml` | CBF frame template. |
| `templates/cbf-external-system/acceptance.yaml` | Acceptance template. |
| `templates/cbf-external-system/machine/` | Machine and use-case templates. |
| `templates/cbf-external-system/controlled-domain/` | Controlled-domain aggregate template. |

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
