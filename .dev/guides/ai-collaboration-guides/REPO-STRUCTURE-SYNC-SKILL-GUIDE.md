# Repo Structure Sync 已退役識別碼

`repo-structure-sync` 自 v0.6.0 起為相容識別碼，於 v0.16.0 退役，
不再提供 canonical skill spec 或 runtime wrapper。新請求使用此名稱時，
應明確回報已退役並提示替代技能 `ai-context-init`，不可靜默轉送。

新工作請使用
[`AI-CONTEXT-INIT-SKILL-GUIDE.md`](AI-CONTEXT-INIT-SKILL-GUIDE.md)。
既有 workflow、task、assessment、release、`initialized_by` 與 provenance
中的歷史識別保持原值。
