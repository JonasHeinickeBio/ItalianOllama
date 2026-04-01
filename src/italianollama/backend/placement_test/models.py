"""
Pydantic models for the Italian Placement Test system.

Provides type-safe data structures for questions, sections, and test configuration.
"""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class CEFRLevel(str, Enum):
    """Common European Framework of Reference levels."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class QuestionOption(BaseModel):
    """Single answer option."""
    key: str = Field(..., description="Option key (a, b, c, d)")
    text: str = Field(..., description="Option text")

    class Config:
        json_schema_extra = {
            "example": {
                "key": "a",
                "text": "prenotare"
            }
        }


class Question(BaseModel):
    """Complete question with metadata."""
    id: int = Field(..., description="Unique question ID")
    level: CEFRLevel = Field(..., description="CEFR level (A1-C1)")
    section: str = Field(..., description="Section letter (A-E)")
    question_text: str = Field(..., description="Question in Italian")
    options: List[QuestionOption] = Field(..., description="Answer options")
    correct_answer: str = Field(..., description="Correct answer key (a, b, c, d)")
    correct_answer_text: str = Field(..., description="Correct answer text")
    grammar_point: str = Field(..., description="Grammar concept being tested")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "level": "A1",
                "section": "A",
                "question_text": "Al ristorante dobbiamo ______ un tavolo.",
                "options": [
                    {"key": "a", "text": "prenotare"},
                    {"key": "b", "text": "cucinare"},
                    {"key": "c", "text": "portare"},
                    {"key": "d", "text": "ordinare"}
                ],
                "correct_answer": "a",
                "correct_answer_text": "prenotare",
                "grammar_point": "Infinitive collocations: prenotare un tavolo"
            }
        }


class TestSection(BaseModel):
    """Section of the placement test."""
    level: CEFRLevel = Field(..., description="CEFR level for this section")
    section_letter: str = Field(..., description="Section identifier (A-E)")
    passing_score: int = Field(default=7, description="Minimum score to advance (out of 10)")
    questions: List[Question] = Field(..., description="Questions in this section")

    class Config:
        json_schema_extra = {
            "example": {
                "level": "A1",
                "section_letter": "A",
                "passing_score": 7,
                "questions": []
            }
        }


class PlacementTestConfig(BaseModel):
    """Configuration and metadata for the entire placement test."""
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    language: str = Field(default="Italian", description="Language being tested")
    version: str = Field(default="1.0.0", description="Test version")
    sections: List[TestSection] = Field(..., description="Test sections by level")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Italian Language Placement Test",
                "description": "50 questions A1–C1",
                "language": "Italian",
                "version": "1.0.0",
                "sections": []
            }
        }


class UserAnswer(BaseModel):
    """User's answer to a question."""
    question_id: int
    selected_answer: str
    is_correct: bool = Field(default=False)
    question_level: CEFRLevel


class PlacementTestResult(BaseModel):
    """Result of a completed placement test."""
    student_id: Optional[str] = None
    total_questions: int
    total_correct: int
    score_percentage: float
    determined_level: CEFRLevel
    section_scores: Dict[str, int] = Field(..., description="Score per section (e.g., {'A': 8, 'B': 7})")
    answers: List[UserAnswer] = Field(default_factory=list, description="All user answers")
    timestamp: Optional[str] = None

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_questions == 0:
            return 0.0
        return round((self.total_correct / self.total_questions) * 100, 1)
