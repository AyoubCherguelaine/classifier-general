from types import SimpleNamespace

import torch

import app.services.classifier_service as classifier_module


class _FakeTokenizer:
    def __call__(self, sequence_pairs, padding, truncation, return_tensors):
        batch_size = len(sequence_pairs)
        return {
            "input_ids": torch.ones((batch_size, 2), dtype=torch.long),
            "attention_mask": torch.ones((batch_size, 2), dtype=torch.long),
        }


class _FakeInferenceModel:
    def __init__(self, logits: torch.Tensor, config: SimpleNamespace | None = None) -> None:
        self._logits = logits
        self.config = config or SimpleNamespace(
            label2id={"CONTRADICTION": 0, "ENTAILMENT": 1},
            id2label={0: "CONTRADICTION", 1: "ENTAILMENT"},
        )

    def __call__(self, **kwargs):
        return SimpleNamespace(logits=self._logits)


class _FakeLoadModel:
    def __init__(self) -> None:
        self.config = SimpleNamespace(
            label2id={"CONTRADICTION": 0, "ENTAILMENT": 1},
            id2label={0: "CONTRADICTION", 1: "ENTAILMENT"},
        )

    def eval(self):
        return self

    def to(self, device):
        return self


def test_classify_uses_runtime_candidate_labels(monkeypatch):
    service = classifier_module.ClassifierService()
    tokenizer = _FakeTokenizer()
    model = _FakeInferenceModel(
        logits=torch.tensor(
            [
                [3.2, 0.4],  # finance -> low entailment
                [0.3, 4.1],  # sport -> highest entailment
                [1.5, 1.9],  # politics -> second-best entailment
            ]
        )
    )

    monkeypatch.setattr(service, "_load_model", lambda: (tokenizer, model))

    predicted = service.classify(
        "This article discusses the latest football transfer strategy.",
        ["finance", "sport", "politics"],
    )

    assert predicted == "sport"


def test_classify_uses_task_specific_entailment_id_when_label_names_are_generic(monkeypatch):
    service = classifier_module.ClassifierService()
    tokenizer = _FakeTokenizer()
    model = _FakeInferenceModel(
        logits=torch.tensor(
            [
                [1.8, 0.3, 0.4],  # finance -> low entailment
                [0.4, 0.7, 3.7],  # sport -> highest entailment
            ]
        ),
        config=SimpleNamespace(
            label2id={"LABEL_0": 0, "LABEL_1": 1, "LABEL_2": 2},
            id2label={0: "LABEL_0", 1: "LABEL_1", 2: "LABEL_2"},
            task_specific_params={"zero-shot-classification": {"entailment_id": 2}},
            num_labels=3,
        ),
    )

    monkeypatch.setattr(service, "_load_model", lambda: (tokenizer, model))
    monkeypatch.setattr(classifier_module.settings, "classifier_entailment_label_id", None)

    predicted = service.classify(
        "The story is mostly about football transfers.",
        ["finance", "sport"],
    )

    assert predicted == "sport"


def test_classify_uses_explicit_entailment_id_setting_when_mapping_is_missing(monkeypatch):
    service = classifier_module.ClassifierService()
    tokenizer = _FakeTokenizer()
    model = _FakeInferenceModel(
        logits=torch.tensor(
            [
                [2.0, 0.3],  # finance -> low entailment
                [0.2, 3.4],  # sport -> highest entailment
            ]
        ),
        config=SimpleNamespace(
            label2id={"NEGATIVE": 0, "POSITIVE": 1},
            id2label={0: "NEGATIVE", 1: "POSITIVE"},
            num_labels=2,
        ),
    )

    monkeypatch.setattr(service, "_load_model", lambda: (tokenizer, model))
    monkeypatch.setattr(classifier_module.settings, "classifier_entailment_label_id", 1)

    predicted = service.classify(
        "The story is mostly about football transfers.",
        ["finance", "sport"],
    )

    assert predicted == "sport"


def test_classify_falls_back_to_mnli_entailment_index_for_generic_three_label_configs(monkeypatch):
    service = classifier_module.ClassifierService()
    tokenizer = _FakeTokenizer()
    model = _FakeInferenceModel(
        logits=torch.tensor(
            [
                [2.3, 0.6, 0.8],  # finance -> low entailment
                [0.4, 0.8, 3.9],  # sport -> highest entailment
            ]
        ),
        config=SimpleNamespace(
            label2id={"LABEL_0": 0, "LABEL_1": 1, "LABEL_2": 2},
            id2label={0: "LABEL_0", 1: "LABEL_1", 2: "LABEL_2"},
            num_labels=3,
        ),
    )

    monkeypatch.setattr(service, "_load_model", lambda: (tokenizer, model))
    monkeypatch.setattr(classifier_module.settings, "classifier_entailment_label_id", None)

    predicted = service.classify(
        "The story is mostly about football transfers.",
        ["finance", "sport"],
    )

    assert predicted == "sport"


def test_classify_falls_back_to_mnli_entailment_index_for_missing_label_mapping(monkeypatch):
    service = classifier_module.ClassifierService()
    tokenizer = _FakeTokenizer()
    model = _FakeInferenceModel(
        logits=torch.tensor(
            [
                [1.8, 0.4, 0.5],  # finance -> low entailment
                [0.2, 0.5, 3.6],  # sport -> highest entailment
            ]
        ),
        config=SimpleNamespace(
            label2id={},
            id2label={},
            num_labels=3,
        ),
    )

    monkeypatch.setattr(service, "_load_model", lambda: (tokenizer, model))
    monkeypatch.setattr(classifier_module.settings, "classifier_entailment_label_id", None)

    predicted = service.classify(
        "The story is mostly about football transfers.",
        ["finance", "sport"],
    )

    assert predicted == "sport"


def test_model_quantization_falls_back_to_non_quantized_model(monkeypatch):
    service = classifier_module.ClassifierService()
    fake_model = _FakeLoadModel()
    fake_tokenizer = object()

    monkeypatch.setattr(
        classifier_module.AutoTokenizer,
        "from_pretrained",
        lambda *args, **kwargs: fake_tokenizer,
    )
    monkeypatch.setattr(
        classifier_module.AutoModelForSequenceClassification,
        "from_pretrained",
        lambda *args, **kwargs: fake_model,
    )
    monkeypatch.setattr(classifier_module.settings, "enable_model_quantization", True)

    def _raise_quantization_error(*args, **kwargs):
        raise RuntimeError("quantization backend unavailable")

    monkeypatch.setattr(
        classifier_module.torch.ao.quantization,
        "quantize_dynamic",
        _raise_quantization_error,
    )

    _, loaded_model = service._load_model()

    assert loaded_model is fake_model
