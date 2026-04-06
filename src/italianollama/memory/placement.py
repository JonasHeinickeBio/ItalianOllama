"""Placement test operations."""

import json
import logging

from italianollama.memory.base import Neo4jBaseClient

logger = logging.getLogger(__name__)


class PlacementTestManager(Neo4jBaseClient):
    """Handles placement test sessions and results."""

    async def create_test_session(
        self,
        student_id: str,
        session_id: str,
    ) -> str:
        """Create a new test session.

        Args:
            student_id: Student ID
            session_id: Unique session identifier

        Returns:
            Neo4j element ID
        """
        logger.info(f"📝 Creating test session - session_id={session_id}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        CREATE (sess:TestSession {
            session_id: $session_id,
            student_id: $student_id,
            started_at: datetime(),
            status: 'in_progress'
        })
        MERGE (s)-[:HAS_TEST_SESSION]->(sess)
        RETURN elementId(sess) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                session_id=session_id,
            )
            record = await result.single()
            return record["id"] if record else None

    async def create_test_result(
        self,
        student_id: str,
        total_correct: int,
        total_questions: int,
        scores_by_section: dict,
        determined_level: str,
    ) -> str:
        """Create test result node.

        Args:
            student_id: Student ID
            total_correct: Number of correct answers
            total_questions: Total questions attempted
            scores_by_section: Dict of section -> score
            determined_level: Final CEFR level (A1-C1)

        Returns:
            Element ID of result node
        """
        logger.info(
            f"📊 Creating test result - student_id={student_id}, "
            f"determined_level={determined_level}"
        )
        query = """
        MATCH (s:Student {student_id: $student_id})
        CREATE (r:TestResult {
            student_id: $student_id,
            total_correct: $total_correct,
            total_questions: $total_questions,
            score_percentage: ROUND(toFloat($total_correct) / $total_questions * 100, 1),
            scores_by_section: $scores_by_section,
            determined_level: $determined_level,
            completed_at: datetime()
        })
        MERGE (s)-[:HAS_TEST_RESULT]->(r)
        RETURN elementId(r) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                total_correct=total_correct,
                total_questions=total_questions,
                scores_by_section=json.dumps(scores_by_section),
                determined_level=determined_level,
            )
            record = await result.single()
            return record["id"] if record else None

    async def record_niveau_test(
        self,
        student_id: str,
        test_type: str,
        level: str,
        readiness: float,
        skill_scores: dict,
    ):
        """Record niveau test results.

        Args:
            student_id: Student ID
            test_type: Type of test (placement, checkpoint, etc.)
            level: Determined level
            readiness: Readiness score
            skill_scores: Scores per skill
        """
        logger.info(f"🎯 Recording niveau test - student_id={student_id}, level={level}")
        query = """
        MATCH (s:Student {student_id: $student_id})
        CREATE (t:NiveauTest {
            test_type: $test_type,
            level: $level,
            readiness: $readiness,
            skill_scores: $skill_scores,
            completed_at: datetime()
        })
        MERGE (s)-[:READY_FOR]->(t)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                test_type=test_type,
                level=level,
                readiness=readiness,
                skill_scores=json.dumps(skill_scores),
            )
        logger.info("✓ Niveau test recorded")

    async def get_test_readiness(self, student_id: str) -> list[dict]:
        """Get CEFR test readiness scores.

        Args:
            student_id: Student ID

        Returns:
            List of test readiness records
        """
        logger.debug(f"📋 Fetching test readiness - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[:READY_FOR]->(t:NiveauTest)
        WITH t.test_type AS type, t.readiness AS readiness, t.skill_scores AS skills
        LIMIT 5
        RETURN type, readiness, skills
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            records = await result.data()
            logger.info(f"✓ Retrieved {len(records)} test readiness records")
            return records

    async def get_placement_history(self, student_id: str) -> list[dict]:
        """Get student's placement test history.

        Args:
            student_id: Student ID

        Returns:
            List of placement test results ordered by date
        """
        logger.debug(f"📊 Fetching placement history - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[:HAS_TEST_RESULT]->(r:TestResult)
        RETURN {
            determined_level: r.determined_level,
            score_percentage: r.score_percentage,
            total_correct: r.total_correct,
            total_questions: r.total_questions,
            completed_at: r.completed_at,
            scores_by_section: r.scores_by_section
        } AS result
        ORDER BY r.completed_at DESC
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            records = await result.data()
            return [dict(r["result"]) for r in records]
