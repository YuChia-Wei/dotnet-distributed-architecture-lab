# ADR-052: Script Generation from Markdown Documentation

## Status
Accepted

## Context
我們的專案有兩種重要的文件需要維護：
1. **Coding Standards 文件** (`.md` 格式) - 給開發人員閱讀的規範文件
2. **檢查腳本** (`.sh` 格式) - 自動化檢查程式碼是否符合規範

原本的問題：
- 檢查腳本的規則是寫死的（hardcoded）
- 當 Coding Standards 文件更新時，檢查腳本不會自動更新
- 需要維護兩份資訊：文件和腳本
- 可能出現文件與檢查邏輯不同步的問題

## Decision
**直接從 Coding Standards Markdown 文件自動生成檢查腳本**

實作方式：
1. 使用 `generate-check-scripts-from-md.sh` 解析 Markdown 文件
2. 識別 `// ✅ 正確` 和 `// ❌ 錯誤` 的程式碼範例
3. 提取規則並生成對應的 Shell 檢查腳本
4. 檢查腳本存放在 `generated/` 目錄
5. 使用相容 wrapper 保持向後相容性

## Consequences

### 好處
1. **Single Source of Truth** - Markdown 文件是唯一的規則來源
2. **自動同步** - 文件更新後重新生成即可，無需手動同步
3. **減少維護成本** - 只需維護一份文件
4. **透明度高** - 看文件就知道會檢查什麼
5. **版本控制友好** - 文件變更即規則變更，易於追蹤

### 壞處
1. **依賴文件格式** - 需要保持 Markdown 格式的一致性
2. **解析限制** - 複雜的檢查邏輯可能難以從文件自動提取
3. **需要重新生成** - 文件更新後需要執行生成器

### 中立
1. 不是所有腳本都從 .md 生成 - 工具類腳本仍然手動維護
2. 需要 Python 環境來執行解析器

## References
- [MD-SCRIPT-GENERATION-GUIDE.md](../../.ai/scripts/MD-SCRIPT-GENERATION-GUIDE.md)
- [Coding Standards](../../.dev/standards/coding-standards.md)
