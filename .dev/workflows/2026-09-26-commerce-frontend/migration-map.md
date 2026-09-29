# v2 migration map — 2026-09-26-commerce-frontend

Migrated at: `2026-09-29T22:11:55+08:00`. Source record: `wf-0fa43e8dc60f4683ae1036abde90494b`; revision `9`; SHA-256 `1212750ced64a2cc08020b324e9448270703138801bb53fce1193a0e3886833c`.

Original bytes: [evidence/v2-source.workflow.json](evidence/v2-source.workflow.json). Original store path: `.dev/workflows-v2/wf-0fa43e8dc60f4683ae1036abde90494b.workflow.json` (retired).

This is a projection of an existing record. The source snapshot is the lossless authority for fields without an original-format column, including all prior states, previous hashes, retrospective, extensions, exact reported-by strings and all source references.

## Identity mapping

| v2 identity | Original-format location |
| --- | --- |
| workflow `wf-0fa43e8dc60f4683ae1036abde90494b` | `workflow.yaml` and `workflow-plan.md` under `2026-09-26-commerce-frontend` |
| task `T001` | `tasks/T001.json` |
| task `T002` | `tasks/T002.json` |
| task `T003` | `tasks/T003.json` |
| task `T004` | `tasks/T004.json` |
| task `T005` | `tasks/T005.json` |
| acceptance `AC01` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC02` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC03` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC04` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC05` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC06` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| acceptance `AC07` | `workflow-plan.md` acceptance table; exact object in source snapshot |
| decision `D-AUDIENCE` | `workflow-plan.md` decisions; exact object in source snapshot |
| evidence `EV-SPEC18` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T002` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T003` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T004` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T005-FAILURES` | `workflow-plan.md` evidence table; exact object in source snapshot |
| evidence `EV-T005-FINAL` | `workflow-plan.md` evidence table; exact object in source snapshot |
| reference `SPEC18` | reference table below; exact object in source snapshot |
| reference `SPEC18-V2` | reference table below; exact object in source snapshot |
| reference `IMPL-T002` | reference table below; exact object in source snapshot |
| reference `IMPL-T003` | reference table below; exact object in source snapshot |
| reference `IMPL-T004` | reference table below; exact object in source snapshot |
| reference `ACCEPTANCE-FINAL` | reference table below; exact object in source snapshot |
| reference `MANIFEST-FINAL` | reference table below; exact object in source snapshot |
| reference `REVIEW-FINAL` | reference table below; exact object in source snapshot |
| reference `SPEC18-FINAL` | reference table below; exact object in source snapshot |

## Reference details

| ID | Kind | Target | Historical v2 resolution | Blocking | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `SPEC18` | opaque | .dev/workflows/2026-09-26-commerce-frontend/requirements.md | `stale` | `False` | 6a1804e0776022834cd760132629fd0ce5661e788511f767630af3d81c579ad7 |
| `SPEC18-V2` | opaque | .dev/workflows/2026-09-26-commerce-frontend/requirements.md | `stale` | `False` | a102860aa0aae6214b154bf2a6d1daa2241cfeb8a9c2eb5edbe9dbaeee984139 |
| `IMPL-T002` | opaque | git:1f008044f101beb8842200f3c6a0099eb731c8c6 | `resolved` | `False` | unknown |
| `IMPL-T003` | opaque | git:c89da4b06548ee8a43eac61538cd11b7c826a246 | `resolved` | `False` | unknown |
| `IMPL-T004` | opaque | git:8ed57760de3e43bf01f0223a8695e2da8647dba9 | `resolved` | `False` | unknown |
| `ACCEPTANCE-FINAL` | opaque | .dev/workflows/2026-09-26-commerce-frontend/acceptance-report.md | `resolved` | `False` | 140cf1e7e44c15db5c81eac83a0bb059565f4e27c115ebc2bee8c1b31c38bf67 |
| `MANIFEST-FINAL` | opaque | .dev/workflows/2026-09-26-commerce-frontend/acceptance-evidence.json | `resolved` | `False` | 02403804b20477720343a46515ace967c1c3264b6c05f9ab24beeaf75cd84472 |
| `REVIEW-FINAL` | opaque | .dev/workflows/2026-09-26-commerce-frontend/review-notes.md | `resolved` | `False` | dfd4c0eede7362aea62b69e8158cddfcc204eb79e496ba99a7bb640ffffe9b0a |
| `SPEC18-FINAL` | opaque | .dev/workflows/2026-09-26-commerce-frontend/specifications.md | `resolved` | `False` | 1086280b6023877589cd42921e2f13fd18f28b171856f191c0cb7e34ef3ffa81 |

## History and limitations

- All 8 previous-state entries and revision 9 remain in the exact JSON snapshot; the migration did not call an unsupported v2 terminal update.
- `recorded_at` in each source history entry is the actual v2 operation time; projected task timestamps use first appearance and last content change observable there. They are not newly invented execution times.
- Task model fields use the existing execution plan. Root model attribution is a configured default, and child attribution comes from the recorded invocation. Missing runtime metrics stay unknown.
- Projected task `template_source` names the target artifact-format contract used for this conversion. It does not claim that a historical skill template generated these projected files.
- All prior failed, blocked, deferred and not-executed entries remain in the source history, even when the final disposition changed.
- At migration, all six local-path references and three Git commit references in this record resolved in the isolated checkout. This read-back does not revalidate the underlying product results.
- Provider operations, owner review, push, PR, merge, deployment, cleanup and framework installation must be established by their own evidence.
