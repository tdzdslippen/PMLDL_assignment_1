"""FastAPI model-serving application."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field


DEFAULT_MODEL_PATH = Path("/app/models/model.joblib")


class PredictionRequest(BaseModel):
    cylinders: int = Field(ge=2, le=16)
    displacement: float = Field(gt=0, le=1000)
    horsepower: float = Field(gt=0, le=1000)
    weight: float = Field(gt=0, le=10000)
    acceleration: float = Field(gt=0, le=100)
    model_year: int = Field(ge=60, le=100)
    origin: int = Field(ge=1, le=3)


class PredictionResponse(BaseModel):
    predicted_mpg: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
    if not model_path.exists():
        raise RuntimeError(f"Model artifact not found: {model_path}")
    app.state.model = joblib.load(model_path)
    yield


app = FastAPI(
    title="Auto MPG Prediction API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    if not hasattr(request.app.state, "model"):
        raise HTTPException(status_code=503, detail="Model is not loaded")
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    feature_frame = pd.DataFrame([payload.model_dump()])
    prediction = request.app.state.model.predict(feature_frame)[0]
    return PredictionResponse(predicted_mpg=round(float(prediction), 2))

