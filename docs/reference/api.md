# API Reference

Base URL: `http://localhost:4002`

Evidence:
- `app/api/router.py`
- `app/routers/classification.py`
- `app/routers/health.py`

## Endpoints

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/health/liveness` | none | `{status}` |
| GET | `/health/readiness` | none | `{status, labels_count}` |
| GET | `/endpoint/` | none | list of routes/methods |
| POST | `/api/classifier` | `{text}` | `"<label>"` |
| POST | `/api/language` | `{text}` | `"<language>"` |
| POST | `/api/transformer` | multipart `file` | `{filename, content}` |
| POST | `/classify` | multipart `file` | `{label, language, type?}` |
| POST | `/configlabel` | `{labels:["a","b"]}` | `string[]` |
| GET | `/labels` | none | `string[]` |

## `POST /configlabel` contract (exact)

Request body:
- JSON object with required `labels` array.
- Example: `{"labels":["tech","health","legal"]}`

Normalization behavior:
- Trim whitespace for each label.
- Remove empty entries.
- Preserve order.
- Keep duplicates as provided.

Response:
- `200` with `string[]`, the stored labels after normalization.
- Example response: `["tech", "health", "legal"]`

Errors:
- `400` with detail `"At least one label is required"` when all parsed labels are empty.
- `422` when `labels` is missing or unknown fields are provided (schema validation error).

Related state behavior:
- Labels are process-local in memory and reset on restart.
- `GET /labels` returns the same current in-memory list.

## Validation and errors
- `400` for input validation and extraction problems.
- `502` for classifier/language inference failures.
- `500` for unexpected failures.

Evidence:
- `app/routers/classification.py` (`_handle_exception`)
- `app/schemas/classification.py`

## Contract notes
- Contract returns plain string for `/api/classifier` and `/api/language` (not wrapped object).
- `/classify` returns optional `type="not english"` when language output is not `en`.

Evidence:
- `app/routers/classification.py`
- `app/pipelines/classification_pipeline.py`
