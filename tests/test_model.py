from pathlib import Path

import joblib
import pandas as pd

from code.models.train import FEATURES, build_pipeline


def test_packaged_pipeline_predicts_after_reload(tmp_path: Path) -> None:
    data = pd.DataFrame(
        [
            [4, 100, 80, 2000, 15, 70, 1],
            [6, 200, 110, 3000, 14, 75, 2],
            [8, 350, 160, 4000, 12, 80, 3],
            [4, 120, 90, 2200, 16, 82, 1],
        ],
        columns=FEATURES,
    )
    target = pd.Series([35.0, 25.0, 15.0, 32.0])
    pipeline = build_pipeline().fit(data, target)
    model_path = tmp_path / "model.joblib"
    joblib.dump(pipeline, model_path)

    prediction = joblib.load(model_path).predict(data.iloc[[0]])

    assert prediction.shape == (1,)
    assert prediction[0] > 0

