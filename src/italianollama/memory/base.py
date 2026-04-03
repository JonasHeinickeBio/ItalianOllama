"""Base Neo4j client with core connection and helper methods."""

import logging

from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)


class Neo4jBaseClient:
    """Base Neo4j async client with connection management."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
    ):
        """Initialize Neo4j client.

        Args:
            uri: Neo4j connection URI (bolt://, neo4j+s://)
            user: Neo4j username
            password: Neo4j password
            database: Database name (default: neo4j)
        """
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

    async def setup_schema(self):
        """Create constraints, indexes, and register schema tokens."""
        logger.info("🛠️ Setting up Neo4j schema...")

        constraints = [
            "CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) "
            "REQUIRE s.student_id IS UNIQUE",
            "CREATE CONSTRAINT vocab_word IF NOT EXISTS FOR (v:Vocabulary) "
            "REQUIRE v.word IS UNIQUE",
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
                    logger.debug("  ✓ Constraint created")
                except Exception as e:
                    logger.debug(f"  ℹ️ Constraint already exists: {e}")

            for i in indexes:
                try:
                    await session.run(i)
                    logger.debug("  ✓ Index created")
                except Exception as e:
                    logger.debug(f"  ℹ️ Index already exists: {e}")

            # Register schema tokens to prevent warnings
            touch_query = """
            OPTIONAL MATCH (s:Student)-[rel:HAS_PLACEMENT_LEVEL]->(l:CEFRLevel)
            OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
            OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
            OPTIONAL MATCH (s)-[:MADE_ERROR]->(err:GrammarError)
            OPTIONAL MATCH (s)-[:READY_FOR]->(t:NiveauTest)
            OPTIONAL MATCH (s)-[:HAS_TEST_RESULT]->(r:TestResult)
            OPTIONAL MATCH (s)-[:HAS_TEST_SESSION]->(sess:TestSession)
            OPTIONAL MATCH (s)-[:ENROLLED_IN]->(session:Session)
            OPTIONAL MATCH (s)-[:MADE_ATTEMPT]->(a:Attempt)
            OPTIONAL MATCH (s)-[:ACHIEVED]->(level:CEFRLevel)
            OPTIONAL MATCH (s)-[:WORKING_ON]->(mod:Module)
            OPTIONAL MATCH (s)-[:EXPERIENCED]->(skill:Skill)
            OPTIONAL MATCH (s)-[:UNDERSTANDS]->(c:Concept)
            RETURN s.student_id, l.name, rel.confidence, v.word, e.type,
                   err.rule, t.test_type, r.total_correct, sess.started_at,
                   a.xp_earned, mod.module_id, skill.skill_id, c.concept_id
            LIMIT 1
            """
            try:
                await session.run(touch_query)
                logger.info("✓ Neo4j schema setup complete")
            except Exception as e:
                logger.debug(f"  ℹ️ Schema token registration: {e}")
