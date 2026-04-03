"""Vocabulary and exercise tracking."""

import logging

from italianollama.memory.base import Neo4jBaseClient

logger = logging.getLogger(__name__)


class LearningManager(Neo4jBaseClient):
    """Handles vocabulary, exercises, and error tracking."""

    async def add_vocabulary(
        self,
        student_id: str,
        word: str,
        definition: str = "",
        topic: str = "",
        confidence: float = 0.5,
    ):
        """Add vocabulary word for student.

        Args:
            student_id: Student ID
            word: Italian word
            definition: Definition or translation
            topic: Vocabulary topic/category
            confidence: Confidence level (0.0-1.0)
        """
        logger.info(f"📚 Adding vocabulary - student_id={student_id}, word={word}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (v:Vocabulary {word: $word})
        SET v.definition = $definition,
            v.topic = $topic
        MERGE (s)-[rel:KNOWS]->(v)
        SET rel.confidence = $confidence,
            rel.learned_at = datetime(),
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                word=word,
                definition=definition,
                topic=topic,
                confidence=confidence,
            )
        logger.info("✓ Vocabulary added")

    async def add_exercise(
        self,
        student_id: str,
        exercise_type: str,
        level: str,
        score: float,
        xp_earned: int = 10,
    ):
        """Record completed exercise.

        Args:
            student_id: Student ID
            exercise_type: Type of exercise (grammar, vocabulary, etc.)
            level: CEFR level of exercise
            score: Score as percentage (0-100)
            xp_earned: Experience points awarded
        """
        logger.info(
            f"✏️ Recording exercise - student_id={student_id}, type={exercise_type}, score={score}"
        )
        query = """
        MERGE (s:Student {student_id: $student_id})
        CREATE (e:Exercise {
            type: $exercise_type,
            level: $level,
            score: $score,
            xp_earned: $xp_earned,
            completed_at: datetime()
        })
        MERGE (s)-[:COMPLETED]->(e)
        SET s.total_xp = COALESCE(s.total_xp, 0) + $xp_earned,
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                exercise_type=exercise_type,
                level=level,
                score=score,
                xp_earned=xp_earned,
            )
        logger.info("✓ Exercise recorded")

    async def add_grammar_error(
        self,
        student_id: str,
        rule: str,
        context: str = "",
        correction: str = "",
    ):
        """Track grammar error.

        Args:
            student_id: Student ID
            rule: Grammar rule that was violated
            context: Example sentence with error
            correction: Corrected version
        """
        logger.info(f"🔴 Recording grammar error - student_id={student_id}, rule={rule}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (err:GrammarError {rule: $rule})
        SET err.context = $context,
            err.correction = $correction,
            err.updated_at = datetime()
        MERGE (s)-[rel:MADE_ERROR]->(err)
        SET rel.error_count = COALESCE(rel.error_count, 0) + 1,
            rel.last_error_at = datetime(),
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                rule=rule,
                context=context,
                correction=correction,
            )
        logger.info("✓ Grammar error recorded")

    async def get_vocabulary(
        self,
        student_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """Get student's vocabulary list.

        Args:
            student_id: Student ID
            limit: Maximum number of words

        Returns:
            List of vocabulary entries with confidence scores
        """
        logger.debug(f"📚 Fetching vocabulary - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[rel:KNOWS]->(v:Vocabulary)
        RETURN {
            word: v.word,
            definition: v.definition,
            topic: v.topic,
            confidence: rel.confidence,
            learned_at: rel.learned_at
        } AS vocab
        ORDER BY rel.confidence DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
            )
            records = await result.data()
            return [dict(r["vocab"]) for r in records]

    async def get_common_errors(
        self,
        student_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get most common grammar errors.

        Args:
            student_id: Student ID
            limit: Maximum number of errors

        Returns:
            List of grammar errors sorted by frequency
        """
        logger.debug(f"🔴 Fetching grammar errors - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[rel:MADE_ERROR]->(e:GrammarError)
        RETURN {
            rule: e.rule,
            context: e.context,
            correction: e.correction,
            error_count: rel.error_count,
            last_error_at: rel.last_error_at
        } AS error
        ORDER BY rel.error_count DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
            )
            records = await result.data()
            return [dict(r["error"]) for r in records]

    async def get_exercise_history(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get exercise attempt history.

        Args:
            student_id: Student ID
            limit: Maximum number of records

        Returns:
            List of exercises with scores
        """
        logger.debug(f"✏️ Fetching exercise history - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[:COMPLETED]->(e:Exercise)
        RETURN {
            type: e.type,
            score: e.score,
            level: e.level,
            xp_earned: e.xp_earned,
            completed_at: e.completed_at
        } AS exercise
        ORDER BY e.completed_at DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
            )
            records = await result.data()
            return [dict(r["exercise"]) for r in records]
