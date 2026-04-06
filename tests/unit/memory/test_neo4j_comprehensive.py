"""Comprehensive unit tests for Neo4j client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.memory.neo4j_client import Neo4jClient


class TestNeo4jClientBasics:
    """Tests for basic Neo4j client operations."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client can be initialized with default params."""
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
            database="neo4j"
        )
        assert client.uri == "bolt://localhost:7687"
        assert client.user == "neo4j"
        assert client.database == "neo4j"
        assert client._driver is None

    @pytest.mark.asyncio
    async def test_client_connect(self):
        """Test client connect method."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        with patch('italianollama.memory.base.AsyncGraphDatabase') as mock_driver_class:
            mock_driver = MagicMock()
            mock_driver_class.driver.return_value = mock_driver
            
            await client.connect()
            
            mock_driver_class.driver.assert_called_once()
            assert client._driver is not None

    @pytest.mark.asyncio
    async def test_client_close(self):
        """Test client close method."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        client._driver = mock_driver
        
        await client.close()
        
        mock_driver.close.assert_called_once()
        assert client._driver is None

    @pytest.mark.asyncio
    async def test_client_close_when_not_connected(self):
        """Test close when already disconnected."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        await client.close()
        
        assert client._driver is None

    @pytest.mark.asyncio
    async def test_verify_connectivity(self):
        """Test connectivity verification."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_result.consume = AsyncMock()
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        result = await client.verify_connectivity()
        
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_connectivity_failure(self):
        """Test connectivity verification fails gracefully."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(side_effect=Exception("Connection failed"))
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        result = await client.verify_connectivity()
        
        assert result is False


class TestStudentManagement:
    """Tests for student management operations."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with driver."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__ = MagicMock(return_value="student_node_123")
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_record)
        mock_result = MagicMock()
        mock_result.single = AsyncMock(return_value=mock_record)
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        return client

    @pytest.mark.asyncio
    async def test_create_student(self, mock_client):
        """Test student creation."""
        result = await mock_client.create_student("student_123", "John Doe")
        
        assert result == "student_node_123"
        mock_client._driver.session.assert_called()

    @pytest.mark.asyncio
    async def test_get_student(self, mock_client):
        """Test getting student info."""
        mock_record = MagicMock()
        mock_record.__getitem__ = lambda self, key: {
            "student_id": "student_123",
            "name": "John Doe",
            "level": "A2",
            "level_confidence": 0.8,
            "vocab_count": 10,
            "exercise_count": 5,
        }.get(key)
        
        mock_client._driver.session.return_value.__aenter__.return_value.run.return_value.single = AsyncMock(return_value=mock_record)
        
        result = await mock_client.get_student("student_123")
        
        assert result is not None
        assert result["student_id"] == "student_123"

    @pytest.mark.asyncio
    async def test_get_student_not_found(self, mock_client):
        """Test getting non-existent student."""
        mock_client._driver.session.return_value.__aenter__.return_value.run.return_value.single = AsyncMock(return_value=None)
        
        result = await mock_client.get_student("nonexistent")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_set_student_level(self, mock_client):
        """Test setting student level."""
        await mock_client.set_student_level("student_123", "B1", 0.9)
        
        mock_client._driver.session.assert_called()


class TestVocabularyManagement:
    """Tests for vocabulary operations."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock()
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        return client

    @pytest.mark.asyncio
    async def test_add_vocabulary(self, mock_client):
        """Test adding vocabulary."""
        await mock_client.add_vocabulary(
            student_id="student_123",
            word="ciao",
            translation="hello",
            topic="greetings",
            level="A1"
        )
        
        mock_client._driver.session.assert_called()

    @pytest.mark.asyncio
    async def test_get_student_vocabulary(self, mock_client):
        """Test getting student vocabulary."""
        mock_record = [
            {"word": "ciao", "translation": "hello", "topic": "greetings", "confidence": 0.5},
            {"word": "grazie", "translation": "thank you", "topic": "greetings", "confidence": 0.7},
        ]
        
        mock_result = MagicMock()
        mock_result.data = AsyncMock(return_value=mock_record)
        mock_client._driver.session.return_value.__aenter__.return_value.run = AsyncMock(return_value=mock_result)
        
        result = await mock_client.get_student_vocabulary("student_123")
        
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_update_vocabulary_confidence(self, mock_client):
        """Test updating vocabulary confidence."""
        await mock_client.update_vocabulary_confidence(
            student_id="student_123",
            word="ciao",
            confidence=0.8
        )
        
        mock_client._driver.session.assert_called()


class TestGrammarErrors:
    """Tests for grammar error tracking."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock()
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        return client

    @pytest.mark.asyncio
    async def test_record_grammar_error(self, mock_client):
        """Test recording grammar error."""
        await mock_client.record_grammar_error(
            student_id="student_123",
            original="Io avere fame",
            corrected="Ho fame",
            rule="verb conjugation",
            level="A2"
        )
        
        mock_client._driver.session.assert_called()

    @pytest.mark.asyncio
    async def test_get_common_errors(self, mock_client):
        """Test getting common errors."""
        mock_record = [
            {"rule": "verb conjugation", "original": "avere", "corrected": "essere", "seen_count": 5}
        ]
        
        mock_result = MagicMock()
        mock_result.data = AsyncMock(return_value=mock_record)
        mock_client._driver.session.return_value.__aenter__.return_value.run = AsyncMock(return_value=mock_result)
        
        result = await mock_client.get_common_errors("student_123")
        
        assert len(result) == 1


class TestExercises:
    """Tests for exercise operations."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock()
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        return client

    @pytest.mark.asyncio
    async def test_record_exercise(self, mock_client):
        """Test recording exercise."""
        await mock_client.record_exercise(
            student_id="student_123",
            exercise_type="vocabulary",
            score=85,
            level="A2"
        )
        
        mock_client._driver.session.assert_called()

    @pytest.mark.asyncio
    async def test_get_exercise_history(self, mock_client):
        """Test getting exercise history."""
        mock_record = [
            {"type": "vocabulary", "score": 85, "level": "A2"}
        ]
        
        mock_result = MagicMock()
        mock_result.data = AsyncMock(return_value=mock_record)
        mock_client._driver.session.return_value.__aenter__.return_value.run = AsyncMock(return_value=mock_result)
        
        result = await mock_client.get_exercise_history("student_123")
        
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_student_stats(self, mock_client):
        """Test getting student stats."""
        mock_record = MagicMock()
        mock_record.__getitem__ = MagicMock(return_value={
            "total_exercises": 10,
            "avg_score": 85.5,
            "total_vocab": 50,
            "total_errors": 5,
        })
        
        mock_result = MagicMock()
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_client._driver.session.return_value.__aenter__.return_value.run = AsyncMock(return_value=mock_result)
        
        result = await mock_client.get_student_stats("student_123")
        
        assert "total_exercises" in result


class TestNiveauTest:
    """Tests for niveau test operations."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock()
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        return client

    @pytest.mark.asyncio
    async def test_record_niveau_test(self, mock_client):
        """Test recording niveau test."""
        await mock_client.record_niveau_test(
            student_id="student_123",
            test_type="TELC",
            level="B1",
            readiness=0.75,
            skill_scores={"reading": 80, "writing": 70}
        )
        
        mock_client._driver.session.assert_called()

    @pytest.mark.asyncio
    async def test_get_test_readiness(self, mock_client):
        """Test getting test readiness."""
        mock_record = [
            {"type": "TELC", "readiness": 0.75, "skills": {"reading": 80}}
        ]
        
        mock_result = MagicMock()
        mock_result.data = AsyncMock(return_value=mock_record)
        mock_client._driver.session.return_value.__aenter__.return_value.run = AsyncMock(return_value=mock_result)
        
        result = await mock_client.get_test_readiness("student_123")
        
        assert len(result) == 1


class TestSchema:
    """Tests for schema setup."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        
        mock_driver = MagicMock()
        mock_session = MagicMock()
        
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock()
        
        mock_driver.session = MagicMock(return_value=mock_session)
        client._driver = mock_driver
        
        return client

    @pytest.mark.asyncio
    async def test_setup_schema(self, mock_client):
        """Test schema setup runs without error."""
        await mock_client.setup_schema()
