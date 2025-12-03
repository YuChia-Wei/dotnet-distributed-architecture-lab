# Q: 為什麼 OrderDomainRepository 中的 dbconnection 不需要檢查是否已開啟，而 OrderEventSourcingRepository 就要?

# Junie Pro Answer

### 為什麼有的要檢查連線、有的不用？

關鍵差異在於你是否「手動開始交易」。

- 當只呼叫 Dapper 的 `Query*`/`Execute*`（`transaction` 參數是 `null`）時：
    - Dapper 會在發出指令前自動檢查 `IDbConnection.State`，若是 `Closed` 就幫你 `Open()`，結束後再依需要關閉。
    - 因此像一般的 `OrderDomainRepository` 僅用 Dapper 執行 SQL 時，不需要自己檢查或開啟連線。

- 當你手動呼叫 `BeginTransaction()`（ADO.NET API）時：
    - ADO.NET 要求連線必須已經是 `Open`，否則會丟 `InvalidOperationException: Connection is not open`。
    - `OrderEventSourcingRepository.SaveAsync` 在 `BeginTransaction()` 前若沒先 `Open()`，就會發生上述例外。

### 對應到你的兩個 Repository
- `OrderDomainRepository`：路徑多半是直接用 Dapper 的 `Execute/Query`，沒有先手動 `BeginTransaction()`，Dapper 會自動開關連線，所以「看起來不需檢查」。
- `OrderEventSourcingRepository`：先呼叫了 `BeginTransaction()` 來圍住多筆寫入事件，此時你必須保證 `IDbConnection.State == Open`，所以需要在交易前檢查並 `Open()`。

### 何時該檢查/開啟連線
- 不需要：
    - 只用 Dapper，且不自行建立 `IDbTransaction`（`transaction: null`）。
- 需要：
    - 你要呼叫 `BeginTransaction()` 建立 `IDbTransaction`。
    - 你要手動用 ADO.NET `DbCommand` 物件執行指令。

### 建議的一致做法
- 只要有「手動交易」就固定寫：
  ```csharp
  if (_dbConnection.State != ConnectionState.Open)
      _dbConnection.Open();
  using var tx = _dbConnection.BeginTransaction();
  try
  {
      // Dapper Execute/Query 傳入 tx
      tx.Commit();
  }
  catch
  {
      tx.Rollback();
      throw;
  }
  ```
- 若未使用手動交易，直接交給 Dapper 管理連線即可，不需額外 `Open()`。

### 一句話總結
`OrderDomainRepository` 靠 Dapper 自動開關連線；`OrderEventSourcingRepository` 因為自己呼叫了 `BeginTransaction()`，必須先把連線打開。
