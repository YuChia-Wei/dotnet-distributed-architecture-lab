# 產品需求文件（PRD）樣板

## 1. 專案概述（Project Overview）
- 摘要：以一段文字描述問題、目標使用者與預期成果。
- 範圍：此次交付涵蓋與不涵蓋的內容。
- 利害關係人：產品、工程、QA、設計、運維等。

## 2. 目標與指標（Goals and Objectives）
- 商業目標：可量測的成果（例：轉換率 +10%）。
- 使用者目標：主要任務（Jobs-to-be-done）與成功標準。
- 衡量指標：KPI 與量測方式。

## 3. 功能需求（Functional Requirements）
- 使用者故事／用例與驗收標準。
- 畫面／流程或 API 行為（依用例列出）。
- 資料模型重點（實體、主欄位、關聯）。

## 4. 非功能需求（Non-functional Requirements）
- 效能：如 P95 < 200ms、吞吐量目標。
- 可靠性：逾時、重試、冪等、耐久性。
- 資安／隱私：身份驗證/授權、PII、OWASP。
- 可擴展性、可觀測性、在地化/國際化。

## 5. 系統架構（System Architecture）
- 方法：參考領域驅動設計（DDD）、CQRS、Clean Architecture。
- 界限內容（Bounded Context）與服務邊界。
- 主要元件與互動（可附示意圖）。
- 訊息代理（Kafka/RabbitMQ）、儲存（PostgreSQL）、部署環境。

## 6. API 設計（RESTful）
- 資源模型與名詞（使用複數）。
- 端點（方法、路徑、狀態碼）：
  - 範例：`POST /orders` → 201，回傳 `{ id }`
  - 範例：`GET /products/{id}` → 200，回傳 `ProductDto`
- 請求/回應結構、驗證規則、錯誤合約。

## 7. 侷限與假設（Constraints and Assumptions）
- 技術侷限：SDK、框架、版本等。
- 營運侷限：環境、配額、SLA。
- 假設與已知風險。

## 8. 里程碑與時程（選填）
- 階段、時間與相依關係。

## 9. 附錄（選填）
- 詞彙、連結（ticket/設計稿）、樣本 payload、圖示。

