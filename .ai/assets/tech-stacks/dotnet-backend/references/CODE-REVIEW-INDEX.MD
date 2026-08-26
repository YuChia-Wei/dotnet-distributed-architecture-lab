# Code Review Index Compatibility Entry (.NET)

This path remains available during the `v0.13.x` migration window. It no
longer owns file-type detection, checklist predicates, severity, or examples.

Start with the canonical routing contract:

- [Code Reviewer file-type and finding routing](../../../skills/code-reviewer/references/review-routing.yaml)

The route contract selects one or more file-type standards and applicable
stable engineering rule IDs. Reviewers must not load every linked standard,
this compatibility entry, or the old monolithic checklist as a combined rule
set.

Compatibility removal is reviewed at `v0.14.0`.
