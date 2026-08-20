import os
import json
import pytest
import fitz
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.curriculum import CurriculumHierarchy
from app.services.ocr import DocumentLayoutArtifact, PageLayout, TextBlock, BoundingBox
from app.agents.syllabus_agent import extract_curriculum_hierarchy, get_model_spec

client = TestClient(app)


def test_provider_model_spec_switching():
    spec_openai = get_model_spec(provider="openai", model_name="gpt-4o")
    assert spec_openai == "openai:gpt-4o"

    spec_gemini = get_model_spec(provider="gemini", model_name="gemini-2.0-flash")
    assert spec_gemini == "google-gla:gemini-2.0-flash"

    spec_groq = get_model_spec(provider="groq", model_name="llama-3.3-70b-versatile")
    assert spec_groq == "groq:llama-3.3-70b-versatile"



@pytest.mark.asyncio
async def test_extract_curriculum_hierarchy_execution():
    layout = DocumentLayoutArtifact(
        document_id="doc_test_agent_1",
        is_scanned=False,
        total_pages=1,
        pages=[
            PageLayout(
                page_number=1,
                width=600,
                height=800,
                text_blocks=[
                    TextBlock(
                        block_id="p1_b1",
                        text="CS501: DATABASE MANAGEMENT SYSTEMS\nUNIT I: Relational Data Model (8 Hours)\nER Modeling: Entities, Attributes, Keys.",
                        bbox=BoundingBox(x0=50, y0=50, x1=550, y1=200),
                    )
                ],
            )
        ],
        raw_full_text="CS501: DATABASE MANAGEMENT SYSTEMS\nUNIT I: Relational Data Model (8 Hours)\nER Modeling: Entities, Attributes, Keys.",
        extraction_method="pymupdf_native",
    )

    hierarchy = await extract_curriculum_hierarchy(layout)
    assert isinstance(hierarchy, CurriculumHierarchy)
    assert hierarchy.source_document_id == "doc_test_agent_1"
    assert len(hierarchy.subjects) == 1
    assert hierarchy.subjects[0].code == "CS501"
    assert len(hierarchy.subjects[0].units) >= 1


def test_golden_file_curriculum_fixture():
    golden_path = os.path.join(os.path.dirname(__file__), "golden_files", "cs_syllabus_golden.json")
    assert os.path.exists(golden_path)

    with open(golden_path, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    curriculum = CurriculumHierarchy(**golden_data)
    assert curriculum.program_name == "B.Tech Computer Science and Engineering"
    assert curriculum.subjects[0].code == "CS501"
    assert curriculum.subjects[0].units[0].learning_outcomes[0].code == "CO1"


def test_syllabus_upload_and_agent_extraction_endpoint():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "CS501: DATABASE MANAGEMENT SYSTEMS", fontsize=14)
    page.insert_text((50, 100), "UNIT I: Introduction & Relational Data Model (8 Hours)", fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()

    response = client.post(
        "/v1/syllabus/upload",
        files={"file": ("syllabus.pdf", pdf_bytes, "application/pdf")},
        headers={"X-API-Key": "wml_dev_key_2026"},
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "document_id" in data
    assert data["status"] == "done"

    doc_id = data["document_id"]
    get_res = client.get(f"/v1/syllabus/{doc_id}", headers={"X-API-Key": "wml_dev_key_2026"})
    assert get_res.status_code == 200

    hierarchy_data = get_res.json()
    assert hierarchy_data["source_document_id"] == doc_id
    assert len(hierarchy_data["subjects"]) >= 1
