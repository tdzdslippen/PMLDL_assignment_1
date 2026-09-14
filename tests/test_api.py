from pathlib import Path

import joblib
import pandas as pd
from fastapi.testclient import TestClient

from code.deployment.api.app import app
from code.models.train import FEATURES, build_pipeline


def test_health_and_prediction(monkeypatch, tmp_path: Path) -> None:
    data = pd.DataFrame(
        [
            [4, 100, 80, 2000, 15, 70, 1],
            [6, 200, 110, 3000, 14, 75, 2],
            [8, 350, 160, 4000, 12, 80, 3],
            [4, 120, 90, 2200, 16, 82, 1],
        ],
        columns=FEATURES,
    )
    model = build_pipeline().fit(data, pd.Series([35.0, 25.0, 15.0, 32.0]))
    model_path = tmp_path / "model.joblib"
    joblib.dump(model, model_path)
    monkeypatch.setenv("MODEL_PATH", str(model_path))

    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post(
            "/predict",
            json={
                "cylinders": 4,
                "displacement": 140.0,
                "horsepower": 90.0,
                "weight": 2500.0,
                "acceleration": 15.5,
                "model_year": 80,
                "origin": 1,
            },
        )

    assert response.status_code == 200
    assert response.json()["predicted_mpg"] > 0

