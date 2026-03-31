# Operations Portability Notes

`.dev/operations/` 幾乎全部屬於專案特定 runtime truth。

## 可保留

- `README.MD`
- `CONTEXT-MAP-GUIDE.MD`
- `EVENT-CATALOG-GUIDE.MD`
- `MQ-TOPOLOGY-GUIDE.MD`
- `RUNBOOK-GUIDE.MD`
- `runbooks/README.MD`

## 應重寫

- `context-map.md`
- `event-catalog.md`
- `mq-topology.md`
- `runbooks/*.md`

## 原則

- 保留文件型別與欄位規範
- 重寫 producer、consumer、queue、topic、retry、DLQ、incident steps
