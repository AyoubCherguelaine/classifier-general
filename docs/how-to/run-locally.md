# Run Locally (Dev Loop)

## 1. Install dependencies
```bash
cd classifier-general
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Evidence:
- `requirements.txt`

## 2. Configure environment
```bash
cp .env.example .env
```

Critical settings:
- `CLASSIFIER_MODEL`
- `ENABLE_MODEL_QUANTIZATION`
- `DEFAULT_LABELS_CSV`

Evidence:
- `app/core/config.py`
- `.env.example`

## 3. Start server
```bash
uvicorn main:app --host 0.0.0.0 --port 4002 --reload
```

Evidence:
- `main.py`
- `app/main.py`

## 4. Test file-based endpoints
```bash
curl -s -X POST http://localhost:4002/api/transformer \
  -F 'file=@/absolute/path/to/sample.pdf'

curl -s -X POST http://localhost:4002/classify \
  -F 'file=@/absolute/path/to/sample.pdf'
```

Uploads are stored under `static/uploads` with random UUID prefixes.

Evidence:
- `app/services/file_storage_service.py`
- `app/services/extraction_service.py`

## Troubleshooting
- `400 Text must contain at least 4 words`:
  - input failed preprocessing minimum-word rule.
- `502 Classifier request failed`:
  - local model load or prediction failed (model ID/token/resource issue).
- OCR extraction quality is low:
  - verify tesseract install and image quality.

Evidence:
- `app/pipelines/text_pipeline.py`
- `app/routers/classification.py`
- `Dockerfile`
