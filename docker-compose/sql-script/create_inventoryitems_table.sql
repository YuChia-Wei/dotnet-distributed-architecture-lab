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

CREATE TABLE IF NOT EXISTS InventoryIntegrationOutbox (
    Id UUID PRIMARY KEY,
    PartitionKey VARCHAR(64) NOT NULL,
    MessageType VARCHAR(255) NOT NULL,
    Data JSONB NOT NULL,
    OccurredOn TIMESTAMPTZ NOT NULL,
    CreatedOn TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PublishedAt TIMESTAMPTZ NULL,
    LockId UUID NULL,
    LockedUntil TIMESTAMPTZ NULL,
    Attempts INT NOT NULL DEFAULT 0 CHECK (Attempts >= 0),
    NextAttemptAt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    LastError TEXT NULL,
    ParkedAt TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS IX_InventoryIntegrationOutbox_Claim
    ON InventoryIntegrationOutbox (NextAttemptAt, CreatedOn, Id)
    WHERE PublishedAt IS NULL AND ParkedAt IS NULL;
