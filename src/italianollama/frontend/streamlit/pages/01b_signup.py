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
logger.info("📝 SIGNUP PAGE INITIALIZED")
logger.info("=" * 100)

# --- Page Configuration ---
st.set_page_config(
    page_title="ItalianOllama - Signup",
    page_icon="🇮🇹",
    layout="centered",
    initial_sidebar_state="collapsed",
)

logger.info("✓ Page configuration set")

# --- Initialize Session State ---
logger.info("🔄 Initializing session state variables...")
initialize_session_state()

# === MAIN PAGE ===
st.title("ItalianOllama 🇮🇹")
st.markdown("### Comincia il tuo percorso di apprendimento dell'italiano!")

# Health check
logger.info("📡 Performing backend health check...")
if not check_backend_health():
    logger.error("❌ Backend health check FAILED - showing error page")
    display_backend_unavailable()
    st.stop()

logger.info("✓ Backend health check PASSED")

# === SIGNUP SECTION ===
st.markdown("---")
st.subheader("📝 Crea il tuo account")
st.caption("Compila il modulo per registrarti come nuovo studente")

with st.form("signup_form", border=True):
    # Email / Student ID
    student_id = st.text_input(
        "Email o ID studente",
        placeholder="mario.rossi@email.com",
        help="Usa una email valida o un ID univoco che ricorderai facilmente",
    )

    # Full name
    name = st.text_input(
        "Nome completo",
        placeholder="Mario Rossi",
        help="Inserisci il tuo nome",
    )

    # Native language (optional)
    native_language = st.selectbox(
        "Lingua madre",
        ["English", "German", "French", "Spanish", "Italian", "Portuguese", "Other"],
        index=0,
        help="Seleziona la tua lingua madre",
    )

    submit = st.form_submit_button("✅ Crea Account", use_container_width=True, type="primary")

    if submit:
        # Validation
        errors = []

        if not student_id or not student_id.strip():
            errors.append("🔍 Email o ID studente è obbligatorio")
        elif len(student_id.strip()) < 3:
            errors.append("🔍 Email o ID deve avere almeno 3 caratteri")

        if not name or not name.strip():
            errors.append("👤 Nome completo è obbligatorio")
        elif len(name.strip()) < 2:
            errors.append("👤 Nome deve avere almeno 2 caratteri")

        if errors:
            logger.warning(f"❌ Validation errors: {errors}")
            for error in errors:
                st.error(error)
            st.stop()

        student_id = student_id.strip()
        name = name.strip()
        logger.info(f"📝 Signup attempt for: student_id={student_id}, name={name}")

        with st.spinner("Creazione del tuo account..."):
            logger.info("📡 Getting API client...")
            api = get_api_client()
            logger.info("✓ API client obtained")

            try:
                # Check if student already exists
                logger.info(f"🔍 Checking if student already exists: {student_id}")
                existing = api.get_student(student_id)

                if existing is not None:
                    logger.warning(f"❌ Student already exists: {student_id}")
                    st.error(f"❌ Questo account esiste già!")
                    st.info(f"💡 Usa l'email **{student_id}** per accedere")
                    if st.button("🔐 Vai al Login", use_container_width=True):
                        logger.info("→ Redirecting to login page")
                        st.switch_page("pages/01_login.py")
                    st.stop()

                logger.info(f"✓ Student does not exist yet - proceeding with creation")

                # Create new student
                logger.info(f"➕ Creating new student: {student_id}")
                result = api.create_student(student_id, name, native_language)
                logger.info(f"✓ api.create_student() returned: {type(result)}")

                # Fetch the created profile
                logger.info(f"📥 Fetching created profile: {student_id}")
                profile = api.get_student(student_id)
                logger.info(
                    f"✓ Profile retrieved | Name: {profile.get('name', 'N/A')}"
                )

                if profile is None:
                    logger.error(f"❌ Failed to retrieve profile after creation: {student_id}")
                    st.error("❌ Errore: non riesco a recuperare il tuo profilo")
                    st.info("💡 Per favore, torna alla pagina di login e prova di nuovo")
                    if st.button("🔐 Vai al Login", use_container_width=True):
                        logger.info("→ Redirecting to login page")
                        st.switch_page("pages/01_login.py")
                    st.stop()

                # Set authenticated state
                st.session_state.authenticated = True
                st.session_state.student_id = student_id
                st.session_state.profile = profile
                logger.info(
                    f"✓ Session state updated | authenticated=True | student_id={student_id}"
                )

                # Show success message
                logger.info("🎉 Signup successful!")
                st.success("✅ Account creato con successo!")
                st.balloons()
                st.markdown(f"### Benvenuto, {name}! 👋")
                st.info(f"Il tuo account è pronto. Reindirizzamento al dashboard...")
                logger.info("⏳ Waiting before redirect to dashboard")
                time.sleep(2)
                logger.info("→ SWITCHING to dashboard page")
                st.switch_page("pages/02_dashboard.py")

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"❌ Exception during signup: {type(e).__name__}: {error_msg}", exc_info=True
                )

                if "already exists" in error_msg.lower():
                    st.error(f"❌ Questo account esiste già!")
                    st.info(f"💡 Usa l'email **{student_id}** per accedere alla pagina di login")
                else:
                    st.error(f"❌ Errore durante la creazione dell'account")
                    st.caption(f"Dettagli: {error_msg}")
                st.stop()

# === LOGIN LINK ===
st.divider()
st.markdown("""
<div style='text-align: center;'>
    <p style='color: gray;'>Hai già un account?</p>
</div>
""", unsafe_allow_html=True)

if st.button("🔐 Accedi", use_container_width=True, type="secondary"):
    logger.info("→ User clicked login link - redirecting to login page")
    st.switch_page("pages/01_login.py")

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
