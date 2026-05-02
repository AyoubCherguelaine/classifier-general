from dataclasses import dataclass, field
from threading import Lock


@dataclass
class LabelConfig:
    labels: list[str] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def get_labels(self) -> list[str]:
        with self._lock:
            return list(self.labels)

    def set_labels(self, labels: list[str]) -> list[str]:
        cleaned = [label.strip() for label in labels if label and label.strip()]
        with self._lock:
            self.labels = cleaned
            return list(self.labels)
