# Classifier-General Documentation

This folder contains reverse-engineered documentation generated from repository evidence.

## Doc Map (Diataxis)
- Tutorial:
  - `docs/tutorials/getting-started.md`
- How-to guides:
  - `docs/how-to/run-locally.md`
  - `docs/how-to/deploy-with-docker-compose.md`
- Reference:
  - `docs/reference/configuration.md`
  - `docs/reference/api.md`
  - `docs/reference/runtime-state.md`
- Explanation:
  - `docs/explanation/architecture.md`
  - `docs/explanation/decisions.md`

## Scope
- Covered modules: classification routes, text preprocessing, extraction pipeline, remote classifier/language services, label config.
- This service has no relational database layer; runtime state is file system + in-memory labels.

## Evidence anchors
- `app/main.py`
- `app/api/router.py`
- `app/routers/*.py`
- `app/pipelines/*.py`
- `app/services/*.py`
- `app/core/*.py`
- `app/schemas/*.py`
- `docker-compose.yml`
- `Dockerfile`
- `tests/test_routes.py`
