from auth.session import require_student
import pandas as pd
import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(page_title="Progressi - ItalianOllama", page_icon="📊", layout="wide")

student_id, token = require_student()

st.title("📊 I Tuoi Progressi")

# Fetch Stats
try:
    resp = requests.get(f"{BACKEND_URL}/api/student/{student_id}/stats")
    stats = resp.json()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Esercizi Completati", stats.get("total_exercises", 0))
    col2.metric("Vocabolario Appreso", stats.get("total_vocab", 0))
    col3.metric("Punteggio Medio", f"{stats.get('avg_score', 0):.1f}")
    col4.metric("Errori di Grammatica", stats.get("total_errors", 0))

except Exception as e:
    st.error(f"Errore nel caricamento delle statistiche: {e}")

# Progress over time (Simulated if no history)
st.subheader("Punteggi Esercizi nel Tempo")
try:
    # Need to fetch history from somewhere - get_exercise_history?
    # For now, placeholder line chart
    data = pd.DataFrame(
        {
            "data": pd.date_range(start="2024-01-01", periods=10, freq="D"),
            "score": [70, 75, 72, 80, 85, 82, 90, 88, 92, 95],
        }
    )
    st.line_chart(data.set_index("data"))
except Exception:
    st.info("Non ci sono ancora abbastanza dati per visualizzare il grafico.")
