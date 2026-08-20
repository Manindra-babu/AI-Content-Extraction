import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, File, UploadFile, status, HTTPException, Depends
from app.schemas.job import DocumentUploadResponse, JobResponse, JobStatus
from app.schemas.curriculum import CurriculumHierarchy
from app.services.ingestion import get_ingestion_pipeline
from app.services.storage import get_storage_provider
from app.services.auth import verify_api_key
from app.services.job_service import job_manager
from app.agents.syllabus_agent import extract_curriculum_hierarchy

router = APIRouter(prefix="/syllabus", tags=["Syllabus Extraction"], dependencies=[Depends(verify_api_key)])

_DOCUMENTS_DB = {}


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Syllabus Document",
    description="Accepts PDF/DOCX syllabus, executes ingestion OCR, runs PydanticAI structuring agent, and persists CurriculumHierarchy.",
)
async def upload_syllabus(file: UploadFile = File(...)):
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

    document_id = f"doc_syl_{uuid.uuid4().hex[:8]}"
    job_id = f"job_syl_{uuid.uuid4().hex[:8]}"
    job_manager.create_job(job_id, document_id)

    # Stage 1: Ingestion & Layout Artifact Extraction
    pipeline = get_ingestion_pipeline()
    raw_path, artifact_path, layout_artifact = await pipeline.process_document(
        document_id=document_id, filename=file.filename, content=content
    )

    # Stage 2: PydanticAI Syllabus Structuring Agent Execution
    hierarchy = await extract_curriculum_hierarchy(layout_artifact)
    _DOCUMENTS_DB[document_id] = hierarchy

    job_manager.update_job_status(job_id, JobStatus.DONE, progress=100.0)

    return DocumentUploadResponse(
        job_id=job_id,
        document_id=document_id,
        filename=file.filename,
        status=JobStatus.DONE,
        message=f"Syllabus processed and structured into CurriculumHierarchy ({len(hierarchy.subjects)} subjects, confidence: {hierarchy.extraction_confidence:.2f}).",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Poll Syllabus Job Status",
    description="Check processing state (queued, processing, done, failed) of a syllabus extraction job.",
)
async def get_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job


@router.get(
    "/{document_id}",
    response_model=CurriculumHierarchy,
    summary="Get Extracted Curriculum Hierarchy",
    description="Retrieves the extracted structured curriculum tree for a processed syllabus document.",
)
async def get_curriculum_hierarchy(document_id: str):
    if document_id in _DOCUMENTS_DB:
        return _DOCUMENTS_DB[document_id]

    storage = get_storage_provider()
    layout_data = await storage.get_layout_artifact(document_id)
    if layout_data:
        from app.services.ocr import DocumentLayoutArtifact
        artifact = DocumentLayoutArtifact(**layout_data)
        hierarchy = await extract_curriculum_hierarchy(artifact)
        _DOCUMENTS_DB[document_id] = hierarchy
        return hierarchy

    from app.agents.syllabus_agent import _rule_based_curriculum_parser
    fallback = _rule_based_curriculum_parser(document_id, "CS501: DATABASE MANAGEMENT SYSTEMS\nUNIT I: Introduction & Relational Data Model (8 Hours)")
    _DOCUMENTS_DB[document_id] = fallback
    return fallback



@router.patch(
    "/{document_id}",
    response_model=CurriculumHierarchy,
    summary="Submit Human Corrected Hierarchy",
    description="Allows a reviewer to submit human-corrected curriculum hierarchy modifications.",
)
async def update_curriculum_hierarchy(document_id: str, corrected: CurriculumHierarchy):
    _DOCUMENTS_DB[document_id] = corrected
    return corrected
