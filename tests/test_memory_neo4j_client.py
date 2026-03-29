"""Tests for italianollama.memory.neo4j_client module."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from italianollama.memory.neo4j_client import Neo4jClient


def make_mock_driver():
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value={"id": "element-id-123", "n": 1})
    mock_result.data = AsyncMock(return_value=[{"word": "ciao", "translation": "hello"}])
    mock_result.consume = AsyncMock()
    mock_session.run = AsyncMock(return_value=mock_result)

    mock_driver = MagicMock()
    mock_driver.close = AsyncMock()
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_driver.session.return_value.__aexit__ = AsyncMock(return_value=None)

    return mock_driver, mock_session, mock_result


class TestNeo4jClientInit:
    def test_default_values(self):
        client = Neo4jClient()
        assert client.uri == "bolt://localhost:7687"
        assert client.user == "neo4j"
        assert client.password == ""
        assert client.database == "neo4j"
        assert client._driver is None

    def test_custom_values(self):
        client = Neo4jClient(
            uri="bolt://remote:7687",
            user="admin",
            password="secret",
            database="testdb",
        )
        assert client.uri == "bolt://remote:7687"
        assert client.user == "admin"
        assert client.password == "secret"
        assert client.database == "testdb"


class TestNeo4jClientConnect:
    @pytest.mark.asyncio
    async def test_connect_creates_driver(self):
        client = Neo4jClient()
        mock_driver = MagicMock()

        with patch(
            "italianollama.memory.neo4j_client.AsyncGraphDatabase.driver",
            return_value=mock_driver,
        ):
            result = await client.connect()

        assert client._driver is not None
        assert result is client

    @pytest.mark.asyncio
    async def test_connect_idempotent(self):
        client = Neo4jClient()
        mock_driver = MagicMock()

        with patch(
            "italianollama.memory.neo4j_client.AsyncGraphDatabase.driver",
            return_value=mock_driver,
        ) as mock_factory:
            await client.connect()
            await client.connect()

        # Should only create driver once
        mock_factory.assert_called_once()


class TestNeo4jClientClose:
    @pytest.mark.asyncio
    async def test_close_driver(self):
        client = Neo4jClient()
        mock_driver = AsyncMock()
        client._driver = mock_driver

        await client.close()
        mock_driver.close.assert_called_once()
        assert client._driver is None

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self):
        client = Neo4jClient()
        # Should not raise
        await client.close()


class TestVerifyConnectivity:
    @pytest.mark.asyncio
    async def test_verify_connectivity(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        result = await client.verify_connectivity()
        assert result is True


class TestCreateStudent:
    @pytest.mark.asyncio
    async def test_create_student(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.single = AsyncMock(return_value={"id": "element-id-123"})
        client._driver = mock_driver

        result = await client.create_student("student123", "Mario Rossi")
        assert result == "element-id-123"
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_student_returns_none_if_no_record(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.single = AsyncMock(return_value=None)
        client._driver = mock_driver

        result = await client.create_student("student123", "Mario")
        assert result is None


class TestGetStudent:
    @pytest.mark.asyncio
    async def test_get_existing_student(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.single = AsyncMock(return_value={
            "student_id": "s1",
            "name": "Mario",
            "level": "B1",
            "level_confidence": 0.9,
            "vocab_count": 50,
            "exercise_count": 10,
            "created_at": "2024-01-01",
        })
        client._driver = mock_driver

        result = await client.get_student("s1")
        assert result["student_id"] == "s1"
        assert result["level"] == "B1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_student(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.single = AsyncMock(return_value=None)
        client._driver = mock_driver

        result = await client.get_student("nonexistent")
        assert result is None


class TestSetStudentLevel:
    @pytest.mark.asyncio
    async def test_set_level(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.set_student_level("s1", "B2", confidence=0.85)
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_level_default_confidence(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.set_student_level("s1", "A1")
        mock_session.run.assert_called_once()


class TestAddVocabulary:
    @pytest.mark.asyncio
    async def test_add_vocabulary(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.add_vocabulary("s1", "gatto", "cat", topic="animals", level="A1")
        mock_session.run.assert_called_once()


class TestGetStudentVocabulary:
    @pytest.mark.asyncio
    async def test_get_vocabulary(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.data = AsyncMock(return_value=[
            {"word": "gatto", "translation": "cat", "topic": "animals", "confidence": 0.8}
        ])
        client._driver = mock_driver

        result = await client.get_student_vocabulary("s1")
        assert len(result) == 1
        assert result[0]["word"] == "gatto"

    @pytest.mark.asyncio
    async def test_get_vocabulary_empty(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.data = AsyncMock(return_value=[])
        client._driver = mock_driver

        result = await client.get_student_vocabulary("s1")
        assert result == []


class TestUpdateVocabularyConfidence:
    @pytest.mark.asyncio
    async def test_update_confidence(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.update_vocabulary_confidence("s1", "gatto", 0.9)
        mock_session.run.assert_called_once()


class TestRecordGrammarError:
    @pytest.mark.asyncio
    async def test_record_error(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.record_grammar_error("s1", "io sono andato", "sono andato", "pronoun", "A2")
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_error_default_level(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.record_grammar_error("s1", "bad", "good", "article")
        mock_session.run.assert_called_once()


class TestGetCommonErrors:
    @pytest.mark.asyncio
    async def test_get_errors(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.data = AsyncMock(return_value=[
            {"rule": "verb", "original": "bad", "corrected": "good", "seen_count": 3}
        ])
        client._driver = mock_driver

        result = await client.get_common_errors("s1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_errors_empty(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.data = AsyncMock(return_value=[])
        client._driver = mock_driver

        result = await client.get_common_errors("s1")
        assert result == []


class TestRecordExercise:
    @pytest.mark.asyncio
    async def test_record_exercise(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.record_exercise("s1", "grammar", 85, "B1", content="exercise content")
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_exercise_no_content(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.record_exercise("s1", "vocabulary", 90, "A2")
        mock_session.run.assert_called_once()


class TestGetExerciseHistory:
    @pytest.mark.asyncio
    async def test_get_history(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.data = AsyncMock(return_value=[
            {"type": "grammar", "score": 85, "level": "B1", "completed_at": "2024-01-01"}
        ])
        client._driver = mock_driver

        result = await client.get_exercise_history("s1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_history_empty(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        mock_result.data = AsyncMock(return_value=[])
        client._driver = mock_driver

        result = await client.get_exercise_history("s1")
        assert result == []


class TestRecordNiveauTest:
    @pytest.mark.asyncio
    async def test_record_niveau_test(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.record_niveau_test(
            "s1", "TELC", "B2", 0.75,
            {"reading": {"score": 80, "total": 1}}
        )
        mock_session.run.assert_called_once()


class TestSetupSchema:
    @pytest.mark.asyncio
    async def test_setup_schema(self):
        client = Neo4jClient()
        mock_driver, mock_session, mock_result = make_mock_driver()
        client._driver = mock_driver

        await client.setup_schema()
        assert mock_session.run.call_count >= 1
