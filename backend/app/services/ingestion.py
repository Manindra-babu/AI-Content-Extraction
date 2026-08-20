import hashlib
import logging
from typing import Tuple
from app.services.storage import BaseStorageProvider, get_storage_provider
from app.services.ocr import extract_document_layout, DocumentLayoutArtifact

logger = logging.getLogger("ingestion_pipeline")


class IngestionPipeline:
    def __init__(self, storage: BaseStorageProvider = None):
        self.storage = storage or get_storage_provider()

    async def process_document(
        self, document_id: str, filename: str, content: bytes
    ) -> Tuple[str, str, DocumentLayoutArtifact]:
        """
        Executes end-to-end ingestion pipeline:
        1. Computes SHA256 checksum for audit & duplicate detection.
        2. Saves raw binary file to storage provider.
        3. Executes OCR & layout segmentation (native PDF vs scanned OCR).
        4. Saves structured layout artifact JSON ({document_id}_layout.json).
        """
        sha256_hash = hashlib.sha256(content).hexdigest()
        logger.info(
            f"Processing document_id={document_id}, filename='{filename}', sha256={sha256_hash[:12]}..."
        )

        # 1. Save raw binary file
        raw_file_path = await self.storage.save_raw_file(document_id, filename, content)

        # 2. Extract page-by-page layout artifact
        layout_artifact = extract_document_layout(raw_file_path, document_id)

        # 3. Save layout artifact JSON
        artifact_path = await self.storage.save_layout_artifact(
            document_id, layout_artifact.model_dump()
        )

        logger.info(
            f"Ingestion complete for doc={document_id}: pages={layout_artifact.total_pages}, "
            f"scanned={layout_artifact.is_scanned}, method={layout_artifact.extraction_method}"
        )

        return raw_file_path, artifact_path, layout_artifact


_pipeline_instance = None


def get_ingestion_pipeline() -> IngestionPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = IngestionPipeline()
    return _pipeline_instance
