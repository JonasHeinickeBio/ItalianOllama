"""
Placement test orchestrator - integrates test engine with Neo4j storage.

Manages the complete flow:
1. Initialize graph with test structure
2. Create test session
3. Record each answer
4. Calculate and store results
5. Link everything together
"""

import logging

from italianollama.backend.placement_test.models import PlacementTestResult
from italianollama.backend.placement_test.question_bank import get_placement_test
from italianollama.backend.placement_test.test_engine import PlacementTestEngine
from italianollama.memory.placement_test_service import PlacementTestNeo4jService

logger = logging.getLogger(__name__)


class PlacementTestOrchestrator:
    """Orchestrates placement test execution with Neo4j persistence."""

    def __init__(self, neo4j_service: PlacementTestNeo4jService):
        """Initialize orchestrator."""
        self.neo4j_service = neo4j_service
        self.test_config = get_placement_test()
        self.test_engine = PlacementTestEngine(self.test_config)
        logger.info("✓ PlacementTestOrchestrator initialized")

    async def initialize_graph(self) -> None:
        """Initialize test structure in graph (run once at startup)."""
        logger.info("🗂️ Initializing placement test graph structure...")

        # Create test node
        await self.neo4j_service._ensure_test_exists(
            test_name=self.test_config.name,
            version=self.test_config.version,
            total_questions=len(self.test_engine.get_all_questions()),
            description=self.test_config.description,
        )

        # Create section nodes and question nodes
        for section in self.test_config.sections:
            await self.neo4j_service._ensure_section_exists(
                section_letter=section.section_letter,
                level=section.level.value,
                question_count=len(section.questions),
                passing_score=section.passing_score,
            )

            for question in section.questions:
                await self.neo4j_service._ensure_question_exists(
                    question_id=question.id,
                    level=question.level.value,
                    section=question.section,
                    text=question.question_text,
                    grammar_point=question.grammar_point,
                )

            # Link section to questions
            await self.neo4j_service._link_section_questions(
                section_letter=section.section_letter,
                question_count=len(section.questions),
            )

        # Link test to sections
        await self.neo4j_service._link_test_sections(
            test_name=self.test_config.name,
            sections=[{"level": s.level.value} for s in self.test_config.sections],
        )

        logger.info("✅ Graph structure initialized successfully")

    async def start_test_session(self, student_id: str) -> str:
        """Start a new test session for student."""
        logger.info(f"🚀 Starting test session for {student_id}")

        # Create session in graph
        session_id = await self.neo4j_service.create_test_session(
            student_id=student_id,
            test_name=self.test_config.name,
        )

        # Link student to session
        await self.neo4j_service.link_student_to_session(student_id)
        await self.neo4j_service.link_session_to_test(student_id, self.test_config.name)

        logger.info(f"✓ Test session started: {session_id}")
        return session_id

    async def record_answer(
        self,
        student_id: str,
        question_id: int,
        selected_answer: str,
    ) -> str:
        """Record a student's answer."""
        logger.debug(f"📝 Recording answer from {student_id} for Q{question_id}")

        # Validate answer
        is_correct = self.test_engine.validate_answer(question_id, selected_answer)

        # Get question for context
        question = self.test_engine._get_question_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")

        # Create answer node in graph
        answer_id = await self.neo4j_service.create_answer_node(
            question_id=question_id,
            student_id=student_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            question_level=question.level.value,
        )

        # Link answer to question
        await self.neo4j_service.link_answer_to_question(answer_id, question_id)

        logger.info(f"✓ Answer recorded: {answer_id} (correct={is_correct})")
        return answer_id

    async def complete_test(
        self,
        student_id: str,
        session_id: str,
        answers: dict[int, str],
    ) -> PlacementTestResult:
        """Complete test, calculate results, and persist to graph."""
        logger.info(f"🎯 Completing test for {student_id}")

        # Score the test using the engine
        result = self.test_engine.score_test(answers, student_id=student_id)
        logger.info(f"✓ Test scored: {result.determined_level.value} ({result.score_percentage}%)")

        # Create test result node
        result_id = await self.neo4j_service.create_test_result(
            student_id=student_id,
            determined_level=result.determined_level.value,
            total_correct=result.total_correct,
            total_questions=result.total_questions,
            score_percentage=result.score_percentage,
        )
        logger.info(f"✓ Result node created: {result_id}")

        # Link result to all answers
        linked_count = await self.neo4j_service.link_result_to_answers(student_id)
        logger.info(f"✓ Linked {linked_count} answers to result")

        # Link student to result
        await self.neo4j_service.link_student_to_result(student_id)
        logger.info("✓ Student linked to result")

        # Link student to determined level
        confidence = 0.95 if result.score_percentage >= 70 else 0.7
        await self.neo4j_service.link_student_to_level(
            student_id=student_id,
            level=result.determined_level.value,
            confidence=confidence,
            percentage=result.score_percentage,
        )
        logger.info(f"✓ Student linked to level {result.determined_level.value}")

        # Complete the session
        await self.neo4j_service.complete_test_session(student_id, session_id, result_id)
        logger.info("✓ Test session completed")

        return result

    async def get_student_history(self, student_id: str) -> dict:
        """Get complete test history for student."""
        logger.debug(f"📊 Fetching test history for {student_id}")

        history = await self.neo4j_service.get_student_placement_history(student_id)
        latest_level = await self.neo4j_service.get_latest_placement_level(student_id)

        return {
            "student_id": student_id,
            "attempts": history,
            "current_level": latest_level,
            "attempt_count": len(history),
        }

    async def get_section_performance(self, student_id: str, section_letter: str) -> dict:
        """Get performance on specific section."""
        logger.debug(f"📊 Fetching section {section_letter} performance for {student_id}")
        return await self.neo4j_service.get_section_performance(student_id, section_letter)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================


async def create_orchestrator(
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "neo4j",
    neo4j_database: str = "neo4j",
    initialize: bool = False,
) -> PlacementTestOrchestrator:
    """
    Create and optionally initialize placement test orchestrator.

    Args:
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
        neo4j_database: Neo4j database name
        initialize: Whether to initialize graph structure

    Returns:
        Initialized PlacementTestOrchestrator instance
    """
    logger.info("🏗️ Creating PlacementTestOrchestrator...")

    # Create Neo4j service
    service = PlacementTestNeo4jService(
        neo4j_uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password,
        database=neo4j_database,
    )
    await service.connect()

    # Create orchestrator
    orchestrator = PlacementTestOrchestrator(service)

    # Initialize graph if requested
    if initialize:
        await orchestrator.initialize_graph()

    logger.info("✓ PlacementTestOrchestrator ready")
    return orchestrator
