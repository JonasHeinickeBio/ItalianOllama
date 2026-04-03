"""
Settings Page - Italian Tutor Frontend (Improved)

User profile and account settings with token management.
Features token renewal, profile viewing, and comprehensive FAQ.
"""

import streamlit as st

from italianollama.frontend.streamlit.pages.utils import (
    get_api_client,
    get_student_id,
    logout,
    render_page_navigation,
    render_sidebar_full,
    require_auth,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Impostazioni - ItalianOllama",
    page_icon="⚙️",
    layout="wide",
)

# --- Check Authentication ---
require_auth()
student_id = get_student_id()

# --- Sidebar ---
render_sidebar_full("⚙️ Impostazioni")

# --- Initialize API ---
api = get_api_client()


# === CACHED DATA FETCHERS ===


@st.cache_data(ttl=60)
def get_profile_data():
    """Fetch cached student profile."""
    try:
        return api.get_student(student_id)
    except Exception:
        return None


# === PAGE CONTENT ===
st.markdown(
    """
    <div class="main-header">
        <h1>⚙️ Impostazioni e Profilo</h1>
        <h2>Gestisci il tuo account e personalizza l'applicazione</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["👤 Profilo", "🔐 Autenticazione", "❓ FAQ", "💡 Supporto"])

# === TAB 1: PROFILE ===
with tab1:
    st.subheader("👤 Profilo Studente")

    profile = get_profile_data()

    if profile:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Informazioni Generali**")
            st.write(f"🆔 **ID:** `{profile.get('student_id', 'N/A')}`")
            st.write(f"👤 **Nome:** {profile.get('name', 'N/A')}")
            st.write(f"🗣️ **Lingua Nativa:** {profile.get('native_language', 'N/A')}")
            st.write(f"📊 **Livello:** {profile.get('level', 'Non determinato')}")

        with col2:
            st.markdown("**Statistiche**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("⭐ XP Totali", profile.get("total_xp", 0))
                st.metric("🔥 Streak", f"{profile.get('current_streak', 0)} gg")
            with col_b:
                st.metric("📚 Vocabolario", profile.get("vocabulary_count", 0))
                st.metric("📝 Sessioni", profile.get("session_count", 0))

        st.markdown("---")

        # Additional metadata
        with st.expander("📋 Dettagli Aggiuntivi"):
            st.write(f"📅 **Data Iscrizione:** {profile.get('created_at', 'N/A')}")
            st.write(f"⏰ **Ultimo Accesso:** {profile.get('last_login', 'N/A')}")
            st.write(f"🎯 **Obiettivo XP Giornaliero:** {profile.get('daily_xp_target', 100)} XP")

        # Edit profile (placeholder)
        st.markdown("---")
        st.subheader("✏️ Modifica Profilo")

        with st.form("update_profile_form"):
            new_name = st.text_input(
                "Nome (opzionale)",
                value=profile.get("name", ""),
                disabled=True,
            )
            st.caption("⚠️ La modifica del profilo sarà disponibile in futuro")

            if st.form_submit_button("💾 Salva Modifiche"):
                st.info("🚀 Feature in sviluppo")

    else:
        st.warning("⚠️ Impossibile caricare il profilo")


# === TAB 2: AUTHENTICATION ===
with tab2:
    st.subheader("🔐 Gestione Autenticazione")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Stato Token**")
        if api.is_token_valid():
            st.success("✅ **Token Valido**")
            st.caption("Il tuo token di autenticazione è attivo")
        else:
            st.warning("⚠️ **Token Non Valido**")
            st.caption("Il token potrebbe essere scaduto")

    with col2:
        st.markdown("**Azioni**")
        if st.button("🔄 Rinnova Token", use_container_width=True):
            with st.spinner("Rinnovando token..."):
                try:
                    if api.login(student_id):
                        st.success("✅ Token rinnovato con successo!")
                        st.info("Il token è stato aggiornato e continuerai ad avere accesso")
                    else:
                        st.error("❌ Errore nel rinnovo del token")
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")

    st.markdown("---")

    st.markdown("**Privacy & Sicurezza**")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("🔐 **Cambia Password**")
            st.caption("Non ancora disponibile")
            st.button("🔒 Cambia Password", disabled=True, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("🔑 **Autenticazione a Due Fattori**")
            st.caption("Aumenta la sicurezza del tuo account")
            st.button("✅ Attiva 2FA", disabled=True, use_container_width=True)

    st.markdown("---")

    st.markdown("**Sessione**")

    if st.button("🚪 Logout da Tutti i Dispositivi", use_container_width=True):
        if st.confirm("Confermi di voler uscire da tutti i dispositivi?"):
            with st.spinner("Disconnessione in corso..."):
                logout()

    st.button("Logout da Questo Dispositivo", on_click=logout, use_container_width=True)


# === TAB 3: FAQ ===
with tab3:
    st.subheader("❓ Domande Frequenti")

    with st.expander("❓ Come funziona la Spaced Repetition (SM-2)?", expanded=False):
        st.write(
            """
        La Spaced Repetition è un algoritmo scientifico che ottimizza il tuo apprendimento:

        - **Revisione Intelligente:** Ogni parola viene ripassata secondo l'intervallo ottimale
        - **Adattivo:** L'algoritmo impara dalla tua confidenza e regola gli intervalli
        - **Ricordo Duraturo:** Studi le parole quando stai per dimenticarle, massimizzando la ritenzione
        - **Efficiente:** Riduci il tempo di studio del 50-70% ottenendo risultati migliori

        **Livelli di Confidenza:**
        - 1 = Completamente dimenticato → ripassa domani
        - 2 = Difficile da ricordare → ripassa tra 2 giorni
        - 3 = Ricordato con difficoltà → ripassa tra 4 giorni
        - 4 = Ricordato facilmente → ripassa tra 7 giorni
        - 5 = Perfetto → ripassa tra 14 giorni
        """
        )

    with st.expander("❓ Come guadagno XP?", expanded=False):
        st.write(
            """
        Guadagni XP completando varie attività:

        | Attività | XP |
        |----------|-----|
        | Completare una sessione di chat | 50 |
        | Aggiungere una nuova parola | 10 |
        | Ripassare vocabolario (SM-2) | 25 |
        | Ottenere una risposta corretta | 25 |
        | Streak di 7 giorni | 100 |
        | Completare un modulo | 100-250 |

        **Bonus:**
        - Sveglia presto (prima delle 8:00): +10 XP
        - Sessione lunga (+30 min): +50 XP
        - Nessun errore in una sessione: +25 XP
        """
        )

    with st.expander("❓ Come funziona il Sistema di Streak?", expanded=False):
        st.write(
            """
        Uno **Streak** è una serie di giorni consecutivi in cui completi almeno un'attività:

        - **Aumenta Ogni Giorno:** Completa una sessione per aumentare lo streak
        - **Azzera se Salti:** Se salti un giorno, torna a 0 (ma hai 24 ore di tolleranza)
        - **Premi Speciali:** Sblocca badge e bonus XP per reaching milestone streak:
          - 7 giorni: 🔥 Badge "Una Settimana"
          - 30 giorni: 🌟 Badge "Un Mese"
          - 100 giorni: 👑 Badge "Campione"
        - **Mantienilo:** La consistenza è la chiave dell'apprendimento!
        """
        )

    with st.expander("❓ Quali sono i Livelli CEFR?", expanded=False):
        st.write(
            """
        CEFR (Common European Framework of Reference) è uno standard internazionale:

        | Livello | Descrizione |
        |---------|-------------|
        | **A1** | Principiante - Frasi semplici, bisogni immediati |
        | **A2** | Elementare - Conversazioni quotidiane |
        | **B1** | Intermedio - Discorsi usuali, autonomia linguistica |
        | **B2** | Intermedio-Alto - Conversazioni spontanee, argomenti complessi |
        | **C1** | Avanzato - Espressione flessibile e uso sofisticato |
        | **C2** | Mastery - Quasi come un parlante nativo |
        """
        )

    with st.expander("❓ Come posso migliorare più velocemente?", expanded=False):
        st.write(
            """
        **Strategie Consigliate:**

        1. **Pratica Regolare:** 30 min al giorno è migliore di 3 ore una volta a settimana
        2. **Chat Attiva:** Usa Sofia per pratiche conversazionali reali
        3. **Revisione Costante:** Non saltare il vocabolario, soprattutto spaced rep
        4. **Impostazione di Obiettivi:** Mira a un livello CEFR specifico
        5. **Varietà:** Alterna chat, vocabolario, e grammatica
        6. **Immersione Media:** Ascolta podcast, guarda film, leggi articoli

        **Pro Tip:** Uno streak di 30+ giorni con 100+ XP al giorno ti porterà da A1 a B1 in ~3 mesi!
        """
        )

    with st.expander("❓ Cosa fare se dimentico una parola?", expanded=False):
        st.write(
            """
        **Non è un fallimento - è normale!**

        - Se assegni confidenza 1-2, la parola riappare presto (domani o tra 2 giorni)
        - L'algoritmo SM-2 prevede sempre l'oblio
        - Ripetere è il segreto del ricordo duraturo
        - Studi dimostrano che serve vederla ~17 volte per ricordarla bene
        - Più rivedi una parola, meno sarai tentato di dimenticarla

        **Non stressarti:** Questo è un viaggio, non una gara!
        """
        )


# === TAB 4: SUPPORT ===
with tab4:
    st.subheader("💡 Centro Supporto")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**📧 Email**")
            st.write("support@italianollama.com")
            if st.button("✉️ Invia Email", use_container_width=True):
                st.info("Apri il tuo client email predefinito")

    with col2:
        with st.container(border=True):
            st.markdown("**💬 Discord**")
            st.write("Unisciti al nostro server")
            if st.button("🎮 Accedi a Discord", use_container_width=True):
                st.info("https://discord.gg/italianollama")

    with col3:
        with st.container(border=True):
            st.markdown("**🐦 Twitter**")
            st.write("@ItalianOllama")
            if st.button("🚀 Seguici", use_container_width=True):
                st.info("https://twitter.com/ItalianOllama")

    st.markdown("---")

    st.markdown("**📚 Risorse Utili**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📖 Documentazione", use_container_width=True):
            st.markdown("[📖 Leggi la documentazione](https://docs.italianollama.com)")

    with col2:
        if st.button("🎓 Tutorial", use_container_width=True):
            st.markdown("[🎓 Guarda i tutorial](https://tutorials.italianollama.com)")

    with col3:
        if st.button("🐛 Report Bug", use_container_width=True):
            st.markdown(
                "[🐛 Segnala un bug](https://github.com/JonasHeinickeBio/ItalianOllama/issues)"
            )

    st.markdown("---")

    st.markdown("**Versione App**")
    st.caption("🔖 ItalianOllama v0.3.0 | 📅 Aprile 2024")


# Navigation
render_page_navigation("⚙️ Impostazioni")
