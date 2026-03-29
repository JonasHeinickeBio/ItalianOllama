"""Neo4j client for memory and state management.

Handles all Neo4j operations for student data, vocabulary, and progress.
"""

import json

from neo4j import AsyncGraphDatabase


class Neo4jClient:
    """Async Neo4j client for Italian Tutor.

    Handles:
    - Student CRUD
    - Vocabulary management
    - Grammar error tracking
    - Exercise history
    - CEFR level tracking
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None

    async def connect(self):
        """Connect to Neo4j."""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self

    async def close(self):
        """Close the connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def verify_connectivity(self) -> bool:
        """Verify connection is working."""
        if not self._driver:
            await self.connect()

        async with self._driver.session(database=self.database) as session:
            result = await session.run("RETURN 1 AS n")
            await result.consume()
        return True

    # ============ Student Management ============

    async def create_student(self, student_id: str, name: str) -> str:
        """Create a new student."""
        query = """
        MERGE (s:Student {student_id: $student_id})
        SET s.name = $name,
            s.created_at = datetime()
        RETURN elementId(s) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, name=name)
            record = await result.single()
            return record["id"] if record else None

    async def get_student(self, student_id: str) -> dict | None:
        """Get student with level and stats."""
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[:HAS_LEVEL]->(l:CEFRLevel)
        OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
        OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
        WITH s, l, count(DISTINCT v) AS vocab_count, count(DISTINCT e) AS exercise_count
        RETURN s.student_id AS student_id,
               s.name AS name,
               l.code AS level,
               l.confidence AS level_confidence,
               vocab_count,
               exercise_count,
               s.created_at AS created_at
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()

            if record:
                return dict(record)
            return None

    async def set_student_level(
        self,
        student_id: str,
        level: str,
        confidence: float = 1.0,
    ):
        """Set or update student's CEFR level."""
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (l:CEFRLevel {code: $level})
        SET l.confidence = $confidence,
            l.assessed_at = datetime()
        MERGE (s)-[:HAS_LEVEL]->(l)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                level=level,
                confidence=confidence,
            )

    # ============ Vocabulary ============

    async def add_vocabulary(
        self,
        student_id: str,
        word: str,
        translation: str,
        topic: str = "general",
        level: str = "A1",
    ):
        """Add vocabulary word for student."""
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (v:Vocabulary {word: $word, language: 'italian'})
        SET v.translation = $translation,
            v.topic = $topic,
            v.level = $level,
            v.confidence = 0.0,
            v.created_at = datetime()
        MERGE (s)-[:KNOWS]->(v)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                word=word,
                translation=translation,
                topic=topic,
                level=level,
            )

    async def get_student_vocabulary(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get student's vocabulary with confidence scores."""
        query = """
        MATCH (s:Student {student_id: $student_id})-[:KNOWS]->(v:Vocabulary)
        RETURN v.word AS word,
               v.translation AS translation,
               v.topic AS topic,
               v.confidence AS confidence
        ORDER BY v.confidence ASC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, limit=limit)
            records = await result.data()
            return records

    async def update_vocabulary_confidence(
        self,
        student_id: str,
        word: str,
        confidence: float,
    ):
        """Update confidence score for vocabulary (spaced repetition)."""
        query = """
        MATCH (s:Student {student_id: $student_id})-[:KNOWS]->(v:Vocabulary {word: $word})
        SET v.confidence = $confidence,
            v.last_practiced = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                word=word,
                confidence=confidence,
            )

    # ============ Grammar Errors ============

    async def record_grammar_error(
        self,
        student_id: str,
        original: str,
        corrected: str,
        rule: str,
        level: str = "A2",
    ):
        """Record a grammar error for tracking."""
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (e:GrammarError {
            original: $original,
            rule: $rule,
            level: $level
        })
        SET e.corrected = $corrected,
            e.seen_count = coalesce(e.seen_count, 0) + 1,
            e.last_seen = datetime()
        MERGE (s)-[:MADE_ERROR]->(e)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                original=original,
                corrected=corrected,
                rule=rule,
                level=level,
            )

    async def get_common_errors(
        self,
        student_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get most common grammar errors for student."""
        query = """
        MATCH (s:Student {student_id: $student_id})-[:MADE_ERROR]->(e:GrammarError)
        RETURN e.rule AS rule,
               e.original AS original,
               e.corrected AS corrected,
               e.seen_count AS seen_count
        ORDER BY e.seen_count DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, limit=limit)
            return await result.data()

    # ============ Exercises ============

    async def record_exercise(
        self,
        student_id: str,
        exercise_type: str,
        score: int,
        level: str,
        content: str | None = None,
    ):
        """Record completed exercise."""
        query = """
        MATCH (s:Student {student_id: $student_id})
        CREATE (e:Exercise {
            type: $exercise_type,
            score: $score,
            level: $level,
            content: $content,
            completed_at: datetime()
        })
        MERGE (s)-[:COMPLETED]->(e)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                exercise_type=exercise_type,
                score=score,
                level=level,
                content=content,
            )

    async def get_exercise_history(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get student's exercise history."""
        query = """
        MATCH (s:Student {student_id: $student_id})-[:COMPLETED]->(e:Exercise)
        RETURN e.type AS type,
               e.score AS score,
               e.level AS level,
               e.completed_at AS completed_at
        ORDER BY e.completed_at DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, limit=limit)
            return await result.data()

    # ============ Niveau Test ============

    async def record_niveau_test(
        self,
        student_id: str,
        test_type: str,
        level: str,
        readiness: float,
        skill_scores: dict,
    ):
        """Record niveau test results."""
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

    # ============ Setup ============

    async def setup_schema(self):
        """Create constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE",
            "CREATE CONSTRAINT vocab_word IF NOT EXISTS FOR (v:Vocabulary) REQUIRE v.word IS UNIQUE",
        ]

        indexes = [
            "CREATE INDEX student_level IF NOT EXISTS FOR (s:Student) ON (s.student_id)",
            "CREATE INDEX vocab_topic IF NOT EXISTS FOR (v:Vocabulary) ON (v.topic)",
            "CREATE INDEX exercise_type IF NOT EXISTS FOR (e:Exercise) ON (e.type)",
        ]

        async with self._driver.session(database=self.database) as session:
            for c in constraints:
                try:
                    await session.run(c)
                except Exception:
                    pass  # Already exists

            for i in indexes:
                try:
                    await session.run(i)
                except Exception:
                    pass
