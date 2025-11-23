namespace InventoryControl.Domains.DomainResults;

/// <summary>
/// 庫存回補結果
/// </summary>
public sealed class StockReturnResult
{
    private StockReturnResult(bool isSuccess, string? errorCode, string? errorMessage)
    {
        this.IsSuccess = isSuccess;
        this.ErrorCode = errorCode;
        this.ErrorMessage = errorMessage;
    }

    public bool IsSuccess { get; }
    public string? ErrorCode { get; }
    public string? ErrorMessage { get; }

    public static StockReturnResult Fail(string errorCode, string? errorMessage = null)
    {
        return new StockReturnResult(false, errorCode, errorMessage);
    }

    public static StockReturnResult Success()
    {
        return new StockReturnResult(true, null, null);
    }
}