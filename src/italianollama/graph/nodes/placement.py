"""Placement test node - Phase 2.

Determines student's CEFR level (A1-C2) through adaptive questions.
"""

from typing import TYPE_CHECKING

from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import CEFR_LEVELS, TutorState

if TYPE_CHECKING:
    from italianollama.memory.neo4j_client import Neo4jClient


# Placement test system prompt
PLACEMENT_PROMPT = """You are conducting a placement test to determine the student's Italian language level.

Ask 3-5 questions to assess the student's level. Start with easy questions and adjust based on responses.

Evaluate and return a JSON with:
- "level": CEFR level (A1, A2, B1, B2, C1, C2)
- "confidence": 0.0-1.0 indicating confidence in assessment
- "reasoning": brief explanation of why you chose this level

Be encouraging and professional."""


async def placement_node(state: TutorState, neo4j_client: "Neo4jClient") -> TutorState:
    """Run placement test to determine student level.

    This node is called when:
    - New student (no level stored)
    - Student requests re-assessment
    """
    llm = LLMClient()

    # Get conversation history
    messages = state.get("messages", [])

    # Check if student already has a level
    existing_level = state.get("current_level")
    if existing_level:
        # Skip placement if level exists
        state["response"] = (
            f"Il tuo livello attuale è {existing_level}. Vuoi fare un nuovo test di placement?"
        )
        state["should_continue"] = True
        return state

    # Run placement test
    try:
        # For new students, generate placement questions
        if len(messages) <= 1:
            response = await llm.chat(
                messages=messages,
                system_prompt=PLACEMENT_PROMPT,
            )

            # Add assistant response to history
            state["messages"] = state.get("messages", []) + [
                {"role": "assistant", "content": response}
            ]
            state["response"] = response
        else:
            # Student answered questions, determine level
            try:
                # Try to parse as JSON first
                level_data = await llm.chat_with_json(
                    messages=messages,
                    response_schema={
                        "level": "string",
                        "confidence": "float",
                        "reasoning": "string",
                    },
                    system_prompt=PLACEMENT_PROMPT,
                )
                level = level_data.get("level", "A1")
                # Validate level is a valid CEFR level
                if level not in CEFR_LEVELS:
                    level = "A1"
                state["current_level"] = level
                state["level_confidence"] = level_data.get("confidence", 0.5)

                # Store in Neo4j
                await neo4j_client.set_student_level(
                    state["student_id"],
                    state["current_level"],
                    state["level_confidence"],
                )

                # Build response with student's CEFR level
                reason = level_data.get("reasoning", "")
                state["response"] = (
                    f"Ho determinato che il tuo livello è {state['current_level']}. {reason}"
                )
            except Exception:
                # Fallback to text response
                response = await llm.chat(messages=messages, system_prompt=PLACEMENT_PROMPT)
                state["response"] = response
                state["messages"] = state.get("messages", []) + [
                    {"role": "assistant", "content": response}
                ]

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Placement node exception: {type(e).__name__}: {e}", exc_info=True)
        state["response"] = (
            "Mi dispiace, ho avuto un problema con il test di placement. Per favore, riprova."
        )

    state["request_done"] = state.get("single_request", False)
    state["should_continue"] = not state.get("request_done", False)
    return state
