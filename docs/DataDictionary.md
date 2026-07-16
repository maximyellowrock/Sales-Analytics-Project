# Data Dictionary

## FactSales

| Column | Description |
|---------|-------------|
| SalesKey | Surrogate key |
| RowID | Original row identifier |
| OrderID | Business order number |
| OrderDateKey | Order date foreign key |
| ShipDateKey | Ship date foreign key |
| CustomerKey | Customer foreign key |
| ProductKey | Product foreign key |
| GeographyKey | Geography foreign key |
| ShipModeKey | Ship mode foreign key |
| SalesAmount | Sales amount |
| Quantity | Quantity sold |
| DiscountRate | Discount percentage |
| ProfitAmount | Profit amount |

---

## DimCustomer

| Column | Description |
|---------|-------------|
| CustomerKey | Surrogate key |
| CustomerID | Business customer ID |
| CustomerName | Customer name |
| Segment | Customer segment |

---

## DimProduct

| Column | Description |
|---------|-------------|
| ProductKey | Surrogate key |
| ProductBusinessKey | Product business key |
| ProductID | Product ID |
| ProductName | Product name |
| Category | Product category |
| SubCategory | Product subcategory |

---

## DimGeography

| Column | Description |
|---------|-------------|
| GeographyKey | Surrogate key |
| Country | Country |
| Region | Sales region |
| StateName | State |
| City | City |
| PostalCode | Postal code |

---

## DimShipMode

| Column | Description |
|---------|-------------|
| ShipModeKey | Surrogate key |
| ShipMode | Shipping method |

---

## DimDate

| Column | Description |
|---------|-------------|
| DateKey | YYYYMMDD key |
| FullDate | Calendar date |
| Day | Day number |
| Month | Month number |
| MonthName | Month name |
| Quarter | Quarter |
| Year | Year |
| WeekdayName | Weekday |