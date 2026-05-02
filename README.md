---
title: Classifier General
emoji: 🌍
colorFrom: gray
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: classifier-general
---

# Classifier General API (Refactored)

Refactored into a modular FastAPI backend with clear layers:
- `app/routers`
- `app/services`
- `app/pipelines`
- `app/schemas`
- `app/models`
- `app/core`

## Preserved Endpoint Contract
- `POST /api/classifier` -> returns label string
- `POST /api/language` -> returns language string
- `POST /api/transformer` -> returns `{ filename, content }`
- `POST /classify` -> returns `{ label, language, type? }`
- `POST /configlabel` -> returns labels array
- `GET /labels` -> returns labels array

`POST /configlabel` exact payload:
- body accepts `{"labels":["label1","label2","label3"]}`
- all resulting labels are trimmed, empty values removed
- duplicates are kept if they are provided
- returns the stored `string[]` labels

Additional operational endpoints:
- `GET /health/liveness`
- `GET /health/readiness`
- `GET /endpoint/`

## Environment
Copy and edit:
```bash
cp .env.example .env
```

Key vars:
- `CLASSIFIER_MODEL`
- `ENABLE_MODEL_QUANTIZATION`
- `HUGGINGFACE_TOKEN`
- `CLASSIFIER_ENTAILMENT_LABEL_ID` (optional override when model config has no entailment label name)
- `DEFAULT_LABELS_CSV`

## Local Run
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 4002 --reload
```

## Docker Run
```bash
docker compose up --build
```

## Tests
```bash
pytest -q
```

## Notes
- OCR requires `tesseract-ocr` (installed in Dockerfile).
- Supported extraction formats in this refactor: `.pdf`, `.docx`, `.xlsx`, image formats, and plain text files.
- The classifier model is loaded directly from Hugging Face Hub and runs true zero-shot classification over runtime labels.
- Language detection runs locally via `langdetect` (no remote language endpoint dependency).
- `/classify` uses only the first PDF page for classification; `/api/transformer` still extracts full content.
