# Architectural Decisions Log (DECISIONS.md)

**Client:** WML  
**Project:** AI Content Extraction Services (Work Order 1)  
**Status:** Active  

This document logs key architectural and design decisions made throughout the lifecycle of the project.

---

## 1. Provider-Agnostic LLM Orchestration Layer
- **Date:** 2026-08-05
- **Decision:** Use **PydanticAI** as the core LLM orchestration and structured output extraction engine.
- **Rationale:** PydanticAI provides a model-agnostic agent framework backed by Pydantic v2 validation. It supports OpenAI (`gpt-4o`, `gpt-4.1`) and Google Gemini (`gemini-1.5-pro`, `gemini-2.0-flash`) out of the box with auto-retry mechanism on schema validation failures. Switching models/providers requires only updating environment configurations (`LLM_PROVIDER` and `LLM_MODEL`).

## 2. Asynchronous Ingestion & Task Queue Architecture
- **Date:** 2026-08-05
- **Decision:** All document extraction operations (`/v1/syllabus/upload` and `/v1/questions/upload`) return an HTTP 202 Accepted response with a unique `job_id` immediately.
- **Rationale:** PDF parsing, OCR, and multi-stage LLM structuring can take 15–60 seconds per document. Synchronous HTTP requests would cause gateway timeouts and poor client experience. **Celery + Redis** handles long-running extraction jobs, and clients poll `/v1/*/jobs/{job_id}` or configure webhook callbacks.

## 3. Storage Layer Strategy (PostgreSQL + S3 Storage)
- **Date:** 2026-08-05
- **Decision:** Use **PostgreSQL 16** (with Async SQLAlchemy) for storing job states, extracted JSON structures, API keys, and system logs. Uploaded files (PDFs/DOCX/Images) are stored in an S3-compatible Object Storage (MinIO for local dev, AWS S3 for production).
- **Rationale:** Separates relational metadata and search indexing from large raw file binary blobs.

## 4. Two-Stage Extraction Pipeline Strategy
- **Date:** 2026-08-05
- **Decision:** Extraction occurs in two distinct stages:
  1. *Document Understanding & OCR Stage:* Text extraction & layout analysis using PyMuPDF/pdfplumber for native PDFs, with Tesseract/docTR fallback for scanned images. Raw text & layout metadata are persisted.
  2. *Structuring Stage:* PydanticAI agent processes layout artifacts into structured Pydantic models.
- **Rationale:** Makes jobs idempotent and resumable. If LLM structuring fails, re-structuring can run directly on saved OCR artifacts without re-running CPU/GPU-intensive OCR.

## 5. API Design & Versioning
- **Date:** 2026-08-05
- **Decision:** All APIs are prefixed with `/v1` and enforce a standardized error envelope (`{ "error": { "code": str, "message": str, "details": dict | null } }`).
- **Rationale:** Prevents breaking changes for WML's integrating applications and guarantees consistent error handling across all clients.
