namespace InventoryControl.Domains.DomainResults;

/// <summary>
/// 增加庫存結果
/// </summary>
public sealed class StockIncreaseResult
{
    private StockIncreaseResult(bool isSuccess, string? errorCode, string? errorMessage)
    {
        this.IsSuccess = isSuccess;
        this.ErrorCode = errorCode;
        this.ErrorMessage = errorMessage;
    }

    public bool IsSuccess { get; }
    public string? ErrorCode { get; }
    public string? ErrorMessage { get; }

    public static StockIncreaseResult Fail(string errorCode, string? errorMessage = null)
    {
        return new StockIncreaseResult(false, errorCode, errorMessage);
    }

    public static StockIncreaseResult Success()
    {
        return new StockIncreaseResult(true, null, null);
    }
}