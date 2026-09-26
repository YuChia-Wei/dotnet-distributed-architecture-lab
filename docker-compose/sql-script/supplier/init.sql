CREATE TABLE IF NOT EXISTS supplier_skus (
  sku varchar(64) PRIMARY KEY, name varchar(120) NOT NULL,
  unit_price numeric(12,2) NOT NULL CHECK (unit_price >= 0), currency char(3) NOT NULL CHECK (currency = 'TWD'),
  order_allowed boolean NOT NULL DEFAULT true
);
CREATE TABLE IF NOT EXISTS supplier_orders (
  supplier_order_id uuid PRIMARY KEY, client_request_id uuid NOT NULL UNIQUE,
  sku varchar(64) NOT NULL, quantity integer NOT NULL CHECK (quantity > 0), unit_price numeric(12,2) NOT NULL CHECK (unit_price >= 0),
  currency char(3) NOT NULL CHECK (currency = 'TWD'), status varchar(16) NOT NULL CHECK (status IN ('accepted','rejected')),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_supplier_orders_created_at ON supplier_orders (created_at DESC);
INSERT INTO supplier_skus (sku,name,unit_price,currency,order_allowed) VALUES
 ('REAL-001','Sandbox real product',100.00,'TWD',true),('MOCK-001','Reserved mock example product',100.00,'TWD',true),('DENY-001','Deterministic rejected product',100.00,'TWD',false)
ON CONFLICT (sku) DO NOTHING;
