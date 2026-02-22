# 📁 Directory Rules - 目錄使用規則（.NET）

## 🚨 重要原則：.ai vs .dev 的區別

### `.ai/` 目錄 - 通用 AI Coding 框架
**只能包含**：
- ✅ 可重用於任何專案的內容
- ✅ 通用的編碼標準和最佳實踐
- ✅ 技術棧範本（使用 Example/BuildingBlocks 等通用命名）
- ✅ 通用的工作流程和 prompts
- ✅ 可複製到其他專案的檔案

**絕對不能包含**：
- ❌ 專案名稱（如 AiScrum, CompanyX）
- ❌ 專案特定 namespace（如 Company.Product）
- ❌ 專案特定的業務邏輯或領域模型
- ❌ 專案的 ADR、規格、任務
- ❌ 專案特定的測試資料或設定

### `.dev/` 目錄 - 專案特定內容
**應該包含**：
- ✅ 專案的 ADR（架構決策記錄）
- ✅ 領域規格（specs/）
- ✅ 任務定義（tasks/）
- ✅ 專案特定的經驗教訓（lessons/）
- ✅ Code review 報告（reports/）

## 🤖 AI 判斷規則

### 1. 內容分類判斷
```
問題：這個內容是否可以原封不動地用在其他專案？
├─ 是 → 放在 .ai/
└─ 否 → 放在 .dev/
```

### 2. 具體判斷標準

| 內容類型 | 放置位置 | 範例 |
|---------|---------|------|
| 編碼標準 | `.dev/standards/coding-standards/` | Repository 限制規則 |
| 專案 ADR | `.dev/adr/` | ADR-031-reactor-interface |
| 通用 prompt | `.ai/prompts/` | command-sub-agent-prompt.md |
| 專案規格 | `.dev/specs/` | product-spec.json |
| 技術範例 | `.dev/standards/examples/` | 使用 Example.* namespace |
| 專案程式碼 | `src/` | 使用實際 root namespace |

### 3. 檔案命名規則

#### `.ai/` 目錄檔案
- 使用通用術語（Product, Sprint, Task）
- 避免專案特定術語
- 範例程式碼使用 `Example.*` 或 `BuildingBlocks.*` 命名

#### `.dev/` 目錄檔案
- 可以使用專案特定術語
- 可以包含專案名稱
- 使用實際 root namespace

## 🔍 檢查命令

```bash
# 檢查 .ai/ 是否包含專案特定內容（請替換你的專案名稱）
rg -n "AiScrum|CompanyX|MyProject" .ai/ --glob "!**/.git/**"
```

## 🚀 AI 行動準則

1. **創建新檔案前**：先判斷通用 or 專案特定
2. **修改現有檔案時**：若 `.ai/` 內出現專案特定內容，需提醒並調整
3. **Code Review 時**：檢查檔案放置是否正確

## 📋 Quick Checklist

- [ ] 內容是否可跨專案重用？否 → `.dev/`
- [ ] 是否包含專案名稱或 root namespace？是 → `.dev/`
- [ ] 是否為 ADR/spec/task？是 → `.dev/`
- [ ] 是否為通用規範？是 → `.ai/`

---
最後更新：2026-02-01
