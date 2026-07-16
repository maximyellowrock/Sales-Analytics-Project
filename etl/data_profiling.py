from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "Sales.xlsx"


def load_sales_data(file_path: Path) -> pd.DataFrame:
    """Load the raw sales worksheet from Excel."""
    return pd.read_excel(file_path, sheet_name="Sales")


def profile_dataframe(dataframe: pd.DataFrame) -> None:
    """Print basic information about the raw dataset."""
    print("\nDATASET SHAPE")
    print(f"Rows: {dataframe.shape[0]:,}")
    print(f"Columns: {dataframe.shape[1]}")

    print("\nCOLUMN NAMES")
    for column in dataframe.columns:
        print(f"- {column}")

    print("\nDATA TYPES")
    print(dataframe.dtypes)

    print("\nMISSING VALUES")
    print(dataframe.isna().sum())

    print("\nDUPLICATE ROWS")
    print(dataframe.duplicated().sum())

    print("\nFIRST FIVE ROWS")
    print(dataframe.head())


def main() -> None:
    sales_data = load_sales_data(SOURCE_FILE)
    profile_dataframe(sales_data)


if __name__ == "__main__":
    main()