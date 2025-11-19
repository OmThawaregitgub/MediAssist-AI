# streamlit_app.py

import streamlit as st
from rag import RAGPipeline

st.set_page_config(
    page_title="AI Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- DARK THEME ----
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        background-color: #0E1117;
    }
    .main > div {
        padding-top: 0rem !important;
    }
    
    .main-header {
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #CCCCCC;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-box {
        height: 65vh;
        overflow-y: auto;
        padding: 15px;
        border-radius: 10px;
        background-color: #1E1E1E;
        margin-bottom: 20px;
        border: 1px solid #333333;
    }
    
    .user-msg {
        background: linear-gradient(135deg, #0059ff, #0099ff);
        padding: 12px 16px;
        border-radius: 18px;
        margin: 10px 10px 10px auto;
        color: white;
        max-width: 70%;
        box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
    }
    
    .bot-msg {
        background: #2D2D2D;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 10px auto 10px 10px;
        color: #E0E0E0;
        max-width: 80%;
        border: 1px solid #404040;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stTextInput>div>div>input {
        background-color: #2D2D2D;
        color: white;
        border: 1px solid #404040;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #0059ff, #0099ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .sources {
        color: #888888;
        font-size: 0.9em;
        margin-top: 10px;
        padding: 10px;
        background: #252525;
        border-radius: 8px;
        border-left: 3px solid #0059ff;
    }
</style>
""", unsafe_allow_html=True)

# ---- SESSION INIT ----
if "chat" not in st.session_state:
    st.session_state.chat = []

if "rag" not in st.session_state:
    with st.spinner("🔄 Initializing AI assistant..."):
        st.session_state.rag = RAGPipeline()

# ---- HEADER ----
st.markdown("<h1 class='main-header'>🤖 AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-header'>Ask me anything - I'm here to help!</h3>", unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    sample_questions = [
        "Explain quantum computing simply",
        "What's the capital of Japan?",
        "How to make chocolate chip cookies?",
        "Tell me about breast cancer treatments",
        "Write a Python function to reverse a string",
        "What's the meaning of life?",
        "Explain blockchain technology"
    ]
    
    for question in sample_questions:
        if st.button(question, key=question):
            st.session_state.input_text = question

# ---- CHAT HISTORY ----
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='user-msg'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        if "📚 **Research Sources:**" in msg:
            parts = msg.split("📚 **Research Sources:**")
            main_content = parts[0]
            sources_content = parts[1]
            st.markdown(f"<div class='bot-msg'><b>Assistant:</b> {main_content}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sources'><b>📚 Research Sources:</b>{sources_content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'><b>Assistant:</b> {msg}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---- INPUT SECTION ----
col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input(
        "Ask me anything...", 
        key="input_text", 
        placeholder="Type your question here...",
        label_visibility="collapsed"
    )
with col2:
    send_btn = st.button("Send", use_container_width=True)

if send_btn and user_query.strip():
    st.session_state.chat.append(("user", user_query))
    with st.spinner("💭 Thinking..."):
        answer = st.session_state.rag.ask(user_query)
    st.session_state.chat.append(("bot", answer))
    st.rerun()

# ---- CLEAR CHAT ----
if st.button("Clear Chat History"):
    st.session_state.chat = []
    st.rerun()
