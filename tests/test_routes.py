from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.pipelines.classification_pipeline import classification_pipeline

client = TestClient(app)


def test_classifier_endpoint_contract(monkeypatch):
    monkeypatch.setattr(classification_pipeline, "classify_text", lambda text: "news")

    response = client.post("/api/classifier", json={"text": "This is a long enough sentence for classification."})

    assert response.status_code == 200
    assert response.json() == "news"


def test_language_endpoint_contract(monkeypatch):
    monkeypatch.setattr(classification_pipeline, "detect_language", lambda text: "en")

    response = client.post("/api/language", json={"text": "This is a language detection sample text."})

    assert response.status_code == 200
    assert response.json() == "en"


def test_labels_config_roundtrip():
    response = client.post("/configlabel", json={"labels": ["tech", "health", "legal"]})
    assert response.status_code == 200
    assert response.json() == ["tech", "health", "legal"]

    get_response = client.get("/labels")
    assert get_response.status_code == 200
    assert get_response.json() == ["tech", "health", "legal"]


def test_labels_config_accepts_labels_list_payload():
    response = client.post("/configlabel", json={"labels": ["tech", "health", "legal"]})
    assert response.status_code == 200
    assert response.json() == ["tech", "health", "legal"]


def test_labels_config_rejects_empty_labels():
    response = client.post("/configlabel", json={"labels": [" ", ""]})
    assert response.status_code == 400
    assert response.json() == {"detail": "At least one label is required"}


def test_labels_config_rejects_missing_labels():
    response = client.post("/configlabel", json={})
    assert response.status_code == 422
    assert "labels" in response.text


def test_labels_config_rejects_text_field():
    response = client.post("/configlabel", json={"text": "tech,health"})
    assert response.status_code == 422
    assert "extra_forbidden" in response.text


def test_labels_config_rejects_texts_field():
    response = client.post("/configlabel", json={"texts": ["tech,health"]})
    assert response.status_code == 422
    assert "extra_forbidden" in response.text


def test_transform_file_contract(monkeypatch):
    monkeypatch.setattr(classification_pipeline, "transform_file", lambda filename, path: "extracted content")

    files = {"file": ("sample.txt", BytesIO(b"hello"), "text/plain")}
    response = client.post("/api/transformer", files=files)

    assert response.status_code == 200
    assert response.json()["filename"] == "sample.txt"
    assert response.json()["content"] == "extracted content"


def test_classify_file_contract(monkeypatch):
    monkeypatch.setattr(
        classification_pipeline,
        "classify_file",
        lambda filename, path: {"label": "finance", "language": "en"},
    )

    files = {"file": ("sample.txt", BytesIO(b"hello"), "text/plain")}
    response = client.post("/classify", files=files)

    assert response.status_code == 200
    assert response.json() == {"label": "finance", "language": "en", "type": None}
