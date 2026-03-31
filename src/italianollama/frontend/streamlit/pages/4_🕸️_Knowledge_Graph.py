from auth.session import require_student
import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="Grafo della Conoscenza - ItalianOllama", page_icon="🕸️", layout="wide"
)

student_id, token = require_student()

st.title("🕸️ Grafo della Conoscenza")
st.markdown("Scopri come le parole e i concetti che hai imparato sono collegati tra loro.")

# Fetch Graph Data
try:
    resp = requests.get(f"{BACKEND_URL}/api/student/{student_id}/graph")
    graph_data = resp.json()

    if not graph_data or not graph_data.get("nodes"):
        st.info("Inizia a studiare per visualizzare il tuo grafo della conoscenza!")
    else:
        # Check if st-link-analysis is installed
        try:
            from streamlit_link_analysis import st_link_analysis

            # Map graph_data to link-analysis format
            elements = {
                "nodes": [
                    {"data": {"id": node["id"], "label": node["label"], **node["properties"]}}
                    for node in graph_data["nodes"]
                ],
                "edges": [
                    {
                        "data": {
                            "id": link["id"],
                            "source": link["source"],
                            "target": link["target"],
                            "label": link["type"],
                        }
                    }
                    for link in graph_data["links"]
                ],
            }

            # Display interactive graph
            st_link_analysis(elements, layout={"name": "cose"})

        except ImportError:
            st.warning(
                "Componente 'streamlit-link-analysis' non installato. Mostrando dati grezzi."
            )
            # Fallback to standard view
            st.json(graph_data)

except Exception as e:
    st.error(f"Errore nel caricamento del grafo: {e}")
