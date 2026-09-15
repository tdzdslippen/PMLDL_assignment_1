FROM python:3.11-slim

WORKDIR /app

COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY code/deployment/app/app.py ./app.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--theme.base=light", "--theme.primaryColor=#436850", "--theme.backgroundColor=#f7fafc", "--theme.secondaryBackgroundColor=#edf4f3", "--theme.textColor=#12372a"]
