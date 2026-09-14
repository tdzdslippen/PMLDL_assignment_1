"""Train, evaluate, package, and locally track an Auto MPG model."""

import json
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
TARGET = "mpg"
FEATURES = [
    "cylinders",
    "displacement",
    "horsepower",
    "weight",
    "acceleration",
    "model_year",
    "origin",
]
NUMERIC_FEATURES = [
    "cylinders",
    "displacement",
    "horsepower",
    "weight",
    "acceleration",
    "model_year",
]
CATEGORICAL_FEATURES = ["origin"]
RANDOM_STATE = 42


def build_pipeline() -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    model = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    return Pipeline(steps=[("preprocessing", preprocessing), ("model", model)])


def train_and_evaluate(
    train_path: Path = PROCESSED_DIR / "train.csv",
    test_path: Path = PROCESSED_DIR / "test.csv",
    model_path: Path = MODEL_PATH,
    metrics_path: Path = METRICS_PATH,
) -> dict[str, float]:
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)
    pipeline = build_pipeline()
    pipeline.fit(train_data[FEATURES], train_data[TARGET])

    predictions = pipeline.predict(test_data[FEATURES])
    metrics = {
        "mae": float(mean_absolute_error(test_data[TARGET], predictions)),
        "rmse": float(mean_squared_error(test_data[TARGET], predictions) ** 0.5),
        "r2": float(r2_score(test_data[TARGET], predictions)),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    tracking_database = PROJECT_ROOT / "mlflow.db"
    mlflow.set_tracking_uri(f"sqlite:///{tracking_database}")
    mlflow.set_experiment("pmldl-assignment-1-auto-mpg")
    with mlflow.start_run():
        mlflow.log_params(
            {
                "model": "RandomForestRegressor",
                "n_estimators": 200,
                "min_samples_leaf": 2,
                "random_state": RANDOM_STATE,
                "train_rows": len(train_data),
                "test_rows": len(test_data),
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(metrics_path)
        mlflow.log_artifact(model_path, artifact_path="model")

    return metrics


if __name__ == "__main__":
    print(json.dumps(train_and_evaluate(), indent=2))
