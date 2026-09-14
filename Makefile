PYTHON ?= .venv/bin/python
AIRFLOW_PYTHON ?= .airflow-venv/bin/python

.PHONY: download pipeline test deploy stop mlflow-ui airflow-init airflow

download:
	PYTHONPATH=. $(PYTHON) -m code.datasets.download_data

pipeline:
	PYTHONPATH=. $(PYTHON) scripts/run_pipeline.py

test:
	PYTHONPATH=. $(PYTHON) -m pytest -q

deploy:
	docker compose -f code/deployment/docker-compose.yml up -d --build

stop:
	docker compose -f code/deployment/docker-compose.yml down

mlflow-ui:
	$(PYTHON) -m mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

airflow-init:
	AIRFLOW_HOME=$(CURDIR)/services/airflow $(AIRFLOW_PYTHON) -m airflow db migrate
	AIRFLOW_HOME=$(CURDIR)/services/airflow $(AIRFLOW_PYTHON) -m airflow users create --username admin --password admin --firstname PMLDL --lastname Student --role Admin --email student@example.com

airflow:
	AIRFLOW_HOME=$(CURDIR)/services/airflow PIPELINE_PYTHON=$(CURDIR)/$(PYTHON) $(AIRFLOW_PYTHON) -m airflow standalone
