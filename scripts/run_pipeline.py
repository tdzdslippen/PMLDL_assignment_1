"""Run data and model stages without Airflow for local verification."""

import json

from code.datasets.preprocess import preprocess
from code.models.train import train_and_evaluate


def main() -> None:
    train_path, test_path = preprocess()
    metrics = train_and_evaluate(train_path, test_path)
    print(json.dumps({"train": str(train_path), "test": str(test_path), **metrics}, indent=2))


if __name__ == "__main__":
    main()

