"""Unified Neo4j client combining all managers.

This module provides a single client class that includes all operations
from base, students, learning, placement, analytics, and chat managers.
"""

import logging

from italianollama.memory.analytics import AnalyticsManager
from italianollama.memory.base import Neo4jBaseClient
from italianollama.memory.chat import ChatManager
from italianollama.memory.learning import LearningManager
from italianollama.memory.placement import PlacementTestManager
from italianollama.memory.students import StudentManager


class Neo4jClient(
    StudentManager,
    LearningManager,
    PlacementTestManager,
    AnalyticsManager,
    ChatManager,
    Neo4jBaseClient,
):
    """Unified Neo4j client with all operations.

    Combines:
    - Neo4jBaseClient: Connection management and schema setup
    - StudentManager: Student CRUD and profile operations
    - LearningManager: Vocabulary, exercises, and error tracking
    - PlacementTestManager: Placement test sessions and results
    - AnalyticsManager: Learning analytics and visualization
    - ChatManager: Chat message storage and retrieval

    Usage:
        client = Neo4jClient(uri="bolt://localhost:7687")
        await client.connect()
        student = await client.get_student("student_id")
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
    ):
        """Initialize unified Neo4j client with all managers.

        Args:
            uri: Neo4j connection URI (bolt://, neo4j+s://)
            user: Neo4j username
            password: Neo4j password
            database: Database name (default: neo4j)
        """
        super().__init__(uri=uri, user=user, password=password, database=database)
        logger = logging.getLogger(__name__)
        logger.info("Unified Neo4j client initialized")
