# Problem Frames

本目錄放置可被 `spec-compliance-validator` 直接讀取的 Problem Frame 規格。

## 目標

- 讓既有的 `requirements` 與 `specs` 文件之外，多一層可驗證、可追溯的 use-case 規格
- 讓外部系統整合、非同步回調、冪等、錯誤對映等問題，能在實作前被寫清楚
- 讓 BDD / Spec by Example / TDD 有更穩定的上游輸入

## 何時使用

優先用在這類 use case：

- 高外部依賴
- 錯誤處理複雜
- 必須追蹤 domain event 與測試覆蓋
- 同步命令與非同步確認混合存在

若是單純 CRUD 或約束很少的功能，不必強制使用。

## 與既有文件的分工

- `.dev/requirement/`
  - business goal、範圍、優先順序、非功能需求
- `.dev/specs/`
  - human-facing 功能說明、流程、UI / API 行為
- `.dev/problem-frames/`
  - 單一 use case 的結構化機器規格，可供 validator 與後續測試設計使用

## 建議流程

1. 先從 `requirements` 與 `specs` 選一個高價值 use case。
2. 先決定是 `cbf/` 或 `swf/`。
3. 補齊最小檔案集：
   - `frame.yaml`
   - `machine/machine.yaml`
   - `machine/use-case.yaml`
   - `controlled-domain/aggregate.yaml` 或 `workpiece/aggregate.yaml`
   - `acceptance.yaml` 或 `requirements/*.yaml`
4. 用 `acceptance.yaml` 建立 BDD / SbE 場景。
5. 用 `spec-compliance-validator` 對照程式碼與測試。

## 最小目錄結構

```text
.dev/problem-frames/{domain}/cbf/{use-case}/
  frame.yaml
  acceptance.yaml
  machine/
    machine.yaml
    use-case.yaml
  controlled-domain/
    aggregate.yaml
```

## 範本與示例

- 可重用範本：`templates/cbf-external-system/`
- 外部付款授權示例：`payments/cbf/authorize-payment/`
- 由既有 requirement/spec 萃取的訂單下單示例：`orders/cbf/place-order/`
- 快速 authoring 指南：`../guides/ai-collaboration-guides/PROBLEM-FRAME-AUTHORING-GUIDE.md`
- 可重用起草 skill：`.claude/skills/problem-frame-author/`

## 對 validator 的價值

validator 需要這些規格，才能檢查：

- use case input 欄位是否齊全
- preconditions / error handling 是否存在
- aggregate contracts / invariants 是否對齊
- domain event 欄位是否完整
- scenario 是否有對應測試
- 每個 `then` 是否有 assertion

沒有這些檔案時，validator 幾乎沒有實際作用。
