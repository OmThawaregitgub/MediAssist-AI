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
st.markdown("<h2 style='text-align:center;'>🏥 MediAssist AI - Breast Cancer Research Assistant</h2>", unsafe_allow_html=True)

# ---- SIDEBAR INFO ----
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("This AI assistant answers medical questions using PubMed research articles about breast cancer.")

# Sample questions
st.sidebar.markdown("### 💡 Sample Questions")
sample_questions = [
    "What are the latest breast cancer treatments?",
    "Tell me about triple-negative breast cancer",
    "What is intermittent fasting in cancer treatment?",
    "How does immunotherapy work for breast cancer?",
    "What are the risk factors for breast cancer?"
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
    padding: 10px;
    border-radius: 10px;
    background-color: #1e1e1e;
    margin-bottom: 20px;
}
.user-msg {
    background: #0059ff;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 8px;
    color: white;
    width: fit-content;
    max-width: 80%;
    margin-left: auto;
}
.bot-msg {
    background: #2e2e2e;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 8px;
    color: white;
    width: fit-content;
    max-width: 80%;
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
