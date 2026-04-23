namespace Lab.BuildingBlocks.Application;

/// <summary>
/// 表示不含值的結果模式回傳物件。
/// </summary>
public sealed class Result
{
    private Result(bool isSuccess, string? errorMessage)
    {
        this.IsSuccess = isSuccess;
        this.ErrorMessage = errorMessage;
    }

    /// <summary>
    /// 取得是否成功。
    /// </summary>
    public bool IsSuccess { get; }

    /// <summary>
    /// 取得失敗時的錯誤訊息。
    /// </summary>
    public string? ErrorMessage { get; }

    /// <summary>
    /// 建立成功結果。
    /// </summary>
    /// <returns>成功結果。</returns>
    public static Result Success()
    {
        return new Result(true, null);
    }

    /// <summary>
    /// 建立失敗結果。
    /// </summary>
    /// <param name="errorMessage">錯誤訊息。</param>
    /// <returns>失敗結果。</returns>
    public static Result Failure(string errorMessage)
    {
        return new Result(false, errorMessage);
    }
}

/// <summary>
/// 表示含有值的結果模式回傳物件。
/// </summary>
/// <typeparam name="TValue">成功時承載的值型別。</typeparam>
public sealed class Result<TValue>
{
    private Result(bool isSuccess, TValue? value, string? errorMessage)
    {
        this.IsSuccess = isSuccess;
        this.Value = value;
        this.ErrorMessage = errorMessage;
    }

    /// <summary>
    /// 取得是否成功。
    /// </summary>
    public bool IsSuccess { get; }

    /// <summary>
    /// 取得成功時承載的值。
    /// </summary>
    public TValue? Value { get; }

    /// <summary>
    /// 取得失敗時的錯誤訊息。
    /// </summary>
    public string? ErrorMessage { get; }

    /// <summary>
    /// 建立成功結果。
    /// </summary>
    /// <param name="value">成功時承載的值。</param>
    /// <returns>成功結果。</returns>
    public static Result<TValue> Success(TValue value)
    {
        return new Result<TValue>(true, value, null);
    }

    /// <summary>
    /// 建立失敗結果。
    /// </summary>
    /// <param name="errorMessage">錯誤訊息。</param>
    /// <returns>失敗結果。</returns>
    public static Result<TValue> Failure(string errorMessage)
    {
        return new Result<TValue>(false, default, errorMessage);
    }
}
