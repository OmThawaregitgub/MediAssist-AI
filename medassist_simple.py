import streamlit as st
import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="MediAssist AI - Healthcare Q&A",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE SIMULATION (Using Session State)
# ============================================

def init_session_state():
    """Initialize all session state variables"""
    if 'users' not in st.session_state:
        st.session_state.users = {
            'admin': {
                'username': 'admin',
                'email': 'admin@medassist.ai',
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'full_name': 'Administrator',
                'created_at': datetime.now().isoformat()
            }
        }
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'conversations' not in st.session_state:
        st.session_state.conversations = {}
    
    if 'current_conversation_id' not in st.session_state:
        st.session_state.current_conversation_id = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'medical_knowledge' not in st.session_state:
        # Initialize with some medical knowledge
        st.session_state.medical_knowledge = [
            {
                "topic": "Intermittent Fasting",
                "content": "Intermittent fasting is an eating pattern that cycles between periods of fasting and eating. It doesn't specify which foods you should eat but rather when you should eat them.",
                "source": "Medical Research Journal, 2023"
            },
            {
                "topic": "16:8 Fasting Method",
                "content": "The 16:8 method involves fasting for 16 hours each day and eating all your meals within an 8-hour window. For example, you might eat between 12 pm and 8 pm, then fast from 8 pm to 12 pm the next day.",
                "source": "Nutrition and Metabolism Study, 2022"
            },
            {
                "topic": "Intermittent Fasting and Diabetes",
                "content": "Research suggests intermittent fasting may help improve insulin sensitivity and blood sugar control in people with type 2 diabetes. However, patients should consult their doctor before starting.",
                "source": "Diabetes Care Journal, 2023"
            },
            {
                "topic": "Metabolic Benefits",
                "content": "Intermittent fasting can lead to weight loss, improved metabolic health, reduced inflammation, and potentially longer lifespan according to animal studies.",
                "source": "Cell Metabolism, 2022"
            },
            {
                "topic": "Safety Considerations",
                "content": "Intermittent fasting is generally safe for most healthy adults but may not be suitable for pregnant women, children, or people with eating disorders.",
                "source": "American Journal of Clinical Nutrition, 2023"
            }
        ]

# ============================================
# AUTHENTICATION FUNCTIONS
# ============================================

def hash_password(password):
    """Hash a password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password, full_name):
    """Register a new user"""
    if username in st.session_state.users:
        return False, "Username already exists"
    
    if '@' not in email:
        return False, "Invalid email address"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Create user
    st.session_state.users[username] = {
        'username': username,
        'email': email,
        'password_hash': hash_password(password),
        'full_name': full_name,
        'created_at': datetime.now().isoformat()
    }
    
    return True, "Registration successful!"

def login_user(username, password):
    """Login a user"""
    if username not in st.session_state.users:
        return False, "User not found"
    
    user = st.session_state.users[username]
    
    if user['password_hash'] != hash_password(password):
        return False, "Incorrect password"
    
    st.session_state.current_user = username
    return True, "Login successful!"

def logout_user():
    """Logout current user"""
    st.session_state.current_user = None
    st.session_state.current_conversation_id = None
    st.session_state.chat_history = []

# ============================================
# CONVERSATION MANAGEMENT
# ============================================

def create_conversation(title="New Conversation"):
    """Create a new conversation"""
    if not st.session_state.current_user:
        return None
    
    conv_id = f"{st.session_state.current_user}_{datetime.now().timestamp()}"
    
    st.session_state.conversations[conv_id] = {
        'id': conv_id,
        'user': st.session_state.current_user,
        'title': title,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'messages': []
    }
    
    st.session_state.current_conversation_id = conv_id
    st.session_state.chat_history = []
    
    return conv_id

def get_user_conversations():
    """Get all conversations for current user"""
    if not st.session_state.current_user:
        return []
    
    user_conversations = []
    for conv_id, conv in st.session_state.conversations.items():
        if conv['user'] == st.session_state.current_user:
            user_conversations.append(conv)
    
    # Sort by updated_at
    user_conversations.sort(key=lambda x: x['updated_at'], reverse=True)
    return user_conversations

def add_message_to_conversation(role, content):
    """Add a message to current conversation"""
    if not st.session_state.current_conversation_id:
        # Create new conversation if none exists
        title = content[:30] + "..." if len(content) > 30 else content
        create_conversation(title)
    
    conv_id = st.session_state.current_conversation_id
    
    if conv_id in st.session_state.conversations:
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.conversations[conv_id]['messages'].append(message)
        st.session_state.conversations[conv_id]['updated_at'] = datetime.now().isoformat()
        
        # Update chat history for display
        st.session_state.chat_history.append(message)

def load_conversation(conv_id):
    """Load a conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id
        st.session_state.chat_history = st.session_state.conversations[conv_id]['messages'].copy()
        return True
    return False

def delete_conversation(conv_id):
    """Delete a conversation"""
    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]
        
        if st.session_state.current_conversation_id == conv_id:
            st.session_state.current_conversation_id = None
            st.session_state.chat_history = []
        
        return True
    return False

# ============================================
# MEDICAL AI FUNCTIONS
# ============================================

def search_medical_knowledge(query):
    """Search medical knowledge base"""
    query_lower = query.lower()
    results = []
    
    for doc in st.session_state.medical_knowledge:
        topic_match = query_lower in doc['topic'].lower()
        content_match = query_lower in doc['content'].lower()
        
        if topic_match or content_match:
            results.append(doc)
    
    return results

def generate_ai_response(query):
    """Generate AI response based on medical knowledge"""
    # Search for relevant information
    search_results = search_medical_knowledge(query)
    
    if search_results:
        # Build response from search results
        response_parts = ["Based on medical research:"]
        
        for i, result in enumerate(search_results[:3], 1):
            response_parts.append(f"\n{i}. **{result['topic']}**")
            response_parts.append(f"   {result['content']}")
            response_parts.append(f"   *Source: {result['source']}*")
        
        response_parts.append("\n\n*Note: This is for informational purposes only. Please consult a healthcare professional for medical advice.*")
        
        return "\n".join(response_parts)
    
    # If no specific medical knowledge found, provide general response
    general_responses = [
        f"I understand you're asking about '{query}'. While I don't have specific research on this topic in my current knowledge base, here's what I can tell you:\n\n"
        f"Intermittent fasting research is ongoing, and new findings are published regularly. For specific medical advice, please consult with a healthcare provider.",
        
        f"Regarding '{query}', medical research on intermittent fasting suggests it can have various effects on metabolism and health.\n\n"
        f"Different fasting protocols (16:8, 5:2, alternate-day) may have different effects. The 16:8 method is the most studied and appears to be safe for most healthy adults.",
        
        f"Your question about '{query}' is important. While I don't have the exact research you're looking for, I can share that:\n\n"
        f"Intermittent fasting should be approached carefully, especially for individuals with pre-existing health conditions. Always consult with a medical professional before making dietary changes."
    ]
    
    import random
    return random.choice(general_responses)

# ============================================
# FILE UPLOAD AND PROCESSING
# ============================================

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    file_info = {
        'filename': uploaded_file.name,
        'size': uploaded_file.size,
        'type': uploaded_file.type,
        'uploaded_at': datetime.now().isoformat(),
        'content': None
    }
    
    try:
        if uploaded_file.type == "text/plain":
            # Text file
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            file_info['content'] = stringio.read()
            
        elif uploaded_file.type == "text/csv":
            # CSV file
            df = pd.read_csv(uploaded_file)
            file_info['content'] = df.to_string()
            
        elif uploaded_file.type == "application/pdf":
            # PDF file (simplified - in production use PyPDF2)
            file_info['content'] = f"PDF file: {uploaded_file.name}\n\n"
            file_info['content'] += "PDF content extraction would be available in the full version with PyPDF2 library."
            
        else:
            # Other file types
            file_info['content'] = f"File: {uploaded_file.name}\nType: {uploaded_file.type}\nSize: {uploaded_file.size} bytes"
        
        # Add to uploaded files
        st.session_state.uploaded_files.append(file_info)
        
        # Extract knowledge from content if it's text-based
        if file_info['content'] and len(file_info['content']) > 100:
            # Simple extraction - in production would be more sophisticated
            lines = file_info['content'].split('\n')
            for line in lines[:10]:  # Check first 10 lines
                if any(keyword in line.lower() for keyword in ['fasting', 'metabol', 'diabet', 'health', 'medical']):
                    # Add to medical knowledge
                    st.session_state.medical_knowledge.append({
                        "topic": f"From {uploaded_file.name}",
                        "content": line[:200] + "..." if len(line) > 200 else line,
                        "source": f"Uploaded document: {uploaded_file.name}"
                    })
        
        return True, "File uploaded successfully!"
        
    except Exception as e:
        return False, f"Error processing file: {str(e)}"

# ============================================
# UI COMPONENTS
# ============================================

def render_login_page():
    """Render login/register page"""
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
                if not username or not password:
                    st.error("Please enter username and password")
                else:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        # Demo credentials
        st.info("Demo credentials: Username: `admin` | Password: `admin123`")
    
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
                    success, message = register_user(username, email, password, full_name)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)
    
    # About section
    st.markdown("---")
    st.markdown("### About MediAssist AI")
    st.info("""
    **MediAssist AI** is a medical research assistant that helps you find accurate, 
    evidence-based information about intermittent fasting and metabolic disorders.
    
    Features:
    - 💬 Intelligent chat with medical AI
    - 🔍 Search through medical knowledge base
    - 📁 Upload and analyze medical documents
    - 🔐 Secure user accounts with conversation history
    - 📊 Track your health queries and responses
    """)

def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        # User info
        user = st.session_state.users.get(st.session_state.current_user, {})
        st.markdown(f"### 👤 {user.get('full_name', st.session_state.current_user)}")
        st.caption(f"Username: {st.session_state.current_user}")
        
        st.markdown("---")
        st.markdown("## 🗂️ Conversations")
        
        # New conversation button
        if st.button("➕ New Conversation", use_container_width=True, type="primary"):
            create_conversation()
            st.rerun()
        
        # Conversation list
        conversations = get_user_conversations()
        if conversations:
            st.markdown("### Recent Conversations")
            
            for conv in conversations[:5]:  # Show last 5 conversations
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    title = conv['title']
                    if len(title) > 20:
                        title = title[:17] + "..."
                    
                    if st.button(
                        f"🗨️ {title}",
                        key=f"conv_btn_{conv['id']}",
                        use_container_width=True
                    ):
                        load_conversation(conv['id'])
                        st.rerun()
                
                with col2:
                    if st.button(
                        "🗑️",
                        key=f"del_btn_{conv['id']}",
                        help="Delete conversation"
                    ):
                        delete_conversation(conv['id'])
                        st.rerun()
        
        # Sample questions
        st.markdown("---")
        st.markdown("### 💡 Sample Questions")
        
        sample_questions = [
            "What is intermittent fasting?",
            "Benefits of 16:8 fasting method",
            "Is intermittent fasting safe for diabetics?",
            "How does fasting affect metabolism?",
            "What are the risks of intermittent fasting?"
        ]
        
        for question in sample_questions:
            if st.button(
                question,
                key=f"sample_{question[:20]}",
                use_container_width=True
            ):
                st.session_state.sample_question = question
        
        # File upload
        st.markdown("---")
        st.markdown("### 📁 Upload Documents")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'csv', 'pdf'],
            key="file_uploader"
        )
        
        if uploaded_file:
            with st.spinner("Processing file..."):
                success, message = process_uploaded_file(uploaded_file)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        # About
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("Version 1.0.0 | MediAssist AI")

def render_chat_interface():
    """Render the main chat interface"""
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if st.session_state.current_conversation_id:
            conv = st.session_state.conversations.get(st.session_state.current_conversation_id, {})
            title = conv.get('title', 'Conversation')
        else:
            title = "New Conversation"
        
        st.markdown(f"# 💬 {title}")
    
    with col2:
        # Quick stats
        conv_count = len(get_user_conversations())
        st.metric("Conversations", conv_count)
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Chat display area
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            # Welcome message
            st.markdown("""
            <div class="chat-message assistant-message">
                <div class="message-header">🤖 MediAssist AI</div>
                <div class="message-content">
                    Hello! I'm MediAssist AI, your medical research assistant. 
                    I can help answer your questions about intermittent fasting, 
                    metabolic disorders, and general health topics.
                    
                    **I have knowledge about:**
                    - Intermittent fasting methods (16:8, 5:2, etc.)
                    - Metabolic benefits and risks
                    - Diabetes and fasting
                    - Weight management
                    - General health implications
                    
                    Ask me anything, or try one of the sample questions from the sidebar!
                </div>
                <div class="message-timestamp">Ready to assist</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display chat history
            for message in st.session_state.chat_history:
                timestamp = datetime.fromisoformat(message['timestamp']).strftime("%H:%M")
                
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-header">👤 You</div>
                        <div class="message-content">{message['content']}</div>
                        <div class="message-timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-header">🤖 MediAssist AI</div>
                        <div class="message-content">{message['content']}</div>
                        <div class="message-timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # User input area
    st.markdown("---")
    
    # Check for sample question
    if 'sample_question' in st.session_state:
        user_input = st.session_state.sample_question
        del st.session_state.sample_question
    else:
        user_input = ""
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_area(
            "Your message:",
            value=user_input,
            height=100,
            placeholder="Type your medical question here...",
            label_visibility="collapsed",
            key="user_query_input"
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
    
    if submit and user_query.strip():
        # Add user message
        add_message_to_conversation('user', user_query)
        
        # Generate AI response
        with st.spinner("🔍 Searching medical knowledge..."):
            ai_response = generate_ai_response(user_query)
            add_message_to_conversation('assistant', ai_response)
        
        st.rerun()
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("Clear Chat History", type="secondary", use_container_width=True):
            st.session_state.chat_history = []
            if st.session_state.current_conversation_id:
                conv_id = st.session_state.current_conversation_id
                if conv_id in st.session_state.conversations:
                    st.session_state.conversations[conv_id]['messages'] = []
            st.rerun()

def render_documents_tab():
    """Render documents management tab"""
    st.header("📚 Document Management")
    
    # Upload section
    st.subheader("Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['txt', 'csv', 'pdf'],
        accept_multiple_files=True,
        key="doc_uploader"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                success, message = process_uploaded_file(uploaded_file)
                if success:
                    st.success(f"✅ {uploaded_file.name}: {message}")
                else:
                    st.error(f"❌ {uploaded_file.name}: {message}")
    
    # List uploaded files
    st.subheader("Your Documents")
    
    if st.session_state.uploaded_files:
        for i, file_info in enumerate(st.session_state.uploaded_files):
            with st.expander(f"📄 {file_info['filename']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {file_info['type']}")
                    st.write(f"**Size:** {file_info['size']:,} bytes")
                    st.write(f"**Uploaded:** {file_info['uploaded_at'][:19]}")
                    
                    if file_info['content'] and len(file_info['content']) > 0:
                        st.write("**Preview:**")
                        preview = file_info['content'][:500] + "..." if len(file_info['content']) > 500 else file_info['content']
                        st.text(preview)
                
                with col2:
                    if st.button(f"Remove", key=f"remove_{i}"):
                        st.session_state.uploaded_files.pop(i)
                        st.rerun()
    else:
        st.info("No documents uploaded yet. Upload some files to get started!")
    
    # Knowledge base
    st.subheader("📖 Medical Knowledge Base")
    
    if st.session_state.medical_knowledge:
        st.write(f"Total knowledge items: {len(st.session_state.medical_knowledge)}")
        
        # Search knowledge
        search_term = st.text_input("Search knowledge base")
        
        if search_term:
            results = [doc for doc in st.session_state.medical_knowledge 
                      if search_term.lower() in doc['topic'].lower() or 
                      search_term.lower() in doc['content'].lower()]
        else:
            results = st.session_state.medical_knowledge[:10]  # Show first 10
        
        for doc in results:
            with st.expander(f"📖 {doc['topic']}"):
                st.write(doc['content'])
                st.caption(f"Source: {doc['source']}")
    else:
        st.info("Knowledge base is empty. Upload documents or ask questions to build knowledge.")

def render_analytics_tab():
    """Render analytics tab"""
    st.header("📊 Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        conv_count = len(get_user_conversations())
        st.metric("Total Conversations", conv_count)
    
    with col2:
        total_messages = sum(len(conv['messages']) for conv in get_user_conversations())
        st.metric("Total Messages", total_messages)
    
    with col3:
        file_count = len(st.session_state.uploaded_files)
        st.metric("Uploaded Files", file_count)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    conversations = get_user_conversations()
    if conversations:
        for conv in conversations[:3]:
            with st.expander(f"🗨️ {conv['title']} ({len(conv['messages'])} messages)"):
                st.write(f"**Created:** {conv['created_at'][:19]}")
                st.write(f"**Last updated:** {conv['updated_at'][:19]}")
                
                if conv['messages']:
                    st.write("**Last message:**")
                    last_msg = conv['messages'][-1]
                    role_icon = "👤" if last_msg['role'] == 'user' else "🤖"
                    st.write(f"{role_icon} {last_msg['content'][:100]}...")
                
                if st.button("Open Conversation", key=f"open_{conv['id']}"):
                    load_conversation(conv['id'])
                    st.switch_page("streamlit_app.py")  # Switch to main tab
    else:
        st.info("No conversations yet. Start chatting!")

def render_settings_tab():
    """Render settings tab"""
    st.header("⚙️ Settings")
    
    # User profile
    st.subheader("User Profile")
    
    user = st.session_state.users.get(st.session_state.current_user, {})
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", value=user.get('username', ''), disabled=True)
            email = st.text_input("Email", value=user.get('email', ''))
        
        with col2:
            full_name = st.text_input("Full Name", value=user.get('full_name', ''))
            new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
        
        if st.form_submit_button("Update Profile"):
            # Update user info
            if email:
                st.session_state.users[st.session_state.current_user]['email'] = email
            if full_name:
                st.session_state.users[st.session_state.current_user]['full_name'] = full_name
            if new_password:
                st.session_state.users[st.session_state.current_user]['password_hash'] = hash_password(new_password)
            
            st.success("Profile updated successfully!")
    
    # App settings
    st.subheader("Application Settings")
    
    # Knowledge base management
    if st.button("Clear Knowledge Base"):
        if st.checkbox("Are you sure? This will remove all medical knowledge items."):
            st.session_state.medical_knowledge = []
            st.success("Knowledge base cleared!")
            st.rerun()
    
    if st.button("Reset All Data"):
        if st.checkbox("⚠️ **DANGER**: Are you absolutely sure? This will delete ALL your conversations and uploaded files."):
            st.session_state.conversations = {}
            st.session_state.uploaded_files = []
            st.session_state.current_conversation_id = None
            st.session_state.chat_history = []
            st.success("All data has been reset!")
            st.rerun()
    
    # About
    st.subheader("About MediAssist AI")
    st.info("""
    **Version:** 1.0.0
    **Status:** Running
    **Storage:** Session-based (data resets on page refresh)
    
    **Note:** This is a demonstration version. In a production environment:
    - Data would be stored in a persistent database
    - More advanced AI models would be used
    - PDF processing would be fully implemented
    - User authentication would be more secure
    """)

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application function"""
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    if not st.session_state.current_user:
        render_login_page()
        return
    
    # Main application - User is logged in
    render_sidebar()
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📚 Documents", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_documents_tab()
    
    with tab3:
        render_analytics_tab()
    
    with tab4:
        render_settings_tab()

if __name__ == "__main__":
    main()