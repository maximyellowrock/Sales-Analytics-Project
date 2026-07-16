from pathlib import Path

import pandas as pd
from sqlalchemy import text

from load_staging import create_sql_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def read_csv_files() -> dict[str, pd.DataFrame]:
    """Read star schema CSV files."""

    dim_customer = pd.read_csv(
        PROCESSED_DATA_DIR / "dim_customer.csv"
    )

    dim_product = pd.read_csv(
        PROCESSED_DATA_DIR / "dim_product.csv"
    )

    dim_geography = pd.read_csv(
        PROCESSED_DATA_DIR / "dim_geography.csv",
        dtype={"PostalCode": "string"},
    )

    dim_ship_mode = pd.read_csv(
        PROCESSED_DATA_DIR / "dim_ship_mode.csv"
    )

    dim_date = pd.read_csv(
        PROCESSED_DATA_DIR / "dim_date.csv"
    )

    fact_sales = pd.read_csv(
        PROCESSED_DATA_DIR / "fact_sales.csv"
    )

    return {
        "DimCustomer": dim_customer,
        "DimProduct": dim_product,
        "DimGeography": dim_geography,
        "DimShipMode": dim_ship_mode,
        "DimDate": dim_date,
        "FactSales": fact_sales,
    }


def prepare_dim_date(
    dim_date: pd.DataFrame,
) -> pd.DataFrame:
    """Rename Date Dimension columns to match SQL Server."""

    return dim_date.rename(
        columns={
            "Day": "DayNumber",
            "Month": "MonthNumber",
            "Quarter": "QuarterNumber",
            "Year": "YearNumber",
        }
    )


def clear_warehouse_tables(engine) -> None:
    """Delete existing warehouse data in foreign-key-safe order."""

    delete_statements = [
        "DELETE FROM dw.FactSales;",
        "DELETE FROM dw.DimCustomer;",
        "DELETE FROM dw.DimProduct;",
        "DELETE FROM dw.DimGeography;",
        "DELETE FROM dw.DimShipMode;",
        "DELETE FROM dw.DimDate;",
    ]

    with engine.begin() as connection:
        for statement in delete_statements:
            connection.execute(text(statement))


def load_dataframe(
    dataframe: pd.DataFrame,
    table_name: str,
    engine,
) -> None:
    """Load one DataFrame into a SQL Server warehouse table."""

    dataframe.to_sql(
        name=table_name,
        schema="dw",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
    )

    print(
        f"{len(dataframe):,} rows loaded into "
        f"dw.{table_name}."
    )


def main() -> None:
    engine = create_sql_engine()
    warehouse_data = read_csv_files()

    warehouse_data["DimDate"] = prepare_dim_date(
        warehouse_data["DimDate"]
    )

    clear_warehouse_tables(engine)

    load_order = [
        "DimCustomer",
        "DimProduct",
        "DimGeography",
        "DimShipMode",
        "DimDate",
        "FactSales",
    ]

    for table_name in load_order:
        load_dataframe(
            warehouse_data[table_name],
            table_name,
            engine,
        )

    print("\nWarehouse load completed successfully.")


if __name__ == "__main__":
    main()