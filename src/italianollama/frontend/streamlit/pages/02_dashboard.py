"""
Dashboard Page - Italian Tutor Frontend (Improved)

Main dashboard showing learning metrics and performance analytics.
Features improved caching, error handling, and consistent UX.
"""

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    get_api_client,
    get_student_id,
    render_page_navigation,
    render_sidebar_full,
    require_auth,
    skill_progress_bar,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Dashboard - ItalianOllama",
    page_icon="📊",
    layout="wide",
)

# --- Check Authentication ---
require_auth()
student_id = get_student_id()

# --- Sidebar ---
render_sidebar_full("📊 Dashboard")

# --- Initialize API ---
api = get_api_client()


# === CACHED DATA FETCHERS ===


@st.cache_data(ttl=60)
def get_profile():
    """Fetch cached student profile."""
    try:
        return api.get_student(student_id)
    except Exception as e:
        st.error(f"Errore nel caricamento del profilo: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_velocity():
    """Fetch cached learning velocity."""
    try:
        return api.get_learning_velocity(student_id, days=7)
    except Exception:
        return None


@st.cache_data(ttl=300)
def get_skills_data():
    """Fetch cached skill breakdown."""
    try:
        return api.get_skills(student_id)
    except Exception:
        return None


@st.cache_data(ttl=300)
def get_errors_data():
    """Fetch cached common errors."""
    try:
        return api.get_common_errors(student_id, limit=5)
    except Exception:
        return None


@st.cache_data(ttl=600)
def get_next_module():
    """Fetch cached module recommendations."""
    try:
        result = api.get_next_module(student_id)
        return result.get("recommendation") if result else None
    except Exception:
        return None


# === PAGE CONTENT ===
profile = get_profile()

st.markdown(
    f"""
    <div class="main-header">
        <h1>Bentornato, {profile.get('name', student_id) if profile else student_id}! 🇮🇹</h1>
        <h2>Ecco il tuo progresso di oggi</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="card" style="text-align: center;">
            <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">📚</div>
        """,
        unsafe_allow_html=True,
    )
    st.metric(
        "XP Totali",
        profile.get("total_xp", 0) if profile else 0,
        delta="+50 oggi" if profile and profile.get("total_xp", 0) > 0 else None,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="card" style="text-align: center;">
            <div style="font-size: 2rem; color: var(--accent-color); margin-bottom: 0.5rem;">🔥</div>
        """,
        unsafe_allow_html=True,
    )
    st.metric(
        "Streak",
        f"{profile.get('current_streak', 0) if profile else 0} giorni",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown(
        """
        <div class="card" style="text-align: center;">
            <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">📖</div>
        """,
        unsafe_allow_html=True,
    )
    st.metric(
        "Vocabolario",
        profile.get("vocabulary_count", 0) if profile else 0,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown(
        """
        <div class="card" style="text-align: center;">
            <div style="font-size: 2rem; color: var(--success-color); margin-bottom: 0.5rem;">📝</div>
        """,
        unsafe_allow_html=True,
    )
    st.metric(
        "Sessioni",
        profile.get("session_count", 0) if profile else 0,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Analytics Section
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3 style="color: var(--primary-color);">📈 Velocità di Apprendimento</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.container(border=True):
        velocity = get_velocity()
        if velocity:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("XP/Giorno", f"{velocity.get('xp_per_day', 0):.1f}")
            with col_b:
                st.metric("Sessioni/Settimana", f"{velocity.get('sessions_per_week', 0):.1f}")
            with col_c:
                st.metric(
                    "Durata Media Sessione",
                    f"{velocity.get('average_session_duration', 0):.0f} min",
                )
        else:
            st.info("📊 Dati non disponibili ancora. Completa alcuni esercizi!")

with col2:
    st.markdown(
        """
        <div class="card">
            <h3 style="color: var(--primary-color);">🎯 Top Skills</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.container(border=True):
        skills = get_skills_data()
        if skills:
            for skill in skills[:5]:  # Show top 5
                skill_progress_bar(
                    skill.get("skill_name", "Unknown"),
                    skill.get("total_xp", 0),
                    min(skill.get("progress_to_next", 0), 1.0),
                )
        else:
            st.info("🎯 Nessuna abilità tracciata ancora")

st.markdown("---")

# Error/Concept Tracking
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3 style="color: var(--error-color);">❌ Errori Comuni</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    errors = get_errors_data()
    if errors:
        for error in errors[:3]:
            with st.container(border=True):
                st.markdown(f"**{error.get('concept', 'Unknown')}**")
                st.caption(f"🔴 Frequenza: {error.get('frequency', 0)} errori")
    else:
        st.success("✅ Nessun errore ricorrente! Continua così!")

with col2:
    st.markdown(
        """
        <div class="card">
            <h3 style="color: var(--success-color);">🎓 Prossimo Modulo</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    module = get_next_module()
    if module:
        with st.container(border=True):
            st.markdown(f"### {module.get('module_name', 'Unknown')}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.caption(f"📌 **Argomento:** {module.get('topic', 'N/A')}")
            with col_b:
                st.caption(f"📊 **Difficoltà:** {module.get('difficulty', 'N/A')}")
            st.caption(f"💡 {module.get('reason', 'Consigliato personalizzato')}")
            if st.button("📚 Inizia", use_container_width=True):
                st.info("🚀 Modulo in avvio...")
    else:
        st.info("📚 Completa altri esercizi per ricevere raccomandazioni")

# Navigation
render_page_navigation("📊 Dashboard")
