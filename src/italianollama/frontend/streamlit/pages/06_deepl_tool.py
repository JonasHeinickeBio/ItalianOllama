"""
DeepL Translation Tool - Italian Tutor Frontend

Features:
- Real-time DeepL translation from Italian to German
- One-click vocabulary storage with DeepL translations
- Part of speech selection and example sentences
- CEFR level assignment
"""

import time

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    get_api_client,
    get_student_id,
    render_page_navigation,
    render_sidebar_full,
    require_auth,
)
from italianollama.utils.deepl import DeepLClient, format_translation_for_vocabulary

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Traduttore DeepL - ItalianOllama",
    page_icon="deepl",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()
student_id = get_student_id()
render_sidebar_full("deepl DeepL Tool")

api = get_api_client()

# === PAGE STATE ===
if "deepl_client" not in st.session_state:
    st.session_state.deepl_client = None
if "deepl_translation" not in st.session_state:
    st.session_state.deepl_translation = ""
if "deepl_last_word" not in st.session_state:
    st.session_state.deepl_last_word = ""

# === INIT DeepL CLIENT ===
try:
    deepl_client = DeepLClient()
    st.session_state.deepl_client = deepl_client if deepl_client.is_available() else None
except Exception:
    st.session_state.deepl_client = None

# === SIDEBAR INFORMATION ===
with st.sidebar:
    st.markdown(
        """
        <div style="background: var(--light-bg); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h4 style="color: var(--secondary-color); margin: 0 0 0.75rem 0;">ℹ️ Come funziona</h4>
            <div style="font-size: 0.85rem; color: #666; line-height: 1.6;">
                <p>1. Inserisci una parola o frase italiana</p>
                <p>2. Ottieni la traduzione automatica in tedesco</p>
                <p>3. Aggiungi alla tua vocabulary con un click</p>
            </div>
        </div>
        """
    )

    if st.session_state.deepl_client:
        st.success("✅ DeepL API connessa")
    else:
        st.warning("⚠️ DeepL API non configurata")

# === MAIN CONTENT ===
st.title("deepl Traduttore DeepL")
st.markdown(" Traduci parole italiane in tedesco e aggiungile alla tua vocabulary")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Inserisci testo")

    italian_text = st.text_input(
        "Parola o frase italiana:",
        placeholder="es. la mela, il gatto, bellissimo",
        key="deepl_input"
    )

    if italian_text and st.session_state.deepl_client:
        if st.button("deepl Traduci in tedesco", use_container_width=True):
            with st.spinner("Traduzione in corso..."):
                try:
                    translation = st.session_state.deepl_client.translate(
                        text=italian_text,
                        target_lang="DE",
                        source_lang="IT"
                    )
                    st.session_state.deepl_translation = translation
                    st.session_state.deepl_last_word = italian_text
                    st.success(f"Traduzione: {translation}")
                except Exception as e:
                    st.error(f"❌ Errore nella traduzione: {str(e)}")

    elif not st.session_state.deepl_client:
        st.info("Configura la DeepL API key nel file .env")

with col2:
    st.subheader("💾 Aggiungi alla vocabulary")

    if st.session_state.deepl_translation:
        st.markdown(
            f"""
            <div style="background: var(--light-bg); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; font-size: 0.9rem; color: #666;">Italiano:</p>
                <p style="margin: 0.25rem 0 0.5rem 0; font-size: 1.2rem; font-weight: bold;">
                    {st.session_state.deepl_last_word}
                </p>
                <p style="margin: 0; font-size: 0.9rem; color: #666;">Tedesco:</p>
                <p style="margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: var(--primary-color);">
                    {st.session_state.deepl_translation}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_a, col_b = st.columns(2)

        with col_a:
            pos = st.selectbox(
                "Part of speech:",
                ["Noun", "Verb", "Adjective", "Adverb", "Phrase"],
                key="deepl_pos"
            )

        with col_b:
            cefr_level = st.selectbox(
                "CEFR Level:",
                ["A1", "A2", "B1", "B2", "C1", "C2"],
                key="deepl_cefr"
            )

        example_sentence = st.text_input(
            "Example sentence (optional):",
            placeholder="es. Io mangio la mela",
            key="deepl_example"
        )

        vocabulary_data = format_translation_for_vocabulary(
            italian_word=st.session_state.deepl_last_word,
            german_translation=st.session_state.deepl_translation,
            pos=pos if pos != "Noun" else "",
            example_sentence=example_sentence
        )

        vocabulary_data["cefr_level"] = cefr_level
        vocabulary_data["topic"] = "deepl-translation"
        vocabulary_data["vocabulary_type"] = "deepl-imported"

        if st.button("✅ Aggiungi alla vocabulary", use_container_width=True, type="primary"):
            with st.spinner("Aggiungendo alla vocabulary..."):
                try:
                    result = api.add_vocabulary(student_id, vocabulary_data)
                    if result:
                        st.success("✅ Parola aggiunta con successo!")
                        time.sleep(1)
                        st.session_state.deepl_translation = ""
                        st.session_state.deepl_last_word = ""
                        st.rerun()
                    else:
                        st.error("❌ Errore nell'aggiunta alla vocabulary")
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")

    else:
        st.info("Traduci una parola per aggiungerla alla vocabulary")

# === RECENT TRANSLATIONS ===
st.markdown("---")
st.subheader(" storico Traduzioni recenti")

recent_vocab = api.get_vocabulary(student_id, due_for_review=False)
deepl_vocab = [w for w in recent_vocab if w.get("vocabulary_type") == "deepl-imported"][:5]

if deepl_vocab:
    for item in deepl_vocab:
        st.markdown(
            f"""
            <div style="background: var(--light-bg); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--primary-color); font-size: 1.1rem;">{item.get('italian_word', 'N/A')}</strong>
                        <span style="color: #666;"> → </span>
                        <strong style="color: var(--secondary-color); font-size: 1.1rem;">{item.get('german_word', 'N/A')}</strong>
                    </div>
                    <div style="text-align: right;">
                        <small style="color: #666;">{item.get('part_of_speech', 'N/A')}</small><br>
                        <small style="color: var(--accent-color);">CEFR: {item.get('cefr_level', 'N/A')}</small>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("Nessuna traduzione recente")

render_page_navigation(exclude_page="deepl DeepL Tool")
