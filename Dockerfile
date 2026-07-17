FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY adapters.py tests.json runner.py test_result.py .
CMD ["python", "runner.py"]