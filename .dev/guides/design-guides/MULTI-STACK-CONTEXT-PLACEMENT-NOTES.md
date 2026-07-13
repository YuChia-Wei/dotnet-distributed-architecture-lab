# 多技術棧 Context 收納規劃筆記

> Status: Exploration
>
> 本文件只保留未來資訊架構評估方向，不代表目前已支援 frontend、full-stack 或其他語言。

## 目前邊界

目前 active tech-stack profile 是 `.NET backend`，包含 C#、Web API、console/worker、MQ consumer、persistence、messaging 與 backend testing。

React / Vite 不應放進目前 dotnet-backend profile，也不應出現在 framework repository 的產品 `project-config`。

## 未來可能的收納方式

```text
.ai/assets/
  shared/
  tech-stacks/
    dotnet-backend/
    frontend-react-vite/
    <language-or-stack-profile>/
```

- `shared/`
  - 與語言、framework 無關的 AI 協作、軟體工程與架構方法。
- `tech-stacks/dotnet-backend/`
  - .NET backend 實作、review 與 validation context。
- `tech-stacks/frontend-react-vite/`
  - 僅在未來有足夠 frontend 規範、skills、validation 與維護需求時建立。
- `.dev/`
  - 目標 repo 實際採用的 frontend/backend 架構與 project truth。

## React / Vite 簡化示例

若未來建立 frontend profile，最小資訊可能包含：

- language: TypeScript
- framework: React
- build tool: Vite
- source roots
- test framework
- API contract integration boundary
- lint / format / build validation

這些欄位只能由目標 repo 的 `package.json`、lockfile、source tree、build config 或使用者確認資料產生。

## 建立新 Profile 前的 Gate

只有符合以下條件才建立新的 tech-stack profile：

- 同類 context 在至少兩個專案中重複使用。
- 已有穩定的 source-of-truth、validation 與維護責任。
- 內容無法合理放在 universal shared context。
- profile 不會把某個產品的 routes、components、hosts 或 deployment facts 當成 reusable rules。

在 gate 未成立前，React / Vite 只保留於本 exploration note。
