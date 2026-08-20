# AI Content Extraction Services (WML - Work Order 1)

Production-grade AI backend services and admin platform designed for WML to automatically ingest academic documents (syllabi and previous question papers), understand structural metadata via LLMs, and expose queryable, structured REST APIs.

---

## Capabilities

1. **Syllabus → Curriculum Hierarchy Extraction**: Extract structured trees (Program → Semester/Year → Subject → Unit → Topic → Sub-topic) with credit hours, learning outcomes, and reference books.
2. **Question Paper → Question Bank Extraction**: Extract individual questions with metadata (marks, question type, Bloom's level, sub-questions, diagram flags) and link questions directly to curriculum nodes.

---

## Stack Summary

- **Backend:** Python 3.11, FastAPI (Async), Pydantic v2, PydanticAI
- **Database & Queue:** PostgreSQL 16, Redis 7, Celery
- **LLM Providers:** OpenAI (`gpt-4o`, `gpt-4.1`) & Google Gemini (`gemini-2.0-flash`)
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Infrastructure:** Docker, Docker Compose

---

## Quick Start (Local Development)

### 1. Environment Setup
Copy the `.env.example` template:
```bash
cp .env.example .env
```
Update `.env` with your OpenAI or Gemini API keys.

### 2. Launch Stack with Docker Compose
```bash
docker compose -f infra/docker-compose.yml up --build
```

### 3. Access Services
- **FastAPI OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** [http://localhost:8000/v1/health](http://localhost:8000/v1/health)
- **Admin / Demo UI:** [http://localhost:5173](http://localhost:5173)

---

## Backend Unit Tests

Run Pytest suite:
```bash
cd backend
pip install -r requirements.txt
pytest
```
