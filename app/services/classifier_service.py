import logging
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import settings
from app.core.exceptions import ClassificationError

logger = logging.getLogger(__name__)


class ClassifierService:
    _HYPOTHESIS_TEMPLATE = "This text is about {}."

    def __init__(self) -> None:
        self._tokenizer: Any | None = None
        self._model: Any | None = None

    def _load_model(self) -> tuple[Any, Any]:
        if self._tokenizer is None or self._model is None:
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    settings.classifier_model,
                    token=settings.huggingface_token,
                )
                model = AutoModelForSequenceClassification.from_pretrained(
                    settings.classifier_model,
                    token=settings.huggingface_token,
                )
                model.eval()
                model.to("cpu")

                if settings.enable_model_quantization:
                    try:
                        # Dynamic INT8 quantization for CPU inference.
                        quantized_model = torch.ao.quantization.quantize_dynamic(
                            model,
                            {torch.nn.Linear},
                            dtype=torch.qint8,
                        )
                        model = quantized_model
                    except Exception:
                        logger.warning(
                            "Model quantization failed; using non-quantized model instead.",
                            exc_info=True,
                        )

                self._tokenizer = tokenizer
                self._model = model
            except Exception as exc:
                raise ClassificationError("Unable to initialize classifier model") from exc

        return self._tokenizer, self._model

    def warmup(self) -> None:
        self._load_model()

    @staticmethod
    def _normalize_labels(labels: list[str]) -> list[str]:
        cleaned = [label.strip() for label in labels if isinstance(label, str) and label.strip()]
        return list(dict.fromkeys(cleaned))

    @staticmethod
    def _parse_label_id(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_task_specific_entailment_id(model: Any) -> int | None:
        task_specific_params = getattr(model.config, "task_specific_params", {}) or {}
        if not isinstance(task_specific_params, dict):
            return None

        zero_shot_params = task_specific_params.get("zero-shot-classification", {})
        if not isinstance(zero_shot_params, dict):
            return None

        return ClassifierService._parse_label_id(zero_shot_params.get("entailment_id"))

    @staticmethod
    def _has_generic_label_names(model: Any) -> bool:
        label2id = getattr(model.config, "label2id", {}) or {}
        id2label = getattr(model.config, "id2label", {}) or {}

        labels: list[str] = []
        labels.extend(label for label in label2id.keys() if isinstance(label, str))
        labels.extend(label for label in id2label.values() if isinstance(label, str))
        if not labels:
            return False

        return all(label.lower().startswith("label_") for label in labels)

    @staticmethod
    def _resolve_entailment_id(model: Any) -> int:
        label2id = getattr(model.config, "label2id", {}) or {}
        for label, label_id in label2id.items():
            if isinstance(label, str) and label.lower().startswith("entail"):
                parsed = ClassifierService._parse_label_id(label_id)
                if parsed is not None:
                    return parsed

        id2label = getattr(model.config, "id2label", {}) or {}
        for label_id, label in id2label.items():
            if isinstance(label, str) and label.lower().startswith("entail"):
                parsed = ClassifierService._parse_label_id(label_id)
                if parsed is not None:
                    return parsed

        task_specific_entailment_id = ClassifierService._extract_task_specific_entailment_id(model)
        if task_specific_entailment_id is not None:
            return task_specific_entailment_id

        if settings.classifier_entailment_label_id is not None:
            return settings.classifier_entailment_label_id

        num_labels = ClassifierService._parse_label_id(getattr(model.config, "num_labels", None))
        if num_labels == 3 and (
            ClassifierService._has_generic_label_names(model) or (not label2id and not id2label)
        ):
            logger.warning(
                "Falling back to entailment label id 2 because model config labels are generic or missing "
                "and no explicit entailment mapping was found. Set CLASSIFIER_ENTAILMENT_LABEL_ID "
                "to override this behavior."
            )
            return 2

        raise ClassificationError(
            "Classifier model is missing an entailment label mapping. "
            "Set CLASSIFIER_ENTAILMENT_LABEL_ID in the environment when the model config "
            "does not expose an entailment label."
        )

    def classify(self, text: str, labels: list[str]) -> str:
        candidate_labels = self._normalize_labels(labels)
        if not candidate_labels:
            raise ClassificationError("No labels configured")

        tokenizer, model = self._load_model()
        entailment_id = self._resolve_entailment_id(model)

        try:
            sequence_pairs = [[text, self._HYPOTHESIS_TEMPLATE.format(label)] for label in candidate_labels]
            inputs = tokenizer(
                sequence_pairs,
                padding=True,
                truncation="only_first",
                return_tensors="pt",
            )

            with torch.no_grad():
                logits = model(**inputs).logits

            if logits.ndim != 2:
                raise ClassificationError("Classifier returned unexpected logits shape")
            if entailment_id < 0 or entailment_id >= logits.shape[-1]:
                raise ClassificationError("Entailment label index is out of range for classifier output")

            entailment_logits = logits[:, entailment_id]
            best_index = int(torch.argmax(entailment_logits).item())
            return candidate_labels[best_index]
        except Exception as exc:
            raise ClassificationError("Classifier prediction failed") from exc

classifier_service = ClassifierService()
