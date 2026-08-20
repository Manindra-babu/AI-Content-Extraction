import pytest
from app.schemas.curriculum import CurriculumHierarchy, Subject, Unit, Topic, LearningOutcome
from app.schemas.question_paper import QuestionPaperExtraction, Question, QuestionType, BloomLevel


def test_curriculum_hierarchy_schema():
    curriculum = CurriculumHierarchy(
        program_name="B.Tech Computer Science",
        semester_or_year="Semester IV",
        subjects=[
            Subject(
                id="subj_cs401",
                code="CS401",
                name="Operating Systems",
                units=[
                    Unit(
                        id="u_1",
                        unit_number=1,
                        title="Process Management",
                        topics=[
                            Topic(
                                id="t_1_1",
                                title="Process Scheduling",
                                subtopics=[
                                    Topic(id="t_1_1_1", title="FCFS & Round Robin", subtopics=[])
                                ],
                                estimated_hours=4.0,
                            )
                        ],
                        learning_outcomes=[
                            LearningOutcome(code="CO1", description="Understand CPU scheduling")
                        ],
                        credit_hours=10.0,
                    )
                ],
                reference_books=["Operating System Concepts by Silberschatz"],
                total_credits=4.0,
            )
        ],
        source_document_id="doc_test_123",
        extraction_confidence=0.98,
    )

    dumped = curriculum.model_dump()
    assert dumped["program_name"] == "B.Tech Computer Science"
    assert len(dumped["subjects"][0]["units"][0]["topics"][0]["subtopics"]) == 1
    assert dumped["subjects"][0]["units"][0]["topics"][0]["subtopics"][0]["title"] == "FCFS & Round Robin"


def test_question_paper_schema():
    paper = QuestionPaperExtraction(
        exam_name="Final Exam 2024",
        subject_name="Operating Systems",
        year=2024,
        total_marks=100.0,
        duration_minutes=180,
        questions=[
            Question(
                id="q1",
                question_number="Q1",
                section="Section A",
                text="What is a deadlock?",
                sub_questions=[],
                marks=5.0,
                question_type=QuestionType.SHORT_ANSWER,
                topic_hint="Deadlocks",
                linked_topic_id="t_2_1",
                bloom_level=BloomLevel.UNDERSTAND,
                has_diagram=False,
                has_table=False,
                options=None,
                source_page=2,
                source_document_id="doc_qp_123",
            )
        ],
        extraction_confidence=0.95,
    )

    dumped = paper.model_dump()
    assert dumped["questions"][0]["question_type"] == "short_answer"
    assert dumped["questions"][0]["bloom_level"] == "understand"
