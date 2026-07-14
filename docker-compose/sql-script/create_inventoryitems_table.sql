CREATE TABLE IF NOT EXISTS InventoryItems (
    Id UUID PRIMARY KEY,
    ProductId UUID NOT NULL,
    Stock INT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS UX_InventoryItems_ProductId
    ON InventoryItems (ProductId);

CREATE TABLE IF NOT EXISTS InventoryReservationOperations (
    OperationId UUID PRIMARY KEY,
    ProductId UUID NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    InventoryItemId UUID NULL,
    IsSuccess BOOLEAN NULL,
    RemainingStock INT NULL,
    FailureReason TEXT NULL,
    CompletedAt TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS IX_InventoryReservationOperations_ProductId
    ON InventoryReservationOperations (ProductId);
