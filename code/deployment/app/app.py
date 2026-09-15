"""Streamlit frontend for the Auto MPG prediction API."""

import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://api:8000/predict")


st.set_page_config(page_title="Auto MPG Predictor", page_icon="🚗")
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(145deg, #f7fafc 0%, #edf4f3 100%);
            color: #12372a;
        }
        .hero {
            padding: 1.8rem 2rem;
            margin-bottom: 1.5rem;
            color: white;
            border-radius: 1.25rem;
            background: linear-gradient(120deg, #12372a 0%, #436850 100%);
            box-shadow: 0 12px 32px rgba(18, 55, 42, 0.18);
        }
        .hero h1 {
            margin: 0 0 0.35rem;
            font-size: 2.25rem;
        }
        .hero p {
            margin: 0;
            color: #dcebe3;
        }
        div[data-testid="stForm"] {
            padding: 1.5rem;
            border: 1px solid #dce7e1;
            border-radius: 1.1rem;
            background: rgba(255, 255, 255, 0.88);
            box-shadow: 0 8px 24px rgba(18, 55, 42, 0.08);
        }
        div[data-testid="stForm"] label,
        div[data-testid="stMetric"] {
            color: #12372a;
        }
        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            border: 0;
            color: white;
            background: #436850;
        }
    </style>
    <div class="hero">
        <h1>🚗 Auto MPG Predictor</h1>
        <p>Estimate a car's city-cycle fuel economy from its specifications.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("prediction_form"):
    st.subheader("Vehicle specifications")
    left_column, right_column = st.columns(2)

    with left_column:
        cylinders = st.number_input("Cylinders", min_value=2, max_value=16, value=4)
        horsepower = st.number_input(
            "Horsepower", min_value=1.0, max_value=1000.0, value=90.0
        )
        acceleration = st.number_input(
            "Acceleration", min_value=1.0, max_value=100.0, value=15.5
        )

    with right_column:
        displacement = st.number_input(
            "Displacement", min_value=1.0, max_value=1000.0, value=140.0
        )
        weight = st.number_input(
            "Weight (lb)", min_value=1.0, max_value=10000.0, value=2500.0
        )
        model_year = st.number_input("Model year", min_value=60, max_value=100, value=80)

    origin_label = st.selectbox("Origin", ["USA", "Europe", "Japan"])
    submitted = st.form_submit_button("Calculate fuel economy")

if submitted:
    payload = {
        "cylinders": cylinders,
        "displacement": displacement,
        "horsepower": horsepower,
        "weight": weight,
        "acceleration": acceleration,
        "model_year": model_year,
        "origin": {"USA": 1, "Europe": 2, "Japan": 3}[origin_label],
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        predicted_mpg = response.json()["predicted_mpg"]
        st.success("Prediction completed")
        st.metric("Estimated fuel economy", f"{predicted_mpg:.2f} MPG")
    except (requests.RequestException, KeyError, ValueError) as error:
        st.error(f"Prediction service is unavailable: {error}")
