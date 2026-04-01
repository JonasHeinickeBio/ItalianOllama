"""Neo4j client for memory and state management.

Handles all Neo4j operations for student data, vocabulary, and progress.
"""

import json
import logging

from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)


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
        logger.info(f"🗂️ Initializing Neo4j Client - uri={uri}, database={database}")
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None
        logger.debug("  ✓ Neo4j Client initialized")

    async def connect(self):
        """Connect to Neo4j."""
        if self._driver is None:
            logger.info(f"🔗 Connecting to Neo4j - uri={self.uri}, user={self.user}")
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("✓ Connected to Neo4j successfully")
        else:
            logger.debug("  ℹ️ Already connected to Neo4j")
        return self

    async def close(self):
        """Close the connection."""
        if self._driver:
            logger.info("🔌 Closing Neo4j connection...")
            await self._driver.close()
            self._driver = None
            logger.info("✓ Neo4j connection closed")
        else:
            logger.debug("  ℹ️ No Neo4j connection to close")

    async def verify_connectivity(self) -> bool:
        """Verify connection is working."""
        logger.debug("📡 Verifying Neo4j connectivity...")
        if not self._driver:
            await self.connect()

        try:
            async with self._driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 AS n")
                await result.consume()
            logger.info("✓ Neo4j connectivity verified successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Neo4j connectivity verification failed - {str(e)}")
            return False

    # ============ Student Management ============

    async def create_student(self, student_id: str, name: str) -> str:
        """Create a new student."""
        logger.info(f"👤 Creating student in Neo4j - student_id={student_id}, name={name}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        SET s.name = $name,
            s.created_at = datetime()
        RETURN elementId(s) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, name=name)
            record = await result.single()
            student_id_neo4j = record["id"] if record else None
            logger.info(f"✓ Student created in Neo4j - neo4j_id={student_id_neo4j}")
            return student_id_neo4j

    async def get_student(self, student_id: str) -> dict | None:
        """Get student with level and stats."""
        logger.debug(f"👤 Fetching student from Neo4j - student_id={student_id}")
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
                student_data = dict(record)
                logger.info(
                    f"✓ Student retrieved from Neo4j - vocab_count={student_data.get('vocab_count', 0)}, exercise_count={student_data.get('exercise_count', 0)}"
                )
                logger.debug(f"  📥 Student data: {student_data}")
                return student_data
            else:
                logger.warning(f"⚠️ Student not found in Neo4j - student_id={student_id}")
            return None

    async def set_student_level(
        self,
        student_id: str,
        level: str,
        confidence: float = 1.0,
    ):
        """Set or update student's CEFR level."""
        logger.info(
            f"📊 Setting student CEFR level - student_id={student_id}, level={level}, confidence={confidence}"
        )
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
        logger.info("✓ Student CEFR level set successfully")

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
        logger.info(
            f"📚 Adding vocabulary to student - word='{word}' | translation='{translation}' | topic={topic} | level={level}"
        )
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
        logger.info("✓ Vocabulary added successfully")

    async def get_student_vocabulary(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get student's vocabulary with confidence scores."""
        logger.debug(
            f"📚 Fetching student vocabulary from Neo4j - student_id={student_id}, limit={limit}"
        )
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
            logger.info(f"✓ Retrieved {len(records)} vocabulary entries")
            logger.debug(f"  📥 Sample entries: {records[:3] if records else 'none'}")
            return records

    async def update_vocabulary_confidence(
        self,
        student_id: str,
        word: str,
        confidence: float,
    ):
        """Update confidence score for vocabulary (spaced repetition)."""
        logger.info(
            f"📝 Updating vocabulary confidence - word='{word}' | confidence={confidence}%"
        )
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
        logger.info("✓ Vocabulary confidence updated successfully")

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
        logger.info(
            f"❌ Recording grammar error - rule={rule} | original='{original[:30]}' | corrected='{corrected[:30]}'"
        )
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
        logger.info("✓ Grammar error recorded successfully")

    async def get_common_errors(
        self,
        student_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get most common grammar errors for student."""
        logger.debug(f"❌ Fetching common grammar errors - student_id={student_id}, limit={limit}")
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
            records = await result.data()
            logger.info(f"✓ Retrieved {len(records)} common grammar errors")
            logger.debug(f"  📥 Top error: {records[0] if records else 'none'}")
            return records

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
        logger.info(
            f"📝 Recording exercise - student_id={student_id}, type={exercise_type}, score={score}, level={level}"
        )
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
        logger.info("✓ Exercise recorded successfully")

    async def get_exercise_history(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get student's exercise history."""
        logger.debug(f"📚 Fetching exercise history - student_id={student_id}, limit={limit}")
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
            records = await result.data()
            logger.info(f"✓ Retrieved {len(records)} exercise history records")
            return records

    async def get_student_stats(self, student_id: str) -> dict:
        """Get aggregated stats for dashboard KPI metrics."""
        logger.debug(f"📊 Fetching aggregated student stats - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
        OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
        OPTIONAL MATCH (s)-[:MADE_ERROR]->(err:GrammarError)
        WITH s,
             count(DISTINCT e) AS total_exercises,
             avg(e.score) AS avg_score,
             count(DISTINCT v) AS total_vocab,
             count(DISTINCT err) AS total_errors
        RETURN total_exercises,
               coalesce(avg_score, 0) AS avg_score,
               total_vocab,
               total_errors,
               5 AS streak  // Placeholder for streak logic
        """
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            stats = dict(record) if record else {}
            logger.info(
                f"✓ Student stats retrieved - exercises={stats.get('total_exercises', 0)}, vocab={stats.get('total_vocab', 0)}, errors={stats.get('total_errors', 0)}"
            )
            logger.debug(f"  📊 Stats: {stats}")
            return stats

    async def get_test_readiness(self, student_id: str) -> list[dict]:
        """Get CEFR test readiness scores for radar chart."""
        logger.debug(f"📈 Fetching test readiness data - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[:READY_FOR]->(t:NiveauTest)
        WITH t ORDER BY t.completed_at DESC
        WITH t.test_type AS type, t.readiness AS readiness, t.skill_scores AS skills
        LIMIT 5
        RETURN type, readiness, skills
        """
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            records = await result.data()
            logger.info(f"✓ Retrieved {len(records)} test readiness records")
            return records

    async def get_full_knowledge_graph(self, student_id: str) -> dict:
        """Get nodes and relationships for st-link-analysis."""
        query = """
        MATCH (s:Student {student_id: $student_id})-[r]->(target)
        RETURN s, r, target
        LIMIT 100
        """
        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            nodes = []
            links = []
            node_ids = set()

            async for record in result:
                s = record["s"]
                target = record["target"]
                r = record["r"]

                for node in [s, target]:
                    if node.element_id not in node_ids:
                        nodes.append(
                            {
                                "id": node.element_id,
                                "label": list(node.labels)[0],
                                "properties": dict(node),
                            }
                        )
                        node_ids.add(node.element_id)

                links.append(
                    {
                        "id": r.element_id,
                        "source": s.element_id,
                        "target": target.element_id,
                        "type": r.type,
                    }
                )

            return {"nodes": nodes, "links": links}

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
        """Create constraints and indexes and silence unknown token warnings."""
        constraints = [
            "CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE",
            "CREATE CONSTRAINT vocab_word IF NOT EXISTS FOR (v:Vocabulary) REQUIRE v.word IS UNIQUE",
        ]

        indexes = [
            "CREATE INDEX student_level_idx IF NOT EXISTS FOR (s:Student) ON (s.student_id)",
            "CREATE INDEX vocab_topic_idx IF NOT EXISTS FOR (v:Vocabulary) ON (v.topic)",
            "CREATE INDEX exercise_type_idx IF NOT EXISTS FOR (e:Exercise) ON (e.type)",
            "CREATE INDEX cefr_code_idx IF NOT EXISTS FOR (l:CEFRLevel) ON (l.code)",
            "CREATE INDEX grammar_rule_idx IF NOT EXISTS FOR (g:GrammarError) ON (g.rule)",
        ]

        async with self._driver.session(database=self.database) as session:
            for c in constraints:
                try:
                    await session.run(c)
                except Exception:
                    pass

            for i in indexes:
                try:
                    await session.run(i)
                except Exception:
                    pass

            # "Touch" labels and relationship types to register them in the DB schema
            # This prevents "UnknownLabelWarning" and "UnknownRelationshipTypeWarning"
            touch_query = """
            OPTIONAL MATCH (s:Student)-[:HAS_LEVEL]->(l:CEFRLevel)
            OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
            OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
            OPTIONAL MATCH (s)-[:MADE_ERROR]->(err:GrammarError)
            OPTIONAL MATCH (s)-[:READY_FOR]->(t:NiveauTest)
            RETURN s.student_id, l.code, l.confidence, v.word, e.type, err.rule, t.test_type LIMIT 1
            """
            try:
                await session.run(touch_query)
            except Exception:
                pass
