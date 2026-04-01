from datetime import datetime
import logging

import jwt
import requests
import streamlit as st

from italianollama.frontend.streamlit.auth.browser_storage import (
    clear_session_cookies,
    save_session_to_cookies,
)

logger = logging.getLogger("session_manager")
logger.setLevel(logging.INFO)

BACKEND_URL = "http://localhost:8000"


def require_student():
    """Verify student is authenticated via JWT stored in session state."""
    if "student_id" not in st.session_state or "access_token" not in st.session_state:
        st.info("Please login to continue")
        st.stop()

    # Optional: Verify token expiration
    try:
        token = st.session_state.access_token
        # Decode without verification just to check exp
        payload = jwt.decode(token, options={"verify_signature": False})
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            st.error("Session expired. Please login again.")
            st.stop()
    except Exception:
        st.error("Invalid session. Please login again.")
        st.stop()

    return st.session_state.student_id, st.session_state.access_token


def login_student(student_id):
    """Call backend to get JWT and store in session + browser cookies."""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/token", json={"student_id": student_id})
        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]

            # Save to session state (in-memory for current session)
            st.session_state.access_token = access_token
            st.session_state.student_id = student_id
            st.session_state.authenticated = True
            logger.info(f"✓ Login successful - stored in session state | student_id={student_id}")

            # Save to browser cookies (persists across page reloads)
            save_session_to_cookies(student_id, access_token, expires_days=7)
            logger.info(f"✓ Session saved to cookies | student_id={student_id}")

            return True
        else:
            st.error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        logger.error(f"❌ Login failed with exception: {e}")
        return False


def logout_student():
    """Clear session state and cookies."""
    logger.info("🔓 Logging out...")

    # Clear session state
    if "student_id" in st.session_state:
        del st.session_state.student_id
    if "access_token" in st.session_state:
        del st.session_state.access_token
    if "authenticated" in st.session_state:
        st.session_state.authenticated = False

    # Clear browser cookies
    clear_session_cookies()
    logger.info("✓ Session cleared from cookies and session state")

    st.rerun()
