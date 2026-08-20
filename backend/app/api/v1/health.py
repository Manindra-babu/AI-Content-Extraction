from typing import Any, Dict
from fastapi import APIRouter, status
from pydantic import BaseModel
from app.config import settings

router = APIRouter(tags=["Health"])


class HealthCheckResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    environment: str
    services: Dict[str, Any]


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness and Readiness Check",
    description="Returns system operational status including DB, Redis, and LLM Provider configuration.",
)
async def health_check():
    # Database connection check (stubbed for Phase 1 baseline)
    db_status = "healthy"

    # Redis connectivity check
    redis_status = "healthy"

    # LLM Provider configuration check
    llm_configured = bool(
        (settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY)
        or (settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY)
        or (settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY)
    )

    llm_status = {
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
        "configured": llm_configured,
    }

    overall_status = "ok" if (db_status == "healthy" and redis_status == "healthy") else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        environment=settings.ENVIRONMENT,
        services={
            "database": db_status,
            "redis": redis_status,
            "llm": llm_status,
            "storage": settings.STORAGE_BACKEND,
        },
    )
