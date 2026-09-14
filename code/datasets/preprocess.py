"""Load, validate, clean, split, and persist Auto MPG data."""

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "auto_mpg.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_PATH = PROCESSED_DIR / "preprocessing_report.json"
TARGET = "mpg"
RANDOM_STATE = 42
TEST_SIZE = 0.2
REQUIRED_COLUMNS = [
    "car_name",
    "cylinders",
    "displacement",
    "horsepower",
    "weight",
    "acceleration",
    "model_year",
    "origin",
    TARGET,
]
NUMERIC_FEATURES = [
    "cylinders",
    "displacement",
    "horsepower",
    "weight",
    "acceleration",
    "model_year",
]


def _validate(data: pd.DataFrame) -> None:
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Raw dataset is empty")


def _iqr_bounds(data: pd.DataFrame) -> dict[str, tuple[float, float]]:
    bounds = {}
    for column in NUMERIC_FEATURES:
        first_quartile = data[column].quantile(0.25)
        third_quartile = data[column].quantile(0.75)
        iqr = third_quartile - first_quartile
        bounds[column] = (first_quartile - 1.5 * iqr, third_quartile + 1.5 * iqr)
    return bounds


def _remove_train_outliers(
    data: pd.DataFrame,
    bounds: dict[str, tuple[float, float]],
) -> pd.DataFrame:
    inlier_mask = pd.Series(True, index=data.index)
    for column, (lower, upper) in bounds.items():
        inlier_mask &= data[column].between(lower, upper)
    return data.loc[inlier_mask].copy()


def preprocess(
    raw_path: Path = RAW_DATA_PATH,
    output_dir: Path = PROCESSED_DIR,
) -> tuple[Path, Path]:
    data = pd.read_csv(raw_path, na_values=["?"])
    _validate(data)

    input_rows = len(data)
    data = data.drop_duplicates().dropna(subset=[TARGET]).copy()
    train_data, test_data = train_test_split(
        data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    medians = train_data[NUMERIC_FEATURES].median()
    train_data[NUMERIC_FEATURES] = train_data[NUMERIC_FEATURES].fillna(medians)
    test_data[NUMERIC_FEATURES] = test_data[NUMERIC_FEATURES].fillna(medians)

    bounds = _iqr_bounds(train_data)
    train_rows_before_outliers = len(train_data)
    train_data = _remove_train_outliers(train_data, bounds)

    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = output_dir / "train.csv"
    test_path = output_dir / "test.csv"
    train_data.to_csv(train_path, index=False)
    test_data.to_csv(test_path, index=False)

    report = {
        "input_rows": input_rows,
        "duplicate_rows_removed": input_rows - len(data),
        "train_rows": len(train_data),
        "test_rows": len(test_data),
        "train_outliers_removed": train_rows_before_outliers - len(train_data),
        "missing_values_after_cleaning": int(
            train_data.isna().sum().sum() + test_data.isna().sum().sum()
        ),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "imputation_medians": medians.to_dict(),
        "outlier_bounds": {
            column: {"lower": lower, "upper": upper}
            for column, (lower, upper) in bounds.items()
        },
        "outlier_policy": "IQR filtering on training rows only; test set remains unbiased",
    }
    (output_dir / REPORT_PATH.name).write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return train_path, test_path


if __name__ == "__main__":
    train_file, test_file = preprocess()
    print(f"Created {train_file} and {test_file}")

