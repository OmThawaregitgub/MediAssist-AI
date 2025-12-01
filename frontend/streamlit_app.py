import streamlit as st
import requests
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Custom CSS
st.set_page_config(
    page_title="MediAssist AI - Healthcare Q&A",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
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
        padding: 10px 15px;
    }
    .stButton > button {
        border-radius: 20px;
        height: 3rem;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .user-message {
        background-color: #0068c9;
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 0.2rem;
    }
    .assistant-message {
        background-color: #f0f2f6;
        color: #262730;
        margin-right: 20%;
        border-bottom-left-radius: 0.2rem;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .message-content {
        line-height: 1.5;
    }
    .message-timestamp {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'conversations' not in st.session_state:
    st.session_state.conversations = []
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None

# Helper functions
def is_authenticated():
    return st.session_state.auth_token is not None

def get_auth_headers():
    if st.session_state.auth_token:
        return {
            'Authorization': f'Bearer {st.session_state.auth_token}',
            'Content-Type': 'application/json'
        }
    return {}

def make_authenticated_request(method, endpoint, **kwargs):
    headers = get_auth_headers()
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{endpoint}",
            **kwargs
        )
        return response
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend server is not running. Please start the backend first.")
        st.info("Run this command in another terminal: `python run_backend.py`")
        return None
    except Exception as e:
        st.error(f"API request failed: {str(e)}")
        return None

# Authentication functions
def login(username, password):
    try:
        form_data = {
            'username': username,
            'password': password
        }
        
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data=form_data
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data['access_token']
            st.session_state.user_info = data['user']
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def register(username, email, password, full_name=None):
    try:
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'full_name': full_name
        }
        
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=user_data
        )
        
        if response.status_code == 200:
            st.success("Registration successful! Please login.")
            return True
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"Registration failed: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def logout():
    st.session_state.auth_token = None
    st.session_state.user_info = None
    st.session_state.chat_history = []
    st.session_state.conversations = []
    st.session_state.current_conversation_id = None
    st.rerun()

# Check if user is authenticated
if not is_authenticated():
    # Show login/register page
    st.title("🏥 MediAssist AI - Medical Research Assistant")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", type="primary")
            
            if submit:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
    
    with tab2:
        st.subheader("Create a new account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*")
                email = st.text_input("Email*")
            with col2:
                full_name = st.text_input("Full Name")
                password = st.text_input("Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            submit = st.form_submit_button("Register", type="primary")
            
            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                elif not username or not email or not password:
                    st.error("Please fill in all required fields!")
                else:
                    if register(username, email, password, full_name):
                        st.rerun()
    
    # Show information about the app
    st.markdown("---")
    st.markdown("### About MediAssist AI")
    st.info("""
    **MediAssist AI** is a medical research assistant that helps you find accurate, 
    evidence-based information about intermittent fasting and metabolic disorders.
    
    Features:
    - 💬 Intelligent chat with medical AI
    - 🔍 Search through research articles
    - 📁 Upload and analyze medical documents
    - 🔐 Secure user accounts with conversation history
    """)
    
    st.stop()

# Main application - User is authenticated
user_info = st.session_state.user_info

# Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown(f"# 🏥 MediAssist AI")
    st.caption(f"Welcome back, {user_info.get('full_name', user_info.get('username', 'User'))}!")

with col2:
    # Quick status
    st.metric("Status", "Online")

with col3:
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# Sidebar
with st.sidebar:
    st.markdown("## 🗂️ Conversations")
    
    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        response = make_authenticated_request(
            'POST',
            '/chat/conversations/new?title=New Conversation'
        )
        if response and response.status_code == 200:
            data = response.json()
            st.session_state.current_conversation_id = data['conversation_id']
            st.session_state.chat_history = []
            st.rerun()
    
    # Get conversations
    response = make_authenticated_request('GET', '/chat/conversations')
    if response and response.status_code == 200:
        conversations = response.json()
        st.session_state.conversations = conversations
        
        if conversations:
            st.markdown("---")
            st.markdown("### Recent Conversations")
            
            for conv in conversations[:10]:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    title = conv['title']
                    if len(title) > 25:
                        title = title[:22] + "..."
                    
                    if st.button(
                        f"🗨️ {title}",
                        key=f"conv_btn_{conv['id']}",
                        use_container_width=True
                    ):
                        # Load conversation
                        conv_response = make_authenticated_request(
                            'GET',
                            f"/chat/conversations/{conv['id']}"
                        )
                        if conv_response and conv_response.status_code == 200:
                            data = conv_response.json()
                            st.session_state.chat_history = []
                            for msg in data['messages']:
                                st.session_state.chat_history.append({
                                    'role': msg['role'],
                                    'content': msg['content'],
                                    'timestamp': datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                                })
                            st.session_state.current_conversation_id = conv['id']
                            st.rerun()
                
                with col2:
                    if st.button(
                        "🗑️",
                        key=f"del_btn_{conv['id']}",
                        help="Delete conversation"
                    ):
                        del_response = make_authenticated_request(
                            'DELETE',
                            f"/chat/conversations/{conv['id']}"
                        )
                        if del_response and del_response.status_code == 200:
                            st.rerun()
    
    # Sample questions
    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    
    sample_questions = [
        "What is intermittent fasting?",
        "Benefits of 16:8 fasting method",
        "Is intermittent fasting safe for diabetics?",
        "How does fasting affect metabolism?"
    ]
    
    for question in sample_questions:
        if st.button(
            question,
            key=f"sample_{question[:20]}",
            use_container_width=True
        ):
            st.session_state.user_input = question
    
    # About section
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    MediAssist AI helps you find medical information 
    from research articles about intermittent fasting 
    and metabolic disorders.
    """)

# Main chat interface
st.markdown("---")

# Display current conversation title
if st.session_state.current_conversation_id:
    conv_title = "New Conversation"
    for conv in st.session_state.conversations:
        if conv['id'] == st.session_state.current_conversation_id:
            conv_title = conv['title']
            break
    st.subheader(f"💬 {conv_title}")
else:
    st.subheader("💬 New Conversation")

# Chat display area
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-message assistant-message">
            <div class="message-header">🤖 MediAssist AI</div>
            <div class="message-content">
                Hello! I'm MediAssist AI, your medical research assistant. 
                I can help answer your questions about intermittent fasting, 
                metabolic disorders, and general health topics.
                
                Ask me anything, or try one of the sample questions from the sidebar!
            </div>
            <div class="message-timestamp">Ready to assist</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                timestamp = message.get('timestamp', datetime.now()).strftime("%H:%M")
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-header">👤 You</div>
                    <div class="message-content">{message['content']}</div>
                    <div class="message-timestamp">{timestamp}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                timestamp = message.get('timestamp', datetime.now()).strftime("%H:%M")
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="message-header">🤖 MediAssist AI</div>
                    <div class="message-content">{message['content']}</div>
                    <div class="message-timestamp">{timestamp}</div>
                </div>
                """, unsafe_allow_html=True)

# User input area
st.markdown("---")

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Your message:",
        key="user_input",
        height=100,
        placeholder="Type your medical question here...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([4, 1])
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        submit = st.form_submit_button(
            "Send",
            use_container_width=True,
            type="primary"
        )
    
    # Check if backend is running
    try:
        health_check = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_check.status_code != 200:
            st.warning("⚠️ Backend server is running but not responding properly.")
    except:
        st.error("🚨 Backend server is not running! Please start it first.")
        st.info("Run this command in another terminal: `python run_backend.py`")

if submit and user_input.strip():
    # Add user message to history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now()
    })
    
    # Prepare request
    request_data = {
        'query': user_input,
        'conversation_id': st.session_state.current_conversation_id,
        'use_reranking': True,
        'top_k': 10
    }
    
    # Get response
    with st.spinner("🔍 Searching medical research..."):
        response = make_authenticated_request(
            'POST',
            '/chat/query',
            json=request_data
        )
    
    if response and response.status_code == 200:
        data = response.json()
        
        # Update current conversation ID if new conversation was created
        if not st.session_state.current_conversation_id:
            st.session_state.current_conversation_id = data['conversation_id']
        
        # Add assistant message to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': data['answer'],
            'timestamp': datetime.now()
        })
        
        # Refresh conversations list
        conv_response = make_authenticated_request('GET', '/chat/conversations')
        if conv_response and conv_response.status_code == 200:
            st.session_state.conversations = conv_response.json()
        
    else:
        if response:
            error_detail = response.json().get('detail', 'Unknown error')
            error_msg = f"Sorry, I encountered an error: {error_detail}"
        else:
            error_msg = "Sorry, I couldn't connect to the server. Please make sure the backend is running."
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': error_msg,
            'timestamp': datetime.now()
        })
    
    st.rerun()

# Add clear chat button at the bottom
if st.session_state.chat_history:
    if st.button("Clear Chat", type="secondary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()