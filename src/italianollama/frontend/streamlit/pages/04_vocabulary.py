"""
Vocabulary Page - Italian Tutor Frontend (Modern & Professional)

Features:
- Modern UI with glassmorphism design
- Flashcard review with SM-2 spaced repetition
- CEFR level filtering and search
- Progress tracking with Neo4j graph database
- Session tracking and analytics dashboard
- Interactive vocabulary cards with confidence tracking
"""

from datetime import datetime
import random
import time
from typing import Any

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    get_api_client,
    get_student_id,
    render_page_navigation,
    render_sidebar_full,
    require_auth,
)

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Vocabolario - ItalianOllama",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
student_id = get_student_id()
render_sidebar_full("📝 Vocabolario")

api = get_api_client()

# Initialize session state for vocabulary tracking
if "vocabulary_state" not in st.session_state:
    st.session_state.vocabulary_state = {
        "last_action": None,
        "last_action_time": None,
    }


# === HELPER FUNCTIONS ===


@st.cache_data(ttl=120)
def get_vocabulary_items(
    due_for_review: bool = False,
    level_filter: str | None = None,
    vocabulary_type: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch vocabulary with caching.

    Args:
        due_for_review: Filter by review status (currently ignored)
        level_filter: Filter by CEFR level
        vocabulary_type: Filter by type (premade, self-made, or None for all)
    """
    try:
        vocabulary = api.get_vocabulary(student_id, due_for_review=due_for_review)
        if vocabulary is None:
            return []

        if vocabulary_type:
            vocabulary = [w for w in vocabulary if w.get("vocabulary_type") == vocabulary_type]

        if level_filter and level_filter != "All":
            vocabulary = [w for w in vocabulary if w.get("cefr_level") == level_filter]

        return vocabulary
    except Exception as e:
        st.error(f"❌ Error fetching vocabulary: {str(e)}")
        return []


@st.cache_data(ttl=300)
def get_cefr_levels() -> list[str]:
    """Get all CEFR levels from vocabulary."""
    try:
        all_vocab = api.get_vocabulary(student_id, due_for_review=False)
        if not all_vocab:
            return ["A1", "A2", "B1", "B2"]
        levels = list(set(w.get("cefr_level", "A1") for w in all_vocab))
        return sorted(levels)
    except Exception:
        return ["A1", "A2", "B1", "B2"]


@st.cache_data(ttl=300)
def get_vocabulary_type_counts() -> dict[str, int]:
    """Get count of vocabulary by type (premade, self-made)."""
    try:
        all_vocab = api.get_vocabulary(student_id, due_for_review=False)
        if not all_vocab:
            return {"premade": 0, "self-made": 0}

        counts = {"premade": 0, "self-made": 0}
        for word in all_vocab:
            vtype = word.get("vocabulary_type", "premade")
            if vtype in counts:
                counts[vtype] += 1

        return counts
    except Exception:
        return {"premade": 0, "self-made": 0}


def track_session(session_type: str, details: dict[str, Any]) -> None:
    """Track session in Neo4j via TutorAPIClient."""
    try:
        session_data = {
            "student_id": student_id,
            "session_type": session_type,
            "started_at": datetime.now().isoformat(),
            "details": details,
            "duration_seconds": details.get("duration", 0),
            "words_reviewed": details.get("words_reviewed", 0),
            "correct_answers": details.get("correct_answers", 0),
            "accuracy": details.get("accuracy", 0),
        }

        # Create session in Neo4j via API
        result = api.create_session(student_id, session_type, details)
        if result:
            session_data["session_id"] = result.get("session_id")
            st.session_state.last_session = session_data
            st.session_state.session_history = api.get_session_history(student_id, limit=10) or []
        else:
            # Fallback to session state if API unavailable
            st.session_state.last_session = session_data

    except Exception as e:
        st.session_state.debug_message = f"Session tracking logged (API unavailable): {str(e)}"


def run_flashcard_review(vocabulary: list[dict[str, Any]], num_cards: int = 10) -> dict[str, Any]:
    """Run flashcard review session and track results."""
    if not vocabulary:
        return {"error": "No vocabulary available"}

    cards = random.sample(vocabulary, min(num_cards, len(vocabulary)))

    results: dict[str, Any] = {
        "total": len(cards),
        "correct": 0,
        "incorrect": 0,
        "session_words": [],
    }

    st.markdown(
        """
        <div class="card" style="text-align: center;">
            <h2 style="margin: 0; color: var(--primary-color);">🃏 Flashcard Review Session</h2>
            <p style="color: #6b7280; margin-top: 0.5rem; font-size: 1.1rem;">
                Reviewing <strong style="color: var(--primary-color); font-size: 1.35rem;">
                {len(cards)} cards</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    progress_container = st.empty()
    progress_bar = progress_container.progress(0)
    cards_completed = 0

    for i, card in enumerate(cards, 1):
        card_container = st.container()

        with card_container:
            st.markdown(
                f"""
            <div class="flashcard">
                <div style="font-size: 0.875rem; color: #9ca3af; margin-bottom: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                    Card {i} of {len(cards)}
                </div>
                <div class="flashcard-word">
                    {i}. {card.get("italian_word", "N/A")}
                </div>
                <div class="flashcard-translation">
                    {card.get("english_translation", "N/A")}
                </div>
                {f'<p style="color: var(--secondary-color); font-weight: 600;">Topic: {card.get("topic", "N/A")}</p>' if card.get("topic") else ""}
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                topic = card.get("topic")
                level = card.get("cefr_level")
                if topic or level:
                    st.markdown(
                        f'<p style="text-align: center; color: #6b7280; font-size: 0.95rem;">'
                        f"📌 {topic or 'N/A'} | Level: {level}</p>",
                        unsafe_allow_html=True,
                    )

            with col2:
                if st.button("💡 Show Definition", key=f"show_def_{i}", use_container_width=True):
                    st.info(f"**Definition/Explanation:** {card.get('definition', 'N/A')}")

            st.markdown("---")

            st.markdown(
                '<p style="text-align: center; font-weight: 700; margin-bottom: 1.25rem; color: var(--primary-color);">'
                "Did you know this word?</p>",
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)

            confidence = None

            with col1:
                if st.button("❌ Not at all", key=f"conf_0_{i}", use_container_width=True):
                    confidence = "❌ Not at all"

            with col2:
                if st.button("🤔 Somewhat", key=f"conf_1_{i}", use_container_width=True):
                    confidence = "🤔 Somewhat"

            with col3:
                if st.button("✅ Confident", key=f"conf_2_{i}", use_container_width=True):
                    confidence = "✅ Confident"

            # Record result
            if confidence:
                if confidence == "✅ Confident":
                    results["correct"] += 1
                elif confidence == "🤔 Somewhat":
                    results["correct"] += 0.5
                else:
                    results["incorrect"] += 1

                results["session_words"].append(
                    {
                        "word": card.get("italian_word"),
                        "level": card.get("cefr_level"),
                        "known": confidence == "✅ Confident",
                    }
                )

                cards_completed = i
                progress_bar.progress(cards_completed / len(cards))

        # Add spacing between cards
        st.markdown("<br>", unsafe_allow_html=True)

    accuracy = (results["correct"] / results["total"]) * 100

    session_details = {
        "duration": 0,
        "words_reviewed": results["total"],
        "correct_answers": results["correct"],
        "accuracy": round(accuracy, 1),
        "flashcards_shown": results["total"],
    }

    track_session("flashcard_review", session_details)

    st.session_state.last_flashcard_session = {
        **results,
        "accuracy": accuracy,
        "session_details": session_details,
    }

    return {
        **results,
        "accuracy": accuracy,
        "session_details": session_details,
    }


# === PAGE CONTENT ===
st.markdown(
    """
    <div class="main-header">
        <h1>📝 Gestione Vocabolario</h1>
        <h2>Costruisci il tuo vocabolario italiano con spaced repetition</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Apply custom tab container styling
st.markdown(
    """
    <style>
    .tab-container [role="tablist"] {
        background: #f8fafc;
        padding: 0.5rem 1rem;
        border-radius: 10px 10px 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create tabs
tab_premade, tab_selfmade, tab_add, tab_flashcard, tab_progress = st.tabs(
    [
        "📖 Premade Vocabulary",
        "Self-made Vocabulary",
        "➕ Add New Word",
        "🃏 Flashcard Review",
        "📊 Progress",
    ]
)

with tab_premade:
    st.markdown('<div class="section-title">📖 Premade Vocabulary</div>', unsafe_allow_html=True)

    vocabulary = get_vocabulary_items(due_for_review=False, vocabulary_type="premade")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Premade", len(vocabulary))
    with col2:
        st.metric(
            "Premade A1-A2",
            len(
                [w for w in vocabulary if w.get("cefr_level") in ["A1.1", "A1.2", "A2.1", "A2.2"]]
            ),
        )
    with col3:
        st.metric(
            "Premade B1+",
            len(
                [w for w in vocabulary if w.get("cefr_level") in ["B1.1", "B1.2", "B2.1", "B2.2"]]
            ),
        )

    st.markdown("---")
    st.markdown(
        '<div class="section-subtitle">Browse premade vocabulary from PDF textbooks</div>',
        unsafe_allow_html=True,
    )

    levels = get_cefr_levels()
    col1, col2 = st.columns([2, 3])

    with col1:
        level_filter = st.selectbox(
            "🔍 Livello CEFR",
            options=["All"] + levels,
            index=0,
            key="premade_level_filter",
        )

    with col2:
        search_term = st.text_input(
            "🔍 Cerca parola...",
            placeholder="Cerca per parola italiana...",
            key="premade_search",
        )

    filtered_vocab = [
        w
        for w in vocabulary
        if (level_filter == "All" or w.get("cefr_level") == level_filter)
        and (
            not search_term
            or search_term.lower() in w.get("italian_word", "").lower()
            or search_term.lower() in w.get("english_translation", "").lower()
            or search_term.lower() in w.get("topic", "").lower()
        )
    ]

    if filtered_vocab:
        st.success(f"📚 Hai **{len(filtered_vocab)}** parole nel tuo vocabolario premade")

        st.markdown(f"**Mostrando {len(filtered_vocab)} parole**")

        cols_per_row = 4
        rows = (len(filtered_vocab) + cols_per_row - 1) // cols_per_row

        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                vocab_idx = row * cols_per_row + col_idx
                if vocab_idx < len(filtered_vocab):
                    word = filtered_vocab[vocab_idx]
                    with cols[col_idx]:
                        st.markdown(
                            f"""
                            <div class="card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                                    <h3 style="color: var(--primary-color); margin: 0; font-size: 1.25rem;">
                                        {word.get("italian_word", "N/A")}
                                    </h3>
                                    {
                                f'<span class="badge badge-{word.get("cefr_level", "a1").lower()}">{word.get("cefr_level", "N/A")}</span>'
                                if word.get("cefr_level")
                                else ""
                            }
                                </div>
                                <p style="color: #4b5563; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 500;">
                                    {word.get("english_translation", "")}
                                </p>
                                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
                                    {
                                f'<span class="badge badge-topic">{word.get("topic", "N/A")}</span>'
                                if word.get("topic")
                                else ""
                            }
                                </div>
                                {
                                f'''
                                <div style="margin-top: 1rem;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.375rem;">
                                        <small style="color: #6b7280; font-weight: 600;">Confidence</small>
                                        <span style="color: var(--accent-color); font-weight: 700;">{word.get("confidence_level", 0) * 100:.0f}%</span>
                                    </div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {min(word.get("confidence_level", 0) * 100, 100)}%; background: linear-gradient(90deg, var(--primary-color), var(--accent-color));">
                                        </div>
                                    </div>
                                </div>
                                '''
                                if word.get("confidence_level") is not None
                                else '<p style="color: #9ca3af; font-style: italic; text-align: center; margin-top: 1rem;">No confidence data available</p>'
                            }
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
    else:
        st.warning("❌ Nessuna parola trovata nel vocabolario premade")


with tab_selfmade:
    st.markdown('<div class="section-title">Self-made Vocabulary</div>', unsafe_allow_html=True)

    vocabulary = get_vocabulary_items(due_for_review=False, vocabulary_type="self-made")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Self-made", len(vocabulary))
    with col2:
        st.metric(
            "Self-made A1-A2",
            len(
                [w for w in vocabulary if w.get("cefr_level") in ["A1.1", "A1.2", "A2.1", "A2.2"]]
            ),
        )
    with col3:
        st.metric(
            "Self-made B1+",
            len(
                [w for w in vocabulary if w.get("cefr_level") in ["B1.1", "B1.2", "B2.1", "B2.2"]]
            ),
        )

    st.markdown("---")
    st.markdown(
        '<div class="section-subtitle">Your custom vocabulary entries</div>',
        unsafe_allow_html=True,
    )

    levels = get_cefr_levels()
    col1, col2 = st.columns([2, 3])

    with col1:
        level_filter = st.selectbox(
            "🔍 Livello CEFR",
            options=["All"] + levels,
            index=0,
            key="selfmade_level_filter",
        )

    with col2:
        search_term = st.text_input(
            "🔍 Cerca parola...",
            placeholder="Cerca per parola italiana...",
            key="selfmade_search",
        )

    filtered_vocab = [
        w
        for w in vocabulary
        if (level_filter == "All" or w.get("cefr_level") == level_filter)
        and (
            not search_term
            or search_term.lower() in w.get("italian_word", "").lower()
            or search_term.lower() in w.get("english_translation", "").lower()
            or search_term.lower() in w.get("topic", "").lower()
        )
    ]

    if filtered_vocab:
        st.success(f"📚 Hai **{len(filtered_vocab)}** parole nel tuo vocabolario self-made")

        st.markdown(f"**Mostrando {len(filtered_vocab)} parole**")

        cols_per_row = 4
        rows = (len(filtered_vocab) + cols_per_row - 1) // cols_per_row

        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                vocab_idx = row * cols_per_row + col_idx
                if vocab_idx < len(filtered_vocab):
                    word = filtered_vocab[vocab_idx]
                    with cols[col_idx]:
                        st.markdown(
                            f"""
                            <div class="card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                                    <h3 style="color: var(--primary-color); margin: 0; font-size: 1.25rem;">
                                        {word.get("italian_word", "N/A")}
                                    </h3>
                                    {
                                f'<span class="badge badge-{word.get("cefr_level", "a1").lower()}">{word.get("cefr_level", "N/A")}</span>'
                                if word.get("cefr_level")
                                else ""
                            }
                                </div>
                                <p style="color: #4b5563; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 500;">
                                    {word.get("english_translation", "")}
                                </p>
                                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
                                    {
                                f'<span class="badge badge-topic">{word.get("topic", "N/A")}</span>'
                                if word.get("topic")
                                else ""
                            }
                                </div>
                                {
                                f'''
                                <div style="margin-top: 1rem;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.375rem;">
                                        <small style="color: #6b7280; font-weight: 600;">Confidence</small>
                                        <span style="color: var(--accent-color); font-weight: 700;">{word.get("confidence_level", 0) * 100:.0f}%</span>
                                    </div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {min(word.get("confidence_level", 0) * 100, 100)}%; background: linear-gradient(90deg, var(--primary-color), var(--accent-color));">
                                        </div>
                                    </div>
                                </div>
                                '''
                                if word.get("confidence_level") is not None
                                else '<p style="color: #9ca3af; font-style: italic; text-align: center; margin-top: 1rem;">No confidence data available</p>'
                            }
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
    else:
        st.warning("❌ Nessuna parola trovata nel vocabolario self-made")


# === TAB 3: ADD NEW WORD ===
with tab_add:
    st.markdown('<div class="section-title">Aggiungi Nuova Parola</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        italian = st.text_input(
            "Parola italiana *",
            placeholder="Es: gatto",
            key="add_italian",
            label_visibility="visible",
        )

    with col2:
        english = st.text_input(
            "Traduzione inglese *",
            placeholder="Es: cat",
            key="add_english",
            label_visibility="visible",
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        pos = st.selectbox(
            "Parte del discorso *",
            ["noun", "verb", "adjective", "adverb", "preposition", "other"],
            key="add_pos",
            label_visibility="visible",
        )

    with col2:
        level = st.selectbox(
            "Livello CEFR *",
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            key="add_level",
            label_visibility="visible",
        )

    with col3:
        topic = st.text_input(
            "Argomento",
            placeholder="Es: food, family",
            key="add_topic",
            label_visibility="visible",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    example_sentence = st.text_area(
        "Frase di esempio (opzionale)",
        placeholder="Es: Il gatto è nero. Lo tengo come animale domestico.",
        key="add_sentence",
        height=100,
        label_visibility="visible",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)

    submit = st.button("✅ Aggiungi Parola", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if submit:
        if not italian or not english:
            st.error("❌ Compila i campi obbligatori")
            st.stop()

        with st.spinner("Aggiungendo parola..."):
            try:
                result = api.add_vocabulary(
                    student_id,
                    italian.strip(),
                    english.strip(),
                    pos,
                    level,
                    topic.strip() if topic else None,
                )
                if result:
                    st.success(f"✅ **{italian}** aggiunta con successo!")
                    st.balloons()
                    time.sleep(1.5)
                    st.session_state.vocabulary_state["last_action"] = "added_word"
                    st.session_state.vocabulary_state["last_action_time"] = datetime.now()
                    st.rerun()
                else:
                    st.error("❌ Errore nell'aggiunta della parola")
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")


# === TAB 4: FLASHCARD REVIEW ===
with tab_flashcard:
    st.markdown(
        '<div class="section-title">Flashcard Review Session</div>', unsafe_allow_html=True
    )

    levels = get_cefr_levels()
    col1, col2 = st.columns([2, 3])

    with col1:
        level_filter = st.selectbox(
            "Livello da ripassare",
            options=["All"] + levels,
            index=0,
            key="flashcard_level",
        )

    with col2:
        st.caption("Seleziona il livello CEFR per la sessione di flashcard")

    due_vocab = get_vocabulary_items(due_for_review=True, level_filter=level_filter)

    if not due_vocab:
        due_vocab = get_vocabulary_items(due_for_review=False, level_filter=level_filter)

    if due_vocab:
        st.success(f"📚 Trovate **{len(due_vocab)}** parole disponibili")

        col1, col2 = st.columns([2, 3])

        with col1:
            num_cards = st.slider(
                "Numero di flashcard da ripassare",
                min_value=5,
                max_value=min(50, len(due_vocab)) if due_vocab else 50,
                value=10,
                step=5,
            )

        with col2:
            st.caption(f"Ripasserai {num_cards} parole per rafforzare la memoria")

        col1, col2 = st.columns([1, 4])

        with col1:
            if st.button("▶️ Inizia Sessione", use_container_width=True, type="primary"):
                st.session_state.is_reviewing = True
                st.session_state.current_review_vocab = due_vocab
                st.session_state.current_review_count = num_cards
                st.rerun()

        with col2:
            if "is_reviewing" in st.session_state and st.session_state.is_reviewing:
                st.success("🔄 Sessione in corso...")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📖</div>
                <h3 style="color: #1f2937; margin-bottom: 1rem;">Nessuna parola disponibile</h3>
                <p style="color: #6b7280;">Aggiungi parole al tuo vocabolario per iniziare a ripassare!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# === TAB 5: PROGRESSO ===
with tab_progress:
    st.markdown('<div class="section-title">Progresso Apprendimento</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Statistiche Generali")

        premade_vocab = get_vocabulary_items(due_for_review=False, vocabulary_type="premade")
        selfmade_vocab = get_vocabulary_items(due_for_review=False, vocabulary_type="self-made")
        all_vocab = premade_vocab + selfmade_vocab

        if all_vocab:
            total_words = len(all_vocab)
            levels_count = {}
            for word in all_vocab:
                lvl = word.get("cefr_level", "Unknown")
                levels_count[lvl] = levels_count.get(lvl, 0) + 1

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>Totali Parole</h3>
                        <div class="value">{total_words}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                known_words = sum(1 for w in all_vocab if w.get("confidence_level", 0) >= 0.8)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>Parole Note</h3>
                        <div class="value">{known_words}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col3:
                unknown_words = sum(1 for w in all_vocab if w.get("confidence_level", 0) < 0.3)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>Da Ripassare</h3>
                        <div class="value">{unknown_words}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown("**Vocabulary Type Distribution**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Premade", len(premade_vocab))
            with col2:
                st.metric("Self-made", len(selfmade_vocab))

            st.markdown("---")

            # CEFR Distribution
            st.markdown("**Distribuzione per Livello CEFR**")
            for level in sorted(levels_count.keys()):
                count = levels_count[level]
                pct = (count / total_words) * 100
                st.progress(
                    min(pct / 100, 1.0),
                    text=f"{level}: {count} ({pct:.1f}%)",
                )
        else:
            st.info("📊 Aggiungi parole per vedere le statistiche")

    with col2:
        st.markdown("### 🏆 Statistiche Sessione Recenti")

        if "last_flashcard_session" in st.session_state:
            session = st.session_state.last_flashcard_session

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """
                    <div class="metric-card">
                        <h3>Carte Viste</h3>
                        <div class="value">{}</div>
                    </div>
                    """.format(session.get("total", 0)),
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    """
                    <div class="metric-card">
                        <h3>Accuracy</h3>
                        <div class="value">{}%</div>
                    </div>
                    """.format(int(session.get("accuracy", 0))),
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            if session.get("accuracy", 0) < 50:
                st.warning("💡 Consiglio: Ripassa queste parole più spesso")
            elif session.get("accuracy", 0) < 80:
                st.info("👍 Buon lavoro! Rivedi le parole sconosciute")
            else:
                st.success("🌟 Eccellente! Continua così")
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <p style="color: #6b7280;">Inizia una sessione flashcard per vedere le tue statistiche!</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    st.markdown("### 📅 Cronologia Sessioni")

    # Display recent session history
    if "session_history" in st.session_state and st.session_state.session_history:
        for session in st.session_state.session_history[-5:]:  # Show last 5
            with st.container(border=True):
                st.markdown(f"**{session.get('session_type', 'N/A').replace('_', ' ').title()}**")
                st.caption(f"📅 {session.get('started_at', 'N/A')}")
                st.caption(
                    f"📊 {session.get('words_reviewed', 0)} parole | "
                    f"{session.get('accuracy', 0):.1f}% accuracy"
                )
    else:
        st.info("La cronologia delle sessioni verrà registrata qui dopo le prime review")


# Navigation
render_page_navigation("📝 Vocabolario")
