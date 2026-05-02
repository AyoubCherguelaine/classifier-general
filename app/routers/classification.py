from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.exceptions import ClassificationError, ExtractionError, LanguageDetectionError, ValidationError
from app.pipelines.classification_pipeline import classification_pipeline
from app.schemas.classification import FileClassifyResponse, FileTransformResponse, LabelUpdateInput, TextInput
from app.services.file_storage_service import file_storage_service
from app.services.label_service import label_service

router = APIRouter(tags=["classification"])


def _handle_exception(exc: Exception) -> None:
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, ExtractionError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, (ClassificationError, LanguageDetectionError)):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error") from exc


@router.post("/api/classifier", response_model=str)
async def classify_text(payload: TextInput) -> str:
    try:
        return classification_pipeline.classify_text(payload.text)
    except Exception as exc:
        _handle_exception(exc)


@router.post("/api/language", response_model=str)
async def detect_language(payload: TextInput) -> str:
    try:
        return classification_pipeline.detect_language(payload.text)
    except Exception as exc:
        _handle_exception(exc)


@router.post("/api/transformer", response_model=FileTransformResponse)
async def transform_file(file: UploadFile = File(...)) -> dict:
    try:
        saved_path = file_storage_service.save_upload(file)
        content = classification_pipeline.transform_file(file.filename or saved_path.name, saved_path)
        return {"filename": file.filename or saved_path.name, "content": content}
    except Exception as exc:
        _handle_exception(exc)


@router.post("/classify", response_model=FileClassifyResponse)
async def classify_uploaded_file(file: UploadFile = File(...)) -> dict:
    try:
        saved_path = file_storage_service.save_upload(file)
        return classification_pipeline.classify_file(file.filename or saved_path.name, saved_path)
    except Exception as exc:
        _handle_exception(exc)


@router.post("/configlabel", response_model=list[str])
async def configure_labels(payload: LabelUpdateInput) -> list[str]:
    labels = label_service.set_labels(payload.get_normalized_labels())
    if not labels:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one label is required")
    return labels


@router.get("/labels", response_model=list[str])
async def get_labels() -> list[str]:
    return label_service.get_labels()
