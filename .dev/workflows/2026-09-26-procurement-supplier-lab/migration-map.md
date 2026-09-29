# v2 migration map — 2026-09-26-procurement-supplier-lab

Migrated at: `2026-09-29T22:11:55+08:00`. Source record: `wf-28ef2d2ffe044802a4ddba263d5e5471`; revision `14`; original Git blob SHA-256 `fe4a21c4469d3c5f6756a69fa2e6424d2d44a2deb661ab5150f83d805f530622`.

Current [history projection](evidence/v2-history.workflow.json), SHA-256 `09e5dbd788710360fbb7863783fb79dc4af8f73cd31750831eea3cb51401c50d`. Original bytes remain in Git commit `f17128ca5e5cf76c27c23b2ed1c1110d19af4108` at the original evidence snapshot path.

This is a projection of an existing record. The retained history includes all prior states, previous hash strings, retrospective, extensions, reported-by strings and reference IDs. Only former ignored-output targets were rebound to hash-verified tracked evidence. Because those target strings changed, the projection is not an immutable v2 tool record; prior v2 content hashes describe the original Git bytes, not the rebound projection.

## Identity mapping

| v2 identity | Original-format location |
| --- | --- |
| workflow `wf-28ef2d2ffe044802a4ddba263d5e5471` | `workflow.yaml` and `workflow-plan.md` under `2026-09-26-procurement-supplier-lab` |
| task `T001` | `tasks/T001.json` |
| task `T002` | `tasks/T002.json` |
| task `T003` | `tasks/T003.json` |
| task `T004` | `tasks/T004.json` |
| task `T005` | `tasks/T005.json` |
| task `T006` | `tasks/T006.json` |
| acceptance `AC01` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC02` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC03` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC04` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC05` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC06` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| evidence `EV-SPEC-01` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FIRST-PG-FAIL` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FIRST-HTTP` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-DIRECT-FLOW` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T003-PG` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T004-PG-BROKER` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-HTTP-REPAIRED` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FINAL-SUPPLIER` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FINAL-HTTP` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FINAL-UI` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FINAL-PROTECTED` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-LEGACY-LOCATOR-LIMIT` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-FINAL-COMPLIANCE` | `workflow-plan.md` evidence table; exact object in source snapshot |
| reference `SPEC-BASELINE` | reference table below; exact object in source snapshot |
| reference `FIRST-PG-TRX` | reference table below; exact object in source snapshot |
| reference `FIRST-HTTP` | reference table below; exact object in source snapshot |
| reference `DIRECT-FLOW` | reference table below; exact object in source snapshot |
| reference `FINAL-PROC-TRX` | reference table below; exact object in source snapshot |
| reference `INVENTORY-TRX` | reference table below; exact object in source snapshot |
| reference `BROKER-RECOVERY` | reference table below; exact object in source snapshot |
| reference `REPAIRED-HTTP` | reference table below; exact object in source snapshot |
| reference `FINAL-HTTP` | reference table below; exact object in source snapshot |
| reference `FINAL-SUPPLEMENTAL` | reference table below; exact object in source snapshot |
| reference `FINAL-BROWSER` | reference table below; exact object in source snapshot |
| reference `FINAL-TESTS` | reference table below; exact object in source snapshot |
| reference `FINAL-PROTECTED` | reference table below; exact object in source snapshot |
| reference `FINAL-ACCEPTANCE` | reference table below; exact object in source snapshot |
| reference `FINAL-MODEL-REVIEW` | reference table below; exact object in source snapshot |
| reference `FINAL-EVIDENCE-MANIFEST` | reference table below; exact object in source snapshot |
| reference `LEGACY-LOCATOR-LIMIT` | reference table below; exact object in source snapshot |
| reference `FINAL-FRAMEWORK-CHECK` | reference table below; exact object in source snapshot |

## Reference details

| ID | Kind | Target | Historical v2 resolution | Blocking | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `SPEC-BASELINE` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/ | `resolved` | `False` | unknown |
| `FIRST-PG-TRX` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/first-procurement-tests/_39081a7221c7_2026-09-26_03_13_22_net10.0.trx | `resolved` | `False` | a79c095cb989e6338f65d9044808a7b8e6b42d44d5712184ddd9ef411b9e3dd7 |
| `FIRST-HTTP` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/http-contracts-first.json | `resolved` | `False` | unknown |
| `DIRECT-FLOW` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/direct-flow.json | `resolved` | `False` | unknown |
| `FINAL-PROC-TRX` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/focused-final-results/_b8d927bdf806_2026-09-26_03_38_06_net10.0.trx | `resolved` | `False` | unknown |
| `INVENTORY-TRX` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/test-results/_0c140fbf1ac6_2026-09-26_03_31_41_net10.0.trx | `resolved` | `False` | unknown |
| `BROKER-RECOVERY` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/broker-recovery.json | `resolved` | `False` | unknown |
| `REPAIRED-HTTP` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/http-contracts-repaired.json | `resolved` | `False` | unknown |
| `FINAL-HTTP` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/http-contracts-final.json | `resolved` | `False` | bcf41254fc6c3317cae432b549cfac01916e20c23c0921054a5710560575936d |
| `FINAL-SUPPLEMENTAL` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/supplemental-http.json | `resolved` | `False` | 3bba5dbe4e8db2a1917d03b1dd5f2891c3550b529a43f82b0c2b978a2f1023fe |
| `FINAL-BROWSER` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/browser-verification.json | `resolved` | `False` | 248f71c9335a59ae834cabe2db3496da166496468c5f5b0103d86ccc9952736c |
| `FINAL-TESTS` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/test-results-summary.json | `resolved` | `False` | 2c1787b2530ec076a850bb236f561a5ac05d63addeca002df6125f46fb000917 |
| `FINAL-PROTECTED` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/observability-comparison.json | `resolved` | `False` | 07271ab0831efde94eaed1f3fe597f00e8303011bbf93af129ddb27131712fae |
| `FINAL-ACCEPTANCE` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/acceptance-report.md | `resolved` | `False` | 9e4bbcbb618eea27247990a79d0bbb15e0c036573974b80900b183261cc962f5 |
| `FINAL-MODEL-REVIEW` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/review-and-model-observations.md | `resolved` | `False` | a25b4e9196b18c56954c6358564ea114ab3fbda481711e8133b275407cd80efd |
| `FINAL-EVIDENCE-MANIFEST` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/manifest.json | `resolved` | `False` | bb953f380111a742f4199726a1538686bd98a74ab8a73244b90423d7ded38b1d |
| `LEGACY-LOCATOR-LIMIT` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/legacy-locator-check.txt | `resolved` | `False` | bb1ac36e416a5a62cf7244e99a6697efd62d48b9e5bba2385dc54dfefd5028df |
| `FINAL-FRAMEWORK-CHECK` | opaque | .dev/workflows/2026-09-26-procurement-supplier-lab/evidence/current-framework-check.json | `resolved` | `False` | 76791e74d7847be9b8f5800e5dc8dea87c6802a207889a5269ca4dbbc74787ed |

## History and limitations

- All 13 previous-state entries and revision 14 remain in the path-rebound history projection; the migration did not call an unsupported v2 terminal update. The exact pre-rebinding bytes are retained by Git history.
- `recorded_at` in each source history entry is the actual v2 operation time; projected task timestamps use first appearance and last content change observable there. They are not newly invented execution times.
- Task model fields use the existing execution plan. Root model attribution is a configured default, and child attribution comes from the recorded invocation. Missing runtime metrics stay unknown.
- Projected task `template_source` names the target artifact-format contract used for this conversion. It does not claim that a historical skill template generated these projected files.
- All prior failed, blocked, deferred and not-executed entries remain in the source history, even when the final disposition changed.
- All 18 reference targets now resolve to tracked files in this checkout. The seven repaired targets were matched by file name and, where the source supplied one, by its recorded SHA-256; the full 39-file evidence manifest passed a fresh SHA-256 read-back. This validates retention and paths, not the underlying product outcomes anew.
- The manifest's current SHA-256 is `cd0ce3a3791e2e1da087b040bfb9f54ee599b0930cd9123b713df194830e55e1`. `FINAL-EVIDENCE-MANIFEST` retains the original historical digest in the v2 history; it does not describe these corrected manifest bytes.
- Provider operations, owner review, push, PR, merge, deployment, cleanup and framework installation must be established by their own evidence.
