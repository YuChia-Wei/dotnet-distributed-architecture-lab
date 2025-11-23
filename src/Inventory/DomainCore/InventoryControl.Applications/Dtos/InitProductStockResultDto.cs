namespace InventoryControl.Applications.Dtos;

public record InitProductStockResultDto
{
    public bool IsSuccess { get; set; }
    public string ErrorMessage { get; set; }
    public int CurrentStock { get; set; }
}