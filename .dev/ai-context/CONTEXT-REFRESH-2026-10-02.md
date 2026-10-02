# Initialized context refresh

The owner requested `ai-context-init@0.1.0` operation `refresh` to correct internal
project context on 2026-10-02. This is one bounded document pass in direct mode
under the target workflow gate. The existing RC4 validation branch and Issue #31
provide the installation context; this request separately authorizes document
edits. It does not change the completed installation task or its historical
acceptance statements.

Source checkpoint: `aed40558c5b2dfb98157267bc29dc8edca09a323` on
`codex/2026-10-02-rc4-validation`. The host working tree was clean before this
refresh. Sandbox reads initially reported the selected skill paths as missing;
an authorized host read confirmed their actual presence and a clean Git state.
No package restoration was needed or performed.

## Bounded corrections and sources

| Document | Correction | Current evidence |
| --- | --- | --- |
| `CLAUDE.md` | Replace the stale RC3 trial pointer with current contract/selection/lock navigation; retain the AGENTS import | [Current contract](CURRENT-FRAMEWORK.md), `.ai/custom/installation.json`, `.ai/framework.lock` |
| `.dev/README.MD`, `.dev/INDEX.md` | Recognize the selected refresh and restored orchestrator routes while retaining target record ownership | [Selected skill registry](skills.md), [workflow guide](../workflows/README.MD) |
| `.dev/ARCHITECTURE.md` | Correct retired `.ai/assets/` paths and distinguish managed guidance from adopted target authority | Git-tracked `.ai/core/knowledge/` and `.ai/core/skills/`, [target engineering rules](TARGET-ENGINEERING-RULES.md) |
| `.dev/requirement/TECH-STACK-REQUIREMENTS.MD` | Include Procurement persistence/receipt flow, frontends and supplier lab; correct host and test counts | `MQArchLab.slnx`, product/sample/test project files, frontend manifests/Dockerfiles and Compose overlays |
| `.dev/project-config.yaml` | Remove the unsupported solution target `netstandard2.0`, include the isolated sample host and record inventory provenance | All 41 solution projects target `net10.0`; 27 source, five sample and nine test projects; `global.json` |

RuntimeCompilation is referenced by seven product hosts and the isolated
`EfCoreWolverine.Host`. Procurement persistence is evidenced by its Infrastructure
project and `PostgresPurchaseStore.cs`; the receipt event is defined in
`src/BC-Contracts/Lab.BoundedContextContracts.Procurement/IntegrationEvents/GoodsReceived.cs`.
Inventory's `GoodsReceivedHandler.cs` delegates to its receipt use case and
`PostgresInventoryGoodsReceiptStore.cs` enforces receipt replay protection.
These are source observations, not executed runtime results.

The Codebase Memory MCP architecture overview was consulted first. Its revision
and indexing time were unavailable; it still exposed retired tooling paths and
the `GoodsReceived` graph query returned zero matches. It was insufficient for
current Procurement coverage. Git-tracked inventory, direct project XML and
current files supplied material evidence. No absence conclusion relies on the
graph, and no graph regeneration or persisted graph artifact was selected.

## Inventory reproduction

The inventory is manually reconciled through the selected instruction operation.
It is a derived discovery view and does not establish a gate pass. Its input
digest covers 61 tracked manifests, project files, Dockerfiles and Compose YAML
files. Product/decision authority remains with current source and adopted records.

From the repository root, use Python 3 to recompute the recorded digest:

```python
import hashlib
import subprocess
from pathlib import Path

tracked = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
inputs = sorted(p for p in tracked if p and (
    p in ["global.json", "MQArchLab.slnx",
          "src/Frontend/Web/package.json", "src/Frontend/Admin/package.json"]
    or (p.startswith(("src/", "samples/", "tests/"))
        and (p.endswith(".csproj") or p.endswith("/Dockerfile")))
    or (p.startswith("docker-compose/") and p.endswith(".yml"))
))
records = "".join(p + "\0" + hashlib.sha256(Path(p).read_bytes()).hexdigest()
                  + "\n" for p in inputs)
print(len(inputs), hashlib.sha256(records.encode("utf-8")).hexdigest())
```

Expected digest at this checkpoint:
`843027e76f49ebee35ec9260f7d0cccc5dd38ceebcf45436be0ede314482abcc`.
For structural parity, parse `MQArchLab.slnx` and each referenced `.csproj` as XML;
compare their path set, target frameworks and source/sample/test counts with
`project-config.yaml`. Read `global.json` for the SDK. Inspect frontend manifests,
Dockerfiles and applicable Compose image declarations for the technology table.
A matching digest detects unchanged inputs; it does not validate business behavior.

## Actual validation and limits

| Check | Result |
| --- | --- |
| Selected document read-back, local links, seed/stale-pointer checks and LF | executed-passed: seven documents, 46 local links |
| YAML parse, solution/project/framework/count/SDK parity and input digest | executed-passed: 41 solution projects, 61 digest inputs; unrelated YAML values preserved |
| Full tracked-file hash comparison against the captured preimage | executed-passed: 1,525 existing tracked files unchanged; only the six selected existing documents changed |
| Git diff whitespace check | executed-passed |
| Configured target AI-context gate | blocked: current target configuration remains unconfigured |
| Product tests, live services, CI and independent review | not-run |
| Installation, lock or managed package changes | not-applicable to refresh |

Root AGENTS and its translation, adopted engineering rules, package bytes,
runtime skill entries, lock/settings, product code, tests, Compose and historical
workflow records are outside this write scope. No commit, push, PR, merge,
Issue-state change, primary adoption or runtime acceptance is asserted.
