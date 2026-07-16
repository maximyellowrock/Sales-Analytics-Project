CREATE TABLE dw.DimCustomer
(
    CustomerKey INT NOT NULL PRIMARY KEY,
    CustomerID NVARCHAR(20) NOT NULL,
    CustomerName NVARCHAR(150) NOT NULL,
    Segment NVARCHAR(50) NOT NULL
);

CREATE TABLE dw.DimProduct
(
    ProductKey INT NOT NULL PRIMARY KEY,
    ProductBusinessKey NVARCHAR(600) NOT NULL UNIQUE,
    ProductID NVARCHAR(30) NOT NULL,
    ProductName NVARCHAR(500) NOT NULL,
    Category NVARCHAR(100) NOT NULL,
    SubCategory NVARCHAR(100) NOT NULL
);

CREATE TABLE dw.DimGeography
(
    GeographyKey INT NOT NULL PRIMARY KEY,
    Country NVARCHAR(100) NOT NULL,
    Region NVARCHAR(50) NOT NULL,
    StateName NVARCHAR(100) NOT NULL,
    City NVARCHAR(100) NOT NULL,
    PostalCode NVARCHAR(20) NOT NULL
);

CREATE TABLE dw.DimShipMode
(
    ShipModeKey INT NOT NULL PRIMARY KEY,
    ShipMode NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE dw.DimDate
(
    DateKey INT NOT NULL PRIMARY KEY,
    FullDate DATE NOT NULL UNIQUE,
    DayNumber TINYINT NOT NULL,
    MonthNumber TINYINT NOT NULL,
    MonthName NVARCHAR(20) NOT NULL,
    QuarterNumber TINYINT NOT NULL,
    YearNumber SMALLINT NOT NULL,
    WeekdayName NVARCHAR(20) NOT NULL
);

CREATE TABLE dw.FactSales
(
    SalesKey INT NOT NULL PRIMARY KEY,
    RowID INT NOT NULL UNIQUE,
    OrderID NVARCHAR(20) NOT NULL,

    OrderDateKey INT NOT NULL,
    ShipDateKey INT NOT NULL,

    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    GeographyKey INT NOT NULL,
    ShipModeKey INT NOT NULL,

    SalesAmount DECIMAL(18,4) NOT NULL,
    Quantity INT NOT NULL,
    DiscountRate DECIMAL(5,2) NOT NULL,
    ProfitAmount DECIMAL(18,4) NOT NULL,

    CONSTRAINT FK_FactSales_OrderDate
        FOREIGN KEY (OrderDateKey)
        REFERENCES dw.DimDate(DateKey),

    CONSTRAINT FK_FactSales_ShipDate
        FOREIGN KEY (ShipDateKey)
        REFERENCES dw.DimDate(DateKey),

    CONSTRAINT FK_FactSales_Customer
        FOREIGN KEY (CustomerKey)
        REFERENCES dw.DimCustomer(CustomerKey),

    CONSTRAINT FK_FactSales_Product
        FOREIGN KEY (ProductKey)
        REFERENCES dw.DimProduct(ProductKey),

    CONSTRAINT FK_FactSales_Geography
        FOREIGN KEY (GeographyKey)
        REFERENCES dw.DimGeography(GeographyKey),

    CONSTRAINT FK_FactSales_ShipMode
        FOREIGN KEY (ShipModeKey)
        REFERENCES dw.DimShipMode(ShipModeKey)
);

CREATE TABLE stg.SalesRaw
(
    RowID INT,
    OrderID NVARCHAR(20),
    OrderDate NVARCHAR(50),
    ShipDate NVARCHAR(50),
    ShipMode NVARCHAR(50),

    CustomerID NVARCHAR(20),
    CustomerName NVARCHAR(150),
    Segment NVARCHAR(50),

    Country NVARCHAR(100),
    City NVARCHAR(100),
    StateName NVARCHAR(100),
    PostalCode NVARCHAR(20),
    Region NVARCHAR(50),

    ProductID NVARCHAR(30),
    Category NVARCHAR(100),
    SubCategory NVARCHAR(100),
    ProductName NVARCHAR(255),

    SalesAmount DECIMAL(18,4),
    Quantity INT,
    DiscountRate DECIMAL(5,2),
    ProfitAmount DECIMAL(18,4),

    LoadedAt DATETIME2 DEFAULT GETDATE()
);