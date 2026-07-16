from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "Sales.xlsx"

SERVER_NAME = r"MAXIM\SQLEXPRESS"
DATABASE_NAME = "SalesAnalyticsDB"


def extract_sales_data(file_path: Path) -> pd.DataFrame:
    """Extract raw sales data from the Excel source."""
    return pd.read_excel(
        file_path,
        sheet_name="Sales",
        engine="openpyxl",
    )


def rename_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Rename source columns to match the SQL staging table."""

    column_mapping = {
        "Row ID": "RowID",
        "Order ID": "OrderID",
        "Order Date": "OrderDate",
        "Ship Date": "ShipDate",
        "Ship Mode": "ShipMode",
        "Customer ID": "CustomerID",
        "Customer Name": "CustomerName",
        "Segment": "Segment",
        "Country": "Country",
        "City": "City",
        "State": "StateName",
        "Postal Code": "PostalCode",
        "Region": "Region",
        "Product ID": "ProductID",
        "Category": "Category",
        "Sub-Category": "SubCategory",
        "Product Name": "ProductName",
        "Sales": "SalesAmount",
        "Quantity": "Quantity",
        "Discount": "DiscountRate",
        "Profit": "ProfitAmount",
    }

    return dataframe.rename(columns=column_mapping)


def create_sql_engine():
    """Create a Windows-authenticated SQL Server connection."""

    connection_string = quote_plus(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={connection_string}"
    )


def load_to_staging(dataframe: pd.DataFrame, engine) -> None:
    """Load the raw sales data into the SQL staging table."""

    dataframe.to_sql(
        name="SalesRaw",
        schema="stg",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
    )


def main() -> None:
    sales_data = extract_sales_data(SOURCE_FILE)
    sales_data = rename_columns(sales_data)

    engine = create_sql_engine()
    load_to_staging(sales_data, engine)

    print(f"{len(sales_data):,} rows loaded into stg.SalesRaw.")


if __name__ == "__main__":
    main()