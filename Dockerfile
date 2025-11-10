FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirement.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY . .

RUN mkdir -p logs plugins/notion_autorun/db && \
    adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["python", "server.py"]
CMD ["-E", "local"]

