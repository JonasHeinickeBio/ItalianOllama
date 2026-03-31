import streamlit as st
import requests
import jwt
from datetime import datetime, timedelta

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
    """Call backend to get JWT and store in session."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/token",
            json={"student_id": student_id}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.student_id = student_id
            return True
        else:
            st.error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

def logout_student():
    """Clear session state."""
    if "student_id" in st.session_state:
        del st.session_state.student_id
    if "access_token" in st.session_state:
        del st.session_state.access_token
    st.rerun()
