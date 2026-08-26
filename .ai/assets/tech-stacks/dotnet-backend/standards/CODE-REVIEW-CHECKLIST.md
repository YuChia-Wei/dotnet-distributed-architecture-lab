# Code Review Checklist Compatibility Entry (.NET)

This monolithic path is retained only for `v0.13.x` compatibility. Its former
duplicated predicates were removed so that load order cannot change review
semantics.

Use the canonical route contract:

- [Code Reviewer file-type and finding routing](../../../skills/code-reviewer/references/review-routing.yaml)

That contract points to the canonical file-type standard and stable rule IDs
for the actual scope. Severity and output shape remain owned by the Code
Reviewer skill. Compatibility removal is reviewed at `v0.14.0`.
