# Runtime State Reference

This service does not define a relational database. State exists in memory and filesystem.

Evidence:
- no `app/database/` package
- `app/models/label_config.py`
- `app/services/file_storage_service.py`

## In-memory state

| State | Location | Lifecycle |
|---|---|---|
| Active labels list | `LabelConfig.labels` | initialized at process start from `DEFAULT_LABELS_CSV`; mutable via `/configlabel`; reset on restart |

Evidence:
- `app/services/label_service.py`
- `app/models/label_config.py`

## Filesystem state

| State | Location | Lifecycle |
|---|---|---|
| Uploaded files | `STATIC_DIR/UPLOAD_SUBDIR` (default `static/uploads`) | created per upload; not automatically deleted by app |
| Static mount | `/static` route | served directly by FastAPI static files |

Evidence:
- `app/core/config.py`
- `app/main.py`
- `app/services/file_storage_service.py`

## External runtime dependencies

| Dependency | Usage |
|---|---|
| Hugging Face model hub | model download/auth for local classifier initialization |
| `langdetect` library | local language inference |
| Tesseract binary | OCR extraction for images |

Evidence:
- `app/services/classifier_service.py`
- `app/services/language_service.py`
- `app/services/extraction_service.py`
- `Dockerfile`

## Unknown or inferred
- Unknown: long-term retention policy for uploaded files.
- Inferred: `static/uploads` can grow unbounded without cleanup process.
