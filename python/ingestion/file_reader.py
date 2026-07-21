from pathlib import Path

import pandas as pd


def read_file(file_path: Path) -> pd.DataFrame:
    extension = file_path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    if extension in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    raise ValueError(f"Unsupported file type: {extension}")