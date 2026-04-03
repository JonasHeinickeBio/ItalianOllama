"""
Chat Page - Italian Tutor with Embedded Chainlit

Chat interface with Sofia, the AI tutor via Chainlit.
Provides both Chainlit embedded view and fallback Streamlit chat.
"""

import os

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    get_api_client,
    get_student_id,
    initialize_session_state,
    render_page_navigation,
    render_sidebar_full,
    require_auth,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Chat - ItalianOllama",
    page_icon="💬",
    layout="wide",
)

# --- Check Authentication ---
require_auth()
student_id = get_student_id()

# --- Sidebar ---
render_sidebar_full("💬 Chat")

# --- Chainlit Configuration ---
CHAINLIT_URL = os.getenv("CHAINLIT_URL", "http://localhost:8000")
chainlit_enabled = os.getenv("CHAINLIT_ENABLED", "true").lower() == "true"

# --- Initialize Chat History ---
initialize_session_state()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "use_chainlit" not in st.session_state:
    st.session_state.use_chainlit = chainlit_enabled

# --- Initialize API ---
api = get_api_client()

# === PAGE CONTENT ===
st.markdown(
    """
    <div class="main-header">
        <h1>Chat con Sofia 💬</h1>
        <h2>Parla in italiano e Sofia ti aiuterà a migliorare!</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar controls for chat
with st.sidebar:
    st.markdown("---")
    st.subheader("💬 Opzioni Chat")

    # Chainlit toggle
    if chainlit_enabled:
        st.session_state.use_chainlit = st.toggle(
            "🚀 Usa Chainlit (Avanzato)",
            value=st.session_state.use_chainlit,
            help="Attiva la versione Chainlit della chat",
        )

    if st.button("🗑️ Cancella Cronologia", use_container_width=True):
        st.session_state.chat_history = []
        st.success("✅ Cronologia cancellata")
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Salva Chat", use_container_width=True):
            st.info("💾 Chat salvata (feature in sviluppo)")
    with col2:
        if st.button("📥 Carica Chat", use_container_width=True):
            st.info("📂 Caricamento chat (feature in sviluppo)")


# === CHAINLIT EMBEDDED VIEW ===
if st.session_state.use_chainlit and chainlit_enabled:
    st.markdown("### 🚀 Interfaccia Chainlit Avanzata")
    st.markdown(
        "Utilizza Chainlit per un'esperienza chat più ricca con streaming real-time "
        "e feedback visivo avanzato."
    )
    # Get JWT token from session state
    jwt_token = st.session_state.get("_api_token") or st.session_state.get("access_token", "")

    # Get or create session_id for session continuity
    if "chat_session_id" not in st.session_state:
        import uuid

        st.session_state.chat_session_id = str(uuid.uuid4())

    # Build Chainlit URL with query parameters including JWT token
    from urllib.parse import urlencode

    params = {
        "student_id": student_id,
        "level": st.session_state.get("cefr_level", "A1"),
        "name": st.session_state.get("user_name", "Student"),
        "session_id": st.session_state.chat_session_id,
    }

    # Add token if available (Chainlit will use this for authentication)
    if jwt_token:
        params["token"] = jwt_token

    query_string = urlencode(params)
    chainlit_embed_url = f"{CHAINLIT_URL}?{query_string}"

    # Create embedded Chainlit view
    chainlit_frame_html = f"""
    <iframe
        src="{chainlit_embed_url}"
        width="100%"
        height="800"
        frameborder="0"
        style="border: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
        allow="microphone; camera; payment"
        title="Sofia - Chainlit Chat Interface"
    ></iframe>
    """

    try:
        # Check if Chainlit is accessible
        import requests

        try:
            response = requests.head(CHAINLIT_URL, timeout=3)
            if response.status_code < 500:
                st.components.v1.html(chainlit_frame_html, height=820)
                with st.expander("🔧 Chainlit Configuration"):
                    st.code(f"URL: {chainlit_embed_url}", language="url")
                    st.write(f"**Student ID**: {student_id}")
                    st.write(f"**Level**: {params['level']}")
            else:
                st.warning(
                    f"⚠️ Chainlit non disponibile su {CHAINLIT_URL} (HTTP {response.status_code}). "
                    "Usa la modalità classica Streamlit qui sotto."
                )
                st.session_state.use_chainlit = False
                st.rerun()
        except requests.Timeout:
            st.error(
                f"❌ Timeout raggiungendo Chainlit su {CHAINLIT_URL}. "
                "Il servizio non risponde in tempo."
            )
            st.session_state.use_chainlit = False

    except Exception as e:
        st.error(
            f"❌ Errore raggiungendo Chainlit: {str(e)}\n\n"
            f"Assicurati che Chainlit sia in esecuzione su {CHAINLIT_URL}"
        )
        st.info(
            "**Per eseguire Chainlit:**\n"
            "```\nchainlit run src/italianollama/frontend/chainlit_app.py "
            "--port 8000 --host 0.0.0.0\n```"
        )


# === FALLBACK STREAMLIT CHAT VIEW ===
else:
    st.markdown("### 💬 Modalità Chat Classica")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                with st.chat_message(
                    message["role"],
                    avatar="🇮🇹" if message["role"] == "user" else "📚",
                ):
                    st.markdown(message["content"])
        else:
            st.info("💭 Nessun messaggio ancora. Inizia a chattare con Sofia!")

    # Input box
    st.markdown("---")
    user_input = st.chat_input("Digita qualcosa in italiano... (Es: Ciao! Come stai?)")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Display user message
        with st.chat_message("user", avatar="🇮🇹"):
            st.markdown(user_input)

        # Get AI response
        with st.spinner("Sofia sta pensando... 🤔"):
            try:
                response = api.chat(user_input, student_id)

                if response:
                    assistant_message = response.get(
                        "response",
                        "Mi dispiace, ho avuto un problema. Riprova tra poco.",
                    )

                    # Add assistant message to history
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": assistant_message}
                    )

                    # Display assistant message
                    with st.chat_message("assistant", avatar="📚"):
                        st.markdown(assistant_message)

                    # Show optional feedback
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("👍 Utile"):
                            st.success("Grazie per il feedback!")
                    with col2:
                        if st.button("🤔 Poco chiaro"):
                            st.info("Proverò a spiegare meglio la prossima volta")
                    with col3:
                        if st.button("😞 Non aiuta"):
                            st.warning("Mi scuso. Prova a riformulare la domanda")
                else:
                    st.error("❌ Errore nella comunicazione con Sofia. Riprova.")

            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")
                # Remove the message from history if there was an error
                if (
                    st.session_state.chat_history
                    and st.session_state.chat_history[-1]["role"] == "user"
                ):
                    st.session_state.chat_history.pop()

# Navigation
render_page_navigation("💬 Chat")
