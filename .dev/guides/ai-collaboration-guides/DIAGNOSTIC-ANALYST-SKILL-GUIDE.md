# Diagnostic Analyst 使用指南

`diagnostic-analyst` 用來釐清已觀察到的故障或效能症狀。它會先列出可被推翻的假說，再設計觀察與最小重現，最後交付根因結論及修復建議。

適合用於「為什麼這次變慢」、「外層檢查通過但套件無法使用」或「相同輸入卻得到不同結果」。如果修復目標與原因已清楚，可直接交給適用的 implementer；架構方向及程式碼規範審查仍由各自技能負責。

## 呼叫方式

```text
請用 diagnostic-analyst 調查這個命令的效能退化。
預期：處理 100 與 1,000 個檔案時，Git 子程序數應維持固定。
實際：1,000 個檔案的耗時明顯增加。
請先列出假說、可推翻它的觀察及觀察強度，再於拋棄式 fixture 計數。
本次只授權診斷與 fixture 實驗；交付修復範圍及回歸建議。
```

```text
請用 diagnostic-analyst 調查外層 route validator 通過、incoming package validator 卻失敗的原因。
綁定指定 archive SHA-256，分別執行兩個驗證邊界並保存輸出。
不要修改歷史套件。若缺少執行環境，請保留 blocked 與待補證據。
```

輸出包含症狀、假說表、證偽方法與強度、最小重現、因果隔離、根因與限制、修復交接、回歸綁定。`unconfirmed` 表示證據不足，`blocked` 表示缺少可執行條件；兩者都不代表已確認根因。

## 歷史案例的操作示範

以下是依歷史來源設計的診斷示範，沒有重新執行事故，也不改寫當時的結論。

| 案例與來源 | 假說及可推翻的觀察 | 最小重現與因果隔離設計 | 交接及回歸綁定 |
| --- | --- | --- | --- |
| [PERF-002 / #251](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/251) | 假說：逐檔 Git 呼叫造成成本隨檔案數增加。若攔截全部子程序後，Git 呼叫數在不同 payload 規模保持固定，則可推翻此假說。偶爾看不到 Git process 的取樣不能推翻它。 | 在同環境比較兩種檔案數，攔截完整 subprocess argv 並計數；以批次 snapshot 路徑作控制介入，另行核對輸出及安全邊界。歷史 retrospective 保留了逐檔與批次呼叫數，以及後續安全審查失敗。 | 交給既有授權的實作 owner；回歸固定呼叫數、輸出一致性與 Git policy drift。效能改善不能取代安全驗證。 |
| [REL-016 / #241](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/241) | 假說：文字黑名單漏掉 transient lifecycle 說法。若從實際發布入口渲染指定缺陷內容即被拒絕，則需調查另一條路徑或歷史版本。 | 在 fixture 重播來源中的公開內容缺陷，執行真正 renderer；控制介入使用有效的 consumer-facing 內容，核對一拒絕一接受。實際 body-only 修正另有 provider 前後讀回。 | 交給 source-release governance；回歸缺陷措辭與合法內容，不推論 tag 或 archive 損壞。 |
| [UPG-005 / #237](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/237) | 假說：外層 edge proof 未執行 archive 自帶 validator，導致假陽性。若對同一 archive 的 edge proof 已呼叫該邊界且傳遞其失敗，則推翻此假說。 | 固定 archive digest，分別執行 edge 與 embedded validator；攔截 embedded 邊界或注入受控失敗，觀察外層是否跟著失敗。歷史來源記錄兩者 exit code 不一致。 | 交給 source-release/upgrade owner；回歸 metadata 與 validator 不一致時，在 target mutation 前拒絕。不能從這個現象推論 target 已被破壞。 |

## 契約與驗證

規則由 [canonical skill](../../../.ai/assets/skills/diagnostic-analyst/skill.yaml)、[診斷契約](../../../.ai/assets/skills/diagnostic-analyst/references/diagnostic-contract.md) 與 [輸出契約](../../../.ai/assets/skills/diagnostic-analyst/references/output-contract.md) 管理；Codex 與 Claude wrapper 只提供入口。

JSON validator 會檢查必填欄位、推論前提及 evidence digest。通過只表示紀錄符合契約；仍需要審查實驗是否真的執行、觀察範圍是否完整，以及控制介入能否排除其他解釋。修復、PR、合併及發布沿用各自的授權邊界。
