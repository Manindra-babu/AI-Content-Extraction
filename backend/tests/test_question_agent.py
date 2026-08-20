import os
import json
import pytest
import fitz
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.question_paper import QuestionPaperExtraction, QuestionType, BloomLevel
from app.schemas.curriculum import CurriculumHierarchy, Subject, Unit, Topic
from app.services.ocr import DocumentLayoutArtifact, PageLayout, TextBlock, BoundingBox
from app.agents.question_agent import extract_question_paper
from app.agents.topic_linker import TopicLinkerService

client = TestClient(app)


@pytest.mark.asyncio
async def test_extract_question_paper_execution():
    layout = DocumentLayoutArtifact(
        document_id="doc_test_qp_1",
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
                        text="Section A\n1(a) Explain Entity-Relationship model with suitable diagram.\n2(a) Calculate 3NF normalization for relation R.",
                        bbox=BoundingBox(x0=50, y0=50, x1=550, y1=200),
                    )
                ],
            )
        ],
        raw_full_text="Section A\n1(a) Explain Entity-Relationship model with suitable diagram.\n2(a) Calculate 3NF normalization for relation R.",
        extraction_method="pymupdf_native",
    )

    extraction = await extract_question_paper(layout)
    assert isinstance(extraction, QuestionPaperExtraction)
    assert len(extraction.questions) >= 1
    assert extraction.questions[0].question_type in [QuestionType.LONG_ANSWER, QuestionType.DIAGRAM_BASED]


def test_golden_file_question_paper_fixture():
    golden_path = os.path.join(os.path.dirname(__file__), "golden_files", "cs_question_paper_golden.json")
    assert os.path.exists(golden_path)

    with open(golden_path, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    extraction = QuestionPaperExtraction(**golden_data)
    assert extraction.exam_name == "Mid-Term Examination 2024"
    assert extraction.questions[0].bloom_level == BloomLevel.UNDERSTAND
    assert extraction.questions[1].question_type == QuestionType.NUMERICAL


def test_topic_linker_service():
    curriculum = CurriculumHierarchy(
        program_name="B.Tech CS",
        semester_or_year="Semester V",
        subjects=[
            Subject(
                id="subj_1",
                code="CS501",
                name="DBMS",
                units=[
                    Unit(
                        id="u1",
                        unit_number=1,
                        title="ER Modeling",
                        topics=[Topic(id="top_er_mod", title="ER Diagrams and Entities", subtopics=[])],
                    )
                ],
            )
        ],
        source_document_id="doc_syl_1",
        extraction_confidence=0.95,
    )

    question_paper = QuestionPaperExtraction(
        exam_name="Mid-Term",
        questions=[
            {
                "id": "q1",
                "question_number": "1(a)",
                "text": "Draw ER Diagram for Banking Enterprise",
                "marks": 5.0,
                "question_type": QuestionType.LONG_ANSWER,
                "topic_hint": "ER Diagramming",
                "source_page": 1,
                "source_document_id": "doc_qp_1",
            }
        ],
        extraction_confidence=0.9,
    )

    linked_qp, linked_count, unlinked_count = TopicLinkerService.link_questions_to_curriculum(
        question_paper, curriculum
    )
    assert linked_count == 1
    assert linked_qp.questions[0].linked_topic_id == "top_er_mod"


def test_question_paper_upload_and_search_endpoints():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "SECTION A", fontsize=14)
    page.insert_text((50, 100), "1(a) Explain ER Diagrams in detail.", fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()

    # Test Upload
    response = client.post(
        "/v1/questions/upload",
        files={"file": ("question_paper.pdf", pdf_bytes, "application/pdf")},
        headers={"X-API-Key": "wml_dev_key_2026"},
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "done"

    # Test Search
    search_res = client.get("/v1/question-bank/search?page=1&page_size=10", headers={"X-API-Key": "wml_dev_key_2026"})
    assert search_res.status_code == 200

    search_data = search_res.json()
    assert "items" in search_data
    assert search_data["total"] >= 1
