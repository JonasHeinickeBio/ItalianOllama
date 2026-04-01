"""
Login Page - Italian Tutor Frontend

Dedicated login page for existing students to authenticate with:
- Backend health checks
- Automatic session state initialization
- Smooth redirect after successful authentication
- Clear error handling for users (not found vs technical errors)
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
logger.info("🔐 LOGIN PAGE INITIALIZED")
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
st.title("ItalianOllama 🇮🇹")
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

# === LOGIN SECTION ===
st.markdown("---")
st.subheader("🔐 Accedi")
st.caption("Inserisci il tuo ID studente per continuare")

with st.form("login_form", border=True):
    student_id = st.text_input(
        "ID Studente",
        placeholder="Esempio: mario.rossi@email.com oppure mario123",
        help="Usa l'ID che hai ricevuto durante la registrazione",
    )
    submit = st.form_submit_button("✅ Accedi", use_container_width=True, type="primary")

    if submit:
        if not student_id or not student_id.strip():
            logger.warning("⚠️ Form submitted with empty student_id")
            st.error("🔍 Per favore inserisci il tuo ID studente")
            st.stop()

        student_id = student_id.strip()
        logger.info(f"🔑 Login attempt for student_id: {student_id}")

        with st.spinner("Verifica dell'accesso in corso..."):
            logger.info("📡 Getting API client...")
            api = get_api_client()
            logger.info("✓ API client obtained")

            try:
                # Attempt to fetch student profile
                logger.info(f"🔍 Looking up student: {student_id}")
                profile = api.get_student(student_id)
                logger.info(
                    f"✓ api.get_student() returned: {type(profile)} | Keys: {list(profile.keys()) if profile else 'None'}"
                )

                if profile is None:
                    logger.warning(f"❌ Student not found: {student_id}")
                    st.error(f"❌ Studente non trovato: **{student_id}**")
                    st.warning("Questo ID studente non esiste nel sistema.")
                    st.info("💡 Hai due opzioni:")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(
                            "1. **Verifica il tuo ID** - Controlla l'email di registrazione"
                        )
                    with col2:
                        st.markdown("2. **Registrati come nuovo** - Crea un nuovo account")
                    st.stop()

                logger.info(
                    f"✓ Student profile found | Name: {profile.get('name', 'N/A')} | Level: {profile.get('level', 'N/A')}"
                )

                # Set authenticated state
                st.session_state.authenticated = True
                st.session_state.student_id = student_id
                st.session_state.profile = profile
                logger.info(
                    f"✓ Session state updated | authenticated=True | student_id={student_id}"
                )

                # Show success message
                logger.info("🎉 Authentication successful!")
                st.success("✅ Login riuscito!")
                st.balloons()
                logger.info("⏳ Reindirizzamento al dashboard...")
                time.sleep(1)
                logger.info("→ SWITCHING to dashboard page")
                st.switch_page("pages/02_dashboard.py")

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"❌ Exception during login: {type(e).__name__}: {error_msg}", exc_info=True
                )

                # Check if it's a 404 not found error
                if "not found" in error_msg.lower() or "404" in error_msg:
                    st.error(f"❌ Studente non trovato: **{student_id}**")
                    st.warning("Questo ID studente non esiste nel sistema.")
                else:
                    st.error("❌ Errore tecnico durante l'accesso")
                    st.caption(f"Dettagli: {error_msg}")
                st.stop()

# === SIGNUP SECTION ===
st.divider()
st.markdown(
    """
<div style='text-align: center;'>
    <h3>👤 Non hai ancora un account?</h3>
    <p style='color: gray;'>Crea un nuovo account per iniziare le lezioni</p>
</div>
""",
    unsafe_allow_html=True,
)

if st.button("📝 Registrati Ora", use_container_width=True, type="secondary"):
    logger.info("→ User clicked signup button - redirecting to signup page")
    st.switch_page("pages/01b_signup.py")

# === FOOTER ===
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>ItalianOllama © 2024 | Powered by LangGraph & Neo4j</p>
    <p>
        <a href="https://github.com/JonasHeinickeBio/ItalianOllama" style="color: gray; text-decoration: none; margin: 0 10px;">
            📚 Source
        </a>
        |
        <a href="https://italianollama.com/docs" style="color: gray; text-decoration: none; margin: 0 10px;">
            📖 Docs
        </a>
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)
