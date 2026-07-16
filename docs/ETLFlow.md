# ETL Flow

## Extract

- Read raw sales data from Excel.
- Load raw data into SQL Server staging table.

## Transform

- Clean text values.
- Standardize dates.
- Validate data quality.
- Create ProductBusinessKey.
- Remove duplicates.
- Build dimension tables.
- Build fact table.

## Load

Load the following tables into the SQL Server Data Warehouse:

- DimCustomer
- DimProduct
- DimGeography
- DimShipMode
- DimDate
- FactSales