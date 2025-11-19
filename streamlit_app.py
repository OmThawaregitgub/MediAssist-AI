# streamlit_app.py

import streamlit as st
from rag import RAGPipeline

st.set_page_config(page_title="RAG Chat Assistant", layout="wide")

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
if "chat" not in st.session_state:
    st.session_state.chat = []

if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()

# ---- TITLE ----
st.markdown("<h2 style='text-align:center;'>💬 RAG Chat Assistant</h2>", unsafe_allow_html=True)

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
        answer = st.session_state.rag.ask(user_query)
        st.session_state.chat.append(("bot", answer))
        st.rerun()

# ---- CLEAR CHAT ----
if st.button("Clear Chat"):
    st.session_state.chat = []
    st.rerun()
