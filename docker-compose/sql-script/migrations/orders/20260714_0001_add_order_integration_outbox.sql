-- Idempotent upgrade for existing Orders PostgreSQL volumes.
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

ALTER TABLE OrderIntegrationOutbox
    ADD COLUMN IF NOT EXISTS AggregateId UUID;

UPDATE OrderIntegrationOutbox
SET AggregateId = (Data ->> 'OrderId')::UUID
WHERE AggregateId IS NULL
  AND Data ? 'OrderId';

ALTER TABLE OrderIntegrationOutbox
    ALTER COLUMN AggregateId SET NOT NULL;

CREATE INDEX IF NOT EXISTS IX_OrderIntegrationOutbox_Claim
    ON OrderIntegrationOutbox (CreatedOn, Id)
    WHERE LockedUntil IS NULL;
