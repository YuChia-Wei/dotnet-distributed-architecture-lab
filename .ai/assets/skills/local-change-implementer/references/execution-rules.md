# Execution Rules

## Default Sequence

1. Identify the primary target.
2. Confirm the specific local operation.
3. Limit the dependency radius.
4. Apply the smallest coherent local change.
5. Update direct usage sites.
6. Update tests only where necessary.
7. Stop before drifting into slice planning or architecture redesign.

## Safety Rules

- Preserve behavior unless the user explicitly asks for semantic change.
- Prefer local consistency over broad cleanup.
- Do not combine multiple independent change goals in one run.
- If the requested change starts affecting architecture boundaries, redirect to `slice-implementer` or `ddd-ca-hex-architect`.
- If the requested change requires introducing a new type, stop and redirect instead of improvising the design.
