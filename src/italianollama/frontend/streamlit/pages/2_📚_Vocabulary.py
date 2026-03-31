import streamlit as st
import pandas as pd
import requests
from auth.session import require_student

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(page_title="Vocabolario - ItalianOllama", page_icon="📚", layout="wide")

student_id, token = require_student()

st.title("📚 Vocabolario")
st.markdown("Sofia tiene traccia di ogni parola che impari e della tua confidenza.")

# Fetch Vocabulary
try:
    resp = requests.get(f"{BACKEND_URL}/api/student/{student_id}/vocabulary")
    vocab = resp.json()
    
    if not vocab:
        st.info("Non hai ancora imparato nessuna parola. Inizia una conversazione con Sofia!")
    else:
        df = pd.DataFrame(vocab)
        
        # Display as confidence heatmap table
        st.subheader("Mappa di Confidenza")
        
        # Formatting confidence as a color gradient
        def color_confidence(val):
            color = 'red' if val < 0.3 else 'orange' if val < 0.7 else 'green'
            return f'color: {color}'

        # Let's pivot for the heatmap if topic exists
        if 'topic' in df.columns and 'word' in df.columns:
            # For simplicity, let's just show the table for now
            st.dataframe(
                df.style.applymap(color_confidence, subset=['confidence']),
                use_container_width=True
            )
            
        # Optional: Heatmap visualization
        st.markdown("---")
        st.subheader("Distribuzione Confidenza")
        st.bar_chart(df.set_index('word')['confidence'])
        
except Exception as e:
    st.error(f"Errore nel caricamento del vocabolario: {e}")
