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

## Persistence Semantics

- New rows start at `Version = 1`.
- Update and delete use optimistic concurrency and fail when the expected version no longer matches.
- Delete is a soft-delete capability represented by `ProductDeleted` and persisted as `IsDeleted = true`.
- Normal aggregate loads and query projections exclude soft-deleted rows.

## Domain Events

- `ProductCreated`
- `ProductUpdated`
- `ProductDeleted`

## Notes

- Product creation and update share the same validation rules for name, description, and price.
- The aggregate currently raises domain events immediately when state changes.
- A reconstructed implementation may model the deletion marker inside the aggregate or repository adapter, but must preserve the observable soft-delete and optimistic-concurrency contract.
