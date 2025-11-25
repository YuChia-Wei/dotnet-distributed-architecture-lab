using System;

namespace InventoryControl.Applications.Dtos;

public record GetAvailableQuantityResultDto(Guid ProductId, int AvailableStock);