from datetime import datetime
from pathlib import Path
import re

import pandas as pd

from load_staging import create_sql_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DATA_DIR / "sales_cleaned.csv"


def extract_staging_data() -> pd.DataFrame:
    """Extract raw sales data from the SQL Server staging table."""

    engine = create_sql_engine()

    query = """
        SELECT *
        FROM stg.SalesRaw;
    """

    return pd.read_sql(query, con=engine)


def parse_mixed_date(value) -> pd.Timestamp:
    """Convert mixed source date formats into a standard date."""

    if pd.isna(value):
        return pd.NaT

    date_text = str(value).strip()
    iso_pattern = r"^\d{4}-\d{2}-\d{2}"

    if re.match(iso_pattern, date_text):
        parsed_date = datetime.strptime(
            date_text[:10],
            "%Y-%m-%d",
        )

        return pd.Timestamp(
            year=parsed_date.year,
            month=parsed_date.day,
            day=parsed_date.month,
        )

    return pd.to_datetime(
        date_text,
        format="%m/%d/%Y",
        errors="coerce",
    )


def transform_sales_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the staging sales data."""

    cleaned_data = dataframe.copy()

    cleaned_data["OrderDate"] = cleaned_data["OrderDate"].apply(
        parse_mixed_date
    )

    cleaned_data["ShipDate"] = cleaned_data["ShipDate"].apply(
        parse_mixed_date
    )

    cleaned_data["PostalCode"] = (
        cleaned_data["PostalCode"]
        .astype("string")
        .str.strip()
        .str.zfill(5)
    )

    text_columns = [
        "OrderID",
        "ShipMode",
        "CustomerID",
        "CustomerName",
        "Segment",
        "Country",
        "City",
        "StateName",
        "Region",
        "ProductID",
        "Category",
        "SubCategory",
        "ProductName",
    ]

    for column in text_columns:
        cleaned_data[column] = (
            cleaned_data[column]
            .astype("string")
            .str.strip()
        )

    cleaned_data["ProductBusinessKey"] = (
        cleaned_data["ProductID"]
        + "|"
        + cleaned_data["ProductName"]
    )

    return cleaned_data


def validate_sales_data(dataframe: pd.DataFrame) -> None:
    """Run basic data-quality checks after transformation."""

    invalid_order_dates = dataframe["OrderDate"].isna().sum()
    invalid_ship_dates = dataframe["ShipDate"].isna().sum()

    invalid_shipping_rows = (
        dataframe["ShipDate"] < dataframe["OrderDate"]
    ).sum()

    duplicate_row_ids = dataframe["RowID"].duplicated().sum()

    print("\nDATA QUALITY RESULTS")
    print(f"Rows: {len(dataframe):,}")
    print(f"Invalid Order Dates: {invalid_order_dates}")
    print(f"Invalid Ship Dates: {invalid_ship_dates}")
    print(f"Ship Date Before Order Date: {invalid_shipping_rows}")
    print(f"Duplicate Row IDs: {duplicate_row_ids}")


def save_processed_data(
    dataframe: pd.DataFrame,
    output_file: Path,
) -> None:
    """Save the cleaned sales data as a CSV file."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        output_file,
        index=False,
        date_format="%Y-%m-%d",
    )


def create_dim_customer(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create the Customer Dimension."""

    dim_customer = (
        dataframe[
            [
                "CustomerID",
                "CustomerName",
                "Segment",
            ]
        ]
        .drop_duplicates()
        .sort_values("CustomerID")
        .reset_index(drop=True)
    )

    dim_customer.insert(
        0,
        "CustomerKey",
        range(1, len(dim_customer) + 1),
    )

    return dim_customer


def create_dim_product(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create the Product Dimension."""

    dim_product = (
        dataframe[
            [
                "ProductBusinessKey",
                "ProductID",
                "ProductName",
                "Category",
                "SubCategory",
            ]
        ]
        .drop_duplicates(
            subset=["ProductBusinessKey"]
        )
        .sort_values(
            [
                "ProductID",
                "ProductName",
            ]
        )
        .reset_index(drop=True)
    )

    dim_product.insert(
        0,
        "ProductKey",
        range(1, len(dim_product) + 1),
    )

    return dim_product


def create_dim_geography(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create the Geography Dimension."""

    geography_columns = [
        "Country",
        "Region",
        "StateName",
        "City",
        "PostalCode",
    ]

    dim_geography = (
        dataframe[geography_columns]
        .drop_duplicates()
        .sort_values(geography_columns)
        .reset_index(drop=True)
    )

    dim_geography.insert(
        0,
        "GeographyKey",
        range(1, len(dim_geography) + 1),
    )

    return dim_geography


def create_dim_ship_mode(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create the Ship Mode Dimension."""

    dim_ship_mode = (
        dataframe[["ShipMode"]]
        .drop_duplicates()
        .sort_values("ShipMode")
        .reset_index(drop=True)
    )

    dim_ship_mode.insert(
        0,
        "ShipModeKey",
        range(1, len(dim_ship_mode) + 1),
    )

    return dim_ship_mode


def create_dim_date(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create the Date Dimension."""

    start_date = min(
        dataframe["OrderDate"].min(),
        dataframe["ShipDate"].min(),
    )

    end_date = max(
        dataframe["OrderDate"].max(),
        dataframe["ShipDate"].max(),
    )

    date_range = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    dim_date = pd.DataFrame(
        {
            "FullDate": date_range,
        }
    )

    dim_date["DateKey"] = (
        dim_date["FullDate"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dim_date["Day"] = dim_date["FullDate"].dt.day
    dim_date["Month"] = dim_date["FullDate"].dt.month
    dim_date["MonthName"] = (
        dim_date["FullDate"].dt.month_name()
    )
    dim_date["Quarter"] = (
        dim_date["FullDate"].dt.quarter
    )
    dim_date["Year"] = dim_date["FullDate"].dt.year
    dim_date["WeekdayName"] = (
        dim_date["FullDate"].dt.day_name()
    )

    return dim_date[
        [
            "DateKey",
            "FullDate",
            "Day",
            "Month",
            "MonthName",
            "Quarter",
            "Year",
            "WeekdayName",
        ]
    ]


def create_fact_sales(
    dataframe: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_geography: pd.DataFrame,
    dim_ship_mode: pd.DataFrame,
) -> pd.DataFrame:
    """Create the Sales Fact table."""

    fact_sales = dataframe.copy()

    fact_sales["OrderDateKey"] = (
        fact_sales["OrderDate"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact_sales["ShipDateKey"] = (
        fact_sales["ShipDate"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact_sales = fact_sales.merge(
        dim_customer[
            [
                "CustomerKey",
                "CustomerID",
            ]
        ],
        on="CustomerID",
        how="left",
    )

    fact_sales = fact_sales.merge(
        dim_product[
            [
                "ProductKey",
                "ProductBusinessKey",
            ]
        ],
        on="ProductBusinessKey",
        how="left",
    )

    geography_columns = [
        "Country",
        "Region",
        "StateName",
        "City",
        "PostalCode",
    ]

    fact_sales = fact_sales.merge(
        dim_geography[
            [
                "GeographyKey",
                *geography_columns,
            ]
        ],
        on=geography_columns,
        how="left",
    )

    fact_sales = fact_sales.merge(
        dim_ship_mode[
            [
                "ShipModeKey",
                "ShipMode",
            ]
        ],
        on="ShipMode",
        how="left",
    )

    fact_sales.insert(
        0,
        "SalesKey",
        range(1, len(fact_sales) + 1),
    )

    fact_columns = [
        "SalesKey",
        "RowID",
        "OrderID",
        "OrderDateKey",
        "ShipDateKey",
        "CustomerKey",
        "ProductKey",
        "GeographyKey",
        "ShipModeKey",
        "SalesAmount",
        "Quantity",
        "DiscountRate",
        "ProfitAmount",
    ]

    return fact_sales[fact_columns]


def find_product_conflicts(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Find Product IDs associated with multiple product names."""

    return (
        dataframe
        .groupby("ProductID")
        .agg(
            ProductNameCount=(
                "ProductName",
                "nunique",
            ),
            CategoryCount=(
                "Category",
                "nunique",
            ),
            SubCategoryCount=(
                "SubCategory",
                "nunique",
            ),
        )
        .query(
            "ProductNameCount > 1 "
            "or CategoryCount > 1 "
            "or SubCategoryCount > 1"
        )
    )


def save_star_schema_files(
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_geography: pd.DataFrame,
    dim_ship_mode: pd.DataFrame,
    dim_date: pd.DataFrame,
    fact_sales: pd.DataFrame,
) -> None:
    """Save dimension and fact tables as CSV files."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dim_customer.to_csv(
        PROCESSED_DATA_DIR / "dim_customer.csv",
        index=False,
    )

    dim_product.to_csv(
        PROCESSED_DATA_DIR / "dim_product.csv",
        index=False,
    )

    dim_geography.to_csv(
        PROCESSED_DATA_DIR / "dim_geography.csv",
        index=False,
    )

    dim_ship_mode.to_csv(
        PROCESSED_DATA_DIR / "dim_ship_mode.csv",
        index=False,
    )

    dim_date.to_csv(
        PROCESSED_DATA_DIR / "dim_date.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    fact_sales.to_csv(
        PROCESSED_DATA_DIR / "fact_sales.csv",
        index=False,
    )


def main() -> None:
    print(f"Running file: {__file__}")

    sales_data = extract_staging_data()
    cleaned_sales_data = transform_sales_data(
        sales_data
    )

    validate_sales_data(cleaned_sales_data)

    save_processed_data(
        cleaned_sales_data,
        OUTPUT_FILE,
    )

    dim_customer = create_dim_customer(
        cleaned_sales_data
    )

    dim_product = create_dim_product(
        cleaned_sales_data
    )

    dim_geography = create_dim_geography(
        cleaned_sales_data
    )

    dim_ship_mode = create_dim_ship_mode(
        cleaned_sales_data
    )

    dim_date = create_dim_date(
        cleaned_sales_data
    )

    fact_sales = create_fact_sales(
        cleaned_sales_data,
        dim_customer,
        dim_product,
        dim_geography,
        dim_ship_mode,
    )

    product_conflicts = find_product_conflicts(
        cleaned_sales_data
    )

    save_star_schema_files(
        dim_customer,
        dim_product,
        dim_geography,
        dim_ship_mode,
        dim_date,
        fact_sales,
    )

    print("\nPRODUCT ID CONFLICTS")
    print(product_conflicts)
    print(
        f"Conflicting Product IDs: "
        f"{len(product_conflicts)}"
    )

    print("\nDIM CUSTOMER")
    print(dim_customer.head())
    print(f"Rows: {len(dim_customer)}")

    print("\nDIM PRODUCT")
    print(dim_product.head())
    print(f"Rows: {len(dim_product)}")

    print("\nDIM GEOGRAPHY")
    print(dim_geography.head())
    print(f"Rows: {len(dim_geography)}")

    print("\nDIM SHIP MODE")
    print(dim_ship_mode)
    print(f"Rows: {len(dim_ship_mode)}")

    print("\nDIM DATE")
    print(dim_date.head())
    print(dim_date.tail())
    print(f"Rows: {len(dim_date)}")

    print("\nFACT SALES")
    print(fact_sales.head())
    print(f"Rows: {len(fact_sales)}")

    foreign_key_columns = [
        "CustomerKey",
        "ProductKey",
        "GeographyKey",
        "ShipModeKey",
    ]

    print("\nNULL FOREIGN KEYS")
    print(
        fact_sales[
            foreign_key_columns
        ].isna().sum()
    )

    print(
        "\nStar schema CSV files "
        "created successfully."
    )

    print(
        f"Cleaned data saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()