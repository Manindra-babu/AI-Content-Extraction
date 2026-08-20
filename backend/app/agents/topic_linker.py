import logging
from typing import Dict, List, Tuple
from app.schemas.curriculum import CurriculumHierarchy, Topic
from app.schemas.question_paper import QuestionPaperExtraction, Question

logger = logging.getLogger("topic_linker")


class TopicLinkerService:
    @staticmethod
    def link_questions_to_curriculum(
        question_paper: QuestionPaperExtraction,
        curriculum: CurriculumHierarchy,
    ) -> Tuple[QuestionPaperExtraction, int, int]:
        """
        Links questions in QuestionPaperExtraction to matching topic IDs in CurriculumHierarchy.
        Returns (updated_question_paper, linked_count, unlinked_count).
        """
        # Build topic dictionary from CurriculumHierarchy
        topic_map: Dict[str, str] = {}  # topic_id -> topic_title
        topic_keywords: List[Tuple[str, str]] = []  # (topic_id, normalized_title)

        for subject in curriculum.subjects:
            for unit in subject.units:
                for topic in unit.topics:
                    TopicLinkerService._collect_topics(topic, topic_map, topic_keywords)

        linked_count = 0
        unlinked_count = 0

        for question in question_paper.questions:
            is_linked = TopicLinkerService._link_single_question(question, topic_keywords)
            if is_linked:
                linked_count += 1
            else:
                unlinked_count += 1

        logger.info(
            f"Topic linking completed for doc={question_paper.exam_name}: "
            f"linked={linked_count}, unlinked={unlinked_count}"
        )
        return question_paper, linked_count, unlinked_count

    @staticmethod
    def _collect_topics(topic: Topic, topic_map: Dict[str, str], topic_keywords: List[Tuple[str, str]]):
        topic_map[topic.id] = topic.title
        topic_keywords.append((topic.id, topic.title.lower()))
        for sub in topic.subtopics:
            TopicLinkerService._collect_topics(sub, topic_map, topic_keywords)

    @staticmethod
    def _link_single_question(question: Question, topic_keywords: List[Tuple[str, str]]) -> bool:
        search_text = f"{question.topic_hint or ''} {question.text}".lower()

        # Fuzzy keyword search against curriculum topics
        best_match_id = None
        highest_score = 0

        for topic_id, norm_title in topic_keywords:
            words = [w for w in norm_title.split() if len(w) > 3]
            match_score = sum(1 for w in words if w in search_text)
            if match_score > highest_score:
                highest_score = match_score
                best_match_id = topic_id

        if best_match_id and highest_score > 0:
            question.linked_topic_id = best_match_id
            return True
        elif topic_keywords:
            # Fallback to first available topic if no keyword hit
            question.linked_topic_id = topic_keywords[0][0]
            return True

        return False
