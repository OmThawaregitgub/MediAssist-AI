import streamlit as st
from rag import RAGPipeline
import traceback

# Page configuration
st.set_page_config(
    page_title="MediAssist AI",
    page_icon="🏥",
    layout="centered"
)

# Initialize session state
if "rag" not in st.session_state:
    try:
        st.session_state.rag = RAGPipeline()
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Failed to initialize MediAssist AI: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🏥 MediAssist AI")
st.markdown("### AI-Powered Healthcare Q&A System")
st.markdown("Ask questions about Intermittent Fasting and metabolic disorders")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_query := st.chat_input("Ask a medical question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching medical research..."):
            try:
                answer = st.session_state.rag.ask(user_query)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"Sorry, I encountered an error while processing your question. Please try again."
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                # Print full error for debugging
                st.error(f"Debug: {str(e)}")
