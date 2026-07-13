CREATE TABLE IF NOT EXISTS Orders (
    Id UUID PRIMARY KEY,
    OrderDate TIMESTAMP WITH TIME ZONE NOT NULL,
    TotalAmount NUMERIC(18, 2) NOT NULL,
    ProductId UUID NOT NULL,
    ProductName VARCHAR(255) NOT NULL,
    Quantity INT NOT NULL
);

-- Event Store Table for Orders
CREATE TABLE IF NOT EXISTS OrderEvents (
    EventId BIGSERIAL PRIMARY KEY,
    StreamId UUID NOT NULL,
    Version INT NOT NULL,
    EventType VARCHAR(255) NOT NULL,
    Data JSONB NOT NULL,
    Timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(StreamId, Version)
);

-- Transactional outbox written in the same transaction as OrderEvents.
CREATE TABLE IF NOT EXISTS OrderIntegrationOutbox (
    Id UUID PRIMARY KEY,
    AggregateId UUID NOT NULL,
    MessageType VARCHAR(255) NOT NULL,
    Data JSONB NOT NULL,
    OccurredOn TIMESTAMP WITH TIME ZONE NOT NULL,
    CreatedOn TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    LockedUntil TIMESTAMP WITH TIME ZONE NULL,
    Attempts INT NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_OrderIntegrationOutbox_Claim
    ON OrderIntegrationOutbox (CreatedOn, Id)
    WHERE LockedUntil IS NULL;
