from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Classifier General API"
    environment: str = "development"
    debug: bool = False

    static_dir: Path = Path("static")
    upload_subdir: str = "uploads"

    classifier_model: str = "AyoubChLin/bert-base-uncased-zeroshot-nli"
    enable_model_quantization: bool = True
    huggingface_token: str | None = None
    classifier_entailment_label_id: int | None = None

    default_labels_csv: str = Field(default="news,sport,finance,politics")

    @property
    def upload_dir(self) -> Path:
        return self.static_dir / self.upload_subdir


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
