# AI Scripts Collection

這個目錄包含自動化檢查與驗證腳本，用於支援目前的 .NET 10 + WolverineFx + Dapper/Npgsql + EF Core 工作流。

> Note:
> 對外預設入口已統一為 .NET 命名，legacy script names 已完成退場。

## Quick Start

### Code Review
```bash
./.ai/scripts/code-review.sh
./.ai/scripts/code-review.sh HEAD~3..HEAD
./.ai/scripts/code-review.sh staged
```

### Full Project Checks
```bash
./.ai/scripts/check-all.sh
./.ai/scripts/check-all.sh --quick
./.ai/scripts/check-all.sh --critical
```

### Recommended .NET-Named Checks
```bash
./.ai/scripts/check-projection-config.sh
./.ai/scripts/check-dotnet-config.sh
./.ai/scripts/check-test-di-compliance.sh
```

## Naming Policy

### Preferred active names

- `check-projection-config.sh`
- `check-dotnet-config.sh`
- `check-test-di-compliance.sh`

## Script Inventory

```text
.ai/scripts/
├── code-review.sh
├── check-all.sh
├── check-aggregate-compliance.sh
├── check-archive-compliance.sh
├── check-coding-standards.sh
├── check-controller-compliance.sh
├── check-data-class-annotations.sh
├── check-domain-events-compliance.sh
├── check-dotnet-config.sh
├── check-framework-api-compliance.sh
├── check-mapper-compliance.sh
├── check-mutation-coverage.sh
├── check-projection-compliance.sh
├── check-projection-config.sh
├── check-prompt-portability.sh
├── check-repository-compliance.sh
├── check-spec-compliance.sh
├── check-test-compliance.sh
├── check-test-di-compliance.sh
├── check-usecase-compliance.sh
├── generate-check-scripts-from-md.sh
├── MD-SCRIPT-GENERATION-GUIDE.md
└── generated/
```

## Stage 6 Alignment Notes

- `.NET` naming is now the default recommendation in docs and orchestrator scripts.
- Legacy wrapper retirement is complete for the projection/config/test-DI script trio.

## Script Notes

### `code-review.sh`

- smart entry point for review-time checks
- selects checks based on changed files

### `check-all.sh`

- full project health report
- supports `--quick`, `--critical`, and full mode

### `check-projection-config.sh`

- preferred entry point for projection/read-model configuration checks
- canonical implementation owner

### `check-dotnet-config.sh`

- preferred entry point for DI/config/environment checks
- canonical implementation owner

### `check-test-di-compliance.sh`

- preferred entry point for test DI compliance checks
- canonical implementation owner

## Related Files

- [AGENTS.md](../../AGENTS.md)
- [.dev/operations/README.MD](../../.dev/operations/README.MD)
- [.dev/specs/tests/TEST-SPEC-GUIDE.MD](../../.dev/specs/tests/TEST-SPEC-GUIDE.MD)
