# MTPMS backend — FastAPI + Alembic migrations at startup.
FROM python:3.12-slim

# Postgres client tools so `docker compose exec backend pg_dump ...` and the
# backup service share one image family; curl for the container healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Retries + generous timeout: a build that dies on one flaky PyPI read is a
# build the client can't reproduce on hotel wifi.
RUN pip install --no-cache-dir --retries 10 --timeout 60 -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts

RUN useradd --create-home mtpms && mkdir -p logs && chown -R mtpms /app
USER mtpms

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD curl -sf http://localhost:8000/api/health || exit 1

# ONE worker, on purpose: the rate limiters and the reminder scheduler are
# in-process. A truck stop's traffic is a rounding error for one uvicorn worker;
# scaling out means moving rate limiting to Redis/nginx first (see DEPLOY.md).
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
