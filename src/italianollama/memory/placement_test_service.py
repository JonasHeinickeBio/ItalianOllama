"""
Placement test Neo4j service with modularized helper functions.

Integrates placement test data into the knowledge graph:
- Tests, sections, questions as graph nodes
- Student test sessions and results
- Individual answers with correctness tracking
- CEFR level assignments
- Session history and progress tracking
"""

import logging

from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER: Cypher Query Builders
# ============================================================================


def get_or_create_placement_test_query() -> str:
    """Query to get or create placement test node."""
    return """
    MERGE (t:PlacementTest {name: $name})
    SET t.version = $version,
        t.total_questions = $total_questions,
        t.description = $description,
        t.created_at = COALESCE(datetime(t.created_at), datetime()),
        t.updated_at = datetime()
    RETURN elementId(t) AS test_id
    """


def get_or_create_section_query() -> str:
    """Query to get or create test section node."""
    return """
    MERGE (s:TestSection {section_letter: $section_letter, level: $level})
    SET s.question_count = $question_count,
        s.passing_score = $passing_score,
        s.created_at = COALESCE(datetime(s.created_at), datetime())
    RETURN elementId(s) AS section_id
    """


def get_or_create_question_query() -> str:
    """Query to get or create question node."""
    return """
    MERGE (q:Question {question_id: $question_id})
    SET q.level = $level,
        q.section = $section,
        q.text = $text,
        q.grammar_point = $grammar_point,
        q.created_at = COALESCE(datetime(q.created_at), datetime())
    RETURN elementId(q) AS question_id
    """


def create_answer_node_query() -> str:
    """Query to create individual answer node."""
    return """
    CREATE (a:UserAnswer {
        question_id: $question_id,
        student_id: $student_id,
        selected_answer: $selected_answer,
        is_correct: $is_correct,
        question_level: $question_level,
        answered_at: datetime()
    })
    RETURN elementId(a) AS answer_id
    """


def create_test_result_query() -> str:
    """Query to create test result node."""
    return """
    CREATE (r:TestResult {
        student_id: $student_id,
        determined_level: $determined_level,
        total_correct: $total_correct,
        total_questions: $total_questions,
        score_percentage: $score_percentage,
        completed_at: datetime()
    })
    RETURN elementId(r) AS result_id
    """


def create_test_session_query() -> str:
    """Query to create test session node."""
    return """
    CREATE (ts:TestSession {
        student_id: $student_id,
        test_name: $test_name,
        started_at: datetime(),
        status: 'IN_PROGRESS'
    })
    RETURN elementId(ts) AS session_id
    """


def link_test_to_section_query() -> str:
    """Query to link test to section."""
    return """
    MATCH (t:PlacementTest {name: $test_name})
    MATCH (s:TestSection {level: $level})
    MERGE (t)-[r:HAS_SECTION]->(s)
    RETURN r
    """


def link_section_to_questions_query() -> str:
    """Query to link section to its questions."""
    return """
    MATCH (s:TestSection {section_letter: $section_letter})
    MATCH (q:Question {section: $section_letter})
    MERGE (s)-[r:HAS_QUESTION]->(q)
    RETURN count(r) AS linked_count
    """


def link_result_to_answers_query() -> str:
    """Query to link result to all its answers."""
    return """
    MATCH (r:TestResult {student_id: $student_id})
    MATCH (a:UserAnswer {student_id: $student_id})
    WHERE a.answered_at >= r.completed_at - duration('PT1M')
    MERGE (r)-[rel:HAS_ANSWER]->(a)
    RETURN count(rel) AS linked_count
    """


def link_student_to_result_query() -> str:
    """Query to link student to test result."""
    return """
    MATCH (stu:Student {student_id: $student_id})
    MATCH (r:TestResult {student_id: $student_id})
    WHERE r.completed_at >= COALESCE(stu.last_test_checked, datetime('1970-01-01'))
    MERGE (stu)-[rel:HAS_TEST_RESULT]->(r)
    SET rel.determined_level = r.determined_level,
        rel.score_percentage = r.score_percentage
    RETURN rel
    """


def link_student_to_session_query() -> str:
    """Query to link student to test session."""
    return """
    MATCH (stu:Student {student_id: $student_id})
    MATCH (ts:TestSession {student_id: $student_id})
    MERGE (stu)-[rel:HAS_TEST_SESSION]->(ts)
    RETURN rel
    """


def link_session_to_test_query() -> str:
    """Query to link session to test."""
    return """
    MATCH (ts:TestSession {student_id: $student_id})
    MATCH (t:PlacementTest {name: $test_name})
    MERGE (ts)-[rel:USED_TEST]->(t)
    RETURN rel
    """


def link_student_to_level_query() -> str:
    """Query to link student to determined CEFR level."""
    return """
    MERGE (level:CEFRLevel {name: $level})
    MATCH (stu:Student {student_id: $student_id})
    MERGE (stu)-[rel:HAS_PLACEMENT_LEVEL]->(level)
    SET rel.determined_at = datetime(),
        rel.confidence = $confidence,
        rel.percentage = $percentage
    RETURN rel
    """


# ============================================================================
# HELPER: Neo4j Service Class
# ============================================================================


class PlacementTestNeo4jService:
    """Service for managing placement test data in Neo4j."""

    def __init__(self, neo4j_uri: str, user: str, password: str, database: str = "neo4j"):
        """Initialize the service."""
        self.uri = neo4j_uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None
        logger.info(f"🗂️ Initialized PlacementTestNeo4jService - uri={neo4j_uri}")

    async def connect(self):
        """Connect to Neo4j."""
        if self._driver is None:
            logger.info(f"🔗 Connecting to Neo4j - uri={self.uri}")
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("✓ Connected to Neo4j")
        return self

    async def close(self):
        """Close Neo4j connection."""
        if self._driver:
            logger.info("🔌 Closing Neo4j connection")
            await self._driver.close()
            self._driver = None

    # ========================================================================
    # TEST SETUP HELPERS
    # ========================================================================

    async def _ensure_test_exists(
        self, test_name: str, version: str, total_questions: int, description: str
    ) -> str:
        """Ensure placement test node exists."""
        logger.debug(f"🧪 Ensuring test exists: {test_name}")
        query = get_or_create_placement_test_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                name=test_name,
                version=version,
                total_questions=total_questions,
                description=description,
            )
            record = await result.single()
            test_id = record["test_id"] if record else None
            logger.info(f"✓ Test exists/created: {test_name} (ID: {test_id})")
            return test_id

    async def _ensure_section_exists(
        self, section_letter: str, level: str, question_count: int, passing_score: int
    ) -> str:
        """Ensure test section node exists."""
        logger.debug(f"📊 Ensuring section exists: {section_letter}")
        query = get_or_create_section_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                section_letter=section_letter,
                level=level,
                question_count=question_count,
                passing_score=passing_score,
            )
            record = await result.single()
            section_id = record["section_id"] if record else None
            logger.info(f"✓ Section exists/created: {section_letter} ({level})")
            return section_id

    async def _ensure_question_exists(
        self, question_id: int, level: str, section: str, text: str, grammar_point: str
    ) -> str:
        """Ensure question node exists."""
        logger.debug(f"❓ Ensuring question exists: Q{question_id}")
        query = get_or_create_question_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                question_id=question_id,
                level=level,
                section=section,
                text=text,
                grammar_point=grammar_point,
            )
            record = await result.single()
            q_id = record["question_id"] if record else None
            return q_id

    async def _link_test_sections(self, test_name: str, sections: list[dict]) -> None:
        """Link test to all its sections."""
        logger.debug(f"🔗 Linking test {test_name} to sections")
        for section in sections:
            query = link_test_to_section_query()
            async with self._driver.session(database=self.database) as session:
                await session.run(query, test_name=test_name, level=section["level"])
        logger.info(f"✓ Linked {len(sections)} sections to test {test_name}")

    async def _link_section_questions(self, section_letter: str, question_count: int) -> int:
        """Link section to its questions."""
        logger.debug(f"🔗 Linking section {section_letter} to questions")
        query = link_section_to_questions_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, section_letter=section_letter)
            record = await result.single()
            linked = record["linked_count"] if record else 0
            logger.info(f"✓ Linked {linked} questions to section {section_letter}")
            return linked

    # ========================================================================
    # ANSWER RECORDING HELPERS
    # ========================================================================

    async def create_answer_node(
        self,
        question_id: int,
        student_id: str,
        selected_answer: str,
        is_correct: bool,
        question_level: str,
    ) -> str:
        """Create a user answer node."""
        logger.debug(f"📝 Creating answer node: Q{question_id} by {student_id}")
        query = create_answer_node_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                question_id=question_id,
                student_id=student_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                question_level=question_level,
            )
            record = await result.single()
            answer_id = record["answer_id"] if record else None
            logger.info(f"✓ Answer created: {answer_id}")
            return answer_id

    async def link_answer_to_question(self, answer_id: str, question_id: int) -> None:
        """Link answer node to question."""
        logger.debug(f"🔗 Linking answer {answer_id} to question {question_id}")
        query = """
        MATCH (a:UserAnswer) WHERE elementId(a) = $answer_id
        MATCH (q:Question {question_id: $question_id})
        MERGE (a)-[r:ANSWERED]->(q)
        RETURN r
        """
        async with self._driver.session(database=self.database) as session:
            await session.run(query, answer_id=answer_id, question_id=question_id)

    # ========================================================================
    # RESULT RECORDING HELPERS
    # ========================================================================

    async def create_test_result(
        self,
        student_id: str,
        determined_level: str,
        total_correct: int,
        total_questions: int,
        score_percentage: float,
    ) -> str:
        """Create test result node."""
        logger.debug(
            f"📊 Creating test result for {student_id}: {determined_level} ({score_percentage}%)"
        )
        query = create_test_result_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                determined_level=determined_level,
                total_correct=total_correct,
                total_questions=total_questions,
                score_percentage=score_percentage,
            )
            record = await result.single()
            result_id = record["result_id"] if record else None
            logger.info(f"✓ Test result created: {result_id}")
            return result_id

    async def link_result_to_answers(self, student_id: str) -> int:
        """Link test result to all student's answers."""
        logger.debug(f"🔗 Linking results to answers for {student_id}")
        query = link_result_to_answers_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            linked = record["linked_count"] if record else 0
            logger.info(f"✓ Linked {linked} answers to result")
            return linked

    async def link_student_to_result(self, student_id: str) -> None:
        """Link student to test result."""
        logger.debug(f"🔗 Linking student {student_id} to result")
        query = link_student_to_result_query()
        async with self._driver.session(database=self.database) as session:
            await session.run(query, student_id=student_id)

    async def link_student_to_level(
        self, student_id: str, level: str, confidence: float, percentage: float
    ) -> None:
        """Link student to determined CEFR level."""
        logger.debug(
            f"🔗 Linking {student_id} to level {level} ({confidence * 100:.0f}% confidence)"
        )
        query = link_student_to_level_query()
        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                level=level,
                confidence=confidence,
                percentage=percentage,
            )
        logger.info(f"✓ Student linked to level {level}")

    # ========================================================================
    # SESSION HELPERS
    # ========================================================================

    async def create_test_session(self, student_id: str, test_name: str) -> str:
        """Create a test session node."""
        logger.debug(f"📅 Creating test session for {student_id}")
        query = create_test_session_query()
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, test_name=test_name)
            record = await result.single()
            session_id = record["session_id"] if record else None
            logger.info(f"✓ Test session created: {session_id}")
            return session_id

    async def complete_test_session(
        self, student_id: str, session_id: str, result_id: str
    ) -> None:
        """Complete a test session and link to result."""
        logger.debug(f"✅ Completing test session {session_id}")
        query = """
        MATCH (ts:TestSession) WHERE elementId(ts) = $session_id
        MATCH (r:TestResult) WHERE elementId(r) = $result_id
        SET ts.status = 'COMPLETED',
            ts.completed_at = datetime()
        MERGE (ts)-[rel:PRODUCED_RESULT]->(r)
        RETURN rel
        """
        async with self._driver.session(database=self.database) as session:
            await session.run(query, session_id=session_id, result_id=result_id)
        logger.info("✓ Test session completed and linked to result")

    async def link_student_to_session(self, student_id: str) -> None:
        """Link student to test session."""
        logger.debug(f"🔗 Linking student {student_id} to session")
        query = link_student_to_session_query()
        async with self._driver.session(database=self.database) as session:
            await session.run(query, student_id=student_id)

    async def link_session_to_test(self, student_id: str, test_name: str) -> None:
        """Link test session to test."""
        logger.debug(f"🔗 Linking session to test {test_name}")
        query = link_session_to_test_query()
        async with self._driver.session(database=self.database) as session:
            await session.run(query, student_id=student_id, test_name=test_name)

    # ========================================================================
    # QUERY HELPERS
    # ========================================================================

    async def get_student_placement_history(self, student_id: str) -> list[dict]:
        """Get student's placement test history."""
        logger.debug(f"📊 Fetching placement history for {student_id}")
        query = """
        MATCH (stu:Student {student_id: $student_id})
        MATCH (stu)-[:HAS_TEST_RESULT]->(r:TestResult)
        OPTIONAL MATCH (r)-[:HAS_ANSWER]->(a:UserAnswer)
        RETURN {
            level: r.determined_level,
            score: r.score_percentage,
            total_correct: r.total_correct,
            total_questions: r.total_questions,
            completed_at: r.completed_at,
            answer_count: count(a)
        } AS result
        ORDER BY r.completed_at DESC
        """
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            records = await result.fetch(10)
            logger.info(f"✓ Found {len(records)} test results for {student_id}")
            return [record["result"] for record in records]

    async def get_latest_placement_level(self, student_id: str) -> dict | None:
        """Get student's latest placement level."""
        logger.debug(f"🎯 Fetching latest placement level for {student_id}")
        query = """
        MATCH (stu:Student {student_id: $student_id})
        MATCH (stu)-[rel:HAS_PLACEMENT_LEVEL]->(level:CEFRLevel)
        RETURN {
            level: level.name,
            confidence: rel.confidence,
            percentage: rel.percentage,
            determined_at: rel.determined_at
        } AS placement
        ORDER BY rel.determined_at DESC
        LIMIT 1
        """
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            placement = record["placement"] if record else None
            if placement:
                logger.info(f"✓ Found level: {placement['level']}")
            return placement

    async def get_section_performance(self, student_id: str, section_letter: str) -> dict:
        """Get student's performance on a specific section."""
        logger.debug(f"📊 Fetching section {section_letter} performance for {student_id}")
        query = """
        MATCH (a:UserAnswer {student_id: $student_id, question_level: $level})
        WHERE a.question_id IN [q.question_id
            WHERE q.section = $section_letter
            FROM (MATCH (q:Question) RETURN q)]
        RETURN {
            total_answered: count(a),
            correct_answers: sum(CASE WHEN a.is_correct THEN 1 ELSE 0 END),
            percentage: round((sum(CASE WHEN a.is_correct THEN 1 ELSE 0 END) * 100.0 / count(a)), 1)
        } AS performance
        """
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, section_letter=section_letter)
            record = await result.single()
            perf = (
                record["performance"]
                if record
                else {"total_answered": 0, "correct_answers": 0, "percentage": 0}
            )
            return perf
