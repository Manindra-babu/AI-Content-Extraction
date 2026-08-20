FROM python:3.11-slim

WORKDIR /app

# Install system dependencies & OCR packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app /app/app

EXPOSE 8000

# Start Celery worker in background and FastAPI uvicorn in foreground (Free Tier Compatible)
CMD ["sh", "-c", "celery -A app.worker.celery_app worker --loglevel=info & uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
