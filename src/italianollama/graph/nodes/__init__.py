"""This package contains all the LangGraph nodes that handle different
aspects of the Italian tutoring conversation.

Modules:
    base: LLM client wrapper for LiteLLM
    placement: CEFR level assessment
    vocabulary: Flashcard/spaced repetition exercises
    grammar: Grammar drilling with error detection
    translation: Italian <-> English translation practice
    free_writing: Open writing prompts with correction
    niveau_test: CEFR exam preparation (TELC, Goethe, etc.)
"""

from .free_writing import free_writing_node
from .grammar import grammar_node
from .niveau_test import niveau_test_node
from .placement import placement_node
from .translation import translation_node
from .vocabulary import vocabulary_node

__all__ = [
    "placement_node",
    "grammar_node",
    "vocabulary_node",
    "translation_node",
    "free_writing_node",
    "niveau_test_node",
]
