import os
import pytest
import fitz
from app.services.storage import LocalStorageProvider
from app.services.ingestion import IngestionPipeline


@pytest.mark.asyncio
async def test_end_to_end_ingestion_pipeline(tmp_path):
    storage = LocalStorageProvider(base_dir=str(tmp_path))
    pipeline = IngestionPipeline(storage=storage)

    # Create mock PDF bytes
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "CS101 Introduction to Computer Science", fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()

    doc_id = "test_ingest_001"
    filename = "cs101_syllabus.pdf"

    raw_path, artifact_path, layout_artifact = await pipeline.process_document(
        document_id=doc_id, filename=filename, content=pdf_bytes
    )

    assert os.path.exists(raw_path)
    assert os.path.exists(artifact_path)
    assert layout_artifact.document_id == doc_id
    assert layout_artifact.total_pages == 1
    assert "Computer Science" in layout_artifact.raw_full_text
