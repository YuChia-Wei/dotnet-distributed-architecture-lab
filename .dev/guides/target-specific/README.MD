# Target-Specific Testing Guide Preservation

This directory preserves the lab's full testing-guide customizations while the
package-managed implementation-guide paths return to their verified framework
bytes for the v0.17.0 disposable upgrade trial.

| Preserved target guide | Restored package-managed guide | Preserved raw SHA-256 |
| --- | --- | --- |
| `DOTNET-DI-TEST-GUIDE.md` | `../implementation-guides/DOTNET-DI-TEST-GUIDE.md` | `1c61f602b2dce3aee32be02f6443c3d8268b66a3b2a9054e6d94a00dc7e08322` |
| `NEW-PROJECT-TEST-SETUP-GUIDE.md` | `../implementation-guides/NEW-PROJECT-TEST-SETUP-GUIDE.md` | `8f8cb9da14000c980069c5ac5fd386db01ae5ade71c4953645693ebe921109ef` |

The preserved guides retain the lab's xUnit v3 package and execution details,
`ValueTask` fixture lifecycle examples, and target test-profile guidance. They
are target-owned human guides. The adjacent package-managed paths provide the
portable framework guidance and must not be edited to carry these lab-specific
facts.

Evidence: disposable candidate starting commit
`ed27f6b7c63fdb45dfa9a8e6ff010b4be63b4045`; v0.17.0 package plan
`../../../../../upgrade-v017/lab-candidate-upgrade-plan.yaml`; parent-authorized
v0.16-to-v0.17 reconciliation on 2026-09-18. The original lab checkout is not
an upgrade target for this trial.
