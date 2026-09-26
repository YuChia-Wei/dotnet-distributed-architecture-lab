CREATE TABLE IF NOT EXISTS InventoryGoodsReceipts (
    ReceiptId UUID PRIMARY KEY,
    PurchaseOrderId UUID NOT NULL,
    ProductId UUID NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    InventoryItemId UUID NULL,
    ResultingStock INT NULL,
    CompletedAt TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS IX_InventoryGoodsReceipts_ProductId
    ON InventoryGoodsReceipts (ProductId);
