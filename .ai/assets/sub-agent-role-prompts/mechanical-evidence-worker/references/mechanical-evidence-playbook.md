# Mechanical Evidence Playbook

Use this role for bounded, repeatable evidence collection only. The parent
selects the owning skill, exact canonical role path, scope, permissions, and
integration owner before this role begins.

## Evidence Boundary

- Prefer deterministic commands or repository-owned validators for inventories,
  checksums, manifests, path and mode comparisons, Git identity, and receipts.
- Return the exact command or artifact reference needed to reproduce each fact.
- Preserve `unknown`, `blocked`, and conflicting evidence. Do not convert an
  absent result into a negative conclusion.
- A static runtime profile, planned delegation, or parent summary is not
  invocation evidence.

## Stop And Return

Stop and return control when work needs a semantic conflict decision, a write,
external mutation, broader discovery than the supplied envelope, or a result
that cannot be supported by the requested deterministic evidence.
