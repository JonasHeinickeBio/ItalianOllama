import os

import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Sofia - Conversazione Italiana",
    page_icon="💬",
    layout="wide",
)

# --- Authentication Check ---
if "student_id" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

student_id = st.session_state.student_id

st.title("Chiacchierata con Sofia 🇮🇹")
st.markdown("Sofia è qui per aiutarti a migliorare il tuo italiano.")

# --- Embed Chainlit via iframe ---
base_url = os.getenv("CHAINLIT_URL", "http://localhost:8501")

# Clean base URL (remove trailing slash and existing query params if any)
base_url = base_url.split("?")[0].rstrip("/")

# Always append student_id as query parameter
CHAINLIT_URL = f"{base_url}?student_id={student_id}"

# Embed using components.v1.iframe
st.components.v1.iframe(CHAINLIT_URL, height=800, scrolling=True)
