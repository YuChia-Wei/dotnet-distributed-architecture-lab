# Skill and Sub-Agent Boundary Rationale

## Decision Pattern

區分兩種 AI 資產：

- top-level skill
- delegated sub-agent role

## Why

### 1. 入口層級不同

skill 是人或 main agent 可以直接啟動的高階能力。  
sub-agent role 是 workflow 內部委派給 worker 的角色。

### 2. 避免 taxonomy 混亂

若把所有可執行 prompt 都升格成 skill，會混淆：

- top-level capability
- worker role
- shared prompt material

### 3. 有助於可攜式知識庫整理

當 skill 與 sub-agent 明確分層後，`.ai/` 才能保持穩定的可移植結構，而不會隨 runtime wrapper 改動反覆重組。

## Why Not

### 每個可執行 prompt 都做成 skill

缺點：

- runtime entry 過多
- 與 delegated worker 邊界模糊
- wrapper strategy 難以維護

## Practical Rule

- top-level capability -> skill
- delegated bounded worker -> sub-agent role prompt
- checklist / template / shared rules -> supporting materials
