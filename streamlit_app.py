# streamlit_app.py

import streamlit as st
from rag import RAGPipeline

st.set_page_config(page_title="MediAssist AI - Breast Cancer Research", layout="wide")

# ---- REMOVE TOP BLANK SPACE ----
st.markdown("""
<style>
.main > div {
    padding-top: 0px !important;
}
.block-container {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---- SESSION INIT ----
if "chat" not in st.session_state:
    st.session_state.chat = []

if "rag" not in st.session_state:
    with st.spinner("🔄 Loading medical research database..."):
        st.session_state.rag = RAGPipeline()
        info = st.session_state.rag.get_collection_info()
    st.sidebar.success(info)

# ---- TITLE ----
st.markdown("<h1 style='text-align:center;'>🏥 MediAssist AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;color:#666;'>Breast Cancer Research Assistant</h3>", unsafe_allow_html=True)

# ---- SIDEBAR INFO ----
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("This AI assistant answers medical questions using PubMed research articles about breast cancer.")

# Sample questions
st.sidebar.markdown("### 💡 Sample Questions")
sample_questions = [
    "What are the latest breast cancer treatments?",
    "Tell me about triple-negative breast cancer",
    "How does immunotherapy work for breast cancer?",
    "What are the risk factors for breast cancer?",
    "Explain breast cancer screening methods"
]

for question in sample_questions:
    if st.sidebar.button(question, key=question):
        st.session_state.input_text = question

# ---- STYLE ----
st.markdown("""
<style>
.chat-box {
    height: 60vh;
    overflow-y: auto;
    padding: 15px;
    border-radius: 10px;
    background-color: #f8f9fa;
    margin-bottom: 20px;
    border: 1px solid #e9ecef;
}
.user-msg {
    background: #007bff;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px;
    color: white;
    max-width: 70%;
    margin-left: auto;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.bot-msg {
    background: #ffffff;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px;
    color: #333;
    max-width: 80%;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input("Ask your medical question:", key="input_text", 
                              placeholder="e.g., What are the latest breast cancer treatments?")
with col2:
    send_btn = st.button("Send", use_container_width=True)

if send_btn and user_query.strip():
    st.session_state.chat.append(("user", user_query))
    with st.spinner("🔍 Searching medical research..."):
        answer = st.session_state.rag.ask(user_query)
    st.session_state.chat.append(("bot", answer))
    st.rerun()

# ---- CLEAR CHAT ----
if st.button("Clear Chat History"):
    st.session_state.chat = []
    st.rerun()
