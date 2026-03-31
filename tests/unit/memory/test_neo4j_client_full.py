"""Additional tests for neo4j_client module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestNeo4jClientFull:
    """Additional tests for Neo4jClient."""

    @pytest.mark.asyncio
    async def test_set_student_level(self):
        """Test setting student level."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.set_student_level("student1", "B1", 0.9)

        assert mock_session.run.called

    @pytest.mark.asyncio
    async def test_add_vocabulary(self):
        """Test adding vocabulary."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.add_vocabulary("student1", "ciao", "hello", "greetings", "A1")

        assert mock_session.run.called

    @pytest.mark.asyncio
    async def test_get_student_vocabulary(self):
        """Test getting student vocabulary."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=[
            {"word": "ciao", "translation": "hello"}
        ])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        result = await client.get_student_vocabulary("student1")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_update_vocabulary_confidence(self):
        """Test updating vocabulary confidence."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.update_vocabulary_confidence("student1", "ciao", 0.8)

        assert mock_session.run.called

    @pytest.mark.asyncio
    async def test_record_grammar_error(self):
        """Test recording grammar error."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.record_grammar_error("student1", "io sono", "sono", "verb_conjugation")

        assert mock_session.run.called

    @pytest.mark.asyncio
    async def test_get_common_errors(self):
        """Test getting common errors."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=[
            {"rule": "verb_conjugation", "seen_count": 3}
        ])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        result = await client.get_common_errors("student1")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_record_exercise(self):
        """Test recording exercise."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.record_exercise("student1", "vocabulary", 85, "A2")

        assert mock_session.run.called

    @pytest.mark.asyncio
    async def test_get_exercise_history(self):
        """Test getting exercise history."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=[
            {"type": "vocabulary", "score": 85}
        ])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        result = await client.get_exercise_history("student1")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_record_niveau_test(self):
        """Test recording niveau test."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.record_niveau_test("student1", "TELC", "B1", 0.75, {"reading": 80})

        assert mock_session.run.called

    @pytest.mark.asyncio
    async def test_setup_schema(self):
        """Test setup schema."""
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient()
        client._driver = MagicMock()
        
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        client._driver.session = MagicMock(return_value=mock_session)

        await client.setup_schema()

        assert mock_session.run.called
