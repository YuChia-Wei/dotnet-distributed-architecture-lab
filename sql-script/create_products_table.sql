CREATE TABLE Products (
    Id UUID PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Price NUMERIC(18, 2) NOT NULL,
    Stock INT NOT NULL
);