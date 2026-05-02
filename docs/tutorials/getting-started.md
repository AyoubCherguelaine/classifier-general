# Getting Started

This tutorial runs the classifier API and validates endpoint contracts.

## Prerequisites
- Docker and Docker Compose
- Internet access for initial Hugging Face model download (unless model is already cached)

Evidence:
- `docker-compose.yml`
- `app/services/classifier_service.py`
- `app/services/language_service.py`

## 1. Prepare environment
```bash
cd classifier-general
cp .env.example .env
```

Evidence:
- `.env.example`
- `app/core/config.py`

## 2. Start API in Docker
```bash
docker compose up --build
```

Service:
- `classifier-api` exposed on `4002`

Evidence:
- `docker-compose.yml`

## 3. Check health
```bash
curl -s http://localhost:4002/health/liveness
curl -s http://localhost:4002/health/readiness
```

Expected:
- `{"status":"ok"}`
- `{"status":"ready","labels_count":<n>}`

Evidence:
- `app/routers/health.py`

## 4. Call text classification
```bash
curl -s -X POST http://localhost:4002/api/classifier \
  -H 'content-type: application/json' \
  -d '{"text":"This is a long enough sentence for classification."}'
```

Evidence:
- `app/routers/classification.py`
- `app/pipelines/classification_pipeline.py`

## 5. Update labels and verify
```bash
curl -s -X POST http://localhost:4002/configlabel \
  -H 'content-type: application/json' \
  -d '{"labels":["tech","health","legal"]}'

curl -s http://localhost:4002/labels
```

Evidence:
- `app/services/label_service.py`
- `app/models/label_config.py`

## 6. Run route contract tests
```bash
docker build -t classifier-general-refactor .
docker run --rm -w /app -e PYTHONPATH=/app classifier-general-refactor pytest -q
```

Evidence:
- `tests/test_routes.py`
