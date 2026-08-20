import os
import pytest
from app.services.storage import LocalStorageProvider


@pytest.mark.asyncio
async def test_local_storage_provider(tmp_path):
    storage = LocalStorageProvider(base_dir=str(tmp_path))
    doc_id = "test_doc_001"
    filename = "sample.pdf"
    content = b"%PDF-1.4 Mock PDF Content"

    # Test saving raw binary file
    raw_path = await storage.save_raw_file(doc_id, filename, content)
    assert os.path.exists(raw_path)
    assert raw_path.endswith("test_doc_001.pdf")

    # Test reading raw binary file
    retrieved_bytes = await storage.get_raw_file_bytes(doc_id)
    assert retrieved_bytes == content

    # Test saving layout artifact JSON
    layout_data = {
        "document_id": doc_id,
        "is_scanned": False,
        "total_pages": 1,
        "pages": [],
        "raw_full_text": "Sample text",
        "extraction_method": "pymupdf_native",
    }
    artifact_path = await storage.save_layout_artifact(doc_id, layout_data)
    assert os.path.exists(artifact_path)
    assert artifact_path.endswith("test_doc_001_layout.json")

    # Test reading layout artifact JSON
    retrieved_layout = await storage.get_layout_artifact(doc_id)
    assert retrieved_layout is not None
    assert retrieved_layout["document_id"] == doc_id
    assert retrieved_layout["extraction_method"] == "pymupdf_native"
