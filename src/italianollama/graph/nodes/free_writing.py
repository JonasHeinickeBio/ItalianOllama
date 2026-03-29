"""Placement test node - Phase 2.

Determines student's CEFR level (A1-C2) through questions.
"""

from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import TutorState

FREE_WRITING_PROMPT = """You are an Italian writing tutor.

Your task is to:
1. Provide an open writing prompt based on student's level ({level})
2. Provide correction and feedback on their writing
3. Suggest improvements

Focus on:
- Grammar accuracy
- Vocabulary usage
- Sentence structure
- Flow and coherence

Be encouraging and constructive."""


async def free_writing_node(state: TutorState, neo4j_client) -> TutorState:
    """Run free writing exercise.

    This node handles:
    - Open writing prompts
    - Correction and feedback
    - Improvement suggestions
    """
    llm = LLMClient()

    level = state.get("current_level", "A2")
    messages = state.get("messages", [])
    exercise_state = state.get("exercise_state", {})

    # Check if starting new exercise
    if not exercise_state.get("started"):
        exercise_state["started"] = True
        exercise_state["exercise"] = "free_writing"
        exercise_state["prompt_topic"] = None

    system_prompt = FREE_WRITING_PROMPT.format(level=level)

    try:
        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
        )

        state["messages"] = messages + [{"role": "assistant", "content": response}]
        state["response"] = response

        # Analyze writing if student submitted text
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        # If student wrote something substantial, analyze it
        if last_user_msg and len(last_user_msg) > 50 and len(messages) > 1:
            try:
                analysis = await llm.chat_with_json(
                    messages=[
                        {"role": "user", "content": f"Analyze this Italian text: {last_user_msg}"}
                    ],
                    response_schema={
                        "grammar_issues": [
                            {"original": "string", "correction": "string", "explanation": "string"}
                        ],
                        "vocabulary_suggestions": [{"word": "string", "suggestion": "string"}],
                        "overall_score": "integer (0-100)",
                        "strengths": ["string"],
                        "improvements": ["string"],
                    },
                )

                # Store writing exercise
                await neo4j_client.record_exercise(
                    student_id=state["student_id"],
                    exercise_type="free_writing",
                    score=analysis.get("overall_score", 50),
                    level=level,
                    content=last_user_msg,
                )

            except Exception:
                pass  # Non-critical

    except Exception as e:
        state["response"] = f"Mi dispiace, errore nell'esercizio di scrittura: {str(e)}"

    state["exercise_state"] = exercise_state
    state["should_continue"] = True
    return state
