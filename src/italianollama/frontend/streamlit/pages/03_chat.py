"""
Chat Page - Italian Tutor Frontend (Improved)

Chat interface with Sofia, the AI tutor.
Features improved error handling and persistent chat history.
"""

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

# --- Initialize Chat History ---
initialize_session_state()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Initialize API ---
api = get_api_client()

# === PAGE CONTENT ===
st.title("Chat con Sofia 💬")
st.markdown("_Parla in italiano e Sofia ti aiuterà a migliorare!_")

# Sidebar controls for chat
with st.sidebar:
    st.markdown("---")
    st.subheader("💬 Opzioni Chat")
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
            st.info("📂 Caricamente chat (feature in sviluppo)")

# Display chat history
chat_container = st.container()
with chat_container:
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            with st.chat_message(
                message["role"], avatar="🇮🇹" if message["role"] == "user" else "📚"
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
