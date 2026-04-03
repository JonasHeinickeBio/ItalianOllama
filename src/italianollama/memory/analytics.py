"""Analytics and visualization operations."""

import logging

from italianollama.memory.base import Neo4jBaseClient

logger = logging.getLogger(__name__)


class AnalyticsManager(Neo4jBaseClient):
    """Handles learning analytics, metrics, and knowledge graph visualization."""

    async def get_learning_velocity(self, student_id: str, days: int = 7) -> dict:
        """Get learning velocity (exercises per day).

        Args:
            student_id: Student ID
            days: Lookback period in days

        Returns:
            Velocity metrics
        """
        logger.debug(f"⚡ Fetching learning velocity - student_id={student_id}, days={days}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[:COMPLETED]->(e:Exercise)
        WHERE e.completed_at >= datetime() - duration({days: $days})
        WITH count(e) AS exercises_completed
        RETURN {
            student_id: $student_id,
            period_days: $days,
            exercises_completed: exercises_completed,
            velocity: ROUND(toFloat(exercises_completed) / $days, 2),
            unit: "exercises/day"
        } AS velocity
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, days=days)
            record = await result.single()

            if record:
                return record["velocity"]
            else:
                return {
                    "student_id": student_id,
                    "period_days": days,
                    "exercises_completed": 0,
                    "velocity": 0.0,
                    "unit": "exercises/day",
                }

    async def get_student_stats(self, student_id: str) -> dict:
        """Get aggregated KPI statistics.

        Args:
            student_id: Student ID

        Returns:
            Dashboard statistics
        """
        logger.debug(f"📊 Fetching student stats - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
        OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
        OPTIONAL MATCH (s)-[:MADE_ERROR]->(err:GrammarError)
        OPTIONAL MATCH (s)-[rel:HAS_PLACEMENT_LEVEL]->(l:CEFRLevel)
        WITH s,
             count(DISTINCT e) AS total_exercises,
             count(DISTINCT v) AS vocab_count,
             count(DISTINCT err) AS error_count,
             ROUND(AVG(e.score), 1) AS avg_score,
             count(DISTINCT CASE WHEN v.confidence >= 0.8 THEN v.word END) AS vocab_mature,
             l.name AS current_level,
             rel.determined_at AS level_determined_at
        RETURN {
            student_id: s.student_id,
            total_exercises: total_exercises,
            avg_score: COALESCE(avg_score, 0),
            total_vocab: vocab_count,
            vocab_mature: COALESCE(vocab_mature, 0),
            total_errors: error_count,
            streak_days: s.current_streak,
            xp_this_week: s.total_xp,
            current_level: current_level,
            level_determined_at: level_determined_at
        } AS stats
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            return dict(record["stats"]) if record else {}

    async def get_knowledge_graph(self, student_id: str, max_nodes: int = 100) -> dict:
        """Export knowledge graph for visualization.

        Args:
            student_id: Student ID
            max_nodes: Maximum number of nodes to return

        Returns:
            {nodes: [...], links: [...]} for visualization
        """
        logger.debug(
            f"🗂️ Fetching knowledge graph - student_id={student_id}, max_nodes={max_nodes}"
        )
        query = """
        MATCH (s:Student {student_id: $student_id})
        MATCH path = (s)-[r*1..3]->(target)
        WITH DISTINCT nodes(path) AS all_nodes, relationships(path) AS all_rels
        UNWIND all_nodes AS node
        WITH collect(DISTINCT {
            id: elementId(node),
            label: labels(node)[0],
            properties: properties(node)
        }) AS nodes,
        collect(DISTINCT {
            id: elementId(rel),
            source: elementId(startNode(rel)),
            target: elementId(endNode(rel)),
            type: type(rel)
        }) AS links
        FROM all_rels AS rel
        RETURN nodes, links
        LIMIT $max_nodes
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, max_nodes=max_nodes)
            record = await result.single()
            if record:
                return {
                    "nodes": record.get("nodes", []),
                    "links": record.get("links", []),
                }
            return {"nodes": [], "links": []}

    async def get_full_knowledge_graph(self, student_id: str) -> dict:
        """Get full knowledge graph (legacy method).

        Args:
            student_id: Student ID

        Returns:
            Knowledge graph with all nodes and relationships
        """
        return await self.get_knowledge_graph(student_id, max_nodes=500)

    async def get_struggling_concepts(
        self,
        student_id: str,
        threshold: float = 0.6,
    ) -> list[dict]:
        """Identify grammar concepts where student is struggling.

        Args:
            student_id: Student ID
            threshold: Mastery threshold below which to flag as struggling

        Returns:
            List of struggling concepts
        """
        logger.debug(
            f"🔴 Fetching struggling concepts - student_id={student_id}, threshold={threshold}"
        )
        query = """
        MATCH (s:Student {student_id: $student_id})-[rel:MADE_ERROR]->(c:GrammarError)
        OPTIONAL MATCH (c)<-[:VIOLATES]-(t:ExerciseTemplate)
        RETURN {
            concept_id: c.rule,
            title: c.rule,
            mastery: 1 - (toFloat(rel.error_count) / 10),
            common_mistakes: c.context,
            practice_templates: collect(DISTINCT t.template_id)
        } AS concept
        ORDER BY rel.error_count DESC
        LIMIT 10
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                threshold=threshold,
            )
            records = await result.data()
            return [dict(r["concept"]) for r in records]
