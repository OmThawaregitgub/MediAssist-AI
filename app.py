import streamlit as st
import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any
import PyPDF2
import time
from dotenv import load_dotenv
from model_list import model_list

# Import our modular components
from llm import LLMClient
from rag import RAGPipeline

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

<<<<<<< HEAD
# load_dotenv()

# Get API key
API_KEY = os.getenv('GEMINI_API_KEY')

print(f"API Key loaded: {'Yes' if API_KEY else 'No'}")
if API_KEY:
    print(f"API Key starts with: {API_KEY[:10]}...")

# # Initialize global instances
# llm_client = LLMClient()
# rag_pipeline = None

=======



# Get API key - try multiple names
API_KEY = st.secrets['GEMINI_API_KEY']

key_value = st.secrets['GEMINI_API_KEY']
    
# Fallback to your key if not found
if not API_KEY:
    print("⚠️ Using provided API key")
    API_KEY = "YOUR_GEMINI_API_KEY"
print("API_KEY OF GOOGLE = ",API_KEY)
>>>>>>> ec4d3b6f0f4ebb36ef9d2ceb008ee0f9a3c85a31
# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="MediAssist AI - Medical Research Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS - DARK THEME
# ============================================

st.markdown("""
<style>
    /* ... (Keep all your CSS styles exactly as they are) ... */
</style>
""", unsafe_allow_html=True)

# ============================================
# CONVERSATION STORAGE
# ============================================

CONVERSATIONS_FILE = "conversations.json"

def load_conversations():
    """Load conversations from file"""
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_conversations(conversations):
    """Save conversations to file"""
    try:
        with open(CONVERSATIONS_FILE, 'w') as f:
            json.dump(conversations, f, indent=2)
    except Exception as e:
        print(f"Error saving conversations: {e}")

def save_conversation(user_id, conversation_id, messages, title=None):
    """Save a conversation with optional title"""
    conversations = load_conversations()
    
    if user_id not in conversations:
        conversations[user_id] = {}
    
    # Generate title from first user message if not provided
    if not title:
        title = "New Conversation"
        for msg in messages:
            if msg['role'] == 'user':
                content = msg['content'].strip()
                if len(content) > 5:
                    title = content[:50] + ("..." if len(content) > 50 else "")
                    break
    
    # Update existing conversation or create new
    if conversation_id in conversations[user_id]:
        conversations[user_id][conversation_id]['messages'] = messages
        conversations[user_id][conversation_id]['title'] = title
        conversations[user_id][conversation_id]['updated_at'] = datetime.now().isoformat()
        conversations[user_id][conversation_id]['message_count'] = len(messages)
    else:
        conversations[user_id][conversation_id] = {
            'id': conversation_id,
            'title': title,
            'messages': messages,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'message_count': len(messages)
        }
    
    save_conversations(conversations)
    return conversations[user_id][conversation_id]

def get_user_conversations(user_id):
    """Get all conversations for a user"""
    conversations = load_conversations()
    return conversations.get(user_id, {})

def delete_conversation(user_id, conversation_id):
    """Delete a conversation"""
    conversations = load_conversations()
    if user_id in conversations and conversation_id in conversations[user_id]:
        del conversations[user_id][conversation_id]
        save_conversations(conversations)
        return True
    return False

def load_conversation(user_id, conversation_id):
    """Load a specific conversation"""
    conversations = load_conversations()
    if user_id in conversations and conversation_id in conversations[user_id]:
        return conversations[user_id][conversation_id]
    return None

def update_conversation_title(user_id, conversation_id, new_title):
    """Update conversation title"""
    conversations = load_conversations()
    if user_id in conversations and conversation_id in conversations[user_id]:
        conversations[user_id][conversation_id]['title'] = new_title
        conversations[user_id][conversation_id]['updated_at'] = datetime.now().isoformat()
        save_conversations(conversations)
        return True
    return False

# ============================================
# INITIALIZATION FUNCTIONS
# ============================================

def init_session_state():
    """Initialize session state"""
    defaults = {
        'users': {
            'admin': {
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'email': 'admin@medassist.ai',
                'full_name': 'Administrator',
                'created_at': datetime.now().isoformat()
            }
        },
        'current_user': None,
        'current_conversation_id': None,
        'conversations': {},
        'llm_initialized': False,
        'rag_initialized': False,
        'editing_conversation': None,
        'edit_conversation_title': "",
        'llm_client': None,           # ADD THIS
        'rag_pipeline': None          # ADD THIS
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize current conversation messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def initialize_systems():
    """Initialize all AI systems"""
    
    print("🚀 Starting system initialization...")
    
    # Show a spinner in the UI
    with st.spinner("Initializing AI systems..."):
        
        # Initialize LLM
        if not st.session_state.llm_initialized:
            print("🔄 Getting LLMClient singleton...")
            try:
                # Get the singleton instance
                llm_client = get_llm_client()
                
                # Initialize it
                result = llm_client.initialize(API_KEY)
                print(f"LLM initialization result: {result}")
                
                # Force set to True
                st.session_state.llm_initialized = True
<<<<<<< HEAD
                print(f"✅ LLM marked as initialized")
                
            except Exception as e:
                print(f"❌ LLM initialization error: {e}")
                st.session_state.llm_initialized = True
                print("⚠️ Marked as initialized despite error")
=======
                st.success("✅ Connected to Gemini Flash Latest")
                return model
            else:
                st.error("❌ No response from model")
                return None
        except Exception as e:
            print(f"gemini-flash-latest failed: {e}")
            
            # Try other models as fallback
            models_to_try = [
                'gemini-2.5-flash',
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest',
                'gemini-pro'
            ]
            
            # for model_name in models_to_try:
            #     try:
            #         print(f"Trying model: {model_name}")
            #         model = genai.GenerativeModel(model_name)
            #         response = model.generate_content("Test")
            #         if response.text:
            #             st.session_state.llm_model = model
            #             st.session_state.llm_initialized = True
            #             st.success(f"✅ Connected to {model_name}")
            return 'gemini-2.5-flash'
            #     except Exception as e2:
            #         print(f"Failed with {model_name}: {e2}")
            #         continue
>>>>>>> ec4d3b6f0f4ebb36ef9d2ceb008ee0f9a3c85a31
        
        # Initialize RAG
        if not st.session_state.rag_initialized:
            try:
                rag_pipeline = get_rag_pipeline()
                
                # Add sample data
                sample_data = [
                    {
                        "text": "Intermittent fasting (IF) is an eating pattern that cycles between periods of fasting and eating. It doesn't specify which foods you should eat but rather when you should eat them.",
                        "metadata": {"source": "Harvard Medical Review", "topic": "Intermittent Fasting", "type": "research"}
                    },
                    {
                        "text": "The 16:8 method involves fasting for 16 hours each day and restricting your daily eating window to 8 hours. For example, you might eat between 12 pm and 8 pm, then fast until 12 pm the next day.",
                        "metadata": {"source": "Nutrition Research Journal", "topic": "Fasting Methods", "type": "method"}
                    },
                    {
                        "text": "Research shows intermittent fasting can improve insulin sensitivity, which is particularly beneficial for people with type 2 diabetes or prediabetes.",
                        "metadata": {"source": "Diabetes Care Journal", "topic": "Diabetes", "type": "research"}
                    },
                    {
                        "text": "Cancer is a group of diseases involving abnormal cell growth with the potential to invade or spread to other parts of the body. There are more than 100 types of cancer.",
                        "metadata": {"source": "National Cancer Institute", "topic": "Cancer Basics", "type": "research"}
                    },
                    {
                        "text": "Common cancer treatments include surgery, chemotherapy, radiation therapy, immunotherapy, and targeted therapy. Treatment depends on the cancer type and stage.",
                        "metadata": {"source": "American Cancer Society", "topic": "Cancer Treatment", "type": "medical"}
                    }
                ]
                
                rag_pipeline.add_documents(
                    documents=[item["text"] for item in sample_data],
                    metadatas=[item["metadata"] for item in sample_data]
                )
                
                st.session_state.rag_initialized = True
                print(f"✅ RAG initialized with {len(sample_data)} documents")
                
            except Exception as e:
                print(f"❌ RAG initialization error: {e}")
                st.session_state.rag_initialized = False
                print("⚠️ RAG initialization failed")
    
    return True

# ============================================
# GLOBAL INSTANCES (SINGLETON PATTERN)
# ============================================

_llm_client_instance = None
_rag_pipeline_instance = None

def get_llm_client():
    """Get or create LLM client singleton"""
    global _llm_client_instance
    print(f"🔍 get_llm_client() called")
    print(f"   - Global instance exists: {_llm_client_instance is not None}")
    
    if _llm_client_instance is None:
        print(f"   🆕 Creating NEW LLMClient instance")
        _llm_client_instance = LLMClient()
        print(f"   📍 New instance ID: {id(_llm_client_instance)}")
    else:
        print(f"   🔄 Returning EXISTING instance")
        print(f"   📍 Existing instance ID: {id(_llm_client_instance)}")
        if hasattr(_llm_client_instance, 'initialized'):
            print(f"   ✅ Instance.initialized: {_llm_client_instance.initialized}")
        else:
            print(f"   ❌ Instance has no 'initialized' attribute!")
    
    return _llm_client_instance


def get_rag_pipeline():
    """Get or create RAG pipeline singleton"""
    global _rag_pipeline_instance
    if _rag_pipeline_instance is None:
        _rag_pipeline_instance = RAGPipeline()
        print("🔄 Created new RAGPipeline singleton")
    return _rag_pipeline_instance

# ============================================
# CORE FUNCTIONS
# ============================================

def generate_response(query: str) -> Dict[str, Any]:
    """Generate AI response - RAG-first architecture"""
    try:
        print(f"\n" + "="*50)
        print(f"🔍 generate_response() called: '{query}'")
        print(f"   - llm_initialized: {st.session_state.get('llm_initialized', False)}")
        print(f"   - rag_initialized: {st.session_state.get('rag_initialized', False)}")
        
        # Initialize variables
        sources = []
        used_rag = False
        answer = ""
        
        # STEP 1: Try RAG first (if available)
        if st.session_state.get('rag_initialized', False):
            try:
                rag_pipeline = get_rag_pipeline()
                search_results = rag_pipeline.search(query, top_k=2)
                print(f"   🔍 RAG search found: {len(search_results)} results")
                
                if search_results:
                    sources = search_results
                    used_rag = True
                    
                    # Combine RAG results into context
                    rag_context = "\n\n".join([f"Source {i+1}: {r['text']}" 
                                              for i, r in enumerate(search_results)])
                    
                    print(f"   📚 RAG context created: {len(rag_context)} chars")
                    
                    # Now use LLM to format the RAG content
                    if st.session_state.get('llm_initialized', False):
                        llm_client = get_llm_client()
                        print(f"   🤖 Calling LLM with RAG context")
                        
                        # Create prompt with RAG context
                        llm_prompt = f"""Based on the following medical information, answer the question: "{query}"

Medical Information:
{rag_context}

Please provide a clear, concise answer:"""
                        
                        answer = llm_client.generate(llm_prompt)
                        print(f"   ✅ LLM generated answer from RAG: {len(answer)} chars")
                    else:
                        # LLM not ready, use RAG directly
                        print(f"   ⚠️ LLM not ready, using RAG text directly")
                        answer = f"I found this information about your question:\n\n{rag_context}"
                
            except Exception as e:
                print(f"   ❌ RAG error: {e}")
        
        # STEP 2: If no RAG results or RAG failed, try LLM directly
        if not answer and st.session_state.get('llm_initialized', False):
            print(f"   🤖 No RAG results, trying LLM directly")
            llm_client = get_llm_client()
            answer = llm_client.generate(query)
            print(f"   ✅ LLM generated direct answer: {len(answer)} chars")
        
        # STEP 3: If still no answer, provide fallback
        if not answer:
            print(f"   ⚠️ No answer generated, using fallback")
            answer = "I'm here to help with medical questions! Try asking about cancer, diabetes, or intermittent fasting."
        
        print(f"   📤 Returning answer: {len(answer)} chars, sources: {len(sources)}")
        print("="*50)
        
        return {
            'answer': answer,
            'sources': sources,
            'used_rag': used_rag
        }
        
    except Exception as e:
        print(f"❌ ERROR in generate_response: {e}")
        import traceback
        traceback.print_exc()
        return {
            'answer': "I'm here to help with medical questions! Try asking about cancer, diabetes, or intermittent fasting.",
            'sources': [],
            'used_rag': False
        }
    
def create_new_conversation():
    """Create a new conversation"""
    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}"
    st.session_state.current_conversation_id = conversation_id
    st.session_state.messages = []
    
    # Initialize empty conversation in history
    if st.session_state.current_user:
        save_conversation(st.session_state.current_user, conversation_id, [])
    
    return conversation_id

def save_current_conversation():
    """Save current conversation"""
    if st.session_state.current_user and st.session_state.current_conversation_id and st.session_state.messages:
        return save_conversation(
            st.session_state.current_user,
            st.session_state.current_conversation_id,
            st.session_state.messages
        )
    return None

def load_specific_conversation(conversation_id):
    """Load a specific conversation by ID"""
    if st.session_state.current_user:
        conversation_data = load_conversation(st.session_state.current_user, conversation_id)
        if conversation_data:
            st.session_state.current_conversation_id = conversation_id
            st.session_state.messages = conversation_data['messages']
            return True
    return False

# ============================================
# AUTHENTICATION FUNCTIONS
# ============================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    if username in st.session_state.users:
        if st.session_state.users[username]['password_hash'] == hash_password(password):
            st.session_state.current_user = username
            st.session_state.conversations = get_user_conversations(username)
            return True
    return False

def register(username, email, password, full_name=""):
    """Register a new user"""
    if username in st.session_state.users:
        return False, "Username already exists"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    st.session_state.users[username] = {
        'password_hash': hash_password(password),
        'email': email,
        'full_name': full_name,
        'created_at': datetime.now().isoformat()
    }
    
    return True, "Registration successful!"

# ============================================
# AUTHENTICATION PAGE
# ============================================

def render_auth_page():
    """Render authentication page with tabs"""
    # Background styling
    st.markdown("""
    <div style='
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        z-index: -1;
    '></div>
    """, unsafe_allow_html=True)
    
    # Main container
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Title
            st.markdown('<h1 class="main-title">🏥 MediAssist AI</h1>', unsafe_allow_html=True)
            st.markdown('<p class="tagline">Your Intelligent Medical Research Assistant</p>', unsafe_allow_html=True)
            
            # Auth container
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            # Tabs for Login/Register
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
            
            with tab1:
                st.markdown("### Welcome Back")
                
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🚀 Login", use_container_width=True):
                        if not username or not password:
                            st.error("Please enter both username and password")
                        elif login(username, password):
                            with st.spinner("Initializing AI systems..."):
                                initialize_systems()
                            st.success("✅ Welcome back!")
                            create_new_conversation()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                
                with col_btn2:
                    if st.button("📝 Register", use_container_width=True, type="secondary"):
                        # Switch to register tab
                        st.rerun()
                
                st.markdown("---")
                st.info("**Demo account:** `admin` / `admin123`")
            
            with tab2:
                st.markdown("### Create Account")
                
                col_name1, col_name2 = st.columns(2)
                with col_name1:
                    first_name = st.text_input("First Name", key="reg_first")
                with col_name2:
                    last_name = st.text_input("Last Name", key="reg_last")
                
                full_name = f"{first_name} {last_name}".strip()
                username = st.text_input("Choose Username", key="reg_user")
                email = st.text_input("Email Address", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
                
                if st.button("📝 Register Account", use_container_width=True):
                    if not username or not email or not password:
                        st.error("Please fill in all required fields")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = register(username, email, password, full_name)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("Please login with your new credentials")
                        else:
                            st.error(f"❌ {message}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Features section
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_feat1, col_feat2, col_feat3 = st.columns(3)
        
        features = [
            ("🤖", "AI Medical Assistant", "Advanced Gemini AI for intelligent medical responses"),
            ("🔍", "RAG Search System", "Search medical database with source citations"),
            ("📚", "Knowledge Base", "Comprehensive medical research database"),
            ("💬", "Smart Chat", "Natural conversations with context awareness"),
            ("📁", "PDF Analysis", "Upload and analyze medical documents"),
            ("⚡", "Real-time Processing", "Instant responses with live analysis")
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            col = [col_feat1, col_feat2, col_feat3][i % 3]
            with col:
                st.markdown(f"""
                <div class='feature-card'>
                    <h3 style='color: #3b82f6; margin: 0 0 10px 0;'>{icon} {title}</h3>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.95rem;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #64748b; padding: 2rem;'>
            <p>© 2024 MediAssist AI | Medical Research Assistant</p>
            <p><small>For educational purposes only. Consult healthcare professionals for medical advice.</small></p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# CHAT INTERFACE
# ============================================

def render_conversation_history():
    """Render conversation history in sidebar"""
    st.markdown("### 💬 Conversation History")
    
    # Get current user's conversations
    conversations = get_user_conversations(st.session_state.current_user)
    
    if not conversations:
        st.info("No previous conversations")
        return
    
    # Sort conversations by last updated (newest first)
    sorted_conversations = sorted(
        conversations.values(),
        key=lambda x: x['updated_at'],
        reverse=True
    )
    
    # Display conversations
    for conv in sorted_conversations:
        is_active = conv['id'] == st.session_state.current_conversation_id
        is_editing = st.session_state.editing_conversation == conv['id']
        
        # Format date
        try:
            date_obj = datetime.fromisoformat(conv['updated_at'].replace('Z', '+00:00'))
            date_str = date_obj.strftime("%b %d, %I:%M %p")
        except:
            date_str = "Recently"
        
        if is_editing:
            # Edit mode
            col1, col2 = st.columns([3, 1])
            with col1:
                new_title = st.text_input(
                    "Edit title",
                    value=conv['title'],
                    key=f"edit_{conv['id']}",
                    label_visibility="collapsed"
                )
                st.session_state.edit_conversation_title = new_title
            
            with col2:
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾", key=f"save_{conv['id']}_btn", help="Save", use_container_width=True):
                        if st.session_state.edit_conversation_title.strip():
                            if update_conversation_title(st.session_state.current_user, conv['id'], 
                                                        st.session_state.edit_conversation_title.strip()):
                                st.session_state.editing_conversation = None
                                st.session_state.edit_conversation_title = ""
                                st.success("Title updated!")
                                time.sleep(1)
                                st.rerun()
                
                with col_cancel:
                    if st.button("✖", key=f"cancel_{conv['id']}_btn", help="Cancel", use_container_width=True):
                        st.session_state.editing_conversation = None
                        st.session_state.edit_conversation_title = ""
                        st.rerun()
        
        else:
            # Display mode
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                button_label = f"{conv['title']} - {date_str}"
                
                # Load conversation button
                if st.button(
                    button_label,
                    key=f"conv_{conv['id']}_load",
                    use_container_width=True,
                    type="secondary" if not is_active else "primary"
                ):
                    if not is_active:
                        # Save current conversation before switching
                        save_current_conversation()
                        # Load selected conversation
                        load_specific_conversation(conv['id'])
                        st.rerun()
            
            with col2:
                # Edit button
                if st.button("✏️", key=f"edit_{conv['id']}_btn", help="Edit title", use_container_width=True):
                    st.session_state.editing_conversation = conv['id']
                    st.session_state.edit_conversation_title = conv['title']
                    st.rerun()
            
            with col3:
                # Delete button
                if st.button("🗑️", key=f"del_{conv['id']}_btn", help="Delete", use_container_width=True):
                    if delete_conversation(st.session_state.current_user, conv['id']):
                        if conv['id'] == st.session_state.current_conversation_id:
                            create_new_conversation()
                        st.success("Conversation deleted")
                        time.sleep(1)
                        st.rerun()

def render_chat_interface():
    """Render chat interface"""
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        user_info = st.session_state.users.get(st.session_state.current_user, {})
        full_name = user_info.get('full_name', st.session_state.current_user)
        st.markdown(f"# 🏥 MediAssist AI")
        st.markdown(f"**Welcome, {full_name}!**")
    
    with col2:
        conversations = get_user_conversations(st.session_state.current_user)
        conv_count = len(conversations)
        st.metric("Conversations", conv_count)
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            save_current_conversation()
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user}")
        st.markdown(f"*Medical Research Assistant*")
        st.markdown("---")
        
        # Status
        st.markdown("#### ⚙️ System Status")
        col_status1, col_status2 = st.columns(2)
        with col_status1:
            if st.session_state.llm_initialized:
                st.success("🤖 AI")
            else:
                st.error("🤖 AI")
        with col_status2:
            if st.session_state.rag_initialized:
                st.success("🗄️ KB")
            else:
                st.error("🗄️ KB")
        
        # New conversation
        if st.button("💬 New Conversation", use_container_width=True, type="primary"):
            save_current_conversation()
            create_new_conversation()
            st.rerun()
        
        # Conversation History
        st.markdown("---")
        render_conversation_history()
        
        # PDF Upload
        st.markdown("---")
        st.markdown("#### 📁 Upload Medical PDF")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            label_visibility="collapsed",
            help="Upload medical research papers or documents"
        )
        
        if uploaded_file and st.session_state.rag_initialized:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    texts = []
                    
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text.strip():
                            texts.append(text.strip())
                    
                    if texts:
                        # Combine text (limit to first 5 pages for performance)
                        combined_text = "\n\n".join(texts[:5])
                        
                        # Add to RAG pipeline
                        rag_pipeline.add_documents(
                            documents=[combined_text],
                            metadatas=[{
                                "source": uploaded_file.name,
                                "type": "pdf",
                                "pages": len(texts),
                                "uploaded_at": datetime.now().isoformat()
                            }]
                        )
                        
                        st.success(f"✅ Added: {uploaded_file.name}")
                        
                        # Generate a quick summary
                        summary_prompt = f"Summarize this medical document in 2-3 bullet points:\n\n{combined_text[:1500]}"
                        summary = llm_client.generate(summary_prompt)
                        st.info(f"**Quick Summary:**\n\n{summary}")
                        
                    else:
                        st.warning("No text could be extracted from the PDF")
                        
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
        
        # Conversation Stats
        st.markdown("---")
        conversations = get_user_conversations(st.session_state.current_user)
        if conversations:
            total_messages = sum(conv.get('message_count', 0) for conv in conversations.values())
            st.markdown(f"**📊 Statistics:**")
            st.markdown(f"- Conversations: {len(conversations)}")
            st.markdown(f"- Total Messages: {total_messages}")
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            save_current_conversation()
            st.session_state.current_user = None
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.editing_conversation = None
            st.session_state.edit_conversation_title = ""
            st.rerun()
    
    # Chat area
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("""
            ## Welcome to MediAssist AI! 👋
            
            I'm your intelligent medical research assistant.
            
            **🎯 How I can help you:**
            - Answer medical questions with research-backed information
            - Analyze medical concepts with source citations
            - Process uploaded medical PDFs
            - Summarize our conversations
            
            **🔍 Try asking me:**
            - "What are the benefits of intermittent fasting?"
            - "How does fasting affect insulin sensitivity?"
            - "Can you summarize what we discussed?"
            
            ⚠️ **Important:** I provide educational information only. Always consult healthcare professionals.
            """)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message.get("sources") and len(message["sources"]) > 0:
                with st.expander("📚 View Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**{source['metadata'].get('source', 'Source')}**")
                        st.markdown(f"> {source['text'][:200]}...")
                        st.markdown(f"*Relevance: {source['similarity']:.2%}*")
                        st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("Ask a medical question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = generate_response(prompt)
                
                # Display response
                st.markdown(response['answer'])
                
                # Show RAG indicator if sources were used
                if response['used_rag'] and response['sources']:
                    st.markdown('<div class="rag-indicator">🔍 Research-Backed Answer</div>', unsafe_allow_html=True)
                    
                    # Show sources in expander
                    with st.expander("📚 View Research Sources"):
                        for source in response['sources']:
                            st.markdown(f"**{source['metadata'].get('source', 'Medical Research')}**")
                            st.markdown(f"> {source['text']}")
                            st.markdown(f"*Relevance: {source['similarity']:.2%}*")
                            st.markdown("---")
        
        # Save assistant message with sources
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response['answer'],
            "sources": response['sources'] if response['used_rag'] else []
        })
        
        # Save conversation
        save_current_conversation()

# ============================================
# MAIN APP
# ============================================

def main():
    """Main application"""
    init_session_state()
    
    # Check if user is logged in
    if st.session_state.current_user is None:
        render_auth_page()
    else:
        # Check if systems need initialization
        if not st.session_state.llm_initialized or not st.session_state.rag_initialized:
            # Show loading screen
            st.markdown("""
            <div style='text-align: center; padding: 5rem;'>
                <h2>🏥 MediAssist AI</h2>
                <p>Initializing systems...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize systems
            if not initialize_systems():
                st.error("Failed to initialize systems. Please check your API key.")
                if st.button("Logout"):
                    st.session_state.current_user = None
                    st.rerun()
                return
            
            # Rerun to show chat interface
            st.rerun()
        else:
            # Systems are initialized, show chat interface
            # If no current conversation, create one
            if not st.session_state.current_conversation_id:
                create_new_conversation()
            
            render_chat_interface()

if __name__ == "__main__":
    main()
