from app.core.config import settings
from app.models.label_config import LabelConfig


class LabelService:
    def __init__(self) -> None:
        initial_labels = [label.strip() for label in settings.default_labels_csv.split(",") if label.strip()]
        self._config = LabelConfig(labels=initial_labels)

    def get_labels(self) -> list[str]:
        return self._config.get_labels()

    def set_labels_from_csv(self, labels_csv: str) -> list[str]:
        labels = [label.strip() for label in labels_csv.split(",") if label.strip()]
        return self._config.set_labels(labels)

    def set_labels(self, labels: list[str]) -> list[str]:
        return self._config.set_labels(labels)


label_service = LabelService()
