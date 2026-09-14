from pathlib import Path

import pandas as pd

from code.datasets.preprocess import REQUIRED_COLUMNS, preprocess


def test_preprocess_creates_clean_disjoint_splits(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw.csv"
    rows = []
    for index in range(30):
        rows.append(
            {
                "car_name": f"car-{index}",
                "cylinders": 4,
                "displacement": 100 + index,
                "horsepower": None if index == 3 else 80 + index,
                "weight": 2000 + index * 10,
                "acceleration": 15,
                "model_year": 70 + index % 10,
                "origin": 1 + index % 3,
                "mpg": 20 + index / 10,
            }
        )
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(raw_path, index=False)

    train_path, test_path = preprocess(raw_path, tmp_path / "processed")
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)

    assert not train_data.isna().any().any()
    assert not test_data.isna().any().any()
    assert set(train_data["car_name"]).isdisjoint(test_data["car_name"])

