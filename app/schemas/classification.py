from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TextInput(BaseSchema):
    text: str = Field(min_length=1)


class LabelUpdateInput(BaseSchema):
    labels: list[str] = Field(
        min_length=1,
        description="Direct list of labels. Items are trimmed and empty values are removed.",
        examples=[["news", "sport", "finance"]],
    )

    def get_normalized_labels(self) -> list[str]:
        return [label.strip() for label in self.labels if isinstance(label, str) and label.strip()]


class ClassifierResponse(BaseSchema):
    label: str


class LanguageResponse(BaseSchema):
    language: str


class FileTransformResponse(BaseSchema):
    filename: str
    content: str


class FileClassifyResponse(BaseSchema):
    label: str
    language: str
    type: str | None = None


class LabelsResponse(BaseSchema):
    labels: list[str]
