# streamlit_app.py (FINAL, CLEANED VERSION)

import streamlit as st
import json
# --- Use the reliable Python file for raw data ---
from rag import RAGPipeline
from pubmed_data import RECORDS as records 
# ------------------------------------------------

st.set_page_config(page_title="MediAssist AI Chat Assistant", layout="wide")

# --- DATA LOADING (Streamlit's cache ensures this runs ONCE) ---
@st.cache_resource
def initialize_rag_pipeline(records_to_load):
    """Initializes RAG, loads data into in-memory ChromaDB, and returns the pipeline."""
    try:
        # 1. Initialize RAG (creates in-memory ChromaDB)
        rag_pipeline = RAGPipeline()
        
        # 2. Add documents to the RAG pipeline's in-memory ChromaDB
        for rec in records_to_load:
            # Flatten the abstract structure from the fetched record
            if isinstance(rec["abstract"], dict):
                # Join all section values (e.g., OBJECTIVE, RESULTS, CONCLUSION)
                abstract_text = " ".join(rec["abstract"].values())
            else:
                abstract_text = rec["abstract"]
                
            document = f"Title: {rec['title']}\nAbstract: {abstract_text}"
            
            # Add to the in-memory vector store
            rag_pipeline.add_document(rec["pmid"], document)
            
        print(f"Successfully loaded {len(records_to_load)} articles into in-memory ChromaDB.")
        return rag_pipeline

    except Exception as e:
        # Catches API key, embedding, or structure errors
        st.error(f"Error during RAG initialization or data loading: {e}")
        return None

# ---- REMOVE TOP BLANK SPACE (CSS Styling) ----
st.markdown("""
<style>
/* Remove top margin/padding */
.main > div {
    padding-top: 0px !important;
}

.block-container {
    padding-top: 0rem !important;
}

/* Chat bubble styles */
.chat-box {
    height: 70vh;
    overflow-y: auto;
    padding: 10px;
    border-radius: 10px;
    background-color: #1e1e1e;
}
.user-msg {
    background: #0059ff;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 8px;
    color: white;
    width: fit-content;
}
.bot-msg {
    background: #2e2e2e;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 8px;
    color: white;
    width: fit-content;
}
</style>
""", unsafe_allow_html=True)


# ---- SESSION INIT & RAG Initialization ----

# Initialize RAG Pipeline and cache it, passing the imported data
if "rag" not in st.session_state:
    st.session_state.rag = initialize_rag_pipeline(records) # <-- Uses the imported data

if "chat" not in st.session_state:
    st.session_state.chat = []

# Guard clause to handle loading failure (e.g., if API key failed)
if st.session_state.rag is None:
    st.stop()


# ---- TITLE ----
st.markdown("<h2 style='text-align:center;'>💬 RAG Chat Assistant</h2>", unsafe_allow_html=True)

# ---- CHAT HISTORY AREA ----
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='user-msg'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'><b>Assistant:</b> {msg}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---- INPUT AT BOTTOM ----
user_query = st.text_input("Ask your question:", key="input_text")

if st.button("Send"):
    if user_query.strip():
        st.session_state.chat.append(("user", user_query))
        answer = st.session_state.rag.ask(user_query)
        st.session_state.chat.append(("bot", answer))
        st.rerun()

# ---- CLEAR CHAT ----
if st.button("Clear Chat"):
    st.session_state.chat = []
    st.rerun()
