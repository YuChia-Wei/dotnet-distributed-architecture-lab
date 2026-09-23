---
name: local-change-implementer
description: Implement one authorized local technical target and operation, with direct call sites and immediate tests inside an explicit semantic radius; preserve accepted contracts and architecture.
---

# Local Change Implementer

Use `implement` for one class, object, method, local symbol or query and one
bounded technical operation. Follow [the local method](references/implement.md).
Supply authorization, expected behavior, target rules, allowed dependency
radius, selected technology/commands and permitted paths.

Several files can remain one local change; semantic impact determines the
boundary. A private helper can remain local only when responsibility,
dependencies, lifetime, transaction and accepted behavior remain within that
boundary. Public contract or coordinated behavior changes need a bounded slice.

This instruction package owns no executable, configuration or managed record
store. It needs a permitted target editor for implementation and target-selected
tools only for requested checks. Source presence is not execution. Missing
selected specialist coverage and skipped/blocked checks remain explicit.
