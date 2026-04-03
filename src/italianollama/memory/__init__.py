"""Memory and persistence layer for Italian Tutor.

Modularized Neo4j client with separation of concerns:
- base: Connection management and schema setup
- students: Student CRUD and profile operations
- learning: Vocabulary, exercises, and error tracking
- placement: Placement test sessions and results
- analytics: Learning analytics and visualization
- chat: Chat message storage and retrieval
- neo4j_client: Unified client with all operations

Usage:
    from italianollama.memory import Neo4jClient

    client = Neo4jClient(uri="bolt://localhost:7687")
    await client.connect()
    student = await client.get_student("student_id")
"""

from italianollama.memory.neo4j_client import Neo4jClient

__all__ = [
    "Neo4jClient",
]
