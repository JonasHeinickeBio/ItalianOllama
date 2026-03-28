"""Neo4j memory graph for storing vocabulary, grammar, and learning history."""

from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class VocabularyNode:
    """Vocabulary node data."""

    word: str
    translation: str
    examples: list[str]
    topic: str
    language: str
    node_id: str | None = None


class MemoryGraph:
    """Neo4j-based knowledge graph for language learning.

    Stores vocabulary, grammar rules, topics, and learning sessions.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
    ):
        """Initialize the memory graph connection.

        Args:
            uri: Neo4j bolt URI
            user: Neo4j username
            password: Neo4j password
            database: Database name
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None
        logger.info(f"MemoryGraph initialized for {uri}")

    async def connect(self):
        """Establish connection to Neo4j."""
        try:
            from neo4j import AsyncGraphDatabase

            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

            # Verify connection
            await self.verify_connectivity()
            logger.info("Successfully connected to Neo4j")

            # Create constraints and indexes
            await self._setup_schema()

        except ImportError:
            logger.error("neo4j driver not installed. Run: pip install neo4j")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self):
        """Close the Neo4j connection."""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed")

    async def verify_connectivity(self):
        """Verify the connection is working."""
        async with self._driver.session(database=self.database) as session:
            result = await session.run("RETURN 1 AS n")
            await result.consume()

    async def _setup_schema(self):
        """Create indexes and constraints."""
        async with self._driver.session(database=self.database) as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT vocab_word IF NOT EXISTS FOR (v:Vocabulary) REQUIRE v.word IS UNIQUE",
                "CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
                "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
            ]

            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    # Constraint might already exist
                    logger.debug(f"Schema setup: {e}")

            # Create indexes
            indexes = [
                "CREATE INDEX vocab_language IF NOT EXISTS FOR (v:Vocabulary) ON (v.language)",
                "CREATE INDEX vocab_topic IF NOT EXISTS FOR (v:Vocabulary) ON (v.topic)",
                "CREATE INDEX session_user IF NOT EXISTS FOR (s:Session) ON (s.user_id)",
            ]

            for index in indexes:
                try:
                    await session.run(index)
                except Exception:
                    pass

            logger.info("Schema setup complete")

    # Vocabulary methods
    async def add_vocabulary(
        self,
        word: str,
        translation: str,
        examples: list[str],
        topic: str,
        language: str = "italian",
    ) -> str:
        """Add a vocabulary word to the graph.

        Args:
            word: The word in the target language
            translation: English translation
            examples: List of example sentences
            topic: Topic/category
            language: Target language

        Returns:
            Node ID
        """
        query = """
        MERGE (v:Vocabulary {word: $word, language: $language})
        SET v.translation = $translation,
            v.examples = $examples,
            v.topic = $topic,
            v.created_at = datetime()

        MERGE (t:Topic {name: $topic, language: $language})
        MERGE (v)-[:BELONGS_TO]->(t)

        RETURN elementId(v) AS node_id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                word=word,
                translation=translation,
                examples=json.dumps(examples),
                topic=topic,
                language=language,
            )
            record = await result.single()
            node_id = record["node_id"] if record else None

            logger.info(f"Added vocabulary: {word} ({language})")
            return node_id

    async def get_vocabulary(
        self, language: str = "italian", topic: str | None = None, limit: int = 100
    ) -> list[dict]:
        """Get vocabulary for a language.

        Args:
            language: Target language
            topic: Optional topic filter
            limit: Maximum results

        Returns:
            List of vocabulary items
        """
        if topic:
            query = """
            MATCH (v:Vocabulary)-[:BELONGS_TO]->(t:Topic {name: $topic, language: $language})
            RETURN v ORDER BY v.created_at DESC LIMIT $limit
            """
            params = {"topic": topic, "language": language, "limit": limit}
        else:
            query = """
            MATCH (v:Vocabulary {language: $language})
            RETURN v ORDER BY v.created_at DESC LIMIT $limit
            """
            params = {"language": language, "limit": limit}

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, params)
            records = await result.data()

            vocab = []
            for record in records:
                v = record["v"]
                vocab.append(
                    {
                        "word": v.get("word"),
                        "translation": v.get("translation"),
                        "examples": json.loads(v.get("examples", "[]")),
                        "topic": v.get("topic"),
                        "language": v.get("language"),
                    }
                )

            return vocab

    async def get_vocabulary_stats(self, language: str = "italian") -> dict:
        """Get vocabulary statistics."""
        queries = {
            "total": """
                MATCH (v:Vocabulary {language: $language})
                RETURN count(v) AS count
            """,
            "by_topic": """
                MATCH (v:Vocabulary {language: $language})-[:BELONGS_TO]->(t:Topic)
                RETURN t.name AS topic, count(v) AS count ORDER BY count DESC
            """,
        }

        async with self._driver.session(database=self.database) as session:
            stats = {}

            # Total count
            result = await session.run(queries["total"], language=language)
            record = await result.single()
            stats["total"] = record["count"] if record else 0

            # By topic
            result = await session.run(queries["by_topic"], language=language)
            records = await result.data()
            stats["by_topic"] = {r["topic"]: r["count"] for r in records}

            return stats

    # Session methods
    async def create_session(
        self,
        session_id: str,
        user_id: str = "default",
        language: str = "italian",
        level: str = "intermediate",
    ) -> str:
        """Create a new learning session."""
        query = """
        MERGE (s:Session {session_id: $session_id})
        SET s.user_id = $user_id,
            s.language = $language,
            s.level = $level,
            s.created_at = datetime(),
            s.message_count = 0
        RETURN elementId(s) AS node_id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query, session_id=session_id, user_id=user_id, language=language, level=level
            )
            record = await result.single()
            return record["node_id"] if record else None

    async def add_message(
        self, session_id: str, role: str, content: str, vocabulary_learned: list[str] | None = None
    ):
        """Add a message to session history."""
        query = """
        MATCH (s:Session {session_id: $session_id})
        CREATE (m:Message {
            role: $role,
            content: $content,
            created_at: datetime()
        })
        CREATE (s)-[:HAS_MESSAGE]->(m)
        SET s.message_count = s.message_count + 1
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(query, session_id=session_id, role=role, content=content)

            # Link vocabulary if provided
            if vocabulary_learned:
                for word in vocabulary_learned:
                    await self._link_vocabulary_session(session_id, word)

    async def _link_vocabulary_session(self, session_id: str, word: str):
        """Link a vocabulary word to a session."""
        query = """
        MATCH (s:Session {session_id: $session_id})
        MATCH (v:Vocabulary {word: $word})
        MERGE (s)-[:LEARNED]->(v)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(query, session_id=session_id, word=word)

    async def get_session(self, session_id: str) -> dict | None:
        """Get session with message history."""
        query = """
        MATCH (s:Session {session_id: $session_id})
        OPTIONAL MATCH (s)-[:HAS_MESSAGE]->(m:Message)
        WITH s, collect(m) AS messages
        RETURN s AS session, messages ORDER BY messages.created_at
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, session_id=session_id)
            record = await result.single()

            if not record:
                return None

            session_data = dict(record["session"])
            session_data["messages"] = [
                {"role": m["role"], "content": m["content"]} for m in record["messages"]
            ]

            return session_data

    # Topic methods
    async def get_topics(self, language: str = "italian") -> list[dict]:
        """Get all topics for a language."""
        query = """
        MATCH (t:Topic {language: $language})
        OPTIONAL MATCH (t)<-[:BELONGS_TO]-(v:Vocabulary)
        WITH t, count(v) AS vocab_count
        RETURN t.name AS name, vocab_count ORDER BY vocab_count DESC
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, language=language)
            records = await result.data()
            return records

    # Grammar methods
    async def add_grammar_rule(
        self,
        rule: str,
        explanation: str,
        examples: list[str],
        topic: str,
        language: str = "italian",
    ) -> str:
        """Add a grammar rule to the graph."""
        query = """
        MERGE (g:GrammarRule {rule: $rule, language: $language})
        SET g.explanation = $explanation,
            g.examples = $examples,
            g.topic = $topic,
            g.created_at = datetime()

        MERGE (t:Topic {name: $topic, language: $language})
        MERGE (g)-[:BELONGS_TO]->(t)

        RETURN elementId(g) AS node_id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                rule=rule,
                explanation=explanation,
                examples=json.dumps(examples),
                topic=topic,
                language=language,
            )
            record = await result.single()
            return record["node_id"] if record else None

    async def get_related_vocabulary(self, word: str, language: str = "italian") -> list[dict]:
        """Find related vocabulary based on topic."""
        query = """
        MATCH (v1:Vocabulary {word: $word, language: $language})-[:BELONGS_TO]->(t:Topic)
        MATCH (v2:Vocabulary)-[:BELONGS_TO]->(t)
        WHERE v2.word <> $word
        RETURN v2
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, word=word, language=language)
            records = await result.data()

            related = []
            for record in records:
                v = record["v2"]
                related.append(
                    {
                        "word": v.get("word"),
                        "translation": v.get("translation"),
                        "topic": v.get("topic"),
                    }
                )

            return related

    def __repr__(self) -> str:
        return f"MemoryGraph(uri={self.uri}, user={self.user})"
