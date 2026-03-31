# Stage 4 Spec Coverage Checklist

## Purpose

Track Stage 4 coverage across active bounded contexts so requirement truth, production specs, and test specs can be completed in a controlled way before Stage 5 runtime documentation starts.

## Coverage Matrix

| Domain | Use Case | Production Spec | Test Spec | Notes |
| --- | --- | --- | --- | --- |
| Product | CreateProduct | Yes | Yes | Core create flow covered |
| Product | UpdateProduct | Yes | Yes | Covers load-update-persist path |
| Product | DeleteProduct | Yes | Yes | Product removal baseline now documented |
| Order | PlaceOrder | Yes | Yes | MQ-aware order placement baseline exists |
| Order | ShipOrder | Yes | Yes | Status transition + integration event |
| Order | DeliverOrder | Yes | Yes | Status transition + integration event |
| Order | CancelOrder | Yes | Yes | Status transition + integration event |
| InventoryItem | DecreaseStock | Yes | Yes | Inventory reservation baseline exists |
| InventoryItem | IncreaseStock | Yes | Yes | Stock increase success/failure baseline |
| InventoryItem | Restock | Yes | Yes | Return-stock scenario baseline |

## Layer Coverage Matrix

| Domain | Aggregate Test Spec | Integration Test Spec | Notes |
| --- | --- | --- | --- |
| Product | Yes | Yes | Aggregate validation and repository persistence baseline added |
| Order | Yes | Yes | Aggregate lifecycle and inventory/MQ-aware integration baseline added |
| InventoryItem | Yes | Yes | Aggregate stock rules and persistence/event publication baseline added |

## Gaps After This Stage Slice

- Aggregate and integration test coverage now exists at a baseline level, but not every adapter or persistence path is covered.
- Integration-focused test specs still need deeper repository/db/MQ contract variants if later stages require stricter operational coverage.
- No cross-domain or E2E test specs exist yet; these should be driven by Stage 5 runtime docs.

## Exit Readiness Signal for Stage 4

Stage 4 is considered materially stronger when:

- every active use case with a production spec also has at least one use-case test spec
- every active bounded context has at least one aggregate and one integration test spec baseline
- remaining gaps are intentional and documented
- later Stage 5 runtime docs can reference concrete use-case and test-spec artifacts instead of only requirements
