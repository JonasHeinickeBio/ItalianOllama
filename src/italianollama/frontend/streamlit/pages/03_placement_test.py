"""
Placement Test Page - Interactive Italian Language Placement Test

Manages test state, question display, answer tracking, and result calculation.
Integrates with Neo4j graph for persistence of all test data.
"""

import asyncio
from datetime import datetime
import logging

import streamlit as st

from italianollama.api.config import get_settings
from italianollama.backend.placement_test import (
    CEFRLevel,
    PlacementTestEngine,
    PlacementTestOrchestrator,
    create_orchestrator,
    get_placement_test,
)
from italianollama.frontend.streamlit.pages.utils import (
    get_student_id,
    render_sidebar_full,
    require_auth,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - PLACEMENT_TEST - %(levelname)s - %(message)s",
)
logger = logging.getLogger("placement_test")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Placement Test - ItalianOllama",
    page_icon="📋",
    layout="wide",
)

# --- Authentication & State ---
require_auth()
student_id = get_student_id()

# --- Sidebar ---
render_sidebar_full("📋 Placement Test")

# ============================================================================
# INITIALIZE TEST STATE
# ============================================================================


def _initialize_orchestrator() -> PlacementTestOrchestrator | None:
    """Initialize test orchestrator with Neo4j connection.

    Returns:
        PlacementTestOrchestrator if successful, None if failed.
    """
    try:
        settings = get_settings()
        orchestrator = asyncio.run(
            create_orchestrator(
                neo4j_uri=settings.neo4j_uri,
                neo4j_user=settings.neo4j_user,
                neo4j_password=settings.neo4j_password,
                neo4j_database=settings.neo4j_database,
                initialize=True,
            )
        )
        logger.info("✓ Initialized test orchestrator with Neo4j connection")
        return orchestrator
    except Exception as e:
        logger.warning(f"⚠ Failed to initialize orchestrator: {e}")
        logger.warning("  Test data will NOT be persisted to Neo4j")
        return None


def initialize_test_state():
    """Initialize session state for placement test."""
    if "test_config" not in st.session_state:
        st.session_state.test_config = get_placement_test()
        logger.info(
            f"✓ Loaded test config with {len(st.session_state.test_config.sections)} sections"
        )

    if "test_engine" not in st.session_state:
        st.session_state.test_engine = PlacementTestEngine(st.session_state.test_config)
        logger.info("✓ Initialized test engine")

    if "test_orchestrator" not in st.session_state:
        st.session_state.test_orchestrator = _initialize_orchestrator()

    if "test_session_id" not in st.session_state:
        st.session_state.test_session_id = None

    if "test_started" not in st.session_state:
        st.session_state.test_started = False

    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    if "test_completed" not in st.session_state:
        st.session_state.test_completed = False

    if "test_result" not in st.session_state:
        st.session_state.test_result = None


initialize_test_state()

engine: PlacementTestEngine = st.session_state.test_engine
test_config = st.session_state.test_config

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_total_questions() -> int:
    """Get total number of questions."""
    return len(engine.get_all_questions())


def get_current_question():
    """Get the current question."""
    return engine.get_question_by_index(st.session_state.current_question_index)


def move_to_next_question():
    """Move to next question."""
    if st.session_state.current_question_index < get_total_questions() - 1:
        st.session_state.current_question_index += 1
    else:
        # Test completed
        st.session_state.test_completed = True


def move_to_previous_question():
    """Move to previous question."""
    if st.session_state.current_question_index > 0:
        st.session_state.current_question_index -= 1


def skip_question():
    """Mark current question as skipped and move to next."""
    current_q = get_current_question()
    if current_q and current_q.id not in st.session_state.answers:
        logger.info(f"⏭️ Skipped question {current_q.id}")
    move_to_next_question()


def complete_test():
    """Complete the test and calculate results."""
    logger.info(f"✓ Test completed by {student_id}")
    logger.info(
        f"  Answered {len(st.session_state.answers)} out of {get_total_questions()} questions"
    )

    # Score test with engine
    result = engine.score_test(st.session_state.answers, student_id=student_id)
    st.session_state.test_result = result
    st.session_state.test_completed = True

    logger.info(
        f"  Score: {result.total_correct}/{result.total_questions} "
        f"({result.score_percentage:.1f}%)"
    )
    logger.info(f"  Determined Level: {result.determined_level.value}")

    # Persist to Neo4j if orchestrator available
    orchestrator: PlacementTestOrchestrator | None = st.session_state.get("test_orchestrator")
    if orchestrator:
        try:
            # Record test result in graph
            _persist_result_to_graph(orchestrator, result, student_id)
            logger.info(f"✓ Test result persisted to Neo4j for {student_id}")
        except Exception as e:
            logger.warning(f"⚠ Failed to persist result to Neo4j: {e}")
            st.warning("⚠ Test result saved locally but not to database")


def _persist_result_to_graph(orchestrator: PlacementTestOrchestrator, result, student_id: str):
    """Persist test result to Neo4j graph.

    Args:
        orchestrator: PlacementTestOrchestrator instance
        result: PlacementTestResult from engine
        student_id: Student identifier
    """
    # Run async operation in sync context
    session_id = st.session_state.get("test_session_id")
    if not session_id:
        session_id = f"session_{datetime.now().isoformat()}"

    asyncio.run(
        orchestrator.complete_test(
            student_id=student_id,
            session_id=session_id,
            answers=st.session_state.answers,
        )
    )


# ============================================================================
# PAGE CONTENT
# ============================================================================

# --- Header ---
st.markdown(
    """
    <div class="main-header">
        <h1>📋 Italian Language Placement Test</h1>
        <h2>Determine your Italian language proficiency level (A1–C1)</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card" style="background: #f8f9fa; margin: 2rem 0;">
        <h3 style="color: var(--primary-color);">📖 How it works</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: var(--white); padding: 1rem; border-radius: 8px; box-shadow: var(--shadow);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                <strong>50 questions</strong><br>
                <small style="color: #666;">Across 5 levels (A1, A2, B1, B2, C1)</small>
            </div>
            <div style="background: var(--white); padding: 1rem; border-radius: 8px; box-shadow: var(--shadow);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                <strong>Smart scoring</strong><br>
                <small style="color: #666;">Level = highest section with ≥ 7/10 correct</small>
            </div>
            <div style="background: var(--white); padding: 1rem; border-radius: 8px; box-shadow: var(--shadow);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏱️</div>
                <strong>~25 minutes</strong><br>
                <small style="color: #666;">Average time to complete</small>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# TEST NOT STARTED
# ============================================================================

if not st.session_state.test_started:
    st.markdown(
        """
        <div class="card" style="background: #fffaf0; border-left: 4px solid var(--accent-color);">
            <h3 style="color: var(--accent-color);">🚀 Ready to begin?</h3>
            <p style="color: #555;">This test will help us determine the right starting level for your Italian lessons.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Ready to begin?")
        st.markdown(
            """
            This test will help us determine the right starting level for your Italian lessons.

            **Scoring system:**
            - Each section has 10 questions
            - You need at least 7 correct answers to "pass" a section
            - Your final level = highest section passed

            **Levels:**
            - 🔤 **A1:** Beginner (greetings, basic grammar)
            - 🔤 **A2:** Elementary (present tense, daily topics)
            - 📘 **B1:** Intermediate (past tenses, complex sentences)
            - 📗 **B2:** Upper Intermediate (subjunctive, nuanced expressions)
            - 🎓 **C1:** Advanced (formal register, literary constructs)
            """
        )

    with col2:
        if st.button("🚀 Start Test", use_container_width=True):
            st.session_state.test_started = True
            logger.info(f"🚀 Test started by {student_id}")
            st.rerun()

# ============================================================================
# TEST IN PROGRESS
# ============================================================================

elif not st.session_state.test_completed:
    current_q = get_current_question()

    if not current_q:
        st.error("❌ Could not load question. Please refresh the page.")
        st.stop()

    # --- Progress Bar ---
    total = get_total_questions()
    progress = (st.session_state.current_question_index + 1) / total
    st.progress(progress, text=f"Question {st.session_state.current_question_index + 1}/{total}")

    # --- Question Display ---
    st.markdown("---")

    # Section and grammar point
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.metric("Level", current_q.level.value)
    with col2:
        st.metric(
            "Grammar Topic",
            current_q.grammar_point[:40] + "..."
            if len(current_q.grammar_point) > 40
            else current_q.grammar_point,
        )
    with col3:
        answered = len(st.session_state.answers)
        st.metric("Answered", f"{answered}/{total}")

    st.markdown("---")

    # Question text
    st.subheader(f"Domanda {current_q.id}")
    st.markdown(f"### {current_q.question_text}")

    # --- Answer Options ---
    st.markdown("**Scegli una risposta:**")

    # Create radio buttons for options
    answer_key = None
    for option in current_q.options:
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            st.write(f"**{option.key.upper()}**")
        with col2:
            if st.button(
                option.text, use_container_width=True, key=f"opt_{current_q.id}_{option.key}"
            ):
                st.session_state.answers[current_q.id] = option.key
                logger.info(f"✓ Question {current_q.id}: Selected {option.key} ({option.text})")
                st.rerun()

    # Show selected answer (if any)
    if current_q.id in st.session_state.answers:
        selected = st.session_state.answers[current_q.id]
        selected_text = next(
            (o.text for o in current_q.options if o.key == selected),
            "Unknown",
        )
        st.success(f"✓ Selezionato: **{selected.upper()} - {selected_text}**")

    # --- Navigation ---
    st.markdown("---")
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

    with nav_col1:
        if st.button(
            "⬅️ Indietro",
            use_container_width=True,
            disabled=st.session_state.current_question_index == 0,
        ):
            move_to_previous_question()
            st.rerun()

    with nav_col2:
        if st.button("⏭️ Salta", use_container_width=True):
            skip_question()
            st.rerun()

    with nav_col3:
        st.empty()

    with nav_col4:
        if st.button("Avanti ➡️", use_container_width=True):
            if current_q.id not in st.session_state.answers:
                st.warning("⚠️ Seleziona una risposta prima di continuare")
            else:
                move_to_next_question()
                st.rerun()

    with nav_col5:
        if st.button("✅ Fine", use_container_width=True):
            if len(st.session_state.answers) < total:
                warning_msg = (
                    f"⚠️ Hai risposto solo a {len(st.session_state.answers)}"
                    f"/{total} domande. Vuoi terminare comunque?"
                )
                if st.warning(warning_msg):
                    complete_test()
                    st.rerun()
            else:
                complete_test()
                st.rerun()

# ============================================================================
# TEST COMPLETED - RESULTS
# ============================================================================

else:
    result = st.session_state.test_result

    if not result:
        st.error("❌ Could not generate results. Please refresh the page.")
        st.stop()

    # --- Results Header ---
    st.markdown(
        """
        <div class="main-header">
            <h1>🎉 Test Completed!</h1>
            <h2>Here are your placement test results</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="card" style="text-align: center;">
                <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">📊</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric(
            "Total Score",
            f"{result.total_correct}/{result.total_questions}",
            f"{result.score_percentage:.1f}%",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            """
            <div class="card" style="text-align: center;">
                <div style="font-size: 2rem; color: var(--accent-color); margin-bottom: 0.5rem;">🎓</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric("Your Level", result.determined_level.value, "CEFR")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(
            """
            <div class="card" style="text-align: center;">
                <div style="font-size: 2rem; color: var(--success-color); margin-bottom: 0.5rem;">✅</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric("Accuracy", f"{result.accuracy}%")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Level Badge ---
    st.markdown("---")
    level_colors = {
        CEFRLevel.A1: "🔤 Beginner",
        CEFRLevel.A2: "🔤 Elementary",
        CEFRLevel.B1: "📘 Intermediate",
        CEFRLevel.B2: "📗 Upper Intermediate",
        CEFRLevel.C1: "🎓 Advanced",
    }
    level_descriptions = {
        CEFRLevel.A1: "You're just starting your Italian journey! Perfect for our A1 course.",
        CEFRLevel.A2: "You have basics down. Ready for A2 conversational practice!",
        CEFRLevel.B1: "Great progress! B1 will help you express complex ideas.",
        CEFRLevel.B2: "Advanced level! B2 introduces nuance and formal register.",
        CEFRLevel.C1: "Impressive! C1 covers literary and sophisticated Italian.",
    }

    st.markdown(
        f"""
        <div class="card" style="background: #f0fff4; border-left: 4px solid var(--success-color);">
            <h3 style="color: var(--success-color); margin-top: 0;">{level_colors[result.determined_level]}</h3>
            <p style="color: #555;">{level_descriptions[result.determined_level]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Section Performance ---
    st.markdown(
        """
        <div class="card">
            <h3 style="color: var(--primary-color);">📊 Performance by Section</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_summary = engine.get_section_summary()
    perf_data = []

    for section_letter in ["A", "B", "C", "D", "E"]:
        if section_letter in result.section_scores:
            score = result.section_scores[section_letter]
            section_info = section_summary[section_letter]
            level = section_info["level"]
            max_score = section_info["question_count"]
            passing = section_info["passing_score"]
            status = "✅ PASSED" if score >= passing else "❌ FAILED"
            perf_data.append(
                {
                    "Section": f"{section_letter} ({level})",
                    "Score": f"{score}/{max_score}",
                    "Status": status,
                }
            )

    try:
        import pandas as pd

        perf_df = pd.DataFrame(perf_data)
        st.dataframe(perf_df, use_container_width=True, hide_index=True)
    except ImportError:
        for row in perf_data:
            st.write(f"**{row['Section']}**: {row['Score']} {row['Status']}")

    # --- Errors (if any) ---
    errors = [a for a in result.answers if not a.is_correct]
    if errors and len(errors) <= 20:
        st.markdown("---")
        st.subheader(f"❌ Questions You Missed ({len(errors)})")
        for error in errors[:5]:  # Show first 5 errors
            question = engine._get_question_by_id(error.question_id)
            if question:
                with st.expander(f"Q{error.question_id}: {question.question_text[:60]}..."):
                    st.write(f"**Your answer:** {error.selected_answer.upper()}")
                    correct_answer_display = (
                        f"{question.correct_answer.upper()} - {question.correct_answer_text}"
                    )
                    st.write(f"**Correct answer:** {correct_answer_display}")
                    st.write(f"**Grammar point:** {question.grammar_point}")

    # --- Next Steps ---
    st.markdown("---")
    st.subheader("📖 Next Steps")
    st.markdown(
        f"""
        ✅ Your placement level is **{result.determined_level.value}**

        1. Return to the dashboard
        2. Select your lessons starting at level **{result.determined_level.value}**
        3. Progress at your own pace

        Good luck! 🇮🇹
        """
    )

    # --- Buttons ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Back to Dashboard", use_container_width=True):
            st.switch_page("pages/02_dashboard.py")
    with col2:
        if st.button("🔄 Retake Test", use_container_width=True):
            # Reset test state
            for key in [
                "test_started",
                "current_question_index",
                "answers",
                "test_completed",
                "test_result",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
