# Configuration Reference

Configuration is managed with Pydantic Settings.

Evidence:
- `app/core/config.py`
- `.env.example`
- `docker-compose.yml`

## Application settings

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `Classifier General API` | FastAPI title |
| `ENVIRONMENT` | `development` | environment label |
| `DEBUG` | `false` | debug mode |

## Filesystem settings

| Variable | Default | Purpose |
|---|---|---|
| `STATIC_DIR` | `static` | static root served at `/static` |
| `UPLOAD_SUBDIR` | `uploads` | upload directory under static root |

## Classifier integration settings

| Variable | Default | Purpose |
|---|---|---|
| `CLASSIFIER_MODEL` | `AyoubChLin/bert-base-uncased-zeroshot-nli` | Hugging Face model ID used for local zero-shot NLI classification |
| `ENABLE_MODEL_QUANTIZATION` | `true` | enable dynamic INT8 quantization with automatic fallback |
| `HUGGINGFACE_TOKEN` | empty | optional auth token for client init |
| `CLASSIFIER_ENTAILMENT_LABEL_ID` | empty | optional integer override for entailment logit index when model config does not expose an `entailment` label |

## Language detector settings

| Variable | Default | Purpose |
|---|---|---|
| none | n/a | language detection now uses local `langdetect` |

## Label settings

| Variable | Default | Purpose |
|---|---|---|
| `DEFAULT_LABELS_CSV` | `news,sport,finance,politics` | initial in-memory labels |

## Behavior notes
- Labels are process-local in memory and reset on restart.
- Upload directory is auto-created at app startup.
- If `label2id`/`id2label` does not include an entailment label, the service checks task-specific config, then `CLASSIFIER_ENTAILMENT_LABEL_ID`, then falls back to index `2` for 3-logit generic/missing mappings.

Evidence:
- `app/services/label_service.py`
- `app/models/label_config.py`
- `app/main.py`
