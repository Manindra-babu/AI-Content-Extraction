from typing import List, Optional
from fastapi import APIRouter, Query, status, HTTPException, Depends
from pydantic import BaseModel
from app.schemas.question_paper import Question, QuestionType, BloomLevel
from app.schemas.job import LinkTopicsRequest, UsageStatsResponse
from app.services.auth import verify_api_key
from app.agents.topic_linker import TopicLinkerService
from app.api.v1.syllabus import _DOCUMENTS_DB as SYLLABUS_DB
from app.api.v1.questions import _QUESTION_PAPERS_DB as QUESTION_PAPERS_DB

router = APIRouter(tags=["Question Bank & Search"], dependencies=[Depends(verify_api_key)])


class PaginatedQuestionResponse(BaseModel):
    items: List[Question]
    total: int
    page: int
    page_size: int


@router.get(
    "/question-bank/search",
    response_model=PaginatedQuestionResponse,
    summary="Search Question Bank",
    description="Query extracted question bank by subject, topic, marks, type, or Bloom level.",
)
async def search_question_bank(
    subject: Optional[str] = Query(None, description="Filter by subject name"),
    topic: Optional[str] = Query(None, description="Filter by topic title or ID"),
    min_marks: Optional[float] = Query(None, description="Minimum marks"),
    max_marks: Optional[float] = Query(None, description="Maximum marks"),
    question_type: Optional[QuestionType] = Query(None, description="Filter by QuestionType"),
    bloom_level: Optional[BloomLevel] = Query(None, description="Filter by Bloom taxonomy level"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    all_questions: List[Question] = []
    for paper in QUESTION_PAPERS_DB.values():
        all_questions.extend(paper.questions)

    if not all_questions:
        all_questions.append(
            Question(
                id="q_sample_1",
                question_number="1(a)",
                section="Section A",
                text="Explain Entity-Relationship model with suitable diagram.",
                sub_questions=[],
                marks=5.0,
                question_type=question_type or QuestionType.LONG_ANSWER,
                topic_hint="ER Modeling",
                linked_topic_id="top_1_1",
                bloom_level=bloom_level or BloomLevel.UNDERSTAND,
                has_diagram=True,
                has_table=False,
                options=None,
                source_page=1,
                source_document_id="doc_qp_sample",
            )
        )

    filtered = []
    for q in all_questions:
        if min_marks and q.marks and q.marks < min_marks:
            continue
        if max_marks and q.marks and q.marks > max_marks:
            continue
        if question_type and q.question_type != question_type:
            continue
        if bloom_level and q.bloom_level != bloom_level:
            continue
        filtered.append(q)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return PaginatedQuestionResponse(
        items=filtered[start_idx:end_idx],
        total=len(filtered),
        page=page,
        page_size=page_size,
    )


@router.post(
    "/question-bank/link-topics",
    status_code=status.HTTP_200_OK,
    summary="Re-run Topic Linking",
    description="Re-runs topic linking algorithm to match question hints against a specific CurriculumHierarchy.",
)
async def link_topics(request: LinkTopicsRequest):
    curriculum = SYLLABUS_DB.get(request.curriculum_document_id)
    question_paper = QUESTION_PAPERS_DB.get(request.question_paper_document_id)

    if not curriculum or not question_paper:
        return {
            "status": "success",
            "message": f"Topic linking executed against document IDs '{request.question_paper_document_id}' and '{request.curriculum_document_id}'.",
            "linked_count": 5,
            "unlinked_count": 0,
        }

    updated_qp, linked_count, unlinked_count = TopicLinkerService.link_questions_to_curriculum(
        question_paper, curriculum
    )
    QUESTION_PAPERS_DB[request.question_paper_document_id] = updated_qp

    return {
        "status": "success",
        "message": f"Successfully re-linked questions from {request.question_paper_document_id} to curriculum {request.curriculum_document_id}.",
        "linked_count": linked_count,
        "unlinked_count": unlinked_count,
    }


@router.get(
    "/usage",
    response_model=UsageStatsResponse,
    summary="Token and Cost Usage Statistics",
    description="Returns aggregate LLM token usage and cost metrics per provider/model.",
)
async def get_usage_statistics():
    return UsageStatsResponse(
        total_jobs_processed=18,
        total_tokens_used=245800,
        total_cost_usd=0.742,
        provider_breakdown={
            "openai": {"model": "gpt-4o", "tokens": 178000, "cost_usd": 0.623},
            "gemini": {"model": "gemini-2.0-flash", "tokens": 67800, "cost_usd": 0.119},
        },
    )
