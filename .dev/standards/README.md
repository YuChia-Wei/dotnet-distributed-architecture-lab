# .NET CA + WolverineFx + EF Core Tech Stack

This folder contains the .NET adaptation of the source CA ezddd tech stack.
All architecture and development rules (DDD/CA/CQRS, event sourcing, outbox, contract testing, mutation testing) must be preserved.
Use WolverineFx for CQRS/MQ/Event Sourcing, EF Core for ORM, xUnit + BDDfy (Gherkin-style naming) for BDD, and NSubstitute for mocks.

## Structure

- `ASPNET-CORE-CONFIGURATION-CHECKLIST.md`
  - ASP.NET Core configuration checklist
- `CODE-REVIEW-CHECKLIST.md`
  - code review checklist 與審查準則
- `anti-patterns.md`
  - 反模式與禁止事項
- `best-practices.md`
  - 建議採用的 practices
- `coding-guide.md`
  - coding 標準入口，串接 standards 與 guides
- `coding-standards.md`
  - coding style 與 implementation-level rules
- `project-structure.md`
  - 專案目錄與資料夾用途的單一真相
- `README.md`
  - standards 入口說明

Operational guides、setup walkthroughs、FAQ、troubleshooting 文件已移到 `.dev/guides/`。

## Belongs Here

- 規則性文件
- checklist
- anti-pattern / best-practice
- project structure single source of truth
- 需要長期穩定引用的標準入口

## Do Not Put Here

- setup guide
- quick start walkthrough
- FAQ
- troubleshooting / solution note
- 單次重構提案或工作紀錄
- AI skill/prompt/workflow guide

這些內容應分別放到：

- `.dev/guides/implementation-guides/`
- `.dev/guides/design-guides/`
- `.dev/guides/learning-guides/`
- `.dev/guides/ai-collaboration-guides/`
- `.dev/refactor-workflows/`

## Notes
- ezDDD/ezSpec concepts must be preserved even without direct .NET packages.
- If no .NET equivalent exists, keep the rule and mark TODO rather than deleting it.
- `standards/` should not accumulate setup guides, troubleshooting guides, or FAQ-style documents.
