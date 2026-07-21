from pathlib import Path

from file_reader import read_file


def inspect_file(file_path):
    df = read_file(file_path)

    print("=" * 60)
    print(f"File: {Path(file_path).name}")
    print("=" * 60)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f" - {column}")

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst 5 rows:")
    print(df.head())