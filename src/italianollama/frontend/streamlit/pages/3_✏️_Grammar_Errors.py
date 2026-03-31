import streamlit as st
import pandas as pd
import requests
from auth.session import require_student

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(page_title="Errori - ItalianOllama", page_icon="✏️", layout="wide")

student_id, token = require_student()

st.title("✏️ Errori di Grammatica")
st.markdown("Sofia annota i tuoi errori comuni in modo da poterti aiutare a migliorare.")

# Fetch Common Errors
try:
    resp = requests.get(f"{BACKEND_URL}/api/student/{student_id}/grammar-errors")
    errors = resp.json()
    
    if not errors:
        st.info("Nessun errore registrato finora. Ottimo lavoro!")
    else:
        df = pd.DataFrame(errors)
        
        # Expandable error list + bar chart
        st.subheader("Errori Comuni per Regola")
        st.bar_chart(df.groupby('rule')['seen_count'].sum())
        
        st.markdown("---")
        st.subheader("I Tuoi Errori nel Dettaglio")
        
        for idx, row in df.iterrows():
            with st.expander(f"Errore su: {row['rule']} ({row['seen_count']} volte)"):
                st.error(f"**Cosa hai detto:** {row['original']}")
                st.success(f"**Cosa avresti dovuto dire:** {row['corrected']}")
                # Placeholder for the book rule retrieved from GraphRAG
                st.info("**Regola del Libro:** 'In italiano, l'articolo concorda sempre in genere e numero con il sostantivo a cui si riferisce.'")
                
except Exception as e:
    st.error(f"Errore nel caricamento degli errori: {e}")
