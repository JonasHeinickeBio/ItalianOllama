"""
Streamlit App - Italian Tutor Frontend (Enhanced Multi-Page)

Main entry point for the multi-page Streamlit application.
Uses Streamlit's pages/ directory structure for better organization:

Pages:
- pages/01_login.py      → Login page (separate authentication)
- pages/02_dashboard.py  → Main dashboard with learning metrics
- pages/03_chat.py       → Chat with Sofia
- pages/04_vocabulary.py → Vocabulary management with spaced rep
- pages/05_settings.py   → User settings and profile management

All pages share session state for persistent user ID across pages.
"""

import os

import streamlit as st

# Try to import config, fallback to defaults
try:
    from italianollama.frontend.config import get_settings

    def get_backend_url() -> str:
        settings = get_settings()
        return settings.backend_url
except ImportError:

    def get_backend_url() -> str:
        return os.getenv("BACKEND_URL", "http://localhost:8000")


# --- Page Configuration ---
st.set_page_config(
    page_title="ItalianOllama - Your AI Italian Tutor",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Initialize Global Session State ---
"""
These session variables are initialized here and accessible from all pages.
They persist across page navigation and user interactions.
"""
if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "profile" not in st.session_state:
    st.session_state.profile = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --- Main App Logic ---
def main():
    """Main app entry point - redirect to login if not authenticated."""

    if not st.session_state.authenticated:
        # Not logged in → redirect to login page
        st.switch_page("pages/01_login.py")
    else:
        # Logged in → redirect to dashboard
        st.switch_page("pages/02_dashboard.py")


if __name__ == "__main__":
    main()
