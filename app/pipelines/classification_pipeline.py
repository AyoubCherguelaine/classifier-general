from pathlib import Path

from app.core.exceptions import ClassificationError, ExtractionError, LanguageDetectionError, ValidationError
from app.pipelines.text_pipeline import preprocess_text
from app.services.classifier_service import classifier_service
from app.services.extraction_service import extraction_service
from app.services.label_service import label_service
from app.services.language_service import language_service


class ClassificationPipeline:
    def classify_text(self, text: str) -> str:
        preprocessed_text = preprocess_text(text)
        labels = label_service.get_labels()
        return classifier_service.classify(preprocessed_text, labels)

    def detect_language(self, text: str) -> str:
        preprocessed_text = preprocess_text(text)
        return language_service.detect_language(preprocessed_text)

    def transform_file(self, original_filename: str, file_path: Path) -> str:
        text = extraction_service.extract_text(original_filename, file_path)
        if not text or not text.strip():
            raise ExtractionError("No text extracted from file")
        return text

    def classify_file(self, original_filename: str, file_path: Path) -> dict:
        text = extraction_service.extract_text(original_filename, file_path, pdf_first_page_only=True)
        if not text or not text.strip():
            raise ExtractionError("No text extracted from file")
        preprocessed_text = preprocess_text(text)

        language = language_service.detect_language(preprocessed_text)
        labels = label_service.get_labels()
        topic = classifier_service.classify(preprocessed_text, labels)

        result = {"label": topic, "language": language}
        if language != "en":
            result["type"] = "not english"
        return result


classification_pipeline = ClassificationPipeline()


__all__ = [
    "classification_pipeline",
    "ClassificationError",
    "LanguageDetectionError",
    "ExtractionError",
    "ValidationError",
]
