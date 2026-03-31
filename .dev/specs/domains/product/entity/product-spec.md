# Product Aggregate Spec

## Aggregate
- Name: `Product`
- Bounded Context: `Products`
- Domain Namespace: `SaleProducts.Domains`

## Description

`Product` represents sellable catalog data managed by the Products bounded context.

## Attributes

- `Id: Guid`
- `Name: string`
- `Description: string`
- `Price: decimal`

## Invariants

- `Name` must not be null, empty, or whitespace.
- `Description` must not be null, empty, or whitespace.
- `Price` must not be negative.

## Behaviors

- Create product
- Update product
- Delete product

## Domain Events

- `ProductCreated`
- `ProductUpdated`
- `ProductDeleted`

## Notes

- Product creation and update share the same validation rules for name, description, and price.
- The aggregate currently raises domain events immediately when state changes.
