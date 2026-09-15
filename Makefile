PYTHON ?= .venv/bin/python
AIRFLOW_PYTHON ?= .airflow-venv/bin/python
AIRFLOW_API_PORT ?= 18000
AIRFLOW_APP_PORT ?= 18501

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
	PATH=$(CURDIR)/.airflow-venv/bin:$(PATH) PYTHONPATH=$(CURDIR)/scripts/airflow_compat AIRFLOW__CORE__LOAD_EXAMPLES=False AIRFLOW_HOME=$(CURDIR)/services/airflow PIPELINE_PYTHON=$(CURDIR)/$(PYTHON) API_PORT=$(AIRFLOW_API_PORT) APP_PORT=$(AIRFLOW_APP_PORT) $(AIRFLOW_PYTHON) -m airflow standalone
