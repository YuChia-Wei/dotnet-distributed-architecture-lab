# dashboards sourced

grafana dashboards url: https://grafana.com/grafana/dashboards

- asp net core: https://grafana.com/grafana/dashboards/19924-asp-net-core/
  - **有針對資料來源進行修正**
- ASP.NET Core Endpoint: https://grafana.com/grafana/dashboards/19925-asp-net-core-endpoint/
  - **有針對資料來源進行修正**
- logs-app: https://grafana.com/grafana/dashboards/13639-logs-app/
  - **有針對資料來源進行修正**
  - **有針對搜尋條件進行修正**
- OpenTelemetry dotnet webapi: https://grafana.com/grafana/dashboards/20568-opentelemetry-dotnet-webapi/
  - **有針對資料來源進行修正**
  - **有針對搜尋條件進行修正**

## 專案自訂 dashboards

- `system-errors-exceptions.json`
  - 快速依 service 與文字查詢 `Error`、`Critical`、`Fatal` logs，以及任何帶有 exception metadata 的 log。
  - 展開具有 `trace_id` 的 log 後，可透過 Loki derived field 的 `View trace` 直接開啟對應 Tempo trace。
