# streamlit_app.py (Updated to include data loading)

import streamlit as st
import json
# Import your RAG class
from rag import RAGPipeline 

st.set_page_config(page_title="RAG Chat Assistant", layout="wide")

# streamlit_app.py (REVISED)

import streamlit as st
from rag import RAGPipeline 
# --- FIX: Import data directly from a Python file instead of missing JSON ---
from pubmed_data import RECORDS as records
# --------------------------------------------------------------------------

st.set_page_config(page_title="RAG Chat Assistant", layout="wide")

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
                # NOTE: Ensure the key is correct for abstract sections (like "SUMMARY" or "OBJECTIVE")
                abstract_text = " ".join(rec["abstract"].values())
            else:
                abstract_text = rec["abstract"]
                
            document = f"Title: {rec['title']}\nAbstract: {abstract_text}"
            
            # Add to the in-memory vector store
            rag_pipeline.add_document(rec["pmid"], document)
            
        print(f"Successfully loaded {len(records_to_load)} articles into in-memory ChromaDB.")
        return rag_pipeline

    except Exception as e:
        # This will now catch any error during populating the vector store, 
        # like a Gemini API key failure or embedding failure.
        st.error(f"Error during RAG initialization or data loading: {e}")
        return None


# ---- REMOVE TOP BLANK SPACE ----
st.markdown("""
<style>
/* Remove top margin/padding */
.main > div {
    padding-top: 0px !important;
}

.block-container {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---- SESSION INIT ----
# Initialize RAG Pipeline and cache it, passing the imported data
if "rag" not in st.session_state:
    st.session_state.rag = initialize_rag_pipeline(records) # <-- PASS THE DATA HERE

if "chat" not in st.session_state:
    st.session_state.chat = []

# Guard clause to handle loading failure
if st.session_state.rag is None:
    st.stop()

# ... (rest of the Streamlit code is the same)

# --- DATA LOADING (Streamlit's cache ensures this runs ONCE) ---
@st.cache_resource
def initialize_rag_pipeline(data_path="pubmed_articles.json"):
    """Initializes RAG, loads data into in-memory ChromaDB, and returns the pipeline."""
    try:
        # 1. Initialize RAG (creates in-memory ChromaDB)
        rag_pipeline = RAGPipeline()
        
        # 2. Load pre-fetched data (assuming you save the abstract list to JSON)
        with open(data_path, 'r') as f:
            records = json.load(f)

        # 3. Add documents to the RAG pipeline's in-memory ChromaDB
        for rec in records:
            # Flatten the abstract structure from the fetched record
            if isinstance(rec["abstract"], dict):
                abstract_text = " ".join(rec["abstract"].values())
            else:
                abstract_text = rec["abstract"]
                
            document = f"Title: {rec['title']}\nAbstract: {abstract_text}"
            
            # Add to the in-memory vector store
            rag_pipeline.add_document(rec["pmid"], document)
            
        print(f"Successfully loaded {len(records)} articles into in-memory ChromaDB.")
        return rag_pipeline

    except Exception as e:
        st.error(f"Error during RAG initialization or data loading: {e}")
        return None


# ---- REMOVE TOP BLANK SPACE ----
st.markdown("""
<style>
/* Remove top margin/padding */
.main > div {
    padding-top: 0px !important;
}

.block-container {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---- SESSION INIT ----
# Initialize RAG Pipeline and cache it
if "rag" not in st.session_state:
    st.session_state.rag = initialize_rag_pipeline()

if "chat" not in st.session_state:
    st.session_state.chat = []

# Guard clause to handle loading failure
if st.session_state.rag is None:
    st.stop()


# ---- TITLE ----
st.markdown("<h2 style='text-align:center;'>💬 RAG Chat Assistant</h2>", unsafe_allow_html=True)

# ... (rest of the style and chat history display remains the same) ...

# ---- STYLE ----
st.markdown("""
<style>
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
        # Use the initialized RAG instance from session state
        answer = st.session_state.rag.ask(user_query) 
        st.session_state.chat.append(("bot", answer))
        st.rerun()

# ---- CLEAR CHAT ----
if st.button("Clear Chat"):
    st.session_state.chat = []
    st.rerun()
