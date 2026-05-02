# Architecture Explanation

## 1. Executive summary
`classifier-general` is a single FastAPI service that classifies text and files with local extraction/preprocessing, a local Hugging Face zero-shot NLI model, and local language detection.

Evidence:
- `app/main.py`
- `app/routers/classification.py`
- `app/services/classifier_service.py`
- `app/services/language_service.py`

## 2. Purpose and scope
### What exists
- Contract-compatible endpoints for classify/language/transform flows.
- Pipeline split into preprocess, extraction, classification orchestration.
- Configurable runtime through environment variables.

Evidence:
- `app/routers/classification.py`
- `app/pipelines/classification_pipeline.py`
- `app/core/config.py`

### How it works
- Router accepts JSON or multipart requests.
- Files are written to disk (`static/uploads`).
- Extraction service parses document/image/text into plain text.
- Text preprocessing enforces minimum quality.
- Pipeline calls language and classifier services.

Evidence:
- `app/services/file_storage_service.py`
- `app/services/extraction_service.py`
- `app/pipelines/text_pipeline.py`
- `app/pipelines/classification_pipeline.py`

### Why designed this way (inferred)
- Maintain old API contract while introducing modular services and safer config handling.

## 3. C4-style views
### Context view
Actors/systems:
- API client sending text/files.
- Hugging Face model hub (model download/auth when needed).
- Local filesystem for uploaded files.

Evidence:
- `app/core/config.py`
- `app/services/classifier_service.py`
- `app/services/language_service.py`

### Container view
- One container/service (`classifier-api`) with FastAPI + OCR binary.

Evidence:
- `docker-compose.yml`
- `Dockerfile`

### Component view
- API routing: `app/routers/*`
- Orchestration pipelines: `app/pipelines/*`
- Integration services: `app/services/classifier_service.py`, `app/services/language_service.py`
- Extraction + storage services: `app/services/extraction_service.py`, `app/services/file_storage_service.py`
- Config/exceptions/schemas: `app/core/*`, `app/schemas/*`

### Code-level workflow: file classification
1. `POST /classify` receives file.
2. File saved to upload directory.
3. Text extracted by extension-specific handlers.
   - For `/classify`, PDF extraction is first-page only.
4. Text preprocessed (regex cleanup + min words).
5. Local language detector called.
6. Zero-shot NLI classifier scores runtime labels and selects top label.
7. Response returns `{label, language}` plus `type=not english` when applicable.

Evidence:
- `app/routers/classification.py`
- `app/services/file_storage_service.py`
- `app/services/extraction_service.py`
- `app/pipelines/text_pipeline.py`
- `app/pipelines/classification_pipeline.py`

## 4. Cross-cutting concerns
### Validation and error mapping
- Input schemas use strict `extra=forbid`.
- Error mapping explicitly separates validation/extraction (400) from classifier/language inference failures (502).

Evidence:
- `app/schemas/classification.py`
- `app/routers/classification.py`

### Configuration and secrets
- Runtime config sourced from env.
- HF token optional and no hardcoded secret in current service code.

Evidence:
- `app/core/config.py`
- `app/services/classifier_service.py`

### Concurrency and mutable state
- Labels guarded by thread lock (`LabelConfig._lock`).
- State is still process-local; multi-instance deployments can diverge.

Evidence:
- `app/models/label_config.py`
- `app/services/label_service.py`

### Testing strategy
- Route contract tests monkeypatch pipeline methods for deterministic tests.
- Tests validate response shape and key endpoint behavior, not remote network calls.

Evidence:
- `tests/test_routes.py`

## 5. Risks, gaps, and technical debt
- Local model initialization can fail if model/token/resources are invalid.
- No upload retention/cleanup process.
- Readiness check does not probe external AI services, only local label readiness.
- No authentication/authorization layer on API endpoints.

Evidence:
- `app/services/language_service.py`
- `app/services/classifier_service.py`
- `app/routers/health.py`
- `app/routers/classification.py`

## 6. Unknown or inferred
- Unknown: expected SLA and acceptable latency.
- Unknown: intended persistence/retention policy for uploaded files.
- Inferred: service is optimized for local/dev contract compatibility and integration testing.
