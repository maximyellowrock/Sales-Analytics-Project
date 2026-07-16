-- SALES ANALYTICS KPI QUERIES

-- 1. Total Sales
SELECT
    SUM(SalesAmount) AS TotalSales
FROM dw.FactSales;


-- 2. Total Profit
SELECT
    SUM(ProfitAmount) AS TotalProfit
FROM dw.FactSales;


-- 3. Profit Margin
SELECT
    SUM(ProfitAmount) * 100.0
    / NULLIF(SUM(SalesAmount), 0) AS ProfitMarginPercentage
FROM dw.FactSales;


-- 4. Total Orders
SELECT
    COUNT(DISTINCT OrderID) AS TotalOrders
FROM dw.FactSales;


-- 5. Total Customers
SELECT
    COUNT(*) AS TotalCustomers
FROM dw.DimCustomer;


-- 6. Total Products
SELECT
    COUNT(*) AS TotalProducts
FROM dw.DimProduct;


-- 7. Total Quantity Sold
SELECT
    SUM(Quantity) AS TotalQuantity
FROM dw.FactSales;


-- 8. Average Order Value
SELECT
    SUM(SalesAmount)
    / NULLIF(COUNT(DISTINCT OrderID), 0) AS AverageOrderValue
FROM dw.FactSales;


-- 9. Average Discount
SELECT
    AVG(DiscountRate) * 100.0 AS AverageDiscountPercentage
FROM dw.FactSales;


-- 10. Sales and Profit by Category
SELECT
    p.Category,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    SUM(f.ProfitAmount) * 100.0
        / NULLIF(SUM(f.SalesAmount), 0) AS ProfitMarginPercentage
FROM dw.FactSales AS f
INNER JOIN dw.DimProduct AS p
    ON f.ProductKey = p.ProductKey
GROUP BY
    p.Category
ORDER BY
    TotalSales DESC;


-- 11. Sales and Profit by SubCategory
SELECT
    p.Category,
    p.SubCategory,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit
FROM dw.FactSales AS f
INNER JOIN dw.DimProduct AS p
    ON f.ProductKey = p.ProductKey
GROUP BY
    p.Category,
    p.SubCategory
ORDER BY
    TotalSales DESC;


-- 12. Sales and Profit by Region
SELECT
    g.Region,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    COUNT(DISTINCT f.OrderID) AS TotalOrders
FROM dw.FactSales AS f
INNER JOIN dw.DimGeography AS g
    ON f.GeographyKey = g.GeographyKey
GROUP BY
    g.Region
ORDER BY
    TotalSales DESC;


-- 13. Sales by Customer Segment
SELECT
    c.Segment,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    COUNT(DISTINCT f.OrderID) AS TotalOrders
FROM dw.FactSales AS f
INNER JOIN dw.DimCustomer AS c
    ON f.CustomerKey = c.CustomerKey
GROUP BY
    c.Segment
ORDER BY
    TotalSales DESC;


-- 14. Monthly Sales Trend
SELECT
    d.YearNumber,
    d.MonthNumber,
    d.MonthName,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit
FROM dw.FactSales AS f
INNER JOIN dw.DimDate AS d
    ON f.OrderDateKey = d.DateKey
GROUP BY
    d.YearNumber,
    d.MonthNumber,
    d.MonthName
ORDER BY
    d.YearNumber,
    d.MonthNumber;


-- 15. Yearly Sales
SELECT
    d.YearNumber,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    COUNT(DISTINCT f.OrderID) AS TotalOrders
FROM dw.FactSales AS f
INNER JOIN dw.DimDate AS d
    ON f.OrderDateKey = d.DateKey
GROUP BY
    d.YearNumber
ORDER BY
    d.YearNumber;


-- 16. Top 10 Customers
SELECT TOP (10)
    c.CustomerID,
    c.CustomerName,
    c.Segment,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    COUNT(DISTINCT f.OrderID) AS TotalOrders
FROM dw.FactSales AS f
INNER JOIN dw.DimCustomer AS c
    ON f.CustomerKey = c.CustomerKey
GROUP BY
    c.CustomerID,
    c.CustomerName,
    c.Segment
ORDER BY
    TotalSales DESC;


-- 17. Top 10 Products
SELECT TOP (10)
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    SUM(f.Quantity) AS TotalQuantity
FROM dw.FactSales AS f
INNER JOIN dw.DimProduct AS p
    ON f.ProductKey = p.ProductKey
GROUP BY
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory
ORDER BY
    TotalSales DESC;


-- 18. Bottom 10 Products by Profit
SELECT TOP (10)
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit
FROM dw.FactSales AS f
INNER JOIN dw.DimProduct AS p
    ON f.ProductKey = p.ProductKey
GROUP BY
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory
ORDER BY
    TotalProfit ASC;


-- 19. Sales by Ship Mode
SELECT
    s.ShipMode,
    SUM(f.SalesAmount) AS TotalSales,
    SUM(f.ProfitAmount) AS TotalProfit,
    COUNT(DISTINCT f.OrderID) AS TotalOrders
FROM dw.FactSales AS f
INNER JOIN dw.DimShipMode AS s
    ON f.ShipModeKey = s.ShipModeKey
GROUP BY
    s.ShipMode
ORDER BY
    TotalSales DESC;


-- 20. Discount Impact
SELECT
    DiscountRate,
    SUM(SalesAmount) AS TotalSales,
    SUM(ProfitAmount) AS TotalProfit,
    COUNT(*) AS SalesLines
FROM dw.FactSales
GROUP BY
    DiscountRate
ORDER BY
    DiscountRate;


-- 21. Loss-Making Sales Lines
SELECT
    COUNT(*) AS LossMakingSalesLines,
    SUM(SalesAmount) AS LossMakingSalesAmount,
    SUM(ProfitAmount) AS TotalLoss
FROM dw.FactSales
WHERE ProfitAmount < 0;


-- 22. Orders by Year and Month
SELECT
    d.YearNumber,
    d.MonthNumber,
    d.MonthName,
    COUNT(DISTINCT f.OrderID) AS TotalOrders
FROM dw.FactSales AS f
INNER JOIN dw.DimDate AS d
    ON f.OrderDateKey = d.DateKey
GROUP BY
    d.YearNumber,
    d.MonthNumber,
    d.MonthName
ORDER BY
    d.YearNumber,
    d.MonthNumber;