# When To Create ADR

只有當變更屬於「結構性決策」時，才建立 ADR。

## Create An ADR When

- 你正在決定新的 architecture boundary
- 你要改變 dependency direction 或 layer responsibility
- 你要引入新的 cross-cutting pattern
  - 例如 outbox、event sourcing、profile isolation、multi-agent governance
- 你要決定 repo-wide 的 canonical source ownership
  - 例如 `.ai/`、`.dev/standards/`、`.dev/guides/` 的分工
- 你需要保留明確的 tradeoff record
  - 之後可能會有人問「為什麼不是另一種做法」

## Do Not Create An ADR When

- 只是補充 usage guide
- 只是新增 checklist、template、example
- 只是把既有規則搬到更好的 canonical doc
- 只是局部 implementation 調整
- 只是 code style、命名、或單一小檔案整理

## Decision Test

若一個決策同時符合以下兩點，通常值得建立 ADR：

1. 會影響多個檔案、模組、或未來多次工作流程
2. 若不記錄 tradeoff，團隊之後很可能重複討論同一件事

## Default Preference

若只是要新增或修正規則：

- 先更新 `.dev/standards/`
- 或更新 `.dev/guides/`
- 或更新 `.ai/`

不要把本來就應該寫進 canonical docs 的規則，先丟進 ADR 再拖著不收斂。
