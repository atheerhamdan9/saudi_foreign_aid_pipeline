FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e . \
    && python -m pip install --no-cache-dir \
       "dbt-core>=1.12,<1.13" \
       "dbt-duckdb>=1.11,<1.12"

ENTRYPOINT ["python", "-m", "pipeline.cli"]
