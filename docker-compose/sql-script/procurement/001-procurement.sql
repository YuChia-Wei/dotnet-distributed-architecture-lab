-- Additive PostgreSQL schema for the single-item Procurement lab.
CREATE TABLE IF NOT EXISTS procurement_purchase_orders (
    id uuid PRIMARY KEY,
    client_request_id uuid NOT NULL UNIQUE,
    product_id uuid NOT NULL,
    supplier_sku varchar(64) NOT NULL,
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price numeric(18, 2) NOT NULL CHECK (unit_price >= 0),
    currency varchar(3) NOT NULL CHECK (currency = 'TWD'),
    provider varchar(16) NOT NULL CHECK (provider IN ('direct', 'wiremock', 'microcks')),
    state varchar(32) NOT NULL,
    supplier_order_id varchar(128),
    received_quantity integer NOT NULL DEFAULT 0 CHECK (received_quantity >= 0 AND received_quantity <= quantity),
    version integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS procurement_receipts (
    receipt_id uuid PRIMARY KEY,
    purchase_order_id uuid NOT NULL REFERENCES procurement_purchase_orders(id),
    product_id uuid NOT NULL,
    quantity integer NOT NULL CHECK (quantity > 0),
    received_at timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_procurement_receipts_order ON procurement_receipts(purchase_order_id);

CREATE TABLE IF NOT EXISTS procurement_outbox (
    id uuid PRIMARY KEY REFERENCES procurement_receipts(receipt_id),
    partition_key varchar(32) NOT NULL,
    payload jsonb NOT NULL,
    attempts integer NOT NULL DEFAULT 0,
    next_attempt_at timestamptz NOT NULL DEFAULT now(),
    locked_by uuid,
    locked_until timestamptz,
    published_at timestamptz,
    parked_at timestamptz,
    last_error varchar(4000),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_procurement_outbox_pending
    ON procurement_outbox(next_attempt_at, created_at)
    WHERE published_at IS NULL AND parked_at IS NULL;
