namespace InventoryControl.Domains.DomainResults;

/// <summary>
/// 扣庫結果
/// </summary>
public sealed class StockDecreaseResult
{
    private StockDecreaseResult(bool isSuccess, string? errorCode, string? errorMessage)
    {
        this.IsSuccess = isSuccess;
        this.ErrorCode = errorCode;
        this.ErrorMessage = errorMessage;
    }

    public bool IsSuccess { get; }
    public string? ErrorCode { get; }
    public string? ErrorMessage { get; }

    public static StockDecreaseResult Fail(string errorCode, string? errorMessage = null)
    {
        return new StockDecreaseResult(false, errorCode, errorMessage);
    }

    public static StockDecreaseResult Success()
    {
        return new StockDecreaseResult(true, null, null);
    }
}