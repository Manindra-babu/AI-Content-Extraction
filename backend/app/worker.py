import logging
import asyncio
from celery import Celery
from app.config import settings

logger = logging.getLogger("celery.worker")

celery_app = Celery(
    "content_extraction_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="process_syllabus_task")
def process_syllabus_task(job_id: str, document_id: str, file_path: str):
    logger.info(f"Celery worker processing syllabus job={job_id} for doc={document_id} at {file_path}")
    from app.services.ocr import extract_document_layout
    from app.agents.syllabus_agent import extract_curriculum_hierarchy

    # Run async pipeline in sync Celery task worker
    layout_artifact = extract_document_layout(file_path, document_id)
    hierarchy = asyncio.run(extract_curriculum_hierarchy(layout_artifact))

    return {
        "job_id": job_id,
        "document_id": document_id,
        "status": "completed",
        "program_name": hierarchy.program_name,
        "subjects_count": len(hierarchy.subjects),
        "confidence": hierarchy.extraction_confidence,
    }


@celery_app.task(name="process_question_paper_task")
def process_question_paper_task(job_id: str, document_id: str, file_path: str):
    logger.info(f"Celery worker processing question paper job={job_id} for doc={document_id}")
    return {"job_id": job_id, "document_id": document_id, "status": "completed"}
