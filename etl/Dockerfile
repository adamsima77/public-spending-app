FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY pyproject.toml .

COPY src/ ./src

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN useradd --create-home --uid 1000 appuser && \
    mkdir -p /app/data /app/download /app/logs /app/state && \
    chown -R appuser:appuser /app

USER appuser

CMD ["python", "src/main.py"]