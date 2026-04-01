"""
Italian Language Placement Test system.

Provides modular, scalable placement test infrastructure for CEFR level determination.

Modules:
    models: Pydantic data models for questions, sections, and results
    question_bank: Question database organized by CEFR level
    test_engine: Scoring engine and level determination logic
"""

from italianollama.backend.placement_test.models import (
    CEFRLevel,
    Question,
    QuestionOption,
    TestSection,
    PlacementTestConfig,
    UserAnswer,
    PlacementTestResult,
)
from italianollama.backend.placement_test.question_bank import get_placement_test
from italianollama.backend.placement_test.test_engine import PlacementTestEngine

__all__ = [
    "CEFRLevel",
    "Question",
    "QuestionOption",
    "TestSection",
    "PlacementTestConfig",
    "UserAnswer",
    "PlacementTestResult",
    "get_placement_test",
    "PlacementTestEngine",
]
