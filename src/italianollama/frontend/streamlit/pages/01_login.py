"""
Login Page - Italian Tutor Frontend (Improved)

Separate login page for user authentication with:
- Backend health checks
- Automatic session state initialization
- Smooth redirect after authentication
- Better error handling
- VERBOSE LOGGING for debugging
"""

import logging
import time

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    check_backend_health,
    display_backend_unavailable,
    get_api_client,
    initialize_session_state,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - STREAMLIT_LOGIN - %(levelname)s - %(message)s"
)
logger = logging.getLogger("streamlit_login")
logger.setLevel(logging.INFO)

# Suppress debug logs from file watchers and other noisy libraries
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("inotify_simple").setLevel(logging.WARNING)

logger.info("=" * 100)
logger.info("🔐 LOGIN PAGE INITIALIZATION STARTED")
logger.info("=" * 100)

# --- Page Configuration ---
st.set_page_config(
    page_title="ItalianOllama - Login",
    page_icon="🇮🇹",
    layout="centered",
    initial_sidebar_state="collapsed",
)

logger.info("✓ Page configuration set")

# --- Initialize Session State ---
logger.info("🔄 Initializing session state variables...")
initialize_session_state()
logger.info(
    f"✓ Session initialized | authenticated={st.session_state.authenticated} | student_id={st.session_state.student_id}"
)

# === MAIN PAGE ===
st.title("Benvenuti a ItalianOllama 🇮🇹")
st.markdown("### Impara l'italiano con Sofia, la tua tutor AI personale.")

# Health check
logger.info("📡 Performing backend health check...")
if not check_backend_health():
    logger.error("❌ Backend health check FAILED - showing error page")
    display_backend_unavailable()
    st.stop()

logger.info("✓ Backend health check PASSED")

# Check if already authenticated
if st.session_state.authenticated and st.session_state.student_id:
    logger.info(f"✓ User already authenticated | student_id={st.session_state.student_id}")
    st.success(f"✅ Già autenticato come: **{st.session_state.student_id}**")
    if st.button("📊 Vai al Dashboard", use_container_width=True):
        logger.info(f"→ Redirecting to dashboard for student: {st.session_state.student_id}")
        st.switch_page("pages/02_dashboard.py")
    st.stop()

# Login form
st.markdown("---")
st.subheader("🔐 Accedi")

with st.form("login_form", border=True):
    student_id = st.text_input(
        "Inserisci il tuo ID studente",
        placeholder="mario.rossi@example.com",
        help="Usa l'ID che hai registrato durante la registrazione",
    )
    submit = st.form_submit_button("✅ Accedi", use_container_width=True)

    if submit:
        if not student_id or not student_id.strip():
            logger.warning("⚠️ Form submitted with empty student_id")
            st.warning("⚠️ Per favore inserisci un ID studente")
            st.stop()

        logger.info(f"🔑 Login attempt started for student_id: {student_id}")

        with st.spinner("Autenticazione in corso..."):
            logger.info("📡 Getting API client...")
            api = get_api_client()
            logger.info("✓ API client obtained")

            try:
                # Attempt login
                logger.info(f"🔐 Calling api.login({student_id})...")
                login_result = api.login(student_id)
                logger.info(f"✓ api.login() returned: {login_result}")

                if not login_result:
                    logger.error(
                        f"❌ Login failed for student_id: {student_id} - api.login() returned False"
                    )
                    st.error("❌ Autenticazione fallita. Verifica il tuo ID.")
                    st.stop()

                logger.info("✓ Login successful! Setting session state...")
                # Set authenticated state
                st.session_state.authenticated = True
                st.session_state.student_id = student_id
                logger.info(
                    f"✓ Session state updated | authenticated=True | student_id={student_id}"
                )

                # Fetch student profile
                logger.info(f"👤 Fetching student profile for: {student_id}")
                with st.spinner("Caricamento profilo..."):
                    profile = api.get_student(student_id)
                    logger.info(
                        f"✓ api.get_student() returned: {type(profile)} | Keys: {list(profile.keys()) if profile else 'None'}"
                    )

                    if profile is None:
                        logger.error(f"❌ Student profile not found: {student_id}")
                        st.error(f"❌ Studente non trovato: {student_id}. Per favore registrati prima.")
                        st.stop()
                    else:
                        logger.info(
                            f"✓ Existing student profile found | Name: {profile.get('name', 'N/A')} | Level: {profile.get('level', 'N/A')}"
                        )

                    st.session_state.profile = profile
                    logger.info("✓ Profile stored in session state")

                # Show success and redirect
                logger.info("🎉 Authentication complete! Showing success message...")
                st.success("✅ Autenticazione riuscita!")
                st.balloons()
                logger.info("⏳ Waiting 1 second before redirect...")
                time.sleep(1)
                logger.info("→ REDIRECTING to dashboard...")
                st.switch_page("pages/02_dashboard.py")

            except Exception as e:
                logger.error(
                    f"❌ Exception during login: {type(e).__name__}: {str(e)}", exc_info=True
                )
                st.error(f"❌ Errore durante l'autenticazione: {str(e)}")
                st.stop()

# Signup prompt
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    st.info("📝 Non hai ancora un account?")
with col2:
    if st.button("Registrati", use_container_width=True, key="signup_btn"):
        logger.info("→ REDIRECTING to signup page...")
        st.switch_page("pages/01b_signup.py")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>ItalianOllama © 2024 | Powered by LangGraph & Neo4j</p>
    <p>
        <a href="https://github.com/JonasHeinickeBio/ItalianOllama" style="color: gray; text-decoration: none;">
            📚 Source Code
        </a>
        |
        <a href="https://italianollama.com/docs" style="color: gray; text-decoration: none;">
            📖 Documentation
        </a>
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)
