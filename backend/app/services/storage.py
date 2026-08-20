import json
import os
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.config import settings


class BaseStorageProvider(ABC):
    @abstractmethod
    async def save_raw_file(self, document_id: str, file_name: str, content: bytes) -> str:
        """Saves raw uploaded binary file content and returns local/remote file path."""
        pass

    @abstractmethod
    async def get_raw_file_bytes(self, document_id: str) -> bytes:
        """Retrieves raw binary content for a document."""
        pass

    @abstractmethod
    async def save_layout_artifact(self, document_id: str, layout_data: Dict[str, Any]) -> str:
        """Saves structured layout JSON artifact."""
        pass

    @abstractmethod
    async def get_layout_artifact(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves structured layout JSON artifact if exists."""
        pass


class LocalStorageProvider(BaseStorageProvider):
    def __init__(self, base_dir: str = settings.LOCAL_STORAGE_PATH):
        self.base_dir = os.path.abspath(base_dir)
        self.raw_dir = os.path.join(self.base_dir, "raw")
        self.artifacts_dir = os.path.join(self.base_dir, "artifacts")

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)

    async def save_raw_file(self, document_id: str, file_name: str, content: bytes) -> str:
        ext = os.path.splitext(file_name)[1].lower() or ".pdf"
        target_path = os.path.join(self.raw_dir, f"{document_id}{ext}")
        with open(target_path, "wb") as f:
            f.write(content)
        return target_path

    async def get_raw_file_bytes(self, document_id: str) -> bytes:
        # Search for raw file matching document_id in raw directory
        for f in os.listdir(self.raw_dir):
            if f.startswith(document_id):
                file_path = os.path.join(self.raw_dir, f)
                with open(file_path, "rb") as fp:
                    return fp.read()
        raise FileNotFoundError(f"Raw document binary not found for document_id={document_id}")

    async def save_layout_artifact(self, document_id: str, layout_data: Dict[str, Any]) -> str:
        target_path = os.path.join(self.artifacts_dir, f"{document_id}_layout.json")
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(layout_data, f, indent=2, ensure_ascii=False)
        return target_path

    async def get_layout_artifact(self, document_id: str) -> Optional[Dict[str, Any]]:
        target_path = os.path.join(self.artifacts_dir, f"{document_id}_layout.json")
        if not os.path.exists(target_path):
            return None
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)


class S3StorageProvider(BaseStorageProvider):
    """Stub S3 storage provider for production AWS integration."""
    def __init__(self, bucket_name: str = settings.S3_BUCKET_NAME):
        self.bucket_name = bucket_name

    async def save_raw_file(self, document_id: str, file_name: str, content: bytes) -> str:
        # Stub for boto3 S3 upload
        return f"s3://{self.bucket_name}/raw/{document_id}_{file_name}"

    async def get_raw_file_bytes(self, document_id: str) -> bytes:
        return b""

    async def save_layout_artifact(self, document_id: str, layout_data: Dict[str, Any]) -> str:
        return f"s3://{self.bucket_name}/artifacts/{document_id}_layout.json"

    async def get_layout_artifact(self, document_id: str) -> Optional[Dict[str, Any]]:
        return None


def get_storage_provider() -> BaseStorageProvider:
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageProvider()
    return LocalStorageProvider()
