# Architecture Decisions (ADR-style)

## ADR-001: Use modular FastAPI layout for classifier backend
- Status: Accepted
- Type: Explicit
- Evidence:
  - `app/main.py`
  - `app/api/router.py`
  - `app/routers/`
  - `app/services/`
  - `app/pipelines/`
- Rationale:
  - Clear separation between transport, orchestration, and integrations.

## ADR-002: Preserve endpoint contracts from prior service behavior
- Status: Accepted
- Type: Explicit
- Evidence:
  - `app/routers/classification.py`
  - `tests/test_routes.py`
- Rationale:
  - Keep clients functional while refactoring internals.

## ADR-003: Use local Hugging Face zero-shot NLI model for classification
- Status: Accepted
- Type: Explicit
- Evidence:
  - `app/core/config.py`
  - `app/services/classifier_service.py`
- Rationale:
  - Perform true runtime-label zero-shot classification with local inference control.

## ADR-004: Use local `langdetect` library for language detection
- Status: Accepted
- Type: Explicit
- Evidence:
  - `app/services/language_service.py`
- Rationale:
  - Remove external dependency and keep language inference local.

## ADR-005: Keep labels in in-memory mutable config
- Status: Accepted (current), Needs review
- Type: Explicit
- Evidence:
  - `app/models/label_config.py`
  - `app/services/label_service.py`
  - `app/routers/classification.py` (`/configlabel`, `/labels`)
- Rationale:
  - Simple runtime tuning without DB migration.
- Tradeoff:
  - No persistence across restarts, no cross-instance consistency.

## ADR-006: Store uploaded files on local filesystem under static mount
- Status: Accepted
- Type: Explicit
- Evidence:
  - `app/services/file_storage_service.py`
  - `app/main.py`
  - `docker-compose.yml`
- Rationale:
  - Enables document/image extraction workflow with minimal infrastructure.

## ADR-007: Map errors into contract-friendly HTTP statuses
- Status: Accepted
- Type: Explicit
- Evidence:
  - `app/routers/classification.py`
  - `app/core/exceptions.py`
- Rationale:
  - Differentiate local validation issues (`400`) from inference failures (`502`).

## ADR-008: No built-in auth layer for this API
- Status: Accepted (current), Needs review
- Type: Inferred
- Evidence:
  - `app/routers/classification.py`
  - absence of auth dependencies/middleware in `app/main.py`
- Rationale:
  - likely positioned as internal or early-stage service.
