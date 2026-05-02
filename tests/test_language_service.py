import pytest

from app.core.exceptions import LanguageDetectionError
import app.services.language_service as language_module


def test_detect_language_returns_en_for_english_and_non_en_for_french():
    service = language_module.LanguageService()

    english_text = "This is a detailed English sentence about technology trends and financial markets."
    french_text = "Ceci est une phrase francaise detaillee sur les tendances technologiques et les marches financiers."

    assert service.detect_language(english_text) == "en"
    assert service.detect_language(french_text) != "en"


def test_detect_language_raises_for_invalid_detector_output(monkeypatch):
    service = language_module.LanguageService()
    monkeypatch.setattr(language_module, "detect", lambda text: "")

    with pytest.raises(LanguageDetectionError, match="did not return a valid label"):
        service.detect_language("This text is long enough for language detection.")


def test_detect_language_wraps_unexpected_detector_errors(monkeypatch):
    service = language_module.LanguageService()

    def _raise_error(_: str):
        raise RuntimeError("unexpected detector failure")

    monkeypatch.setattr(language_module, "detect", _raise_error)

    with pytest.raises(LanguageDetectionError, match="unexpected error"):
        service.detect_language("This text is long enough for language detection.")
