import os
import pytest
import fitz  # PyMuPDF
from app.services.ocr import detect_is_scanned, extract_document_layout, DocumentLayoutArtifact


def create_mock_native_pdf(file_path: str):
    doc = fitz.open()
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 50), "CS501 DATABASE MANAGEMENT SYSTEMS", fontsize=14)
    page1.insert_text((50, 100), "UNIT I: Introduction & Relational Data Model (8 Hours)", fontsize=11)
    page1.insert_text((50, 130), "ER Modeling: Entities, Attributes, Entity Sets, Relationships, Keys, ER Diagrams.", fontsize=10)

    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 50), "UNIT II: Relational Algebra & SQL (10 Hours)", fontsize=11)
    doc.save(file_path)
    doc.close()


def test_native_pdf_ocr_extraction(tmp_path):
    pdf_path = os.path.join(tmp_path, "sample_syllabus.pdf")
    create_mock_native_pdf(pdf_path)

    # Test detection
    is_scanned, total_pages, reason = detect_is_scanned(pdf_path)
    assert is_scanned is False
    assert total_pages == 2

    # Test layout extraction
    layout = extract_document_layout(pdf_path, "test_doc_syl_1")
    assert isinstance(layout, DocumentLayoutArtifact)
    assert layout.is_scanned is False
    assert layout.total_pages == 2
    assert layout.extraction_method == "pymupdf_native"
    assert "DATABASE MANAGEMENT SYSTEMS" in layout.raw_full_text
    assert "UNIT II" in layout.raw_full_text


def test_scanned_image_ocr_fallback(tmp_path):
    image_path = os.path.join(tmp_path, "scanned_paper.png")
    # Write mock image bytes
    with open(image_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01")

    is_scanned, total_pages, reason = detect_is_scanned(image_path)
    assert is_scanned is True

    layout = extract_document_layout(image_path, "test_doc_image_1")
    assert layout.is_scanned is True
    assert layout.extraction_method == "tesseract_ocr"
