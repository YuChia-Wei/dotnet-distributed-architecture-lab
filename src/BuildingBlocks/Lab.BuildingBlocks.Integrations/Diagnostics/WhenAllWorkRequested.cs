namespace Lab.BuildingBlocks.Integrations.Diagnostics;

/// <summary>供等待兩項並行作業的教學範例接收之外部事件。</summary>
public sealed record WhenAllWorkRequested(Guid ProbeId, DateTime OccurredOn) : IIntegrationEvent;
