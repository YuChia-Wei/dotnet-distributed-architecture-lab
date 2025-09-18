# Feature Specification: Product Stock Restoration on Order Cancellation

**Feature Branch**: `003-product-consumer-ordercancelled`  
**Created**: 2025-09-18  
**Status**: Draft  
**Input**: User description: "Product Consumer 要接收 OrderCancelled 事件，並且將該訂單內紀錄的產品以及購買數量回填至產品庫存中"

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As the inventory system, when an order is cancelled, I need to automatically process an `OrderCancelled` event to return the products from that order back into the available stock. This ensures that inventory levels are accurate and cancelled items can be purchased by other customers.

### Acceptance Scenarios
1. **Given** a product "P1" has a stock level of 50 units, **When** an `OrderCancelled` event is received for an order that contained 5 units of "P1", **Then** the stock level of product "P1" MUST be updated to 55 units.
2. **Given** the system successfully processes an `OrderCancelled` event with a unique identifier, **When** the same event is received again, **Then** the system MUST NOT add the product quantities to the stock again, ensuring the operation is idempotent.

### Edge Cases
- **What happens when** the `OrderCancelled` event contains a Product ID that does not exist?
  - The system should log this as a warning and continue processing other products in the event without failing.
- **How does the system handle** a negative or zero quantity for a product in the event?
  - The item should be skipped, logged as an invalid data entry, and the process should continue.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The Product service/consumer MUST subscribe to and consume the `OrderCancelled` integration event.
- **FR-002**: Upon receiving an `OrderCancelled` event, the system MUST parse the event to extract the list of products, including each product's ID and the quantity to be restocked.
- **FR-003**: For each valid product in the event, the system MUST increase the corresponding product's stock quantity by the amount specified in the event.
- **FR-004**: The event processing logic MUST be idempotent. If the same `OrderCancelled` event is processed multiple times, the stock restoration must only occur once.
- **FR-005**: The system MUST log the outcome of each stock restoration attempt (e.g., success, warning for non-existent product, or failure).

### Key Entities *(include if feature involves data)*
- **Product**: Represents an item for sale. Key attributes include `ProductId` and `StockQuantity`.
- **OrderCancelled Event**: An integration event indicating an order has been cancelled. Its payload contains a list of items, where each item has a `ProductId` and `Quantity`.

---

## Review & Acceptance Checklist
*GATE: To be checked before moving to the planning phase.*

### Content Quality
- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

### Requirement Completeness
- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous  
- [X] Success criteria are measurable
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

---
