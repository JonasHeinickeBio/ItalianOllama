"""
Placement test engine for scoring and level determination.

Handles test completion logic, answer validation, and CEFR level assignment.
"""

from datetime import datetime
from typing import Dict, List, Optional

from italianollama.backend.placement_test.models import (
    CEFRLevel,
    PlacementTestConfig,
    PlacementTestResult,
    UserAnswer,
    Question,
)


class PlacementTestEngine:
    """Engine for managing placement test logic and scoring."""

    def __init__(self, test_config: PlacementTestConfig):
        """
        Initialize the test engine.

        Args:
            test_config: PlacementTestConfig with all sections and questions
        """
        self.config = test_config
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate test configuration integrity."""
        if not self.config.sections:
            raise ValueError("Test configuration must have at least one section")

        # Ensure questions are ordered and unique
        all_questions = self.get_all_questions()
        question_ids = [q.id for q in all_questions]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Duplicate question IDs found in configuration")

    def get_all_questions(self) -> List[Question]:
        """Get all questions from all sections."""
        questions = []
        for section in self.config.sections:
            questions.extend(section.questions)
        return questions

    def get_section_questions(self, section_letter: str) -> List[Question]:
        """
        Get questions for a specific section.

        Args:
            section_letter: Section identifier (A-E)

        Returns:
            List of questions in that section
        """
        for section in self.config.sections:
            if section.section_letter == section_letter:
                return section.questions
        return []

    def validate_answer(self, question_id: int, selected_answer: str) -> bool:
        """
        Validate if an answer is correct.

        Args:
            question_id: The question ID
            selected_answer: The user's answer key (a, b, c, d)

        Returns:
            True if answer is correct, False otherwise
        """
        question = self._get_question_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        return selected_answer.lower() == question.correct_answer

    def _get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Get a question by ID."""
        for question in self.get_all_questions():
            if question.id == question_id:
                return question
        return None

    def score_test(
        self,
        answers: Dict[int, str],
        student_id: Optional[str] = None,
    ) -> PlacementTestResult:
        """
        Score a completed test and determine CEFR level.

        Args:
            answers: Dictionary mapping question_id -> selected_answer_key
            student_id: Optional student identifier

        Returns:
            PlacementTestResult with scores and determined level
        """
        all_questions = self.get_all_questions()
        total_correct = 0
        section_scores: Dict[str, int] = {}
        user_answers: List[UserAnswer] = []

        # Score each question and track section performance
        for question in all_questions:
            if question.id not in answers:
                continue

            selected_answer = answers[question.id]
            is_correct = self.validate_answer(question.id, selected_answer)

            # Track answer
            user_answers.append(
                UserAnswer(
                    question_id=question.id,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                    question_level=question.level,
                )
            )

            if is_correct:
                total_correct += 1

            # Track section scores
            section = question.section
            if section not in section_scores:
                section_scores[section] = 0
            if is_correct:
                section_scores[section] += 1

        # Determine CEFR level based on last passing section
        determined_level = self._determine_level(section_scores)

        return PlacementTestResult(
            student_id=student_id,
            total_questions=len(answers),
            total_correct=total_correct,
            score_percentage=(total_correct / len(answers) * 100) if answers else 0,
            determined_level=determined_level,
            section_scores=section_scores,
            answers=user_answers,
            timestamp=datetime.now().isoformat(),
        )

    def _determine_level(self, section_scores: Dict[str, int]) -> CEFRLevel:
        """
        Determine CEFR level based on section scores.

        CEFR progression: A1 (A) → A2 (B) → B1 (C) → B2 (D) → C1 (E)
        Rule: Last section where score >= passing_score determines level

        Args:
            section_scores: Dictionary mapping section letter -> score

        Returns:
            The determined CEFRLevel
        """
        # Map sections to levels in order
        section_order = [
            ("A", CEFRLevel.A1),
            ("B", CEFRLevel.A2),
            ("C", CEFRLevel.B1),
            ("D", CEFRLevel.B2),
            ("E", CEFRLevel.C1),
        ]

        # Find the last section where the user passed
        highest_passed_level = CEFRLevel.A1  # Default to A1

        for section_letter, level in section_order:
            if section_letter in section_scores:
                # Check if they passed this section (7+ out of 10)
                score = section_scores[section_letter]
                section_obj = next(
                    (s for s in self.config.sections if s.section_letter == section_letter),
                    None,
                )
                if section_obj and score >= section_obj.passing_score:
                    highest_passed_level = level

        return highest_passed_level

    def get_section_summary(self) -> Dict[str, Dict]:
        """
        Get a summary of all sections for UI display.

        Returns:
            Dictionary with section metadata
        """
        summary = {}
        for section in self.config.sections:
            summary[section.section_letter] = {
                "level": section.level.value,
                "name": f"Section {section.section_letter}",
                "question_count": len(section.questions),
                "passing_score": section.passing_score,
            }
        return summary

    def get_question_by_index(self, index: int) -> Optional[Question]:
        """Get question by position index (0-based)."""
        all_questions = self.get_all_questions()
        if 0 <= index < len(all_questions):
            return all_questions[index]
        return None

    def get_random_question(self, exclude_ids: Optional[List[int]] = None) -> Optional[Question]:
        """Get a random question, optionally excluding certain IDs."""
        import random

        all_questions = self.get_all_questions()
        if exclude_ids:
            all_questions = [q for q in all_questions if q.id not in exclude_ids]
        return random.choice(all_questions) if all_questions else None
