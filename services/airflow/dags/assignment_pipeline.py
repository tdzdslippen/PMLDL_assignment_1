"""Airflow DAG for the complete PMLDL Assignment 1 pipeline."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PYTHON_EXECUTABLE = os.getenv("PIPELINE_PYTHON", sys.executable)
TASK_ENV = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}


with DAG(
    dag_id="pmldl_assignment_1",
    description="Clean data, train Auto MPG model, and deploy API plus UI",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "pmldl-student",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["pmldl", "assignment-1"],
) as dag:
    preprocess_data = BashOperator(
        task_id="preprocess_data",
        bash_command=f"{PYTHON_EXECUTABLE} -m code.datasets.preprocess",
        cwd=str(PROJECT_ROOT),
        env=TASK_ENV,
    )

    train_model = BashOperator(
        task_id="train_and_evaluate",
        bash_command=f"{PYTHON_EXECUTABLE} -m code.models.train",
        cwd=str(PROJECT_ROOT),
        env=TASK_ENV,
    )

    deploy_services = BashOperator(
        task_id="deploy_api_and_app",
        bash_command=(
            f"docker compose -f {PROJECT_ROOT / 'code/deployment/docker-compose.yml'} "
            "up -d --build --remove-orphans"
        ),
        env=TASK_ENV,
    )

    preprocess_data >> train_model >> deploy_services
