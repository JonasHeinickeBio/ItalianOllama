import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from auth.session import require_student

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(page_title="Prontezza Test - ItalianOllama", page_icon="🎯", layout="wide")

student_id, token = require_student()

st.title("🎯 Prontezza per il Test CEFR")
st.markdown("Sofia stima quanto sei pronto per sostenere l'esame ufficiale CILS o PLIDA.")

# Fetch Readiness
try:
    resp = requests.get(f"{BACKEND_URL}/api/student/{student_id}/test-readiness")
    readiness_data = resp.json()
    
    if not readiness_data:
        # Provide sample data if no tests taken
        st.info("Fai il tuo primo test di livello per visualizzare la tua prontezza!")
        readiness_data = [{
            "type": "CILS - B1",
            "readiness": 0.65,
            "skills": '{"Vocabolario": 0.7, "Grammatica": 0.6, "Comprensione": 0.8, "Conversazione": 0.5}'
        }]
    
    for test in readiness_data:
        st.subheader(f"Dettaglio: {test['type']}")
        
        # Skill scores for radar chart
        import json
        skills = json.loads(test['skills']) if isinstance(test['skills'], str) else test['skills']
        
        df = pd.DataFrame({
            'Abilità': list(skills.keys()),
            'Punteggio': list(skills.values())
        })
        
        # Radar Chart
        fig = px.line_polar(df, r='Punteggio', theta='Abilità', line_close=True)
        fig.update_traces(fill='toself')
        
        st.plotly_chart(fig)
        
        # Total readiness gauge
        st.metric("Prontezza Complessiva", f"{test['readiness']*100:.0f}%")
        
except Exception as e:
    st.error(f"Errore nel caricamento della prontezza: {e}")
