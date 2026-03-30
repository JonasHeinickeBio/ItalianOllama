"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_neo4j_client():
    """Create a mock Neo4j client with all required methods."""
    client = MagicMock()
    
    # Set up async methods as AsyncMocks
    client.connect = AsyncMock()
    client.close = AsyncMock()
    client.verify_connectivity = AsyncMock(return_value=True)
    client.create_student = AsyncMock(return_value="student_node_id")
    client.get_student = AsyncMock(return_value={
        "student_id": "test_student",
        "name": "Test Student",
        "level": "A2",
        "level_confidence": 0.8,
        "vocab_count": 10,
        "exercise_count": 5,
    })
    client.set_student_level = AsyncMock()
    client.add_vocabulary = AsyncMock()
    client.get_student_vocabulary = AsyncMock(return_value=[
        {"word": "ciao", "translation": "hello", "topic": "greetings", "confidence": 0.5},
        {"word": "grazie", "translation": "thank you", "topic": "greetings", "confidence": 0.7},
    ])
    client.update_vocabulary_confidence = AsyncMock()
    client.record_grammar_error = AsyncMock()
    client.get_common_errors = AsyncMock(return_value=[])
    client.record_exercise = AsyncMock()
    client.get_exercise_history = AsyncMock(return_value=[])
    client.record_niveau_test = AsyncMock()
    client.setup_schema = AsyncMock()
    
    return client


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock()
    
    # Set up async methods
    client.chat = AsyncMock(return_value="Questo è un test di risposta.")
    client.chat_with_json = AsyncMock(return_value={
        "score": 85,
        "feedback": "Good job!",
        "improvements": ["Try using more verbs"],
    })
    
    return client


@pytest.fixture
def sample_tutor_state():
    """Create a sample tutor state for testing."""
    return {
        "student_id": "test_student_123",
        "session_id": "session_456",
        "messages": [
            {"role": "user", "content": "Ciao, come stai?"},
            {"role": "assistant", "content": "Ciao! Sto bene, grazie. E tu?"},
        ],
        "current_level": "A2",
        "level_confidence": 0.8,
        "exercise_type": None,
        "exercise_state": {},
        "response": "",
        "should_continue": True,
    }


@pytest.fixture
def sample_tutor_state_no_level():
    """Create a sample tutor state without a level set."""
    return {
        "student_id": "test_student_123",
        "session_id": "session_456",
        "messages": [
            {"role": "user", "content": "Ciao, voglio imparare l'italiano."},
        ],
        "current_level": None,
        "level_confidence": 0.0,
        "exercise_type": None,
        "exercise_state": {},
        "response": "",
        "should_continue": True,
    }