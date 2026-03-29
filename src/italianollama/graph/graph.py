"""Tutor Graph - LangGraph builder for Italian tutor.

This module builds the main LangGraph workflow that orchestrates
the conversation flow between different exercise types.

Graph Structure:
    ┌─────────┐
    │ router  │ ← Entry point - determines next node
    └────┬────┘
         │
    ┌────┴────────────────────────────────────────┐
    │                                             │
    ▼                                             ▼
┌─────────┐  ┌──────────┐  ┌────────────┐  ┌─────────┐
│placement│  │ vocabulary│  │  grammar   │  │  chat   │
│  (CEFR) │  │(flashcard)│  │  (drills)  │  │  (free) │
└────┬────┘  └─────┬────┘  └─────┬──────┘  └────┬────┘
     │             │              │              │
     └─────────────┴──────────────┴──────────────┘
                         │
                         ▼
                   ┌─────────┐
                   │ router  │ ← Loops back for next turn
                   └─────────┘

Phases:
    Phase 1: Basic chat (Sofia persona)
    Phase 2: Placement test (CEFR assessment)
    Phase 3: Exercise nodes (vocabulary, grammar, translation, writing)
    Phase 4: Niveau test (exam preparation)
"""

from typing import TYPE_CHECKING

from langgraph.graph import StateGraph

from italianollama.graph.nodes import (
    free_writing_node,
    grammar_node,
    niveau_test_node,
    placement_node,
    translation_node,
    vocabulary_node,
)
from italianollama.graph.nodes.base import LLMClient
from italianollama.graph.state import TutorState

if TYPE_CHECKING:
    from italianollama.memory.neo4j_client import Neo4jClient


# Sofia persona for free chat
SOFIA_PERSONA = """You are Sofia, a friendly and patient Italian language tutor.

You help students learn Italian through conversation. Be encouraging, use simple language for beginners,
and gradually increase complexity. Always provide translations and explanations when helpful.

Respond in Italian or English based on what seems appropriate for the student's level."""


async def router_node(state: TutorState) -> TutorState:
    """Determine which node to route to based on student input.

    This is the entry point that analyzes the conversation and decides
    which exercise type to invoke next.
    """
    messages = state.get("messages", [])
    current_level = state.get("current_level")
    exercise_type = state.get("exercise_type")

    # Get last user message
    last_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_msg = msg.get("content", "").lower()
            break

    # Determine route
    if not current_level:
        # No level yet - go to placement
        route = "placement"
    elif "placement" in last_msg or ("test" in last_msg and "livello" in last_msg):
        route = "placement"
    elif exercise_type == "grammar":
        route = "grammar"
    elif exercise_type == "vocabulary" or "vocabolario" in last_msg or "flashcard" in last_msg:
        route = "vocabulary"
    elif exercise_type == "translation" or "traduzione" in last_msg:
        route = "translation"
    elif exercise_type == "niveau" or "exam" in last_msg or "certificazione" in last_msg:
        route = "niveau_test"
    elif exercise_type == "free_writing" or "scrivere" in last_msg or "writing" in last_msg:
        route = "free_writing"
    else:
        # Default: free chat
        route = "chat"

    state["router_decision"] = route
    return state


async def chat_node(state: TutorState, neo4j_client: "Neo4jClient") -> TutorState:
    """Simple chat node - Phase 1.

    Free chat with Sofia persona for general conversation.
    This is the default node when no specific exercise is requested.
    """
    llm = LLMClient()
    messages = state.get("messages", [])

    try:
        response = await llm.chat(messages=messages, system_prompt=SOFIA_PERSONA)
        state["messages"] = messages + [{"role": "assistant", "content": response}]
        state["response"] = response
    except Exception as e:
        state["response"] = f"Ciao! {str(e)}"

    state["should_continue"] = True
    return state


# Node wrapper functions to pass neo4j_client
def create_node_wrapper(node_func):
    """Create a wrapper that passes neo4j_client to the node function."""

    async def wrapper(state: TutorState, neo4j_client: "Neo4jClient") -> TutorState:
        return await node_func(state, neo4j_client)

    return wrapper


def create_tutor_graph(neo4j_client: "Neo4jClient", checkpoint_db=None):
    """Create and compile the tutor LangGraph.

    Args:
        neo4j_client: Neo4j client for memory
        checkpoint_db: Optional checkpoint storage (for LangGraph persistence)

    Returns:
        Compiled LangGraph for the tutor
    """

    # Create the graph
    workflow = StateGraph(TutorState)

    # ============ Add Nodes ============

    # Router - entry point
    async def router_wrapper(state: TutorState):
        return await router_node(state)

    workflow.add_node("router", router_wrapper)

    # Chat (default free conversation)
    async def chat_wrapper(state: TutorState):
        return await chat_node(state, neo4j_client)

    workflow.add_node("chat", chat_wrapper)

    # Phase 2: Placement test
    async def placement_wrapper(state: TutorState):
        return await placement_node(state, neo4j_client)

    workflow.add_node("placement", placement_wrapper)

    # Phase 3: Exercise nodes
    async def grammar_wrapper(state: TutorState):
        return await grammar_node(state, neo4j_client)

    workflow.add_node("grammar", grammar_wrapper)

    async def vocabulary_wrapper(state: TutorState):
        return await vocabulary_node(state, neo4j_client)

    workflow.add_node("vocabulary", vocabulary_wrapper)

    async def translation_wrapper(state: TutorState):
        return await translation_node(state, neo4j_client)

    workflow.add_node("translation", translation_wrapper)

    async def free_writing_wrapper(state: TutorState):
        return await free_writing_node(state, neo4j_client)

    workflow.add_node("free_writing", free_writing_wrapper)

    # Phase 4: Niveau test (exam preparation)
    async def niveau_test_wrapper(state: TutorState):
        return await niveau_test_node(state, neo4j_client)

    workflow.add_node("niveau_test", niveau_test_wrapper)

    # ============ Define Edges ============

    # Start at router
    workflow.set_entry_point("router")

    # Router determines next node via conditional edges
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("router_decision", "chat"),
        {
            "placement": "placement",
            "grammar": "grammar",
            "vocabulary": "vocabulary",
            "translation": "translation",
            "free_writing": "free_writing",
            "niveau_test": "niveau_test",
            "chat": "chat",
        },
    )

    # All exercise nodes lead back to router for continued conversation
    for node in [
        "placement",
        "grammar",
        "vocabulary",
        "translation",
        "free_writing",
        "niveau_test",
        "chat",
    ]:
        workflow.add_edge(node, "router")

    # Compile the graph
    return workflow.compile()


__all__ = ["create_tutor_graph", "router_node", "chat_node"]
