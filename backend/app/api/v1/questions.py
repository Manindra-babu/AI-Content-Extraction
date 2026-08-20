import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, File, UploadFile, status, HTTPException, Depends
from app.schemas.job import DocumentUploadResponse, JobResponse, JobStatus
from app.schemas.question_paper import QuestionPaperExtraction
from app.services.ingestion import get_ingestion_pipeline
from app.services.storage import get_storage_provider
from app.services.auth import verify_api_key
from app.services.job_service import job_manager
from app.agents.question_agent import extract_question_paper

router = APIRouter(prefix="/questions", tags=["Question Paper Extraction"], dependencies=[Depends(verify_api_key)])

_QUESTION_PAPERS_DB = {}


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Question Paper Document",
    description="Accepts PDF/image of question paper, executes ingestion/OCR, runs PydanticAI question agent, and persists QuestionPaperExtraction.",
)
async def upload_question_paper(file: UploadFile = File(...)):
    filename_lower = (file.filename or "").lower()
    allowed_exts = [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".webp", ".txt"]
    if not any(filename_lower.endswith(ext) for ext in allowed_exts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file.filename}'. Allowed formats: PDF, DOCX, DOC, PNG, JPG, JPEG, WEBP, TXT.",
        )


    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    document_id = f"doc_qp_{uuid.uuid4().hex[:8]}"
    job_id = f"job_qp_{uuid.uuid4().hex[:8]}"
    job_manager.create_job(job_id, document_id)

    # Stage 1: Ingestion & OCR Layout Artifact Extraction
    pipeline = get_ingestion_pipeline()
    raw_path, artifact_path, layout_artifact = await pipeline.process_document(
        document_id=document_id, filename=file.filename, content=content
    )

    # Stage 2: PydanticAI Question Extraction Agent Execution
    extraction = await extract_question_paper(layout_artifact)
    _QUESTION_PAPERS_DB[document_id] = extraction

    job_manager.update_job_status(job_id, JobStatus.DONE, progress=100.0)

    return DocumentUploadResponse(
        job_id=job_id,
        document_id=document_id,
        filename=file.filename,
        status=JobStatus.DONE,
        message=f"Question paper processed ({len(extraction.questions)} questions extracted, confidence: {extraction.extraction_confidence:.2f}).",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Poll Question Paper Job Status",
    description="Check processing state of a question paper extraction job.",
)
async def get_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job


@router.get(
    "/{document_id}",
    response_model=QuestionPaperExtraction,
    summary="Get Extracted Question Paper",
    description="Retrieves extracted structured questions for a processed question paper document.",
)
async def get_question_paper_extraction(document_id: str):
    if document_id in _QUESTION_PAPERS_DB:
        return _QUESTION_PAPERS_DB[document_id]

    storage = get_storage_provider()
    layout_data = await storage.get_layout_artifact(document_id)
    if layout_data:
        from app.services.ocr import DocumentLayoutArtifact
        artifact = DocumentLayoutArtifact(**layout_data)
        extraction = await extract_question_paper(artifact)
        _QUESTION_PAPERS_DB[document_id] = extraction
        return extraction

    raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")


@router.patch(
    "/{document_id}",
    response_model=QuestionPaperExtraction,
    summary="Submit Corrected Question Bank",
    description="Allows a reviewer to submit human-corrected question bank modifications.",
)
async def update_question_paper_extraction(document_id: str, corrected: QuestionPaperExtraction):
    _QUESTION_PAPERS_DB[document_id] = corrected
    return corrected
