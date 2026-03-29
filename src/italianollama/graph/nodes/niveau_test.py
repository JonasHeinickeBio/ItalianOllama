"""Niveau test (CEFR exam prep) node - Phase 4.

Simulates official CEFR test structure (TELC, Goethe-style).
"""

from typing import TYPE_CHECKING

from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import TutorState

if TYPE_CHECKING:
    from italianollama.memory.neo4j_client import Neo4jClient


# Available test types
TEST_TYPES = ["TELC", "Goethe", "CELI", "CILS", "PLIDA"]

NIVEAU_TEST_PROMPT = """You are preparing a student for an official Italian language proficiency test.

Test type: {test_type}
Target level: {level}

Your task is to:
1. Simulate test questions (reading, writing, listening comprehension)
2. Evaluate responses
3. Calculate readiness score per skill
4. Provide targeted improvement suggestions

Skills to assess:
- Reading comprehension
- Written production
- Listening comprehension (if text-based: describe audio scenario)
- Oral expression (via text prompts)

Provide detailed feedback and track readiness."""


async def niveau_test_node(state: TutorState, neo4j_client: "Neo4jClient") -> TutorState:
    """Run niveau/placement test for exam preparation.

    This node handles:
    - Official test simulation (TELC, Goethe, etc.)
    - Readiness scoring per skill
    - Test readiness tracking
    """
    llm = LLMClient()

    level = state.get("current_level", "B1")
    messages = state.get("messages", [])
    exercise_state = state.get("exercise_state", {})

    # Check if starting new test
    if not exercise_state.get("started"):
        exercise_state["started"] = True
        exercise_state["exercise"] = "niveau_test"
        exercise_state["test_type"] = "TELC"
        exercise_state["skills"] = {
            "reading": {"score": 0, "total": 0},
            "listening": {"score": 0, "total": 0},
            "speaking": {"score": 0, "total": 0},
        }

    test_type = exercise_state.get("test_type", "TELC")
    system_prompt = NIVEAU_TEST_PROMPT.format(test_type=test_type, level=level)

    try:
        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
        )

        state["messages"] = messages + [{"role": "assistant", "content": response}]
        state["response"] = response

        # Evaluate test responses
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        if last_user_msg and len(messages) > 1:
            try:
                test_result = await llm.chat_with_json(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Evaluate this test response: {last_user_msg}",
                        }
                    ],
                    response_schema={
                        "skill": "string (reading/writing/listening/speaking)",
                        "score": "integer (0-100)",
                        "feedback": "string",
                        "is_complete": "boolean",
                    },
                )

                skill = test_result.get("skill", "writing")
                score = test_result.get("score", 50)

                # Update skill scores
                if skill in exercise_state["skills"]:
                    s = exercise_state["skills"][skill]
                    s["score"] = s.get("score", 0) + score
                    s["total"] = s.get("total", 0) + 1

                # Calculate overall readiness
                total_score = sum(s["score"] for s in exercise_state["skills"].values())
                total_max = sum(s["total"] for s in exercise_state["skills"].values())
                readiness = (total_score / total_max) if total_max > 0 else 0

                # Store test results
                await neo4j_client.record_niveau_test(
                    student_id=state["student_id"],
                    test_type=test_type,
                    level=level,
                    readiness=readiness,
                    skill_scores=exercise_state["skills"],
                )

                state["response"] += (
                    f"\n\nIl tuo punteggio readiness per {test_type} {level}: {int(readiness * 100)}%"
                )

            except Exception:
                pass  # Non-critical

    except Exception as e:
        state["response"] = f"Mi dispiace, errore nel test: {str(e)}"

    state["exercise_state"] = exercise_state
    state["should_continue"] = True
    return state
