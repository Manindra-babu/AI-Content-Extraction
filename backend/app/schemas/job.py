from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ErrorDetails(BaseModel):
    code: str = Field(description="Error code classification")
    message: str = Field(description="Human readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional context or validation details")


class ErrorResponse(BaseModel):
    error: ErrorDetails


class JobResponse(BaseModel):
    job_id: str
    document_id: str
    status: JobStatus
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    progress_percentage: float = 0.0


class DocumentUploadResponse(BaseModel):
    job_id: str
    document_id: str
    filename: str
    status: JobStatus
    message: str = "Document uploaded successfully and queued for processing."


class LinkTopicsRequest(BaseModel):
    curriculum_document_id: str = Field(description="ID of extracted CurriculumHierarchy document to link against")
    question_paper_document_id: str = Field(description="ID of QuestionPaperExtraction document")


class UsageStatsResponse(BaseModel):
    total_jobs_processed: int
    total_tokens_used: int
    total_cost_usd: float
    provider_breakdown: Dict[str, Dict[str, Any]]
