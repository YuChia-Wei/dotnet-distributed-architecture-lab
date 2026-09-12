namespace Lab.BuildingBlocks.Integrations.Diagnostics;

/// <summary>供兩個獨立處理器接收的原始外部 MQ 事件。</summary>
public sealed record IndependentWorkRequested(Guid ProbeId, DateTime OccurredOn) : IIntegrationEvent;
