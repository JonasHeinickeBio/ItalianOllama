"""Integration tests for full Neo4j data model.

Tests the complete student data model including:
- Student profile with all attributes
- Vocabulary (multiple words with confidence)
- Grammar errors (various rules with context)
- Exercises (multiple attempts with XP)
- Placement tests (sessions and results)
- Chat messages (conversation history)
- Learning sessions (flashcard reviews)
- Analytics (velocity, stats, knowledge graph)
"""

import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from italianollama.memory.neo4j_client import Neo4jClient

load_dotenv()


class TestFullStudentDataModel:
    """Test complete student data model with all data points."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create and setup Neo4j client."""
        client = Neo4jClient(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE"),
        )
        await client.connect()
        await client.setup_schema()
        yield client
        await client.close()

    @pytest.mark.asyncio
    async def test_full_student_workflow(self, client):
        """Test complete student workflow with all data points."""
        student_id = "test_student_integration_001"

        try:
            await client.create_student(
                student_id=student_id,
                name="Test Student",
                native_language="English",
            )

            student = await client.get_student(student_id)
            assert student is not None
            assert student["student_id"] == student_id
            assert student["name"] == "Test Student"
            assert student["native_language"] == "English"

            await client.set_student_level(
                student_id=student_id,
                level="A2",
                confidence=0.85,
            )

            await client.add_vocabulary(
                student_id=student_id,
                word="ciao",
                definition="hello",
                topic="greetings",
                confidence=0.6,
            )

            await client.add_vocabulary(
                student_id=student_id,
                word="grazie",
                definition="thank you",
                topic="greetings",
                confidence=0.4,
            )

            await client.add_vocabulary(
                student_id=student_id,
                word="per favore",
                definition="please",
                topic="politeness",
                confidence=0.5,
            )

            vocab_list = await client.get_vocabulary(student_id, limit=50)
            assert len(vocab_list) >= 3

            words_found = [v["word"] for v in vocab_list]
            assert "ciao" in words_found
            assert "grazie" in words_found

            await client.add_exercise(
                student_id=student_id,
                exercise_type="vocabulary",
                level="A2",
                score=85,
                xp_earned=10,
            )

            await client.add_exercise(
                student_id=student_id,
                exercise_type="grammar",
                level="A2",
                score=75,
                xp_earned=8,
            )

            exercise_history = await client.get_exercise_history(student_id, limit=20)
            assert len(exercise_history) >= 2

            exercise_types = [e["type"] for e in exercise_history]
            assert "vocabulary" in exercise_types
            assert "grammar" in exercise_types

            await client.add_grammar_error(
                student_id=student_id,
                rule="gender agreement",
                context="La macchina rosso",
                correction="La macchina rossa",
            )

            await client.add_grammar_error(
                student_id=student_id,
                rule="verb conjugation",
                context="Io sono avere fame",
                correction="Io ho fame",
            )

            errors = await client.get_common_errors(student_id, limit=10)
            assert len(errors) >= 2

            rules_found = [e["rule"] for e in errors]
            assert "gender agreement" in rules_found
            assert "verb conjugation" in rules_found

            session_id = await client.create_session(
                student_id=student_id,
                session_type="flashcard_review",
                details={"topic": "greetings", "duration": 300},
            )
            assert session_id is not None

            session_updated = await client.update_session(
                session_id=session_id,
                words_reviewed=10,
                correct_answers=8,
                accuracy=0.8,
                duration_seconds=300,
            )
            assert session_updated is True

            session_history = await client.get_session_history(student_id, limit=10)
            assert len(session_history) >= 1

            session_types = [s["session_type"] for s in session_history]
            assert "flashcard_review" in session_types

            session_result = await client.create_test_session(student_id, "session_001")
            assert session_result is not None

            test_result_id = await client.create_test_result(
                student_id=student_id,
                total_correct=22,
                total_questions=30,
                scores_by_section={"reading": 80, "listening": 70, "grammar": 75},
                determined_level="A2",
            )
            assert test_result_id is not None

            placement_history = await client.get_placement_history(student_id)
            assert len(placement_history) >= 1

            first_result = placement_history[0]
            assert first_result["determined_level"] == "A2"
            assert first_result["score_percentage"] == 73.3

            await client.record_niveau_test(
                student_id=student_id,
                test_type="placement",
                level="A2",
                readiness=0.75,
                skill_scores={"reading": 80, "listening": 70, "grammar": 75, "writing": 65},
            )

            test_readiness = await client.get_test_readiness(student_id)
            assert len(test_readiness) >= 1

            chat_msg1 = await client.save_chat_message(
                student_id=student_id,
                user_content="Ciao, come stai?",
                assistant_content="Ciao! Sto bene, grazie. E tu?",
                session_id="chat_001",
            )
            assert chat_msg1 is not None

            chat_msg2 = await client.save_chat_message(
                student_id=student_id,
                user_content=" Sto bene anch'io. Voglio imparare l'italiano.",
                assistant_content="Fantastico! Quali argomenti ti interessano?",
                session_id="chat_001",
            )
            assert chat_msg2 is not None

            chat_history = await client.get_chat_history(student_id, limit=50)
            assert len(chat_history) >= 2

            user_messages = [m["user_content"] for m in chat_history]
            assert any("Ciao, come stai?" in msg for msg in user_messages)

            velocity = await client.get_learning_velocity(student_id, days=7)
            assert "exercises_completed" in velocity
            assert "velocity" in velocity

            stats = await client.get_student_stats(student_id)
            assert "total_exercises" in stats
            assert "total_vocab" in stats
            assert "current_level" in stats

            knowledge_graph = await client.get_knowledge_graph(student_id, max_nodes=100)
            assert "nodes" in knowledge_graph
            assert "links" in knowledge_graph

            struggling = await client.get_struggling_concepts(student_id, threshold=0.6)
            assert isinstance(struggling, list)

            final_student = await client.get_student(student_id)
            assert final_student["vocab_count"] >= 3
            assert final_student["exercise_count"] >= 2

        finally:
            cleanup_query = """
            MATCH (s:Student {student_id: $student_id})
            DETACH DELETE s
            """
            async with client._driver.session(database=client.database) as session:
                await session.run(cleanup_query, student_id=student_id)

    @pytest.mark.asyncio
    async def test_multiple_students_comparative(self, client):
        """Test multiple students with different data patterns."""
        student_ids = [
            "test_student_001",
            "test_student_002",
            "test_student_003",
        ]

        try:
            for i, student_id in enumerate(student_ids):
                await client.create_student(
                    student_id=student_id,
                    name=f"Student {i+1}",
                    native_language="English",
                )

                await client.set_student_level(
                    student_id=student_id,
                    level="A1" if i < 2 else "B1",
                    confidence=0.8 + (i * 0.05),
                )

                for j, word in enumerate(["ciao", "grazie", "per favore"]):
                    await client.add_vocabulary(
                        student_id=student_id,
                        word=word,
                        definition=f"definition {j}",
                        topic="greetings",
                        confidence=0.5 + (j * 0.1),
                    )

                await client.add_exercise(
                    student_id=student_id,
                    exercise_type="vocabulary",
                    level="A1" if i < 2 else "B1",
                    score=80 + (i * 5),
                    xp_earned=10,
                )

            for student_id in student_ids:
                student = await client.get_student(student_id)
                assert student is not None
                assert student["level"] is not None

                vocab = await client.get_vocabulary(student_id, limit=10)
                assert len(vocab) >= 3

            for student_id in student_ids:
                errors = await client.get_common_errors(student_id)
                assert isinstance(errors, list)

                stats = await client.get_student_stats(student_id)
                assert stats["total_exercises"] >= 1

        finally:
            cleanup_query = """
            MATCH (s:Student)
            WHERE s.student_id STARTS WITH 'test_student_'
            DETACH DELETE s
            """
            async with client._driver.session(database=client.database) as session:
                await session.run(cleanup_query)

    @pytest.mark.asyncio
    async def test_cypher_validation_queries(self, client):
        """Test specific Cypher queries to validate data model correctness."""
        student_id = "cypher_test_student"

        try:
            await client.create_student(
                student_id=student_id,
                name="Cypher Test",
                native_language="English",
            )

            await client.set_student_level(student_id, "A2", 0.85)

            for word in ["ciao", "grazie", "per favore", "buongiorno"]:
                await client.add_vocabulary(
                    student_id=student_id,
                    word=word,
                    definition="test",
                    topic="greetings",
                    confidence=0.5,
                )

            for i in range(3):
                await client.add_exercise(
                    student_id=student_id,
                    exercise_type=["vocabulary", "grammar", "listening"][i],
                    level="A2",
                    score=75 + (i * 5),
                    xp_earned=10,
                )

            async with client._driver.session(database=client.database) as session:
                query = """
                MATCH (s:Student {student_id: $student_id})
                RETURN s.name AS name, s.native_language AS native_language,
                       s.total_xp AS total_xp, s.current_streak AS current_streak
                """
                result = await session.run(query, student_id=student_id)
                record = await result.single()
                assert record["name"] == "Cypher Test"
                assert record["native_language"] == "English"

                query = """
                MATCH (s:Student {student_id: $student_id})-[rel:HAS_PLACEMENT_LEVEL]->(l:CEFRLevel)
                RETURN l.name AS level, rel.confidence AS confidence
                """
                result = await session.run(query, student_id=student_id)
                record = await result.single()
                assert record["level"] == "A2"
                assert record["confidence"] == 0.85

                query = """
                MATCH (s:Student {student_id: $student_id})-[rel:KNOWS]->(v:Vocabulary)
                RETURN v.word AS word, rel.confidence AS confidence
                ORDER BY rel.confidence DESC
                """
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                assert len(records) >= 4
                assert records[0]["word"] == "ciao"

                query = """
                MATCH (s:Student {student_id: $student_id})-[:COMPLETED]->(e:Exercise)
                RETURN e.type AS type, e.score AS score
                ORDER BY e.completed_at DESC
                """
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                assert len(records) >= 3
                types = [r["type"] for r in records]
                assert "vocabulary" in types
                assert "grammar" in types

                query = """
                MATCH (s:Student {student_id: $student_id})-[rel:MADE_ERROR]->(err:GrammarError)
                RETURN err.rule AS rule, err.context AS context
                """
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                assert len(records) == 0

                query = """
                MATCH (s:Student {student_id: $student_id})-[:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
                RETURN count(msg) AS message_count
                """
                result = await session.run(query, student_id=student_id)
                record = await result.single()
                assert record["message_count"] == 0

                query = """
                MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
                RETURN sess.session_type AS session_type, sess.accuracy AS accuracy
                """
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                assert len(records) == 0

                query = """
                MATCH (s:Student {student_id: $student_id})-[:HAS_TEST_RESULT]->(r:TestResult)
                RETURN r.determined_level AS level, r.score_percentage AS percentage
                """
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                assert len(records) == 0

                query = """
                MATCH (s:Student {student_id: $student_id})-[:READY_FOR]->(t:NiveauTest)
                RETURN t.test_type AS test_type, t.level AS level
                """
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                assert len(records) == 0

        finally:
            cleanup_query = """
            MATCH (s:Student {student_id: $student_id})
            DETACH DELETE s
            """
            async with client._driver.session(database=client.database) as session:
                await session.run(cleanup_query, student_id=student_id)
