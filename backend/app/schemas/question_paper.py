from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    NUMERICAL = "numerical"
    TRUE_FALSE = "true_false"
    DIAGRAM_BASED = "diagram_based"
    CASE_STUDY = "case_study"


class BloomLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class Question(BaseModel):
    id: str = Field(description="Unique question identifier")
    question_number: str = Field(description="Question number/label e.g., '1(a)' or 'Q3'")
    section: Optional[str] = Field(default=None, description="Section header e.g. 'Section A'")
    text: str = Field(description="Full text content of the question")
    sub_questions: List[Question] = Field(default_factory=list, description="Nested sub-questions")
    marks: Optional[float] = Field(default=None, description="Marks allocated for this question")
    question_type: QuestionType = Field(description="Categorized question type")
    topic_hint: Optional[str] = Field(default=None, description="LLM inferred topic hint")
    linked_topic_id: Optional[str] = Field(
        default=None, description="Resolved topic ID against CurriculumHierarchy"
    )
    bloom_level: Optional[BloomLevel] = Field(
        default=None, description="Inferred Bloom's Taxonomy level"
    )
    has_diagram: bool = Field(default=False, description="Flag indicating presence of diagram/figure")
    has_table: bool = Field(default=False, description="Flag indicating presence of tabular data")
    options: Optional[List[str]] = Field(default=None, description="Options if question is MCQ")
    source_page: int = Field(description="Page number in original document where question appears")
    source_document_id: str = Field(description="ID of source document")


class QuestionPaperExtraction(BaseModel):
    exam_name: Optional[str] = Field(default=None, description="Exam title e.g. Mid-Term Examination 2024")
    subject_name: Optional[str] = Field(default=None, description="Subject name")
    year: Optional[int] = Field(default=None, description="Year of examination")
    total_marks: Optional[float] = Field(default=None, description="Maximum total marks")
    duration_minutes: Optional[int] = Field(default=None, description="Duration in minutes")
    questions: List[Question] = Field(default_factory=list, description="Extracted questions")
    extraction_confidence: float = Field(
        ge=0.0, le=1.0, description="Model self-reported confidence score (0-1)"
    )


# Rebuild model for recursive typing in Question
Question.model_rebuild()
