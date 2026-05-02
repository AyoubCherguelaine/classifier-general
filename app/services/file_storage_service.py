from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class FileStorageService:
    def __init__(self) -> None:
        settings.static_dir.mkdir(parents=True, exist_ok=True)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, upload_file: UploadFile) -> Path:
        original_name = Path(upload_file.filename or "uploaded_file").name
        safe_name = original_name.replace("/", "_")
        target_path = settings.upload_dir / f"{uuid4().hex}_{safe_name}"

        with target_path.open("wb") as destination:
            while True:
                chunk = upload_file.file.read(1024 * 1024)
                if not chunk:
                    break
                destination.write(chunk)

        return target_path


file_storage_service = FileStorageService()
