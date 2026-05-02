from langdetect import DetectorFactory, LangDetectException, detect

from app.core.exceptions import LanguageDetectionError

# Ensure deterministic language detection outcomes across runs.
DetectorFactory.seed = 0


class LanguageService:
    def detect_language(self, text: str) -> str:
        try:
            language = detect(text)
        except LangDetectException as exc:
            raise LanguageDetectionError("Language detection failed") from exc
        except Exception as exc:
            raise LanguageDetectionError("Language detector raised an unexpected error") from exc

        normalized_language = language.split("-", 1)[0].strip().lower() if isinstance(language, str) else ""
        if not normalized_language:
            raise LanguageDetectionError("Language detector did not return a valid label")

        return normalized_language


language_service = LanguageService()
