"""Translation exercise node - Phase 3.

Italian <-> English translation with scoring."""

from typing import TYPE_CHECKING

from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import TutorState

if TYPE_CHECKING:
    from italianollama.memory.neo4j_client import Neo4jClient


TRANSLATION_PROMPT = """You are an Italian translation tutor.

Your task is to:
1. Provide sentences for translation practice
2. Evaluate student's translation accuracy
3. Provide scoring and feedback

For scoring (0-100):
- 90-100: Perfect or near-perfect translation
- 70-89: Minor errors, meaning preserved
- 50-69: Some errors but main idea clear
- 0-49: Significant errors or incorrect

Provide encouraging feedback and explain mistakes."""


async def translation_node(state: TutorState, neo4j_client: "Neo4jClient") -> TutorState:
    """Run translation exercise.

    This node handles:
    - Italian to English translation
    - English to Italian translation
    - Scoring with feedback
    """
    llm = LLMClient()

    level = state.get("current_level", "A2")
    messages = state.get("messages", [])
    exercise_state = state.get("exercise_state", {})

    # Check if starting new exercise
    if not exercise_state.get("started"):
        exercise_state["started"] = True
        exercise_state["exercise"] = "translation"
        exercise_state["direction"] = "it_en"  # or en_it
        exercise_state["total_score"] = 0
        exercise_state["exercises"] = 0

    system_prompt = TRANSLATION_PROMPT

    try:
        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
        )

        state["messages"] = messages + [{"role": "assistant", "content": response}]
        state["response"] = response

        # Evaluate translation if student submitted one
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        if last_user_msg and len(messages) > 1:
            # Score the translation
            try:
                score_data = await llm.chat_with_json(
                    messages=[
                        {"role": "user", "content": f"Evaluate this translation: {last_user_msg}"}
                    ],
                    response_schema={
                        "score": "integer (0-100)",
                        "feedback": "string",
                        "improvements": ["string"],
                    },
                )

                score = score_data.get("score", 50)
                exercise_state["total_score"] = exercise_state.get("total_score", 0) + score
                exercise_state["exercises"] = exercise_state.get("exercises", 0) + 1

                # Store exercise result
                await neo4j_client.record_exercise(
                    student_id=state["student_id"],
                    exercise_type="translation",
                    score=score,
                    level=level,
                )

            except Exception:
                pass  # Non-critical

    except Exception as e:
        state["response"] = f"Mi dispiace, errore nell'esercizio di traduzione: {str(e)}"

    state["exercise_state"] = exercise_state
    state["should_continue"] = True
    return state
