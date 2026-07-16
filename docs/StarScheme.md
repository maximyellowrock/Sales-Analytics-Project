# Star Schema

## Fact Table

FactSales

## Dimension Tables

- DimCustomer
- DimProduct
- DimDate
- DimGeography
- DimShipMode

## Relationships

FactSales links to every dimension using surrogate keys.

```
           DimCustomer
                |
DimDate ---- FactSales ---- DimProduct
                |
         DimGeography
                |
          DimShipMode
```

The Star Schema improves query performance and simplifies reporting in Power BI.