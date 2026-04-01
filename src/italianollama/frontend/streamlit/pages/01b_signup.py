"""
Signup Page - Italian Tutor Frontend

User registration page for new students:
- Create new student account
- Enter student ID and name
- Backend health checks
- Automatic redirect after signup
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
    level=logging.INFO, format="%(asctime)s - STREAMLIT_SIGNUP - %(levelname)s - %(message)s"
)
logger = logging.getLogger("streamlit_signup")
logger.setLevel(logging.INFO)

# Suppress debug logs from file watchers and other noisy libraries
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("inotify_simple").setLevel(logging.WARNING)

logger.info("=" * 100)
logger.info("📝 SIGNUP PAGE INITIALIZATION STARTED")
logger.info("=" * 100)

# --- Page Configuration ---
st.set_page_config(
    page_title="ItalianOllama - Registrazione",
    page_icon="📝",
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
st.title("Registrazione - ItalianOllama 🇮🇹")
st.markdown("### Crea il tuo account per iniziare ad imparare l'italiano")

# Health check
logger.info("📡 Performing backend health check...")
if not check_backend_health():
    logger.error("❌ Backend health check FAILED - showing error page")
    display_backend_unavailable()
    st.stop()

logger.info("✓ Backend health check PASSED")

# Signup form
with st.form("signup_form", border=True):
    st.subheader("📋 Crea il tuo Account")
    
    student_id = st.text_input(
        "ID Studente",
        placeholder="mario.rossi@example.com",
        help="Usa un email o ID univoco che ricorderai facilmente",
    )
    
    name = st.text_input(
        "Nome",
        placeholder="Mario Rossi",
        help="Inserisci il tuo nome completo",
    )
    
    native_language = st.selectbox(
        "Lingua Madre",
        options=["English", "Spanish", "French", "German", "Italian", "Portuguese", "Other"],
        index=0,
        help="Qual è la tua lingua madre?",
    )
    
    submit = st.form_submit_button("✅ Registrati", use_container_width=True)

    if submit:
        if not student_id or not student_id.strip():
            logger.warning("⚠️ Form submitted with empty student_id")
            st.warning("⚠️ Per favore inserisci un ID studente")
            st.stop()

        if not name or not name.strip():
            logger.warning("⚠️ Form submitted with empty name")
            st.warning("⚠️ Per favore inserisci il tuo nome")
            st.stop()

        logger.info(f"📝 Signup attempt started for student_id: {student_id}, name: {name}")

        with st.spinner("Creazione account in corso..."):
            logger.info("📡 Getting API client...")
            api = get_api_client()
            logger.info("✓ API client obtained")

            try:
                # Create new student
                logger.info(f"👤 Creating new student - student_id={student_id}, name={name}, native_language={native_language}")
                profile = api.create_student(
                    student_id=student_id,
                    name=name,
                    native_language=native_language,
                )
                logger.info(
                    f"✓ api.create_student() returned: {type(profile)} | Keys: {list(profile.keys()) if profile else 'None'}"
                )

                if profile is None:
                    logger.error(f"❌ Failed to create student: {student_id}")
                    st.error("❌ Errore durante la creazione dell'account. Per favore riprova.")
                    st.stop()

                logger.info(f"✓ Student created successfully | student_id: {student_id}")
                
                # Auto-login the new student
                logger.info(f"🔐 Auto-logging in new student: {student_id}")
                login_result = api.login(student_id)
                
                if not login_result:
                    logger.error(f"❌ Auto-login failed for new student: {student_id}")
                    st.error("Account creato! Per favore accedi con il tuo ID.")
                    st.stop()

                logger.info("✓ Auto-login successful!")
                
                # Set authenticated state
                st.session_state.authenticated = True
                st.session_state.student_id = student_id
                st.session_state.profile = profile
                logger.info(
                    f"✓ Session state updated | authenticated=True | student_id={student_id}"
                )

                # Show success and redirect
                logger.info("🎉 Signup complete! Showing success message...")
                st.success("✅ Account creato con successo!")
                st.balloons()
                logger.info("⏳ Waiting 1 second before redirect...")
                time.sleep(1)
                logger.info("→ REDIRECTING to dashboard...")
                st.switch_page("pages/02_dashboard.py")

            except Exception as e:
                logger.error(
                    f"❌ Exception during signup: {type(e).__name__}: {str(e)}", exc_info=True
                )
                st.error(f"❌ Errore durante la registrazione: {str(e)}")
                st.stop()

# Back to login
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    st.info("🔐 Hai già un account?")
with col2:
    if st.button("Accedi", use_container_width=True, key="login_btn"):
        logger.info("→ REDIRECTING to login page...")
        st.switch_page("pages/01_login.py")

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
