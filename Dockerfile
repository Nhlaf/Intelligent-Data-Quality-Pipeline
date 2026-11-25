FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=60
ENV PIP_RETRIES=3
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

ARG OFFLINE_INSTALL=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN --mount=type=bind,source=.,target=/build-context,readonly \
    if [ "$OFFLINE_INSTALL" = "true" ]; then \
        pip install --no-cache-dir \
        --no-index \
        --find-links=/build-context/wheelhouse \
        -r requirements.txt; \
    else \
        pip install --no-cache-dir \
        -r requirements.txt; \
    fi

COPY . .

RUN rm -rf /app/wheelhouse

RUN mkdir -p \
    data/raw \
    data/bronze \
    data/silver \
    data/gold \
    data/quarantine \
    logs

EXPOSE 8000 8501

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]