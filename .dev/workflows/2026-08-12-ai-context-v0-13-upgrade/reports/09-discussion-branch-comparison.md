# Comparison With The AI Context Architecture Kit Standards Discussion

## Comparison Basis

- Installed target: `REL-v0.13.0` at audited checkpoint
  `46928f4379f57a7bec155056aacdf6dbcf070f81`.
- Discussion branch:
  `codex/2026-07-30-ai-context-architecture-kit-standards-discussion` at
  `b29ef357d7c6c7cb202d11896466a039e1e17483`.
- Common ancestor: `a06ba3a6...`.
- The discussion branch is not an ancestor of the current upgrade branch.
  Matching results are therefore correspondence, not evidence that the branch
  was integrated.
- Analysis model: `gpt-5.6-sol`, reasoning effort `max`.

The discussion contains 37 `DEC-*` decisions. The denominator is exactly the
issue draft's sixteen acceptance-criteria checkboxes; it is not filtered from
the DEC inventory. Scoring uses `achieved = 1`, `partial = 0.5`, and
`not achieved` or `contradicted = 0`.

## Result

**Repository-local expectation coverage: 47%**

- Achieved: 3
- Partially achieved: 9
- Not achieved: 3
- Contradicted: 1
- Weighted result: `(3 + 9 × 0.5) / 16 = 7.5 / 16 = 46.875%`, rounded to 47%.

## Acceptance-Criteria Matrix

| # | Discussion expectation | Result | Installed v0.13 evidence |
| ---: | --- | --- | --- |
| 1 | Five identity kinds with referential integrity (`DEC-022/023`) | Partial | Ownership schema names concept/rule/constraint/capability/binding, but installed catalogs instantiate rules only; constraints are empty and no concrete concept/capability/binding records exist. |
| 2 | Profile-owned rules need no invented universal concept (`DEC-024`) | Achieved | The dotnet catalog owns rules such as `AGGREGATE-ES-001` and `PROJECT-GRAMMAR-001` without hollow core concepts. |
| 3 | Routine projection loads only task-relevant semantics (`DEC-025/031`) | Partial | Code-review routing is selective and target GWT1–7 pass, but all twenty effective routes currently load the same thirteen rules. |
| 4 | Concrete constraints are available before code generation (`DEC-006/007`) | Partial | Action skills load fresh packets with full normative statements, but eleven profile documents remain unpacketized and catalogs expose no constraint identities. |
| 5 | Complete target-effective state; ledger stores deltas (`DEC-009/010/014`) | Partial | Four CUST records correctly preserve target deltas and state is complete for the thirteen registered rules, but both catalogs have empty constraint sets and eleven profile baseline documents remain `identity-allocation-required` / `unpacketized-fail-closed`. |
| 6 | Deviation, tuning, and waiver have distinct verifiable contracts (`DEC-017–019`) | Partial | State schema distinguishes dispositions, but tuning/tooling waiver evidence remains simplified and has no installed example proving the complete model. |
| 7 | `.editorconfig` remains target-owned; no per-edit semantic review (`DEC-021`) | Partial | Recipes leave severity/wiring to the target and nothing is activated, but the complete native-edit versus review lifecycle is not executable as one contract. |
| 8 | Final CI consistency defaults to warning and is separate from analyzer severity (`DEC-020/021`) | Partial | Schema/action skills distinguish strictness from analyzer severity, but target CI is unconfigured and no authoritative cross-artifact CI check is active. |
| 9 | .NET profile owns Architecture Kit version range and Diagnostic mapping (`DEC-008/027`) | Not achieved | No Architecture Kit package identity/range or consumer compatibility binding exists; recipes explicitly do not claim cutover. |
| 10 | AI Context and Architecture Kit version independently with compatibility fixtures (`DEC-028`) | Not achieved | AI Context versions independently, but Architecture Kit range, fixtures, and consumer proof are absent. |
| 11 | No diagnostics claim before installation; preserve a deferred checkpoint (`DEC-012/013/015`) | Partial | Provider activation is false and recipes are not selected, so no false diagnostic claim is made; an Architecture Kit-specific pending-review checkpoint is absent. |
| 12 | Retain bundled provider until readiness-gated Architecture Kit cutover; never dual-run (`DEC-029/030`) | **Contradicted** | v0.13 removed 36 provider files and retained six inactive recipes without Architecture Kit readiness/binding evidence. The four stale target claims were corrected, but the strategic contradiction remains. |
| 13 | Deferred package adoption may complete upgrade while recording the validation gap (`DEC-030`) | Partial | The upgrade completed with provider/recipes inactive and gaps recorded, but deferral is not Architecture Kit-specific and has no continuation action. |
| 14 | Cross-language fixture prevents .NET/Roslyn semantics leaking into universal context (`DEC-024`) | Not achieved | Core/profile layering helps structurally, but no installed .NET/TypeScript/Java/Rust acceptance fixture was found. |
| 15 | External skills cannot bypass policy, approval, test, review, or completion (`DEC-032–034`) | Achieved | Orchestrator routing, role-execution safety gates, target commands, and terminal completion contracts enforce the boundary. |
| 16 | Migration, rollback, downstream validation, and owner approval retain evidence | Achieved | All seven hops retain plans/receipts, failed and successful audits, owner decisions, target gates, and final packet/state evidence. |

## Other Discussion Decisions

- `DEC-003` remains active: adoption review, pinning, and no-silent-package-
  policy still apply. `DEC-011` refines its bootstrap behavior. `DEC-014`
  supersedes only the semantic-adoption portions of `DEC-004` and `DEC-011`.
- Narrower supersessions remain exact: `DEC-012` supersedes only `DEC-011`'s
  analyzer-severity reading; `DEC-027` supersedes the Architecture-Kit-owned
  comparison part of `DEC-020`; `DEC-037` supersedes only `DEC-035`'s no-push
  clause.
- `DEC-035` and `DEC-037` are achieved at the workflow level: the discussion
  branch remains separate and was not silently merged into this upgrade.
- `DEC-036` remains intentionally pending because no upstream proposal Issue
  has been published. This workflow has no publication authorization.
- The old discussion checkpoint `AICDISC-ADAPTER-001` remains historically
  failed. Current `.codex/agents/context-translator.toml` and the directory-
  scoped ignore exception fix present reachability, but do not rewrite that old
  checkpoint as passed.

## Focus-Area Conclusions

- **Project/solution grammar:** achieved. `PROJECT-GRAMMAR-001` is a profile-
  owned baseline rule and matches current domain/presentation project layout.
- **Reference source includes:** achieved. They are explicitly reference-only,
  have no target build/test commands, and are not wired into the solution.
- **Analyzer/provider boundary:** activation honesty is achieved, but the
  Architecture Kit transition strategy is contradicted. Only DBA1009 has a
  stable catalog rule identity among the seventeen DBA mappings.
- **Code-review routing:** achieved for the target projection, partial for the
  published downstream package because the stock portable test imports an
  omitted source-only module.
- **Target truth:** the four stale bundled-provider claims discovered during
  comparison were fixed and independently accepted at `46928f4`.
- **Portability:** partial. The target overlay passes; the stock validator still
  fails with 36 source-projection errors.

## Priority Gaps

1. Decide whether the Architecture Kit integration remains a target. If yes,
   implement package range, Diagnostic crosswalk, parity, consumer proof,
   opt-in, and readiness checkpoint. If no, explicitly supersede `DEC-029/030`.
2. Instantiate the normalized identity model beyond rules: concrete concepts,
   constraints, capabilities, and bindings with referential integrity.
3. Narrow effective-rule routing so task packets do not always load all rules.
4. Close the downstream package over every declared portable validation path.
5. Add executable CI warning/severity, complete waiver evidence, and cross-
   language leakage fixtures.

## Authorization Boundary

This comparison does not merge the discussion branch, publish its prepared
Issue, choose an Architecture Kit provider, activate analysis tooling, or
authorize any upstream mutation.
