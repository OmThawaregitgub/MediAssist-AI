import streamlit as st
from rag import RAGPipeline
import time
import os

# Page configuration
st.set_page_config(
    page_title="MediAssist AI",
    page_icon="🏥",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .setup-instructions {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def show_api_key_instructions():
    """Show detailed instructions for setting up API key"""
    st.markdown("""
    <div class="setup-instructions">
        <h3>🔑 API Key Setup Required</h3>
        <p>To use MediAssist AI, you need to set up your Google Gemini API key.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 Setup Instructions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### For Local Development")
        st.code("""
# Create a .env file in your project root:
echo 'API_KEY=your_actual_api_key_here' > .env
        """, language="bash")
        
        st.markdown("""
1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in your project folder
3. Add your API key: `API_KEY=your_key_here`
4. Restart the application
        """)
    
    with col2:
        st.markdown("#### For Streamlit Cloud")
        st.code("""
In Streamlit Cloud:
1. Go to your app dashboard
2. Click 'Settings' ⚙️
3. Go to 'Secrets' tab
4. Add your API key:
   API_KEY=your_actual_api_key_here
        """, language="bash")
        
        st.markdown("""
1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Go to your Streamlit app settings
3. Add the secret in format shown
4. Redeploy the app
        """)
    
    st.markdown("---")
    st.markdown("### 🔐 Getting Your Google Gemini API Key")
    
    steps = [
        "1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)",
        "2. Sign in with your Google account",
        "3. Click 'Create API Key'",
        "4. Copy the generated API key",
        "5. Add it to your environment as shown above"
    ]
    
    for step in steps:
        st.markdown(step)
    
    st.markdown("""
    <div class="info-box">
        <strong>Note:</strong> The API key is required for the AI to generate responses. 
        Without it, the app cannot function properly.
    </div>
    """, unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏥 MediAssist AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Healthcare Q&A System for Intermittent Fasting Research</div>', unsafe_allow_html=True)

# Initialize session state
if "rag" not in st.session_state:
    try:
        with st.spinner("🔄 Initializing MediAssist AI... This may take a few seconds."):
            st.session_state.rag = RAGPipeline()
            st.markdown("""
            <div class="success-box">
                <strong>✅ Success!</strong> MediAssist AI initialized successfully!
            </div>
            """, unsafe_allow_html=True)
            time.sleep(2)  # Brief pause to show success message
            
    except ValueError as e:
        if "API_KEY" in str(e):
            st.markdown("""
            <div class="error-box">
                <strong>❌ Initialization Failed</strong><br>
                API_KEY not found in environment variables
            </div>
            """, unsafe_allow_html=True)
            
            # Show detailed instructions
            show_api_key_instructions()
            st.stop()
        else:
            st.markdown(f"""
            <div class="error-box">
                <strong>❌ Initialization Error</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.stop()
            
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
            <strong>❌ Unexpected Error</strong><br>
            {str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.info("Please check the logs for more details and try refreshing the page.")
        st.stop()

# Initialize chat messages if not exists
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "👋 Hello! I'm MediAssist AI, your specialized assistant for intermittent fasting and metabolic health research. I can help you with evidence-based information about various fasting protocols, their benefits, and clinical considerations. What would you like to know?"
        }
    ]

# Display system status
st.markdown("""
<div class="info-box">
    <strong>System Status:</strong> ✅ Ready | 
    <strong>Database:</strong> ✅ Loaded | 
    <strong>AI Model:</strong> ✅ Connected
</div>
""", unsafe_allow_html=True)

# Display example questions
with st.expander("💡 Example Questions You Can Ask"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - What is the 16:8 intermittent fasting method?
        - How does intermittent fasting affect insulin sensitivity?
        - Is intermittent fasting safe for type 2 diabetic patients?
        """)
    with col2:
        st.markdown("""
        - What are the different types of intermittent fasting?
        - Can intermittent fasting help with weight loss?
        - What is time-restricted feeding?
        """)

st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_query := st.chat_input("Ask about intermittent fasting, metabolic health..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching medical research and generating evidence-based answer..."):
            try:
                # Verify RAG pipeline is properly initialized
                if not hasattr(st.session_state.rag, 'llm'):
                    st.error("🤖 AI model not properly initialized. Please refresh the page.")
                else:
                    answer = st.session_state.rag.ask(user_query)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = "I apologize, but I encountered a technical issue while processing your question. Please try again in a moment."
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Show error details in expander
                with st.expander("Technical Details (for debugging)"):
                    st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <i>MediAssist AI - Evidence-based healthcare insights powered by RAG and AI</i><br>
    <i>Always consult healthcare professionals for medical advice</i>
</div>
""", unsafe_allow_html=True)
