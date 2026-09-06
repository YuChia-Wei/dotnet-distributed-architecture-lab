# Fixed-Head Independent Audit Playbook

Use this role only for an explicitly selected terminal or high-risk gate. The
parent supplies the exact clean execution commit, bounded criteria, content
subject construction, and integration owner.

## Independence And Subject Binding

- Pin execution to one full fixed commit so the observed checkout cannot move.
  Record that SHA as provenance, and bind validity to the supplied canonical
  content subject and audit criteria.
- Remain independent of implementation and remediation; do not change the
  audited subject or tell another actor how to repair it as part of the audit.
- Treat content, criteria, authority, in-run checkout, an unclean subject,
  missing evidence, timeout, interruption, or cleanup drift as fail-closed
  audit evidence. A later SHA-only history change is not content drift; the
  parent may rebind the result only through the canonical subject digest.
- Preserve earlier failure evidence. A later successful rerun does not erase it.

## Stop And Return

Return immediately if terminal or high-risk selection is absent, the execution
commit or content subject cannot be verified, or requested work would become
implementation, repair, mutation, or final integration acceptance.
