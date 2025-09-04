CREATE TABLE IF NOT EXISTS Products (
    Id UUID PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Price NUMERIC(18, 2) NOT NULL,
    Stock INT NOT NULL,
    IsDeleted BOOLEAN NOT NULL DEFAULT FALSE,
    Version INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ProductSales (
    ProductId UUID NOT NULL,
    OrderId UUID NOT NULL,
    Quantity INT NOT NULL,
    SaleDate TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (ProductId, OrderId),
    CONSTRAINT fk_products
        FOREIGN KEY(ProductId)
        REFERENCES Products(Id)
        ON DELETE CASCADE
);