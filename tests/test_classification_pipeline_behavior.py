from pathlib import Path

from app.pipelines.classification_pipeline import classification_pipeline
import app.pipelines.classification_pipeline as pipeline_module


def test_classify_file_uses_pdf_first_page_only(monkeypatch):
    extraction_flags: list[bool] = []

    def _fake_extract_text(file_name, file_path, pdf_first_page_only=False):
        extraction_flags.append(pdf_first_page_only)
        return "This is enough content for preprocessing and classification."

    monkeypatch.setattr(pipeline_module.extraction_service, "extract_text", _fake_extract_text)
    monkeypatch.setattr(pipeline_module.language_service, "detect_language", lambda text: "en")
    monkeypatch.setattr(pipeline_module.label_service, "get_labels", lambda: ["news", "sport"])
    monkeypatch.setattr(pipeline_module.classifier_service, "classify", lambda text, labels: "news")

    result = classification_pipeline.classify_file("sample.pdf", Path("sample.pdf"))

    assert extraction_flags == [True]
    assert result == {"label": "news", "language": "en"}


def test_transform_file_uses_full_extraction(monkeypatch):
    extraction_flags: list[bool] = []

    def _fake_extract_text(file_name, file_path, pdf_first_page_only=False):
        extraction_flags.append(pdf_first_page_only)
        return "This is full extracted content."

    monkeypatch.setattr(pipeline_module.extraction_service, "extract_text", _fake_extract_text)

    content = classification_pipeline.transform_file("sample.pdf", Path("sample.pdf"))

    assert extraction_flags == [False]
    assert content == "This is full extracted content."
