-- Idempotent upgrade for existing Orders PostgreSQL volumes.
CREATE TABLE IF NOT EXISTS OrderIntegrationOutbox (
    Id UUID PRIMARY KEY,
    AggregateId UUID NOT NULL,
    MessageType VARCHAR(255) NOT NULL,
    Data JSONB NOT NULL,
    OccurredOn TIMESTAMP WITH TIME ZONE NOT NULL,
    CreatedOn TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    LockId UUID NULL,
    LockedUntil TIMESTAMP WITH TIME ZONE NULL,
    Attempts INT NOT NULL DEFAULT 0,
    NextAttemptAt TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    LastError TEXT NULL,
    ParkedAt TIMESTAMP WITH TIME ZONE NULL
);

ALTER TABLE OrderIntegrationOutbox
    ADD COLUMN IF NOT EXISTS AggregateId UUID;

UPDATE OrderIntegrationOutbox
SET AggregateId = (Data ->> 'OrderId')::UUID
WHERE AggregateId IS NULL
  AND Data ? 'OrderId';

ALTER TABLE OrderIntegrationOutbox
    ALTER COLUMN AggregateId SET NOT NULL;

ALTER TABLE OrderIntegrationOutbox
    ADD COLUMN IF NOT EXISTS LockId UUID,
    ADD COLUMN IF NOT EXISTS NextAttemptAt TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS LastError TEXT,
    ADD COLUMN IF NOT EXISTS ParkedAt TIMESTAMP WITH TIME ZONE;

UPDATE OrderIntegrationOutbox
SET NextAttemptAt = COALESCE(NextAttemptAt, CreatedOn, NOW())
WHERE NextAttemptAt IS NULL;

ALTER TABLE OrderIntegrationOutbox
    ALTER COLUMN NextAttemptAt SET DEFAULT NOW(),
    ALTER COLUMN NextAttemptAt SET NOT NULL;

DROP INDEX IF EXISTS IX_OrderIntegrationOutbox_Claim;

CREATE INDEX IX_OrderIntegrationOutbox_Claim
    ON OrderIntegrationOutbox (NextAttemptAt, CreatedOn, Id)
    WHERE ParkedAt IS NULL;
