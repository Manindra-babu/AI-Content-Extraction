from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class LearningOutcome(BaseModel):
    code: Optional[str] = Field(default=None, description="Outcome code, e.g. CO1, LO-02")
    description: str = Field(description="Description of the learning outcome")


class Topic(BaseModel):
    id: str = Field(description="Unique topic identifier")
    title: str = Field(description="Topic title")
    subtopics: List[Topic] = Field(default_factory=list, description="Nested subtopics")
    estimated_hours: Optional[float] = Field(default=None, description="Estimated contact hours")


class Unit(BaseModel):
    id: str = Field(description="Unique unit identifier")
    unit_number: int = Field(description="Sequential unit/module number")
    title: str = Field(description="Unit or module title")
    topics: List[Topic] = Field(default_factory=list, description="Topics within this unit")
    learning_outcomes: List[LearningOutcome] = Field(
        default_factory=list, description="Target learning outcomes"
    )
    credit_hours: Optional[float] = Field(default=None, description="Credit hours allocated")


class Subject(BaseModel):
    id: str = Field(description="Unique subject identifier")
    code: Optional[str] = Field(default=None, description="Subject code, e.g. CS101")
    name: str = Field(description="Full subject name")
    units: List[Unit] = Field(default_factory=list, description="Units/modules in subject")
    reference_books: List[str] = Field(default_factory=list, description="Reference textbooks")
    total_credits: Optional[float] = Field(default=None, description="Total credit points")


class CurriculumHierarchy(BaseModel):
    program_name: str = Field(description="Academic program name, e.g. B.Tech Computer Science")
    semester_or_year: str = Field(description="Semester or year specification")
    subjects: List[Subject] = Field(default_factory=list, description="Extracted subjects")
    source_document_id: str = Field(description="ID of the uploaded source document")
    extraction_confidence: float = Field(
        ge=0.0, le=1.0, description="Model self-reported extraction confidence score (0-1)"
    )


# Rebuild model for recursive typing in Topic
Topic.model_rebuild()
