"""Grammar exercise node - Phase 3.

Grammar drilling with error detection and correction.
"""

from typing import TYPE_CHECKING

from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import TutorState

if TYPE_CHECKING:
    from italianollama.memory.neo4j_client import Neo4jClient


GRAMMAR_PROMPT = """You are an Italian language tutor focusing on grammar.

Your task is to:
1. Present a grammar exercise based on the student's level ({level})
2. Detect errors in student's responses
3. Provide corrections with explanations

Respond in Italian or English based on student's level.
Be encouraging and explain grammar rules clearly."""


async def grammar_node(state: TutorState, neo4j_client: "Neo4jClient") -> TutorState:
    """Run grammar exercise.

    This node handles grammar drilling:
    - Verb conjugations
    - Article usage
    - Sentence structure
    - Subjunctive mood
    """
    llm = LLMClient()

    level = state.get("current_level", "A2")
    messages = state.get("messages", [])
    exercise_state = state.get("exercise_state", {})

    # Check if starting new exercise
    if not exercise_state.get("started"):
        exercise_state["started"] = True
        exercise_state["exercise"] = "grammar"
        exercise_state["score"] = 0
        exercise_state["total"] = 0

    system_prompt = GRAMMAR_PROMPT.format(level=level)

    try:
        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
        )

        state["messages"] = messages + [{"role": "assistant", "content": response}]
        state["response"] = response

        # Check if student's last message contains an error to analyze
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        if last_user_msg and len(messages) > 1:
            # Analyze for grammar errors
            try:
                error_analysis = await llm.chat_with_json(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Analyze this Italian sentence for grammar errors: {last_user_msg}",
                        }
                    ],
                    response_schema={
                        "has_errors": "boolean",
                        "errors": [
                            {"original": "string", "corrected": "string", "rule": "string"}
                        ],
                        "explanation": "string",
                    },
                )

                exercise_state["total"] = exercise_state.get("total", 0) + 1

                if error_analysis.get("has_errors"):
                    for error in error_analysis.get("errors", []):
                        await neo4j_client.record_grammar_error(
                            student_id=state["student_id"],
                            original=error.get("original", ""),
                            corrected=error.get("corrected", ""),
                            rule=error.get("rule", ""),
                            level=level,
                        )
                else:
                    exercise_state["score"] = exercise_state.get("score", 0) + 1
            except Exception:
                pass  # Non-critical if error analysis fails

        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Grammar node exception: {type(e).__name__}: {e}", exc_info=True)
        state["response"] = (
            "Mi dispiace, errore nell'esercizio di grammatica. Per favore, riprova."
        )

    state["exercise_state"] = exercise_state
    state["request_done"] = state.get("single_request", False)
    state["should_continue"] = not state.get("request_done", False)
    return state
