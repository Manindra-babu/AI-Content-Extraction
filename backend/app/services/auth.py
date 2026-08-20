import time
import logging
from typing import Dict, List, Tuple
from fastapi import HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import settings

logger = logging.getLogger("auth_service")

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header_scheme)) -> str:
    """
    FastAPI security dependency validating server-to-server integration API keys.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-API-Key request header.",
        )

    if api_key not in settings.VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-API-Key credentials provided.",
        )

    return api_key


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = settings.RATE_LIMIT_PER_MINUTE, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_db: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        # Exclude docs, redoc, openapi, and health check from rate limiting
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/redoc") or path.endswith("/openapi.json") or path.endswith("/health") or path == "/":
            return await call_next(request)

        client_key = request.headers.get("X-API-Key") or request.client.host
        now = time.time()

        # Clean timestamps older than window
        timestamps = self.requests_db.get(client_key, [])
        valid_timestamps = [t for t in timestamps if t > now - self.window_seconds]

        if len(valid_timestamps) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for key={client_key} on path={path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit of {self.max_requests} requests per minute exceeded.",
                        "details": {"window_seconds": self.window_seconds},
                    }
                },
            )

        valid_timestamps.append(now)
        self.requests_db[client_key] = valid_timestamps

        response = await call_next(request)
        return response
