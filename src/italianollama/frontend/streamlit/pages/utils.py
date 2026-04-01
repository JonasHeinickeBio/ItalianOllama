"""
Utility functions and helpers for Streamlit pages.

This module provides reusable components, decorators, and helper functions
for all pages in the multi-page application.
"""

from collections.abc import Callable
from functools import wraps
import logging
import os
from typing import Any

import streamlit as st

from italianollama.frontend.streamlit.tutor_api import TutorAPIClient

# Configure logging - suppress noisy file watcher debug logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - STREAMLIT_UTILS - %(levelname)s - %(message)s"
)
logger = logging.getLogger("streamlit_utils")
logger.setLevel(logging.INFO)

# Suppress debug logs from file watchers and other noisy libraries
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("inotify_simple").setLevel(logging.WARNING)

# ============================================================================
# INITIALIZATION & CONFIGURATION
# ============================================================================


def get_api_client() -> TutorAPIClient:
    """Get or initialize the API client."""
    # If not in session state OR is None, initialize it
    if "api_client" not in st.session_state or st.session_state.api_client is None:
        try:
            backend_url = get_backend_url()
            logger.info(f"🌐 Initializing TutorAPIClient with backend_url: {backend_url}")
            st.session_state.api_client = TutorAPIClient(backend_url)
            logger.info("✓ TutorAPIClient initialized successfully")
        except Exception as e:
            logger.error(
                f"❌ Failed to initialize TutorAPIClient: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            st.session_state.api_client = None
            raise
    else:
        logger.debug("✓ Using existing cached API client")
    return st.session_state.api_client


def get_backend_url() -> str:
    """Get backend URL from environment or config."""
    try:
        from italianollama.frontend.config import get_settings

        settings = get_settings()
        backend_url = settings.backend_url
        logger.info(f"📍 Backend URL from config: {backend_url}")
        return backend_url
    except ImportError:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        logger.info(f"📍 Backend URL from environment (default): {backend_url}")
        return backend_url


def initialize_session_state():
    """Initialize all required session state variables."""
    logger.debug("🔄 Initializing session state...")
    defaults = {
        "student_id": None,
        "authenticated": False,
        "profile": None,
        "chat_history": [],
        "api_client": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            logger.debug(f"  ✓ Set {key} = {value}")
    logger.info(f"✓ Session state initialized with {len(defaults)} variables")


# ============================================================================
# AUTHENTICATION & GUARDS
# ============================================================================


def require_auth() -> bool:
    """Check if user is authenticated, redirect to login if not."""
    logger.debug("🔐 Checking authentication...")
    initialize_session_state()
    if not st.session_state.get("authenticated"):
        logger.warning(
            f"⚠️ Unauthorized access attempt - authenticated={st.session_state.get('authenticated')}"
        )
        st.error("❌ Non autenticato. Vai alla pagina di login.")
        if st.button("🔐 Vai al Login", use_container_width=True):
            logger.info("→ User clicked 'Vai al Login' button - redirecting...")
            st.switch_page("pages/01_login.py")
        st.stop()
    logger.debug(f"✓ Authentication verified - student_id: {st.session_state.get('student_id')}")
    return True


def get_student_id() -> str | None:
    """Get current student ID, require auth first."""
    require_auth()
    return st.session_state.student_id


# ============================================================================
# SIDEBAR COMPONENTS
# ============================================================================


def render_sidebar_header():
    """Render consistent sidebar header with branding."""
    logger.debug("🎨 Rendering sidebar header...")
    st.markdown("### 📚 ItalianOllama")
    st.markdown(f"**ID:** `{st.session_state.student_id}`")
    st.markdown("---")
    logger.debug("✓ Sidebar header rendered")


def render_sidebar_navigation(current_page: str = "") -> str:
    """
    Render sidebar page navigation.

    Args:
        current_page: Current page for highlighting

    Returns:
        Selected page name
    """
    logger.debug(f"🎨 Rendering sidebar navigation (current: {current_page})...")
    pages = {
        "📊 Dashboard": "pages/02_dashboard.py",
        "💬 Chat": "pages/03_chat.py",
        "📝 Vocabolario": "pages/04_vocabulary.py",
        "⚙️ Impostazioni": "pages/05_settings.py",
    }

    page = st.radio(
        "Navigazione:",
        list(pages.keys()),
        label_visibility="collapsed",
    )

    st.markdown("---")

    if st.button("🚪 Logout", use_container_width=True):
        logger.info("👤 User clicked logout button")
        logout()

    logger.debug(f"✓ Navigation rendered - selected page: {page}")
    return page


def render_sidebar_full(current_page: str = ""):
    """Render complete sidebar with header, profile, navigation."""
    logger.debug(f"🎨 Rendering full sidebar (current_page: {current_page})...")
    with st.sidebar:
        render_sidebar_header()

        # Profile info
        logger.debug("👤 Fetching student profile...")
        api = get_api_client()
        profile = api.get_student(st.session_state.student_id)
        if profile:
            logger.debug(
                f"✓ Profile retrieved - name: {profile.get('name', 'N/A')}, level: {profile.get('level', 'N/A')}"
            )
            st.markdown(f"**Nome:** {profile.get('name', 'Studente')}")
            st.markdown(f"**Livello:** {profile.get('level', 'N/A')}")
            st.markdown(f"**XP:** {profile.get('total_xp', 0)} ⭐")
            st.markdown(f"**Streak:** {profile.get('current_streak', 0)} 🔥")
        else:
            logger.warning(f"⚠️ Profile not found for student {st.session_state.student_id}")

        st.markdown("---")

        render_sidebar_navigation(current_page)
    logger.debug("✓ Full sidebar rendered")


def logout():
    """Handle user logout."""
    logger.info(f"🚪 Logout initiated for student_id: {st.session_state.student_id}")
    api = get_api_client()
    logger.debug("📡 Clearing API token...")
    api.clear_token()
    logger.debug("✓ Token cleared")

    logger.debug("🔄 Resetting session state...")
    st.session_state.authenticated = False
    st.session_state.student_id = None
    st.session_state.profile = None
    st.session_state.chat_history = []
    logger.info("✓ Session state reset")

    st.success("✅ Disconnesso con successo!")
    logger.info("→ Redirecting to login page...")
    import time

    time.sleep(1)
    st.switch_page("pages/01_login.py")


# ============================================================================
# CACHING DECORATORS
# ============================================================================


def cache_student_data(ttl: int = 60):
    """Decorator for caching student-specific data with TTL."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and student id
            cache_key = f"cache_{func.__name__}_{st.session_state.student_id}"

            # Use st.cache_data
            cached_func = st.cache_data(ttl=ttl)(func)
            return cached_func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# UI COMPONENTS
# ============================================================================


def metric_card(label: str, value: Any, emoji: str = "📊", delta: str | None = None):
    """Render a metric card with consistent styling."""
    st.metric(label, value, delta=delta)


def error_card(title: str, message: str):
    """Render an error card."""
    with st.container(border=True):
        st.error(f"**{title}**\n{message}")


def info_card(title: str, message: str):
    """Render an info card."""
    with st.container(border=True):
        st.info(f"**{title}**\n{message}")


def success_card(title: str, message: str):
    """Render a success card."""
    with st.container(border=True):
        st.success(f"**{title}**\n{message}")


def skill_progress_bar(name: str, xp: int, progress: float):
    """Render a skill with progress bar."""
    with st.container(border=True):
        st.markdown(f"**{name}**")
        st.progress(min(progress, 1.0), text=f"{xp} XP")


# ============================================================================
# FOOTER NAVIGATION
# ============================================================================


def render_page_navigation(exclude_page: str = ""):
    """Render footer navigation buttons between pages."""
    pages = {
        "📊 Dashboard": "pages/02_dashboard.py",
        "💬 Chat": "pages/03_chat.py",
        "📝 Vocabolario": "pages/04_vocabulary.py",
        "⚙️ Impostazioni": "pages/05_settings.py",
    }

    # Filter out current page
    available_pages = {k: v for k, v in pages.items() if k != exclude_page}

    st.markdown("---")
    cols = st.columns(len(available_pages))

    for col, (label, page_path) in zip(cols, available_pages.items(), strict=False):
        with col:
            if st.button(label, use_container_width=True):
                st.switch_page(page_path)


# ============================================================================
# ERROR HANDLING
# ============================================================================


def handle_api_error(error: Exception, user_message: str = "Errore nella comunicazione"):
    """Handle and display API errors uniformly."""
    st.error(f"❌ {user_message}")
    st.caption(f"Dettagli: {str(error)}")


def with_error_handling(func: Callable) -> Callable:
    """Decorator to handle errors in API calls."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handle_api_error(e)
            return None

    return wrapper


# ============================================================================
# STATUS CHECKS
# ============================================================================


def check_backend_health() -> bool:
    """Check if backend is available."""
    try:
        api = get_api_client()
        result = api.health_check()
        # health check returns a dict like {"status": "ok", "neo4j": "connected", "litellm": "unreachable"}
        # We consider it healthy if it returns a dict with status "ok" or "degraded"
        if result:
            status = result.get("status")
            is_healthy = status in ("ok", "degraded")
            if is_healthy:
                logger.info(f"✓ Backend health check PASSED - status: {status}")
            else:
                logger.error(f"❌ Backend health check FAILED - status: {status}")
            return is_healthy
        else:
            logger.error("❌ Backend health check returned None")
            return False
    except Exception as e:
        logger.error(f"❌ Backend health check exception: {e}")
        return False


def display_backend_unavailable():
    """Display error when backend is unavailable."""
    st.error("⚠️ Backend non disponibile. Controlla la connessione.")
    st.info("Verifica che il server FastAPI sia in esecuzione su `http://localhost:8000`")
