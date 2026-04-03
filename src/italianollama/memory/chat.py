"""Chat message persistence to Neo4j.

Provides a manager for storing and retrieving chat conversations
linked to student profiles in the knowledge graph.
"""

import logging
from typing import Any

from .base import Neo4jBaseClient

logger = logging.getLogger(__name__)


class ChatManager(Neo4jBaseClient):
    """Manage chat message storage and retrieval.

    Stores user-assistant conversations, metadata, and conversation context
    for learning analytics and personalization.
    """

    async def save_chat_message(
        self,
        student_id: str,
        user_content: str,
        assistant_content: str,
        session_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Save a chat message exchange to Neo4j.

        Args:
            student_id: Student identifier
            user_content: User's input message
            assistant_content: AI tutor's response
            session_id: Optional session identifier for grouping

        Returns:
            Message metadata dict or None on error
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        CREATE (msg:ChatMessage {
            timestamp: datetime(),
            user_content: $user_content,
            assistant_content: $assistant_content,
            content_length: $content_length,
            session_id: $session_id
        })
        CREATE (s)-[:HAS_CHAT_MESSAGE {timestamp: datetime()}]->(msg)
        RETURN msg {
            id: id(msg),
            timestamp: msg.timestamp,
            user_len: size($user_content),
            assistant_len: size($assistant_content)
        }
        """

        params = {
            "student_id": student_id,
            "user_content": user_content,
            "assistant_content": assistant_content,
            "content_length": len(user_content) + len(assistant_content),
            "session_id": session_id or "default",
        }

        try:
            async with self._driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                if record:
                    logger.debug(
                        "Chat message saved | student=%s | user_len=%d | assistant_len=%d",
                        student_id,
                        params["content_length"] // 2,
                        params["content_length"] // 2,
                    )
                    return dict(record[0])
                return None
        except Exception as e:
            logger.error("Failed to save chat message for %s: %s", student_id, e)
            return None

    async def get_chat_history(
        self,
        student_id: str,
        limit: int = 50,
        session_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve chat history for a student.

        Args:
            student_id: Student identifier
            limit: Maximum number of messages to return (default: 50)
            session_id: Optional session filter

        Returns:
            List of chat message dicts ordered by timestamp (newest first)
        """
        query = (
            """
        MATCH (s:Student {student_id: $student_id})-[r:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
        """
            + ("WHERE msg.session_id = $session_id" if session_id else "")
            + """
        RETURN msg {
            timestamp: msg.timestamp,
            user_content: msg.user_content,
            assistant_content: msg.assistant_content,
            session_id: msg.session_id
        }
        ORDER BY msg.timestamp DESC
        LIMIT $limit
        """
        )

        params = {
            "student_id": student_id,
            "limit": limit,
        }
        if session_id:
            params["session_id"] = session_id

        try:
            async with self._driver.session() as session:
                result = await session.run(query, params)
                records = await result.all()
                return [dict(record[0]) for record in records]
        except Exception as e:
            logger.error("Failed to retrieve chat history for %s: %s", student_id, e)
            return []

    async def get_conversation_summary(
        self,
        student_id: str,
        window_days: int = 7,
    ) -> dict[str, Any]:
        """Get aggregated chat statistics for a period.

        Args:
            student_id: Student identifier
            window_days: Number of days to look back

        Returns:
            Summary dict with message counts and average response times
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
        WHERE msg.timestamp >= datetime(datetime().withZone()) - duration({days: $window_days})
        RETURN {
            total_messages: count(msg),
            avg_user_length: round(avg(size(msg.user_content))),
            avg_assistant_length: round(avg(size(msg.assistant_content))),
            latest_message: max(msg.timestamp),
            unique_sessions: count(DISTINCT msg.session_id)
        }
        """

        params = {
            "student_id": student_id,
            "window_days": window_days,
        }

        try:
            async with self._driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                if record:
                    return dict(record[0])
                return {
                    "total_messages": 0,
                    "avg_user_length": 0,
                    "avg_assistant_length": 0,
                }
        except Exception as e:
            logger.error("Failed to get conversation summary for %s: %s", student_id, e)
            return {}

    async def delete_chat_session(
        self,
        student_id: str,
        session_id: str,
    ) -> bool:
        """Delete all messages in a chat session.

        Args:
            student_id: Student identifier
            session_id: Session to delete

        Returns:
            True if deletion succeeded
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[r:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
        WHERE msg.session_id = $session_id
        DETACH DELETE msg
        """

        params = {
            "student_id": student_id,
            "session_id": session_id,
        }

        try:
            async with self._driver.session() as session:
                await session.run(query, params)
                logger.info("Deleted chat session %s for student %s", session_id, student_id)
                return True
        except Exception as e:
            logger.error("Failed to delete chat session: %s", e)
            return False
