namespace Lab.BuildingBlocks.Integrations;

/// <summary>
/// 整合事件，也可稱 application event，主要為 application 層的業務邏輯執行完後要發出的事件
/// </summary>
/// <remarks>
/// ref: https://medium.com/%40serhatalftkn/domain-events-vs-integration-events-understanding-the-differences-and-when-to-use-each-3977278034d3
/// </remarks>
public interface IIntegrationEvent
{
    /// <summary>
    /// 發生時間
    /// </summary>
    DateTime OccurredOn { get; }
}