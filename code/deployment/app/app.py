"""Streamlit frontend for the Auto MPG prediction API."""

import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://api:8000/predict")


st.set_page_config(page_title="Auto MPG Predictor", page_icon="🚗")
st.title("Fuel Consumption Prediction")
st.caption("Estimate city-cycle fuel consumption in miles per gallon.")

with st.form("prediction_form"):
    cylinders = st.number_input("Cylinders", min_value=2, max_value=16, value=4)
    displacement = st.number_input("Displacement", min_value=1.0, value=140.0)
    horsepower = st.number_input("Horsepower", min_value=1.0, value=90.0)
    weight = st.number_input("Weight (lb)", min_value=1.0, value=2500.0)
    acceleration = st.number_input("Acceleration", min_value=1.0, value=15.5)
    model_year = st.number_input("Model year", min_value=60, max_value=100, value=80)
    origin_label = st.selectbox("Origin", ["USA", "Europe", "Japan"])
    submitted = st.form_submit_button("Predict")

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
        st.success(f"Predicted fuel economy: {response.json()['predicted_mpg']:.2f} MPG")
    except (requests.RequestException, KeyError, ValueError) as error:
        st.error(f"Prediction service is unavailable: {error}")

