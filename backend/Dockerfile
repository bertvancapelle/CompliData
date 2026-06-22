# Dockerfile — LIKARA API
FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies apart kopiëren voor layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Applicatiecode
COPY . .

# Geen root in productie
RUN useradd -m -u 1000 complidata && chown -R complidata:complidata /app
USER complidata

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
