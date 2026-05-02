import re

from app.core.exceptions import ValidationError


MIN_WORDS = 4


def preprocess_text(text: str) -> str:
    if text is None:
        raise ValidationError("Text is required")

    cleaned = text.replace("\n", " ")
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"[^\w\s$€%.,-/]|(?<=\d)[.,/](?=\d)", " ", cleaned).lower().strip()

    if len(cleaned.split(" ")) < MIN_WORDS:
        raise ValidationError(f"Text must contain at least {MIN_WORDS} words after preprocessing")

    return cleaned
