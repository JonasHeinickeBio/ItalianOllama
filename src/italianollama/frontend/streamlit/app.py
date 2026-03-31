from auth.session import login_student
import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="ItalianOllama - Your AI Italian Tutor",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Check Login ---
if "student_id" not in st.session_state:
    st.title("Benvenuti a ItalianOllama 🇮🇹")
    st.markdown("### Impara l'italiano con Sofia, la tua tutor AI personale.")

    with st.form("login_form"):
        student_id = st.text_input("Inserisci il tuo ID studente (e.g. your email or name)")
        submit = st.form_submit_button("Accedi / Registrati")

        if submit:
            if student_id:
                if login_student(student_id):
                    # Check if student exists in backend
                    try:
                        resp = requests.get(f"{BACKEND_URL}/students/{student_id}")
                        if resp.status_code == 404:
                            # Create new student
                            requests.post(
                                f"{BACKEND_URL}/students",
                                json={"student_id": student_id, "name": student_id},
                            )
                            st.session_state.new_student = True
                        else:
                            st.session_state.new_student = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
            else:
                st.warning("Per favore inserisci un ID.")
    st.stop()

# --- Welcome Screen ---
student_id = st.session_state.student_id


# Fetch student profile
@st.cache_data(ttl=60)
def get_profile(sid):
    try:
        resp = requests.get(f"{BACKEND_URL}/students/{sid}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


profile = get_profile(student_id)
name = profile.get("name", student_id) if profile else student_id
level = profile.get("level") if profile else None

st.sidebar.markdown(f"**Studente:** {name}")
if level:
    st.sidebar.markdown(f"**Livello:** {level}")

# Navigation for new students
if not level or st.session_state.get("show_onboarding"):
    st.session_state.show_onboarding = True

    st.title(f"Ciao {name}! 👋")
    st.markdown("Sofia ha bisogno di 2 minuti per trovare il tuo livello iniziale.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Inizia il test di livello", use_container_width=True):
            st.session_state.onboarding_step = "placement"
            st.rerun()
    with col2:
        if st.button("💁‍♂️ Conosco già il mio livello", use_container_width=True):
            st.session_state.onboarding_step = "level_select"
            st.rerun()

    # Handle onboarding steps
    step = st.session_state.get("onboarding_step")

    if step == "placement":
        st.markdown("---")
        st.subheader("Placement Quiz (Simulazione)")
        st.info("Qui inizierà il quiz adattivo di 5-8 domande.")
        # Simulating placement test result
        if st.button("Completa il test (Risultato: B1)"):
            requests.post(
                f"{BACKEND_URL}/chat", json={"student_id": student_id, "message": "/set_level B1"}
            )
            st.session_state.onboarding_step = "goal"
            st.rerun()

    elif step == "level_select":
        st.markdown("---")
        st.subheader("Qual è il tuo livello?")
        level_choice = st.selectbox("Scegli un livello CEFR", ["A1", "A2", "B1", "B2", "C1", "C2"])
        if st.button("Conferma"):
            requests.post(
                f"{BACKEND_URL}/chat",
                json={"student_id": student_id, "message": f"/set_level {level_choice}"},
            )
            st.session_state.onboarding_step = "goal"
            st.rerun()

    elif step == "goal":
        st.markdown("---")
        st.subheader("Qual è il tuo obiettivo?")
        goals = [
            "Viaggio ✈️",
            "Lavoro / Professionale 💼",
            "Esame CILS/PLIDA 🎓",
            "Conversazione libera 🗣️",
        ]
        goal_choice = st.radio("Scegli uno:", goals)
        if st.button("Salva obiettivo"):
            st.session_state.goal = goal_choice
            st.session_state.show_onboarding = False
            st.success("Ottimo! Cominciamo la nostra prima sessione.")
            if st.button("Vai alla Chat"):
                st.switch_page("pages/0_💬_Chat.py")

else:
    # Returning student
    st.title(f"Bentornato, {name}! 🇮🇹")

    # Random greeting based on level
    greetings = {
        "A1": "Ciao! Oggi impariamo nuove parole?",
        "A2": "Buongiorno! Sei pronto per un po' di grammatica?",
        "B1": "Bentornato! Come va il tuo studio dell'italiano?",
        "B2": "Ottimo rivederti! Facciamo una conversazione avanzata?",
        "C1": "Piacere di rivederti. Quale sfida affrontiamo oggi?",
        "C2": "Benvenuto! Continuiamo la nostra esplorazione della lingua?",
    }
    st.info(greetings.get(level, "Ciao! Sofia è pronta per la tua sessione quotidiana."))

    # Stats summary
    try:
        resp = requests.get(f"{BACKEND_URL}/api/student/{student_id}/stats")
        stats = resp.json()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Esercizi", stats.get("total_exercises", 0))
        c2.metric("Vocabolario", stats.get("total_vocab", 0))
        c3.metric("Punteggio Medio", f"{stats.get('avg_score', 0):.1f}")
        c4.metric("Streak 🔥", stats.get("streak", 0))

        # Session Badge simulation
        if stats.get("avg_score", 0) > 8.5:
            st.success("🌟 Il tuo livello attuale è: ECCELLENTE!")
        elif stats.get("avg_score", 0) > 6.0:
            st.warning("💪 Stai andando bene, continua così!")
        else:
            st.info("📚 Pratica costante porta al successo!")

    except Exception:
        st.warning("Impossibile caricare le statistiche.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Inizia Conversazione", type="primary", use_container_width=True):
            st.switch_page("pages/0_💬_Chat.py")
    with col2:
        if st.button("📊 Vedi Dashboard Completa", use_container_width=True):
            st.switch_page("pages/1_📊_Progress.py")

    # Sidebar Logout
    if st.sidebar.button("Log out"):
        from auth.session import logout_student

        logout_student()
