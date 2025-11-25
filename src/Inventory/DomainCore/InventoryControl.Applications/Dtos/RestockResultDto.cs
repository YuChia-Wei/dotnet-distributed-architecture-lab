namespace InventoryControl.Applications.Dtos;

public record RestockResultDto
{
    public bool IsSuccess { get; set; }
    public string ErrorMessage { get; set; }
    public int CurrentStock { get; set; }
}