"""Vocabulary exercise node - Phase 3.

Flashcard loop with spaced repetition."""

from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import TutorState

VOCABULARY_PROMPT = """You are an Italian vocabulary tutor.

Your task is to:
1. Present vocabulary flashcards based on student's level ({level})
2. Test translation and usage
3. Track confidence scores for spaced repetition

Topics to cover:
- daily_conversation
- food_and_dining
- travel
- healthcare
- science

Be encouraging and provide example sentences."""


async def vocabulary_node(state: TutorState, neo4j_client) -> TutorState:
    """Run vocabulary exercise (flashcards).

    This node handles vocabulary learning:
    - Flashcard presentation
    - Translation tests
    - Spaced repetition based on confidence
    """
    llm = LLMClient()

    level = state.get("current_level", "A2")
    messages = state.get("messages", [])
    exercise_state = state.get("exercise_state", {})

    # Check if starting new exercise
    if not exercise_state.get("started"):
        exercise_state["started"] = True
        exercise_state["exercise"] = "vocabulary"
        exercise_state["current_card"] = 0
        exercise_state["correct"] = 0
        exercise_state["total"] = 0

    system_prompt = VOCABULARY_PROMPT.format(level=level)

    try:
        # Get words student is learning
        words = await neo4j_client.get_student_vocabulary(
            student_id=state["student_id"],
            limit=10,
        )

        if words:
            # Add learned words context
            word_list = ", ".join([f"{w['word']} ({w['translation']})" for w in words])
            system_prompt += f"\n\nThe student is currently learning: {word_list}"

        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
        )

        state["messages"] = messages + [{"role": "assistant", "content": response}]
        state["response"] = response

        # Check for new vocabulary words to learn
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        if last_user_msg and len(last_user_msg) > 20:
            # Extract potential new words
            try:
                new_words = await llm.chat_with_json(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Extract any Italian words from this text that might be new vocabulary: {last_user_msg}",
                        }
                    ],
                    response_schema={
                        "words": [{"italian": "string", "english": "string", "topic": "string"}]
                    },
                )

                for word in new_words.get("words", []):
                    await neo4j_client.add_vocabulary(
                        student_id=state["student_id"],
                        word=word.get("italian", ""),
                        translation=word.get("english", ""),
                        topic=word.get("topic", "general"),
                        level=level,
                    )
            except Exception:
                pass  # Non-critical

        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Vocabulary node exception: {type(e).__name__}: {e}", exc_info=True)
        state["response"] = (
            "Mi dispiace, errore nell'esercizio di vocabolario. Per favore, riprova."
        )

    state["exercise_state"] = exercise_state
    state["request_done"] = state.get("single_request", False)
    state["should_continue"] = not state.get("request_done", False)
    return state
