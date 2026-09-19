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
- A private implementation helper type may remain local only when it preserves
  the accepted target, radius, behavior, responsibility, dependency direction,
  lifetime, and transaction boundary. Route a public, responsibility-changing,
  dependency/lifetime/transaction-affecting type to a bounded slice; request
  architecture work only for unresolved or changed responsibility, dependency,
  lifetime, transaction, or semantic decisions.
- Carry existing authorization and normative sources through the handoff; do
  not request the same approval again when it already covers the receiving work.
