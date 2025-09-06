# Feature Specification: Publish Product Stock Deducted Event

**Feature Branch**: `001-publish-product-stock`
**Created**: 2025-09-06
**Status**: Draft
**Input**: User description: "product 在下單事件處理器之後，應該要發布產品數量扣除成功的事件，提供 order consumer 去更新訂單的狀態為產品已備貨完畢"

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a system, after an order is placed, I need to deduct the ordered quantity from the product's stock and notify the Order service that the products are allocated, so the order can proceed to the next step.

### Acceptance Scenarios
1.  **Given** the Product service receives an `OrderPlaced` event,
    **When** the stock for all products in the order is successfully deducted,
    **Then** the Product service MUST publish a `ProductStockDeducted` event containing the original `OrderId` and product details.
2.  **Given** the Order service is running,
    **When** it consumes a `ProductStockDeducted` event,
    **Then** it MUST update the corresponding order's status to "Allocated" (or a similar state representing product readiness).

### Edge Cases
- What happens when stock is insufficient for a product? [NEEDS CLARIFICATION: Should the event still be published? Should a different event be published? What is the compensation logic?]
- What happens if the `OrderPlaced` event contains a product that does not exist? [NEEDS CLARIFICATION: How should the system handle this error?]

---

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The system MUST consume `OrderPlaced` events in the Product service context.
- **FR-002**: The system MUST deduct the item quantity from the stock for each product listed in the `OrderPlaced` event.
- **FR-003**: The system MUST publish a `ProductStockDeducted` integration event upon successful stock deduction.
- **FR-004**: The `ProductStockDeducted` event MUST contain the `OrderId` and a list of the products whose stock was deducted.
- **FR-005**: The Order service MUST consume the `ProductStockDeducted` event.
- **FR-006**: The system MUST update the order status to "Allocated" (or a similar defined state) after consuming the `ProductStockDeducted` event.

### Key Entities *(include if feature involves data)*
- **ProductStockDeducted Event**: Represents the successful deduction of stock for an order.
  - Attributes: `OrderId`, `Products` list.
- **Order**: Represents a customer's order.
  - Attributes: `Status` (updated by this feature).

---

## Review & Acceptance Checklist

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---