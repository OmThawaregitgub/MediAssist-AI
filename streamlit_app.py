import streamlit as st
from rag import RAGPipeline

# ----------------------------------------------------
# 🌐 PAGE CONFIGURATION
# ----------------------------------------------------
st.set_page_config(page_title="MediAssist AI - Healthcare Q&A", layout="wide")

# Remove unnecessary white space and apply custom UI styling
st.markdown("""
<style>
    .main > div {
        padding-top: 0px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    h2 {
        margin-bottom: 0.5rem !important;
    }
    .chat-box {
        margin-top: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 🔄 SESSION STATE INITIALIZATION
# ----------------------------------------------------
# Store chat history
if "chat" not in st.session_state:
    st.session_state.chat = []

# Initialize RAG pipeline once per session
if "rag" not in st.session_state:
    try:
        st.session_state.rag = RAGPipeline()

        # Display assistant information in sidebar
        if hasattr(st.session_state.rag, 'get_collection_info'):
            info = st.session_state.rag.get_collection_info()
            st.sidebar.info(info)

    except Exception as e:
        st.error(f"Failed to initialize MediAssist AI: {e}")
        st.stop()

# ----------------------------------------------------
# 🏥 PAGE TITLE
# ----------------------------------------------------
st.markdown(
    "<h2 style='text-align:center; margin-bottom: 0.5rem;'>🏥 MediAssist AI - Medical Research Assistant</h2>",
    unsafe_allow_html=True
)

# ----------------------------------------------------
# 📌 SIDEBAR INFORMATION
# ----------------------------------------------------
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    "This AI assistant answers medical questions using research articles "
    "about intermittent fasting and metabolic disorders."
)

# Sidebar sample questions for quick prompts
st.sidebar.markdown("### 💡 Sample Questions")
sample_questions = [
    "What is intermittent fasting?",
    "Benefits of 16:8 fasting method",
    "Is intermittent fasting safe for diabetics?",
    "How does fasting affect metabolism?"
]

# Clicking a sample question auto-fills the chat input
for question in sample_questions:
    if st.sidebar.button(question, key=question):
        st.session_state.input_text = question
        st.rerun()

# ----------------------------------------------------
# 🎨 CHAT UI STYLING
# ----------------------------------------------------
st.markdown("""
<style>
.chat-box {
    height: 60vh;
    overflow-y: auto;
    padding: 10px;
    border-radius: 10px;
    background-color: #1e1e1e;
    margin-bottom: 20px;
    border: 1px solid #444;
    margin-top: 0.5rem !important;
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
    border: 1px solid #444;
}
.stButton button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 💬 CHAT DISPLAY AREA
# ----------------------------------------------------
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

# Display initial message if no chat history exists
if not st.session_state.chat:
    st.markdown(
        "<div class='bot-msg'><b>Assistant:</b> Hello! I'm MediAssist AI. "
        "I can help answer your questions about intermittent fasting and metabolic health. "
        "What would you like to know?</div>",
        unsafe_allow_html=True
    )
else:
    # Iterate through chat history and render messages
    for role, msg in st.session_state.chat:
        if role == "user":
            st.markdown(
                f"<div class='user-msg'><b>You:</b> {msg}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='bot-msg'><b>Assistant:</b> {msg}</div>",
                unsafe_allow_html=True
            )

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 📝 USER INPUT FORM
# ----------------------------------------------------
# Using a form allows Enter key submission
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])

    # Text input field
    with col1:
        user_query = st.text_input(
            "Ask your medical question:",
            key="input_text",
            placeholder="e.g., What are the benefits of intermittent fasting?",
            label_visibility="collapsed"
        )

    # Submit button
    with col2:
        submit_btn = st.form_submit_button("Send", use_container_width=True)

# Handle user input submission
if submit_btn and user_query.strip():
    st.session_state.chat.append(("user", user_query))

    # Query the RAG pipeline
    with st.spinner("🔍 Searching medical research..."):
        try:
            answer = st.session_state.rag.ask(user_query)
            st.session_state.chat.append(("bot", answer))
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat.append(("bot", error_msg))

    st.rerun()

# ----------------------------------------------------
# 🧹 CLEAR CHAT BUTTON
# ----------------------------------------------------
if st.button("Clear Chat"):
    st.session_state.chat = []
    st.rerun()
