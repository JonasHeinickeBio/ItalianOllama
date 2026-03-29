"""Placement test node - Phase 2.

Determines student's CEFR level (A1-C2) through questions.
"""

from app.graph.nodes.base import LLMClient
from app.graph.state import TutorState

# CEFR levels
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Placement test system prompt
PLACEMENT_PROMPT = """You are conducting a placement test to determine the student's Italian language level.

Ask 3-5 questions to assess the student's level. Start with easy questions and adjust based on responses.

Evaluate and return a JSON with:
- "level": CEFR level (A1, A2, B1, B2, C1, C2)
- "confidence": 0.0-1.0 indicating confidence in assessment
- "reasoning": brief explanation of why you chose this level

Be encouraging and professional."""


async def placement_node(state: TutorState, neo4j_client) -> TutorState:
    """Run placement test to determine student level.
        router_decision: str  # Decision from router node


        This node is called when:
        - New student (no level stored)


    # CEFR Level constants
    CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

    # Exercise type constants
    EXERCISE_TYPES = [
        "placement",
        "grammar",
        "vocabulary",
        "translation",
        "free_writing",
        "niveau_test",
        "chat",
    ]
        # Routing
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
            # Extract level from response
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
                state["current_level"] = level_data.get("level", "A1")
                state["level_confidence"] = level_data.get("confidence", 0.5)

                # Store in Neo4j
                await neo4j_client.set_student_level(
                    state["student_id"],
                    state["current_level"],
                    state["level_confidence"],
                )

                state["response"] = (
                    f"Ho determinato che il tuo livello è {state['current_level']}. {level_data.get('reasoning', '')}"
                )
            except Exception:
                # Fallback to text response
                response = await llm.chat(messages=messages, system_prompt=PLACEMENT_PROMPT)
                state["response"] = response
                state["messages"] = state.get("messages", []) + [
                    {"role": "assistant", "content": response}
                ]

    except Exception as e:
        state["response"] = f"Mi dispiace, ho avuto un problema con il test di placement: {str(e)}"

    state["should_continue"] = True
    return state
