"""Unit tests for Neo4j client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.memory.neo4j_client import Neo4jClient


class TestNeo4jClient:
    """Tests for the Neo4j client."""

    @pytest.fixture
    def neo4j_client(self):
        """Create a Neo4j client instance."""
        return Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="test_password",
            database="testdb",
        )

    @pytest.fixture
    def mock_driver(self):
        """Create a mock driver with session."""
        with patch("italianollama.memory.neo4j_client.AsyncGraphDatabase.driver") as mock_driver:
            mock_session = MagicMock()
            mock_session.run = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_driver_instance = MagicMock()
            mock_driver_instance.session = MagicMock(return_value=mock_session)
            mock_driver.return_value = mock_driver_instance

            yield mock_driver_instance

    def test_neo4j_client_init(self):
        """Test Neo4j client initialization."""
        client = Neo4jClient()
        assert client.uri == "bolt://localhost:7687"
        assert client.user == "neo4j"
        assert client.password == ""
        assert client.database == "neo4j"
        assert client._driver is None

    def test_neo4j_client_init_custom(self):
        """Test Neo4j client with custom parameters."""
        client = Neo4jClient(
            uri="bolt://custom:7687",
            user="custom_user",
            password="secret",
            database="mydb",
        )
        assert client.uri == "bolt://custom:7687"
        assert client.user == "custom_user"
        assert client.password == "secret"
        assert client.database == "mydb"

    @pytest.mark.asyncio
    async def test_neo4j_client_connect(self, neo4j_client):
        """Test Neo4j client connect method."""
        with patch("italianollama.memory.neo4j_client.AsyncGraphDatabase.driver") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance

            await neo4j_client.connect()

            assert neo4j_client._driver is not None
            mock_driver.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_close(self, neo4j_client):
        """Test Neo4j client close method."""
        with patch("italianollama.memory.neo4j_client.AsyncGraphDatabase.driver") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver_instance.close = AsyncMock()
            mock_driver.return_value = mock_driver_instance

            await neo4j_client.connect()
            await neo4j_client.close()

            mock_driver_instance.close.assert_called_once()
            assert neo4j_client._driver is None

    @pytest.mark.asyncio
    async def test_neo4j_client_verify_connectivity(self, neo4j_client, mock_driver):
        """Test Neo4j client verify connectivity."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.consume = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.verify_connectivity()

        assert result is True

    @pytest.mark.asyncio
    async def test_neo4j_client_create_student(self, neo4j_client, mock_driver):
        """Test Neo4j client create student."""
        neo4j_client._driver = mock_driver

        mock_record = {"id": "node_123"}

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.create_student("student_1", "Mario Rossi")

        assert result == "node_123"

    @pytest.mark.asyncio
    async def test_neo4j_client_get_student(self, neo4j_client, mock_driver):
        """Test Neo4j client get student."""
        neo4j_client._driver = mock_driver

        mock_record = {
            "student_id": "student_1",
            "name": "Mario Rossi",
            "level": "B1",
            "level_confidence": 0.9,
            "vocab_count": 50,
            "exercise_count": 20,
        }

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.get_student("student_1")

        assert result is not None
        assert result["student_id"] == "student_1"

    @pytest.mark.asyncio
    async def test_neo4j_client_get_student_not_found(self, neo4j_client, mock_driver):
        """Test Neo4j client get student when not found."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.get_student("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_neo4j_client_set_student_level(self, neo4j_client, mock_driver):
        """Test Neo4j client set student level."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.set_student_level("student_1", "B2", 0.85)

        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_add_vocabulary(self, neo4j_client, mock_driver):
        """Test Neo4j client add vocabulary."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.add_vocabulary(
            "student_1",
            "ciao",
            "hello",
            "greetings",
            "A1",
        )

        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_get_student_vocabulary(self, neo4j_client, mock_driver):
        """Test Neo4j client get student vocabulary."""
        neo4j_client._driver = mock_driver

        mock_data = [
            {"word": "ciao", "translation": "hello", "topic": "greetings", "confidence": 0.5},
            {"word": "grazie", "translation": "thank you", "topic": "greetings", "confidence": 0.7},
        ]

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=mock_data)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.get_student_vocabulary("student_1")

        assert len(result) == 2
        assert result[0]["word"] == "ciao"

    @pytest.mark.asyncio
    async def test_neo4j_client_update_vocabulary_confidence(self, neo4j_client, mock_driver):
        """Test Neo4j client update vocabulary confidence."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.update_vocabulary_confidence("student_1", "ciao", 0.8)

        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_record_grammar_error(self, neo4j_client, mock_driver):
        """Test Neo4j client record grammar error."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.record_grammar_error(
            "student_1",
            "io avere",
            "io ho",
            "verb_conjugation",
            "A2",
        )

        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_get_common_errors(self, neo4j_client, mock_driver):
        """Test Neo4j client get common errors."""
        neo4j_client._driver = mock_driver

        mock_data = [
            {"rule": "verb_conjugation", "original": "io avere", "corrected": "io ho", "seen_count": 3}
        ]

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=mock_data)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.get_common_errors("student_1")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_neo4j_client_record_exercise(self, neo4j_client, mock_driver):
        """Test Neo4j client record exercise."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.record_exercise(
            "student_1",
            "vocabulary",
            85,
            "A2",
        )

        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_get_exercise_history(self, neo4j_client, mock_driver):
        """Test Neo4j client get exercise history."""
        neo4j_client._driver = mock_driver

        mock_data = [
            {"type": "vocabulary", "score": 85, "level": "A2"}
        ]

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=mock_data)
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        result = await neo4j_client.get_exercise_history("student_1")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_neo4j_client_record_niveau_test(self, neo4j_client, mock_driver):
        """Test Neo4j client record niveau test."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.record_niveau_test(
            "student_1",
            "TELC",
            "B1",
            0.75,
            {"reading": 80, "writing": 70},
        )

        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_client_setup_schema(self, neo4j_client, mock_driver):
        """Test Neo4j client setup schema."""
        neo4j_client._driver = mock_driver

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = MagicMock(return_value=mock_session)

        await neo4j_client.setup_schema()

        # Should run multiple constraints and indexes
        assert mock_session.run.call_count >= 5
