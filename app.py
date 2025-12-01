import streamlit as st
import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import PyPDF2
from dotenv import load_dotenv
import time

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

# Try to load from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️ .env file not found at: {env_path}")
    load_dotenv()

# Get API key - try multiple names
API_KEY = None
possible_keys = ['GEMINI_API_KEY', 'GOOGLE_API_KEY', 'API_KEY']

for key_name in possible_keys:
    key_value = os.getenv(key_name)
    if key_value and len(key_value) > 30:
        API_KEY = key_value
        print(f"✅ Found API key: {key_name}")
        break

# Fallback to your key if not found
if not API_KEY:
    print("⚠️ Using provided API key")
    API_KEY = "YOUR_GEMINI_API_KEY"

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
    /* Dark theme - Remove all white backgrounds */
    .stApp {
        background: #0f172a;
        color: #e2e8f0;
    }
    
    /* Remove white backgrounds from all Streamlit elements */
    .stApp > header {
        background-color: #0f172a;
    }
    
    .stApp > div:first-child {
        background-color: #0f172a;
    }
    
    /* Main container background */
    .main .block-container {
        background: #0f172a;
        padding-top: 2rem;
    }
    
    /* Login/Register containers */
    .auth-container {
        background: #1e293b;
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #334155;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin: 2rem auto;
        max-width: 450px;
        backdrop-filter: blur(10px);
    }
    
    /* Titles */
    .main-title {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    .tagline {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
    }
    
    /* Secondary buttons */
    .secondary-btn {
        background: transparent !important;
        border: 2px solid #3b82f6 !important;
        color: #3b82f6 !important;
    }
    
    .secondary-btn:hover {
        background: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Conversation history buttons */
    .conv-history-btn {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        text-align: left !important;
        padding: 0.8rem !important;
        margin: 0.2rem 0 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .conv-history-btn:hover {
        background: #2d3748 !important;
        border-color: #3b82f6 !important;
        transform: translateX(5px) !important;
    }
    
    .active-conv {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        border-color: #3b82f6 !important;
        color: white !important;
    }
    
    /* Edit mode input */
    .edit-conv-input {
        background: #0f172a !important;
        border: 2px solid #3b82f6 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        margin: 0.2rem 0 !important;
        width: 100% !important;
    }
    
    /* Small action buttons */
    .action-btn-small {
        padding: 0.3rem 0.8rem !important;
        font-size: 0.8rem !important;
        margin: 0.1rem !important;
        min-height: auto !important;
    }
    
    .edit-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    }
    
    .save-btn {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    }
    
    .cancel-btn {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%) !important;
    }
    
    .delete-btn {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    }
    
    /* Small action buttons styling */
    div[data-testid="column"] button {
        transition: all 0.2s ease !important;
    }
    
    /* Edit button styling */
    div[data-testid="column"] button[kind="secondary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Save button styling */
    div[data-testid="column"] button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Delete button styling */
    div[data-testid="column"] button[title="Delete"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Cancel button styling */
    div[data-testid="column"] button[title="Cancel"] {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextInput > div > div > textarea {
        background: #0f172a !important;
        border: 2px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 0.8rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextInput > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid #334155;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
        transition: 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Chat styling */
    div[data-testid="stChatMessage"] {
        border-radius: 15px;
        margin-bottom: 1rem;
        max-width: 85%;
        animation: slideIn 0.3s ease-out;
        border: 1px solid #334155;
        background: #1e293b !important;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* User message */
    div[data-testid="stChatMessage"][aria-label*="user"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        color: white;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 5px;
    }
    
    /* Assistant message */
    div[data-testid="stChatMessage"][aria-label*="assistant"] {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        margin-right: auto;
        margin-left: 0;
        border-bottom-left-radius: 5px;
        border-left: 4px solid #3b82f6;
    }
    
    /* RAG indicator */
    .rag-indicator {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        margin: 10px 0;
        display: inline-block;
        font-weight: 600;
        animation: pulse 2s infinite;
        border: none;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] > div {
        background: #0f172a !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove all white backgrounds from tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: #1e293b !important;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        color: #94a3b8 !important;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
        color: #e2e8f0 !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: #1e293b !important;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #334155;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
    }
    
    /* Chat input */
    .stChatInputContainer {
        border-top: 1px solid #334155;
        background: #0f172a !important;
        padding-top: 1rem;
    }
    
    /* Success/error messages */
    .stAlert {
        border-radius: 10px;
        border: 1px solid;
        background: #1e293b !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3b82f6;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2563eb;
    }
    
    /* Remove white from all Streamlit containers */
    .element-container, .st-emotion-cache-1jicfl7 {
        background: transparent !important;
    }
    
    /* Fix file uploader */
    .st-emotion-cache-1gulkj5 {
        background: #0f172a !important;
        border: 2px solid #334155 !important;
        color: #e2e8f0 !important;
    }
    
    /* Fix selectboxes */
    .stSelectbox > div > div {
        background: #0f172a !important;
        border: 2px solid #334155 !important;
        color: #e2e8f0 !important;
    }
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
                # Extract first meaningful user message for title
                content = msg['content'].strip()
                if len(content) > 5:  # Avoid very short messages
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
        'vector_db_initialized': False,
        'llm_initialized': False,
        'embedding_model': None,
        'chroma_client': None,
        'chroma_collection': None,
        'llm_model': None,
        'editing_conversation': None,  # Track which conversation is being edited
        'edit_conversation_title': ""  # Store edit title
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize current conversation messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def initialize_llm():
    """Initialize Gemini LLM with gemini-flash-latest"""
    try:
        if not API_KEY:
            st.error("❌ No API key available")
            return None
        
        genai.configure(api_key=API_KEY)
        
        # Try gemini-flash-latest first
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Hello")
            
            if response.text:
                st.session_state.llm_model = model
                st.session_state.llm_initialized = True
                st.success("✅ Connected to Gemini Flash Latest")
                return model
            else:
                st.error("❌ No response from model")
                return None
        except Exception as e:
            print(f"gemini-flash-latest failed: {e}")
            
            # Try other models as fallback
            models_to_try = [
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest',
                'gemini-pro'
            ]
            
            for model_name in models_to_try:
                try:
                    print(f"Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Test")
                    if response.text:
                        st.session_state.llm_model = model
                        st.session_state.llm_initialized = True
                        st.success(f"✅ Connected to {model_name}")
                        return model
                except Exception as e2:
                    print(f"Failed with {model_name}: {e2}")
                    continue
        
        st.error("❌ Could not connect to any Gemini model")
        return None
                    
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            st.error("❌ Invalid API Key. Please check your Google AI Studio API key.")
        elif "quota" in error_msg.lower():
            st.error("⚠️ API quota exceeded. Please try again later.")
        else:
            st.error(f"❌ Connection error: {error_msg}")
        return None

def initialize_vector_db():
    """Initialize vector database"""
    try:
        chroma_path = "chroma_pubmed"
        if not os.path.exists(chroma_path):
            os.makedirs(chroma_path, exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_or_create_collection(
            name="medical_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        st.session_state.chroma_client = client
        st.session_state.chroma_collection = collection
        st.session_state.embedding_model = embedding_model
        st.session_state.vector_db_initialized = True
        
        # Add comprehensive sample data
        if collection.count() == 0:
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
                    "text": "During fasting periods, the body switches from using glucose as its primary fuel source to burning stored fat, a process called metabolic switching.",
                    "metadata": {"source": "Cell Metabolism", "topic": "Metabolism", "type": "research"}
                },
                {
                    "text": "Studies suggest intermittent fasting may help with weight loss by reducing calorie intake and increasing fat oxidation during fasting periods.",
                    "metadata": {"source": "Obesity Research", "topic": "Weight Loss", "type": "research"}
                },
                {
                    "text": "Fasting triggers autophagy, the body's cellular cleanup process, which may help remove damaged cells and support cellular repair.",
                    "metadata": {"source": "Nature Medicine", "topic": "Cellular Health", "type": "research"}
                }
            ]
            
            texts = [item["text"] for item in sample_data]
            metadatas = [item["metadata"] for item in sample_data]
            embeddings = embedding_model.encode(texts).tolist()
            
            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=[f"sample_{i}" for i in range(len(texts))]
            )
        
        return True
    except Exception as e:
        st.error(f"❌ Vector database error: {str(e)}")
        return False

# ============================================
# CORE FUNCTIONS
# ============================================

def search_vector_db(query: str, top_k: int = 3):
    """Search in vector database"""
    if not st.session_state.vector_db_initialized:
        return []
    
    try:
        query_embedding = st.session_state.embedding_model.encode(query).tolist()
        results = st.session_state.chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if results['documents'] and results['documents'][0]:
            formatted_results = []
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted_results.append({
                    'text': doc,
                    'metadata': meta or {},
                    'similarity': float(1 - dist),
                    'rank': i + 1
                })
            return formatted_results
        return []
    except Exception as e:
        print(f"Vector search error: {e}")
        return []

def generate_response(query: str):
    """Generate AI response with robust error handling"""
    try:
        # Handle greetings
        greetings = ['hi', 'hello', 'hey', 'how are you', 'good morning', 'good afternoon', 'good evening']
        clean_query = query.lower().strip()
        
        if clean_query in greetings:
            return {
                'answer': "Hello! 👋 I'm MediAssist AI, your intelligent medical research assistant. I can help answer questions about intermittent fasting, metabolic health, diabetes, nutrition, and general medical topics. What would you like to know today?",
                'sources': [],
                'used_rag': False
            }
        
        if 'how are you' in clean_query:
            return {
                'answer': "I'm doing great, thank you for asking! As an AI, I'm always ready to help with medical questions. I'm excited to assist you with your health-related queries today! 😊",
                'sources': [],
                'used_rag': False
            }
        
        # Handle requests for conversation summary
        summary_keywords = ['summary', 'summarize', 'summarise', 'recap', 'overview', 'what did we discuss', 'what was our conversation']
        if any(keyword in clean_query for keyword in summary_keywords):
            # Get conversation messages
            if st.session_state.messages:
                # Extract conversation text
                conversation_text = ""
                for msg in st.session_state.messages:
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    conversation_text += f"{role}: {msg['content']}\n\n"
                
                prompt = f"""Please provide a concise summary of this conversation between a user and MediAssist AI:

CONVERSATION:
{conversation_text}

Please provide:
1. A brief overview of what was discussed
2. Key topics covered
3. Any important conclusions or advice given
4. Main questions asked by the user

Keep the summary clear and concise (3-5 bullet points)."""
                
                try:
                    response = st.session_state.llm_model.generate_content(prompt)
                    if response and response.text:
                        return {
                            'answer': f"Here's a summary of our conversation:\n\n{response.text}",
                            'sources': [],
                            'used_rag': False
                        }
                except Exception as e:
                    print(f"Summary generation error: {e}")
        
        # Handle requests for document summaries (when user has uploaded a PDF)
        if 'pdf' in clean_query or 'document' in clean_query or 'file' in clean_query:
            # Check if this is about an uploaded document or just asking about PDFs in general
            if 'upload' in clean_query or 'attached' in clean_query or 'provide' in clean_query:
                # User is asking about uploading a document
                return {
                    'answer': "You can upload medical PDF documents using the 'Upload Medical PDF' section in the sidebar. Once uploaded, I can analyze the content and help you with questions about it. Please use the sidebar uploader to add your document.",
                    'sources': [],
                    'used_rag': False
                }
        
        # Check if medical question
        medical_keywords = [
            'fasting', 'diabet', 'metabol', 'health', 'medical', 'diet', 'weight',
            'insulin', 'glucose', 'blood', 'pressure', 'cholesterol', 'heart',
            'exercise', 'nutrition', 'calorie', 'metabolism', 'treatment',
            'disease', 'symptom', 'patient', 'doctor', 'hospital', 'medicine',
            'drug', 'therapy', 'surgery', 'clinical', 'research', 'study',
            'obesity', 'weight loss', 'fat', 'protein', 'carb', 'vitamin',
            'mineral', 'supplement', 'sleep', 'stress', 'anxiety', 'depression',
            'pain', 'fever', 'cough', 'headache', 'allergy', 'immune'
        ]
        
        is_medical = any(kw in clean_query for kw in medical_keywords)
        
        # For medical questions, try RAG
        if is_medical and st.session_state.vector_db_initialized:
            results = search_vector_db(query)
            
            if results and len(results) > 0:
                # Build context
                context_parts = []
                for result in results:
                    source_name = result['metadata'].get('source', 'Medical Research')
                    context_parts.append(f"[{source_name}]: {result['text']}")
                
                context = "\n\n".join(context_parts)
                
                prompt = f"""You are MediAssist AI, a professional medical research assistant. Based on the following verified medical information, answer the user's question accurately and helpfully.

VERIFIED MEDICAL INFORMATION:
{context}

USER QUESTION: {query}

IMPORTANT INSTRUCTIONS:
1. Provide a clear, accurate answer based SOLELY on the medical information above
2. If the information doesn't fully cover the question, acknowledge this limitation
3. Use professional but accessible medical language
4. Include necessary disclaimers about consulting healthcare professionals
5. When referring to specific information, mention the source
6. Structure your answer with clear paragraphs
7. End with a summary of key points

ANSWER:"""
                
                try:
                    response = st.session_state.llm_model.generate_content(prompt)
                    if response and response.text:
                        return {
                            'answer': response.text,
                            'sources': results,
                            'used_rag': True
                        }
                except Exception as e:
                    print(f"RAG generation error: {e}")
        
        # General response for non-medical or if RAG fails
        try:
            prompt = f"""You are MediAssist AI, a helpful and knowledgeable assistant. Answer the following question in a clear, informative, and friendly manner.

QUESTION: {query}

Please provide a thoughtful and helpful response."""
            
            response = st.session_state.llm_model.generate_content(prompt)
            if response and response.text:
                return {
                    'answer': response.text,
                    'sources': [],
                    'used_rag': False
                }
        except Exception as e:
            print(f"General generation error: {e}")
    
    except Exception as e:
        print(f"Overall generation error: {e}")
    
    # If everything fails, provide a friendly fallback
    return {
        'answer': "I apologize, but I'm having trouble generating a response right now. This could be due to a temporary issue. Please try rephrasing your question or try again in a moment. For medical emergencies, please consult a healthcare professional immediately.",
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
            # Load user conversations
            st.session_state.conversations = get_user_conversations(username)
            return True
    return False

def register(username, email, password, full_name=""):
    """Register a new user"""
    if username in st.session_state.users:
        return False, "Username already exists"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Create new user
    st.session_state.users[username] = {
        'password_hash': hash_password(password),
        'email': email,
        'full_name': full_name,
        'created_at': datetime.now().isoformat()
    }
    
    return True, "Registration successful!"

# ============================================
# AUTHENTICATION PAGES
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
                                initialize_llm()
                                initialize_vector_db()
                            st.success("✅ Welcome back!")
                            create_new_conversation()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                
                with col_btn2:
                    # Quick register button instead of admin login
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
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close auth container
        
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
                    # Use a unique key for save button
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
                    # Use a unique key for cancel button
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
        
        # Get current conversation info
        current_conv = None
        if st.session_state.current_conversation_id and st.session_state.current_user in conversations:
            current_conv = conversations.get(st.session_state.current_conversation_id)
        
        if current_conv:
            st.metric("Messages", current_conv.get('message_count', 0))
        else:
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
            if st.session_state.vector_db_initialized:
                st.success("🗄️ DB")
            else:
                st.error("🗄️ DB")
        
        # New conversation
        if st.button("💬 New Conversation", use_container_width=True, type="primary"):
            # Save current conversation first
            save_current_conversation()
            # Create new one
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
        
        if uploaded_file and st.session_state.vector_db_initialized:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    texts = []
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text.strip():
                            texts.append(text)
                    
                    if texts:
                        # Combine first 3 pages
                        combined_text = "\n\n".join(texts[:3])
                        
                        # Add to vector DB
                        embedding = st.session_state.embedding_model.encode(combined_text).tolist()
                        st.session_state.chroma_collection.add(
                            documents=[combined_text],
                            embeddings=[embedding],
                            metadatas=[{
                                "source": uploaded_file.name,
                                "type": "pdf",
                                "pages": len(texts),
                                "uploaded_at": datetime.now().isoformat()
                            }],
                            ids=[f"pdf_{datetime.now().timestamp()}"]
                        )
                        st.success(f"✅ Added: {uploaded_file.name}")
                        
                        # Auto-generate a summary
                        with st.spinner("Generating summary..."):
                            prompt = f"""Please provide a concise summary of this medical document:

DOCUMENT CONTENT (first 3 pages):
{combined_text[:2000]}

Please provide:
1. Main topic/theme
2. Key findings or points
3. Relevance to medical research
4. Any important data or statistics mentioned

Keep the summary clear and concise (3-4 bullet points)."""
                            
                            try:
                                response = st.session_state.llm_model.generate_content(prompt)
                                if response and response.text:
                                    st.info(f"**Document Summary:**\n\n{response.text}")
                            except:
                                pass
                    else:
                        st.warning("No text could be extracted")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
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
        # Welcome message
        with st.chat_message("assistant"):
            st.markdown("""
            ## Welcome to MediAssist AI! 👋
            
            I'm your intelligent medical research assistant, powered by advanced AI and a comprehensive medical knowledge base.
            
            **🎯 How I can help you:**
            - Answer questions about **intermittent fasting** and **metabolism**
            - Provide research-backed information on **diabetes** and **nutrition**
            - Analyze **medical concepts** with source citations
            - Help with **general health** and **wellness** questions
            - **Summarize our conversations** - just ask "Can you summarize our conversation?"
            
            **🔍 Try asking me:**
            - "What are the benefits of intermittent fasting?"
            - "How does fasting affect insulin sensitivity?"
            - "Can you summarize what we discussed?"
            - "Is fasting safe for type 2 diabetes?"
            
            ⚠️ **Important Note:** I provide educational information only. Always consult healthcare professionals for medical advice.
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
                        st.markdown(f"*Similarity: {source['similarity']:.2%}*")
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

def generate_response(query: str):
    """Generate AI response with robust error handling"""
    try:
        # Handle greetings
        greetings = ['hi', 'hello', 'hey', 'how are you', 'good morning', 'good afternoon', 'good evening']
        clean_query = query.lower().strip()
        
        if clean_query in greetings:
            return {
                'answer': "Hello! 👋 I'm MediAssist AI, your intelligent medical research assistant. I can help answer questions about intermittent fasting, metabolic health, diabetes, nutrition, and general medical topics. What would you like to know today?",
                'sources': [],
                'used_rag': False
            }
        
        if 'how are you' in clean_query:
            return {
                'answer': "I'm doing great, thank you for asking! As an AI, I'm always ready to help with medical questions. I'm excited to assist you with your health-related queries today! 😊",
                'sources': [],
                'used_rag': False
            }
        
        # Handle requests for conversation summary
        summary_keywords = ['summary', 'summarize', 'summarise', 'recap', 'overview', 'what did we discuss', 'what was our conversation']
        if any(keyword in clean_query for keyword in summary_keywords):
            # Check if it's about uploaded documents
            if 'document' in clean_query or 'pdf' in clean_query or 'file' in clean_query or 'upload' in clean_query:
                # User is asking about uploaded document summary
                if st.session_state.vector_db_initialized:
                    # Search for PDFs in the vector database
                    try:
                        results = st.session_state.chroma_collection.get(
                            where={"type": "pdf"},
                            include=["documents", "metadatas"]
                        )
                        
                        if results and results['documents']:
                            # Combine all PDF content
                            all_pdf_content = "\n\n".join(results['documents'])
                            pdf_sources = results['metadatas']
                            
                            prompt = f"""Please analyze the following uploaded medical document(s) and provide a comprehensive summary:

UPLOADED DOCUMENT(S) CONTENT:
{all_pdf_content[:5000]}  # Limit to 5000 characters

USER REQUEST: {query}

Please provide:
1. Overall topic and main theme
2. Key findings, data, or statistics mentioned
3. Important conclusions or recommendations
4. Relevance to medical/healthcare context
5. Any limitations or areas requiring further research

Provide a clear, structured summary that helps the user understand what the document contains."""

                            try:
                                response = st.session_state.llm_model.generate_content(prompt)
                                if response and response.text:
                                    # Format sources for display
                                    formatted_sources = []
                                    for i, (doc, meta) in enumerate(zip(results['documents'], pdf_sources)):
                                        formatted_sources.append({
                                            'text': doc[:300] + ("..." if len(doc) > 300 else ""),
                                            'metadata': meta or {},
                                            'similarity': 1.0,
                                            'rank': i + 1
                                        })
                                    
                                    return {
                                        'answer': f"Based on the document(s) you've uploaded, here's a summary:\n\n{response.text}",
                                        'sources': formatted_sources,
                                        'used_rag': True
                                    }
                            except Exception as e:
                                print(f"PDF summary generation error: {e}")
                    except Exception as e:
                        print(f"PDF search error: {e}")
                
                # If no PDFs found or error occurred
                return {
                    'answer': "I don't see any uploaded documents in the database yet. Please use the 'Upload Medical PDF' section in the sidebar to upload your medical document first, then ask me about it.",
                    'sources': [],
                    'used_rag': False
                }
            else:
                # It's about conversation summary
                if st.session_state.messages:
                    # Extract conversation text
                    conversation_text = ""
                    for msg in st.session_state.messages:
                        role = "User" if msg['role'] == 'user' else "Assistant"
                        conversation_text += f"{role}: {msg['content']}\n\n"
                    
                    prompt = f"""Please provide a concise summary of this conversation between a user and MediAssist AI:

CONVERSATION:
{conversation_text}

Please provide:
1. A brief overview of what was discussed
2. Key topics covered
3. Any important conclusions or advice given
4. Main questions asked by the user

Keep the summary clear and concise (3-5 bullet points)."""
                    
                    try:
                        response = st.session_state.llm_model.generate_content(prompt)
                        if response and response.text:
                            return {
                                'answer': f"Here's a summary of our conversation:\n\n{response.text}",
                                'sources': [],
                                'used_rag': False
                            }
                    except Exception as e:
                        print(f"Summary generation error: {e}")
        
        # Handle requests about uploaded documents
        document_keywords = ['document', 'pdf', 'file', 'uploaded', 'attached']
        if any(keyword in clean_query for keyword in document_keywords):
            # Check for specific document questions
            if st.session_state.vector_db_initialized:
                try:
                    # Search in vector DB for PDF documents
                    results = st.session_state.chroma_collection.get(
                        where={"type": "pdf"},
                        include=["documents", "metadatas"]
                    )
                    
                    if results and results['documents']:
                        # User is asking about an uploaded document
                        # Search for relevant content in the PDF
                        search_results = search_vector_db(query, top_k=2)
                        
                        if search_results:
                            # Build context from PDF content
                            context_parts = []
                            for result in search_results:
                                source_name = result['metadata'].get('source', 'Uploaded Document')
                                context_parts.append(f"[From {source_name}]: {result['text']}")
                            
                            context = "\n\n".join(context_parts)
                            
                            prompt = f"""Based on the following content from the uploaded document(s), answer the user's question:

UPLOADED DOCUMENT CONTENT:
{context}

USER QUESTION: {query}

Please provide an accurate answer based on the document content. If the document doesn't contain the information needed, acknowledge this limitation."""

                            try:
                                response = st.session_state.llm_model.generate_content(prompt)
                                if response and response.text:
                                    return {
                                        'answer': response.text,
                                        'sources': search_results,
                                        'used_rag': True
                                    }
                            except Exception as e:
                                print(f"Document answer generation error: {e}")
                        
                        # If no specific search results but we have PDFs
                        all_pdf_content = "\n\n".join(results['documents'][:2])  # First 2 documents
                        prompt = f"""The user is asking about uploaded documents. Here is the content from uploaded PDF(s):

DOCUMENT CONTENT:
{all_pdf_content[:3000]}

USER QUESTION: {query}

Please provide a helpful response based on the document content. If you cannot find the specific information, explain what the documents do contain."""
                        
                        try:
                            response = st.session_state.llm_model.generate_content(prompt)
                            if response and response.text:
                                # Format sources for display
                                formatted_sources = []
                                for i, (doc, meta) in enumerate(zip(results['documents'][:2], results['metadatas'][:2])):
                                    formatted_sources.append({
                                        'text': doc[:300] + ("..." if len(doc) > 300 else ""),
                                        'metadata': meta or {},
                                        'similarity': 0.8,
                                        'rank': i + 1
                                    })
                                
                                return {
                                    'answer': response.text,
                                    'sources': formatted_sources,
                                    'used_rag': True
                                }
                        except Exception as e:
                            print(f"General document response error: {e}")
                    
                except Exception as e:
                    print(f"Document search error: {e}")
            
            # If no PDFs found or user is asking how to upload
            if 'upload' in clean_query or 'how to' in clean_query or 'where' in clean_query:
                return {
                    'answer': "You can upload medical PDF documents using the 'Upload Medical PDF' section in the sidebar. Once uploaded, I can analyze the content and help you with questions about it. Please use the sidebar uploader to add your document.",
                    'sources': [],
                    'used_rag': False
                }
        
        # Check if medical question
        medical_keywords = [
            'fasting', 'diabet', 'metabol', 'health', 'medical', 'diet', 'weight',
            'insulin', 'glucose', 'blood', 'pressure', 'cholesterol', 'heart',
            'exercise', 'nutrition', 'calorie', 'metabolism', 'treatment',
            'disease', 'symptom', 'patient', 'doctor', 'hospital', 'medicine',
            'drug', 'therapy', 'surgery', 'clinical', 'research', 'study',
            'obesity', 'weight loss', 'fat', 'protein', 'carb', 'vitamin',
            'mineral', 'supplement', 'sleep', 'stress', 'anxiety', 'depression',
            'pain', 'fever', 'cough', 'headache', 'allergy', 'immune'
        ]
        
        is_medical = any(kw in clean_query for kw in medical_keywords)
        
        # For medical questions, try RAG from both medical knowledge and uploaded PDFs
        if is_medical and st.session_state.vector_db_initialized:
            # First search in medical knowledge base
            results = search_vector_db(query)
            
            # Also check for PDFs that might be relevant
            pdf_context = ""
            pdf_sources = []
            try:
                pdf_results = st.session_state.chroma_collection.get(
                    where={"type": "pdf"},
                    include=["documents", "metadatas"]
                )
                if pdf_results and pdf_results['documents']:
                    # Search within PDFs for relevant content
                    pdf_search = search_vector_db(query)
                    if pdf_search:
                        pdf_context = "\n\nRELEVANT DOCUMENT CONTENT:\n" + "\n\n".join([f"[From {r['metadata'].get('source', 'Document')}]: {r['text']}" for r in pdf_search])
                        pdf_sources = pdf_search
            except:
                pass
            
            if results and len(results) > 0:
                # Build context
                context_parts = []
                for result in results:
                    source_name = result['metadata'].get('source', 'Medical Research')
                    context_parts.append(f"[{source_name}]: {result['text']}")
                
                context = "\n\n".join(context_parts)
                
                # Add PDF context if available
                if pdf_context:
                    context += "\n\n" + pdf_context
                
                prompt = f"""You are MediAssist AI, a professional medical research assistant. Based on the following verified medical information, answer the user's question accurately and helpfully.

VERIFIED MEDICAL INFORMATION:
{context}

USER QUESTION: {query}

IMPORTANT INSTRUCTIONS:
1. Provide a clear, accurate answer based SOLELY on the medical information above
2. If the information doesn't fully cover the question, acknowledge this limitation
3. Use professional but accessible medical language
4. Include necessary disclaimers about consulting healthcare professionals
5. When referring to specific information, mention the source
6. Structure your answer with clear paragraphs
7. End with a summary of key points

ANSWER:"""
                
                try:
                    response = st.session_state.llm_model.generate_content(prompt)
                    if response and response.text:
                        # Combine sources
                        all_sources = results + pdf_sources
                        return {
                            'answer': response.text,
                            'sources': all_sources,
                            'used_rag': True
                        }
                except Exception as e:
                    print(f"RAG generation error: {e}")
        
        # General response for non-medical or if RAG fails
        try:
            prompt = f"""You are MediAssist AI, a helpful and knowledgeable assistant. Answer the following question in a clear, informative, and friendly manner.

QUESTION: {query}

Please provide a thoughtful and helpful response."""
            
            response = st.session_state.llm_model.generate_content(prompt)
            if response and response.text:
                return {
                    'answer': response.text,
                    'sources': [],
                    'used_rag': False
                }
        except Exception as e:
            print(f"General generation error: {e}")
    
    except Exception as e:
        print(f"Overall generation error: {e}")
    
    # If everything fails, provide a friendly fallback
    return {
        'answer': "I apologize, but I'm having trouble generating a response right now. This could be due to a temporary issue. Please try rephrasing your question or try again in a moment. For medical emergencies, please consult a healthcare professional immediately.",
        'sources': [],
        'used_rag': False
    }

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
        # Ensure AI is initialized
        if not st.session_state.llm_initialized:
            with st.spinner("Initializing AI..."):
                if not initialize_llm():
                    st.error("Failed to initialize AI. Please check your API key and try again.")
                    if st.button("Logout"):
                        st.session_state.current_user = None
                        st.rerun()
                    return
        
        # Ensure vector DB is initialized
        if not st.session_state.vector_db_initialized:
            with st.spinner("Initializing database..."):
                if not initialize_vector_db():
                    st.error("Failed to initialize database.")
        
        render_chat_interface()

if __name__ == "__main__":
    main()