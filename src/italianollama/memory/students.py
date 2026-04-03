"""Student management operations."""

import logging

from italianollama.memory.base import Neo4jBaseClient

logger = logging.getLogger(__name__)


class StudentManager(Neo4jBaseClient):
    """Handles student CRUD and profile operations."""

    async def create_student(
        self,
        student_id: str,
        name: str,
        native_language: str = "English",
    ) -> str:
        """Create a new student.

        Args:
            student_id: Unique identifier for student
            name: Display name
            native_language: L1 language for contrastive analysis

        Returns:
            Element ID of created student
        """
        logger.info(f"👤 Creating student - student_id={student_id}, name={name}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        SET s.name = $name,
            s.native_language = $native_language,
            s.created_at = datetime(),
            s.last_active = datetime(),
            s.total_xp = COALESCE(s.total_xp, 0),
            s.current_streak = COALESCE(s.current_streak, 0)
        RETURN elementId(s) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                name=name,
                native_language=native_language,
            )
            record = await result.single()
            student_neo4j_id = record["id"] if record else None
            logger.info(f"✓ Student created in Neo4j - neo4j_id={student_neo4j_id}")
            return student_neo4j_id

    async def get_student(self, student_id: str) -> dict | None:
        """Get comprehensive student profile.

        Returns:
            Student object with level, stats, and metadata
        """
        logger.debug(f"👤 Fetching student - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[rel:HAS_PLACEMENT_LEVEL]->(l:CEFRLevel)
        OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
        OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
        WITH s, l, rel, count(DISTINCT v) AS vocab_count, count(DISTINCT e) AS exercise_count
        RETURN s.student_id AS student_id,
               s.name AS name,
               l.name AS level,
               rel.confidence AS level_confidence,
               vocab_count,
               exercise_count,
               s.created_at AS created_at,
               s.last_active AS last_active,
               s.total_xp AS total_xp,
               s.current_streak AS current_streak,
               s.native_language AS native_language
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()

            if record:
                student_data = dict(record)
                vocab_cnt = student_data.get("vocab_count", 0)
                exercise_cnt = student_data.get("exercise_count", 0)
                logger.info(
                    f"✓ Student retrieved - vocab_count={vocab_cnt}, exercise_count={exercise_cnt}"
                )
                return student_data
            else:
                logger.warning(f"⚠️ Student not found: {student_id}")
                return None

    async def set_student_level(
        self,
        student_id: str,
        level: str,
        confidence: float = 1.0,
    ):
        """Set or update student's CEFR level.

        Args:
            student_id: Student identifier
            level: CEFR level (A1-C1)
            confidence: Confidence score (0.0-1.0)
        """
        logger.info(
            f"📊 Setting student CEFR level - student_id={student_id}, "
            f"level={level}, confidence={confidence}"
        )
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (l:CEFRLevel {name: $level})
        MERGE (s)-[rel:HAS_PLACEMENT_LEVEL]->(l)
        SET rel.confidence = $confidence,
            rel.determined_at = datetime(),
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                level=level,
                confidence=confidence,
            )
        logger.info("✓ Student CEFR level set successfully")
