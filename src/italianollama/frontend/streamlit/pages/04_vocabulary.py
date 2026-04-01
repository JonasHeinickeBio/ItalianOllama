"""
Vocabulary Page - Italian Tutor Frontend (Improved)

Vocabulary management with spaced repetition (SM-2 algorithm).
Features improved error handling and better UX for word review.
"""

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    get_api_client,
    get_student_id,
    render_page_navigation,
    render_sidebar_full,
    require_auth,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Vocabolario - ItalianOllama",
    page_icon="📝",
    layout="wide",
)

# --- Check Authentication ---
require_auth()
student_id = get_student_id()

# --- Sidebar ---
render_sidebar_full("📝 Vocabolario")

# --- Initialize API ---
api = get_api_client()


# === CACHED DATA FETCHERS ===


@st.cache_data(ttl=120)
def get_vocabulary_items(due_for_review: bool = False):
    """Fetch vocabulary with caching."""
    try:
        return api.get_vocabulary(student_id, due_for_review=due_for_review)
    except Exception:
        return None


# === PAGE CONTENT ===
st.title("📝 Gestione Vocabolario")
st.markdown("_Costruisci il tuo vocabolario italiano con spaced repetition_")

tab1, tab2, tab3 = st.tabs(
    ["📖 Il Mio Vocabolario", "➕ Aggiungi Nuova Parola", "🔄 Ripassa (SM-2)"]
)

# === TAB 1: MY VOCABULARY ===
with tab1:
    st.subheader("Il mio Vocabolario")

    vocabulary = get_vocabulary_items(due_for_review=False)

    if vocabulary:
        st.success(f"📚 Hai **{len(vocabulary)}** parole nel tuo vocabolario")

        # Search/Filter
        search_term = st.text_input("🔍 Cerca una parola...", placeholder="Search by Italian word")

        # Filter vocabulary if search term provided
        if search_term:
            vocabulary = [
                w for w in vocabulary if search_term.lower() in w.get("italian_word", "").lower()
            ]

        # Display vocabulary
        if vocabulary:
            for word in vocabulary[:30]:  # Show first 30
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1], gap="small")

                with col1:
                    st.markdown(f"**{word.get('italian_word', 'N/A')}**")
                    st.caption(word.get("english_translation", ""))

                with col2:
                    st.badge(word.get("cefr_level", "N/A"))

                with col3:
                    topic = word.get("topic")
                    if topic:
                        st.caption(f"📌 {topic}")

                with col4:
                    confidence = word.get("confidence_level", 0)
                    st.progress(
                        min(confidence, 1.0),
                        text=f"{int(confidence * 100)}%",
                    )
        else:
            st.warning("❌ Nessuna parola trovata")
    else:
        st.info("📖 Ancora nessuna parola nel tuo vocabolario. Inizia ad aggiungerne!")


# === TAB 2: ADD NEW WORD ===
with tab2:
    st.subheader("➕ Aggiungi Nuova Parola")

    with st.form("add_vocab_form", border=True):
        col1, col2 = st.columns(2)

        with col1:
            italian = st.text_input(
                "Parola italiana *",
                placeholder="Es: gatto",
                help="Inserisci la parola italiana",
            )

        with col2:
            english = st.text_input(
                "Traduzione inglese *",
                placeholder="Es: cat",
                help="Inserisci la traduzione",
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            pos = st.selectbox(
                "Parte del discorso *",
                ["noun", "verb", "adjective", "adverb", "preposition", "other"],
            )

        with col2:
            level = st.selectbox(
                "Livello CEFR *",
                ["A1", "A2", "B1", "B2", "C1", "C2"],
            )

        with col3:
            topic = st.text_input(
                "Argomento",
                placeholder="Es: food, family",
                help="Categorizza la parola (opzionale)",
            )

        st.divider()

        example_sentence = st.text_area(
            "Frase di esempio (opzionale)",
            placeholder="Es: Il gatto è nero.",
            help="Un'esempio di utilizzo della parola",
        )

        submit = st.form_submit_button("✅ Aggiungi Parola", use_container_width=True)

        if submit:
            if not italian or not english:
                st.error("❌ Compila i campi obbligatori (marcati con *)")
                st.stop()

            with st.spinner("Aggiungendo parola..."):
                try:
                    result = api.add_vocabulary(
                        student_id,
                        italian.strip(),
                        english.strip(),
                        pos,
                        level,
                        topic.strip() if topic else None,
                    )
                    if result:
                        st.success(f"✅ Parola aggiunta: **{italian}**")
                        st.balloons()
                        st.cache_data.clear()  # Clear cache to show new word
                    else:
                        st.error("❌ Errore nell'aggiunta della parola")
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")


# === TAB 3: SPACED REPETITION ===
with tab3:
    st.subheader("🔄 Ripassa Vocabolario (Spaced Repetition SM-2)")
    st.markdown("_L'algoritmo SM-2 ottimizza il tuo apprendimento attraverso review intelligenti_")

    due_vocab = get_vocabulary_items(due_for_review=True)

    if due_vocab:
        st.success(f"📚 Hai **{len(due_vocab)}** parole da ripassare oggi!")
        st.info("💡 Valuta la tua confidenza da 1 (non ricordo) a 5 (perfetto)")

        st.markdown("---")

        for i, word in enumerate(due_vocab[:10], 1):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {i}. {word.get('italian_word')}")
                    st.write(f"__{word.get('english_translation', 'N/A')}__")

                    topic = word.get("topic")
                    if topic:
                        st.caption(f"📌 Argomento: {topic}")

                    st.caption(f"Livello: {word.get('cefr_level', 'N/A')}")

                with col2:
                    confidence = st.select_slider(
                        "Confidenza",
                        options=[1, 2, 3, 4, 5],
                        value=3,
                        key=f"conf_{i}",
                        help="1=Dimenticato, 5=Perfetto",
                    )

                # Update button
                if st.button(f"✅ Salva Risposta #{i}", use_container_width=True, key=f"save_{i}"):
                    with st.spinner(f"Salvando risposta {i}/{len(due_vocab)}..."):
                        try:
                            api.update_vocabulary_confidence(
                                word.get("vocabulary_id"),
                                confidence,
                            )
                            st.success("✅ Risposta salvata!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"❌ Errore: {str(e)}")

                st.divider()
    else:
        st.success("✅ Complimenti! Nessuna parola da ripassare oggi.")
        st.balloons()

        # Suggestions
        with st.container(border=True):
            st.markdown("### 📚 Suggerimenti")
            st.markdown(
                """
                - Aggiungi nuove parole per accelerare il tuo apprendimento
                - Prova a usare le parole nel chat con Sofia
                - Il nostro algoritmo SM-2 ti aiuterà a ricordare veramente
                """
            )


# Navigation
render_page_navigation("📝 Vocabolario")
