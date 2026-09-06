# v0.16.0 Upgrade Preflight

## Verdict

`ready-to-plan`

## Version Identity

- Installed target: `REL-v0.15.1`, tag `v0.15.1`, package-source commit `f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af`.
- Stable GitHub Release: `REL-v0.16.0`, tag `v0.16.0`, peeled tag commit `f1ead6d676193ba24d8517aed08f05fcfa23cbd3`.
- Admitted package source: build commit `4d1a5c7d039618f007784679d9968c357347272b`, payload fingerprint `702838f88d99e1fc48deae6bd8d442cf8f76341ed2ce01e1d00fc3b6399e2c75`.
- Public ZIP: `1514924` bytes, SHA-256 `d136b69e4153e7c85f892871fb0d3e6c5d8f88c7fd89d43fdb1b03ca88c5c85d`.
- Public sidecar: `105` bytes, SHA-256 `1003157a4a7db7fe647b8e9647cea9b76100a2572e554859b08953abee257931`.

The hosted assets exactly match the adjacent sidecar and source `release-asset-admission/v1` record. The v0.16 source release policy explicitly permits the immutable archive to retain its preparation-commit provenance while the public Release body binds the final tag commit. Both identities are retained here; target package authority is not relabelled as the later tag commit.

## Provenance And Effective-State Health

- Target worktree was clean at `f1a0298fdca0dafe1d653802006e60bc004a74a5`, equal to `origin/main`.
- Provenance is schema `2.0`, version `v0.15.1`, with no unresolved reconciliation.
- Selected mandatory components remain `software-development-core` and `ai-context-lifecycle-core`; profile `dotnet-backend`; provider `repo-backlog` enabled.
- Effective-rule state is present for framework `v0.15.1`, retains 13 explicit rule dispositions and 20 route packets, and passed the target-owned gate.
- Ignored personal CLI routing state was not read or changed; `/.dev/ai-context/local/` remains ignored.

## Route And Package Validation

| Check | Result |
| --- | --- |
| GitHub Release state | stable, non-draft, non-prerelease; published `2026-09-05T15:28:23Z` |
| ZIP and sidecar | exact SHA-256 and filename match |
| Incoming payload validator | passed; 650 payload files and 18 portable entrypoints |
| Support matrix | SHA-256 `79daeb0746bcc5b062c12b2c6bdc358384aed8cdba73f5a0d092166340f7452f` |
| Route resolver | `v0.15.1-to-v0.16.0-direct`, one edge, no diagnostics |
| Required cutover | `retained-direct-upgrade-v1: passed` |
| Existing target gate | passed, including 34 target-owned tests |

## Migration Plan

1. Obtain the original public v0.15.1 `metadata/files.yaml` and verify its matrix-bound digest `8edcb120fe00b16e803f161ec31861ff45a30d8697a5a3e5c58931f7f2b5d1ad`.
2. Generate an external package plan and remediation packet from the immutable v0.16.0 package with the v0.15.1 source manifest.
3. Review every operation and source-specific semantic cutover. Preserve target-owned files and the recorded component/provider selection.
4. Seal the owner decision under Issue #9 authority, apply through the durable v5 transaction, execute target validation, and retain the target-validation receipt.
5. Perform the separate AI-context audit, finalize authority and effective state, validate the terminal receipt, and commit a local checkpoint.

## Result

No package bytes or provenance were changed during preflight. Workflow-only evidence was created on the dedicated branch; package planning remains the next no-write step.
