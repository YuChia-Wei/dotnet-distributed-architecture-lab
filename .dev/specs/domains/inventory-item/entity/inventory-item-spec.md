# InventoryItem Aggregate Spec

## Aggregate
- Name: `InventoryItem`
- Bounded Context: `Inventory`
- Domain Namespace: `InventoryControl.Domains`

## Description

`InventoryItem` tracks available stock for a product in the Inventory bounded context.

## Attributes

- `Id: Guid`
- `ProductId: Guid`
- `Stock: int`

## Behaviors

- Initialize stock
- Increase stock
- Decrease stock
- Restock returned quantity

## Business Rules

- Decrease operations must fail when requested quantity exceeds available stock.
- Negative decrease quantity is invalid.

## Domain Events

- `StockIncreased`
- `StockDecreased`
- `StockReturned`

## Notes

- The aggregate returns domain result objects for stock operations instead of using exceptions for expected business failures such as insufficient stock.
