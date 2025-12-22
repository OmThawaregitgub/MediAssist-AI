import streamlit as st
import json
import uuid
import datetime
import sqlite3
import hashlib
import os
import bcrypt
from datetime import datetime as dt
from pathlib import Path

# Try to initialize the LLM with fallback
try:
    from llm import LargeLanguageModel
    llm = LargeLanguageModel()
    llm_available = True
except ImportError:
    llm_available = False
except Exception:
    llm_available = False

# Fallback medical knowledge base
FALLBACK_MEDICAL_KNOWLEDGE = {
    "cancer": {
        "what is": "Cancer is a disease caused by uncontrolled division of abnormal cells in the body.",
        "symptoms": "Common symptoms include unexplained weight loss, fatigue, lumps, persistent cough, unusual bleeding.",
        "treatment": "Treatments include surgery, chemotherapy, radiation therapy, immunotherapy, and targeted therapy.",
        "prevention": "Prevention strategies include not smoking, healthy diet, regular exercise, sun protection, vaccination.",
        "types": "Common types: breast cancer, lung cancer, prostate cancer, colorectal cancer, skin cancer.",
        "diagnosis": "Diagnosed through biopsies, imaging tests (CT, MRI), blood tests, and genetic testing."
    },
    "diabetes": {
        "what is": "Diabetes is a chronic condition where the body cannot properly process glucose due to insulin issues.",
        "symptoms": "Increased thirst, frequent urination, extreme hunger, unexplained weight loss, fatigue.",
        "types": "Type 1 (autoimmune), Type 2 (insulin resistance), Gestational (during pregnancy).",
        "treatment": "Medications (insulin, metformin), blood sugar monitoring, diet control, exercise.",
        "complications": "Heart disease, kidney damage, nerve damage, eye problems, foot issues.",
        "management": "Regular monitoring, balanced diet, exercise, medication adherence, regular check-ups."
    },
    "liver": {
        "what is": "The liver is a vital organ responsible for detoxification, protein synthesis, and digestion.",
        "diseases": "Common liver diseases: hepatitis, cirrhosis, fatty liver disease, liver cancer.",
        "symptoms": "Jaundice, abdominal pain, swelling, fatigue, nausea, dark urine.",
        "causes": "Alcohol abuse, viral infections, obesity, medications, autoimmune conditions.",
        "prevention": "Limit alcohol, maintain healthy weight, practice safe sex, get vaccinated for hepatitis.",
        "treatment": "Depends on condition: medications, lifestyle changes, surgery, or transplantation."
    },
    "obesity": {
        "what is": "Obesity is a condition of excessive body fat that increases health risks.",
        "causes": "Genetics, overeating, physical inactivity, medications, psychological factors.",
        "risks": "Heart disease, diabetes, high blood pressure, certain cancers, sleep apnea.",
        "treatment": "Diet modification, increased physical activity, behavior therapy, medications, surgery.",
        "prevention": "Balanced diet, regular exercise, portion control, limiting processed foods.",
        "management": "Calorie control, regular exercise, medical supervision, support groups."
    }
}

# Fallback response generator
def generate_fallback_response(prompt):
    """Generate a response when LLM is not available"""
    prompt_lower = prompt.lower()
    
    # Check for specific diseases
    for disease in ["cancer", "diabetes", "liver", "obesity", "fatty", "hepatitis", "tumor"]:
        if disease in prompt_lower:
            if disease in FALLBACK_MEDICAL_KNOWLEDGE:
                knowledge = FALLBACK_MEDICAL_KNOWLEDGE[disease]
                
                # Extract specific aspect being asked about
                for aspect, info in knowledge.items():
                    if aspect in prompt_lower:
                        return f"Regarding {disease.capitalize()} ({aspect.replace('_', ' ')}):\n\n{info}\n\n*Note: This is general information. Please consult a healthcare professional for personalized advice.*"
                
                # General information about the disease
                return f"General Information about {disease.capitalize()}:\n\n" + \
                       f"- What is it: {knowledge['what is']}\n" + \
                       f"- Common symptoms: {knowledge['symptoms']}\n" + \
                       f"- Treatment options: {knowledge['treatment']}\n" + \
                       f"- Prevention: {knowledge['prevention']}\n\n" + \
                       "*Note: This is general information. Please consult a healthcare professional for personalized advice.*"
    
    # General medical questions
    medical_keywords = ["symptom", "treatment", "cure", "medicine", "drug", "diagnos", "test", 
                       "prevent", "cause", "risk", "exercise", "diet", "food", "vitamin"]
    
    if any(keyword in prompt_lower for keyword in medical_keywords):
        return "I understand you're asking about medical information. For accurate and personalized medical advice, please consult with a qualified healthcare professional. They can consider your specific situation and provide appropriate guidance.\n\nIf you're experiencing medical symptoms, please seek immediate medical attention."
    
    # Greetings and general questions
    greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    if any(greeting in prompt_lower for greeting in greetings):
        return "Hello! I'm MediAssist, your medical information assistant. How can I help you today with medical questions?"
    
    # Questions about the assistant
    if "who are you" in prompt_lower or "what are you" in prompt_lower:
        return "I'm MediAssist, an AI-powered medical information assistant. I can provide general information about medical conditions, symptoms, treatments, and prevention strategies. Remember, I don't replace professional medical advice."
    
    # Default response for other queries
    return "I understand you're asking: '" + prompt + "'\n\nFor medical questions, I can provide general information about conditions like cancer, diabetes, liver diseases, obesity, and related topics. If your question is medical in nature, please rephrase it specifically, and I'll do my best to provide helpful information.\n\nIf you need specific medical advice, please consult a healthcare professional."

# Page configuration with dark theme
st.set_page_config(
    page_title="MediAssist AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
def init_db():
    conn = sqlite3.connect('medichat.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User chats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            chat_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, tab_name)
        )
    ''')
    
    # User files table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_content BLOB NOT NULL,
            file_type TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Chat history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tab_name TEXT NOT NULL,
            history_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Authentication functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, email, password):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                 (username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        if user and check_password(password, user[2]):
            return user[0], user[1]  # user_id, username
        return None
    finally:
        conn.close()

# Save/load user data functions
def save_user_chat(user_id, tab_name, chat_data):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        chat_json = json.dumps(chat_data, default=str)
        
        c.execute('SELECT id FROM user_chats WHERE user_id = ? AND tab_name = ?', (user_id, tab_name))
        existing = c.fetchone()
        
        if existing:
            c.execute('''UPDATE user_chats 
                        SET chat_data = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?''', 
                     (chat_json, existing[0]))
        else:
            c.execute('''INSERT INTO user_chats (user_id, tab_name, chat_data) 
                        VALUES (?, ?, ?)''', 
                     (user_id, tab_name, chat_json))
        
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def load_user_chats(user_id):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        c.execute('SELECT tab_name, chat_data FROM user_chats WHERE user_id = ?', (user_id,))
        rows = c.fetchall()
        
        tabs = {}
        for row in rows:
            try:
                chat_data = json.loads(row[1]) if row[1] else []
                tabs[row[0]] = chat_data
            except:
                tabs[row[0]] = []
        
        return tabs
    except:
        return {}
    finally:
        conn.close()

def save_user_files(user_id, tab_name, uploaded_files):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        
        for uploaded_file in uploaded_files:
            file_content = uploaded_file.read()
            c.execute('''INSERT INTO user_files (user_id, tab_name, file_name, file_content, file_type)
                        VALUES (?, ?, ?, ?, ?)''',
                     (user_id, tab_name, uploaded_file.name, file_content, uploaded_file.type))
        
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_user_files(user_id, tab_name):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        c.execute('SELECT file_name, file_type FROM user_files WHERE user_id = ? AND tab_name = ?',
                 (user_id, tab_name))
        return c.fetchall()
    except:
        return []
    finally:
        conn.close()

def save_chat_history(user_id, tab_name, history_data):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        history_json = json.dumps(history_data, default=str)
        
        c.execute('''INSERT INTO chat_history (user_id, tab_name, history_data)
                    VALUES (?, ?, ?)''',
                 (user_id, tab_name, history_json))
        
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def load_chat_history(user_id, tab_name):
    try:
        conn = sqlite3.connect('medichat.db')
        c = conn.cursor()
        c.execute('''SELECT history_data FROM chat_history 
                    WHERE user_id = ? AND tab_name = ? 
                    ORDER BY created_at DESC LIMIT 5''',
                 (user_id, tab_name))
        rows = c.fetchall()
        
        history = []
        for row in rows:
            try:
                history_data = json.loads(row[0])
                history.append(history_data)
            except:
                continue
        
        return history
    except:
        return []
    finally:
        conn.close()

# Custom CSS - DARK THEME
st.markdown("""
<style>
    /* Dark theme variables */
    :root {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-tertiary: #94a3b8;
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --border: #475569;
    }
    
    /* Main background */
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Main container */
    .main {
        background: var(--bg-primary);
    }
    
    /* Login/Signup forms - DARK */
    .auth-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    }
    
    .auth-form {
        background: var(--bg-secondary);
        padding: 2.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        width: 100%;
        max-width: 450px;
        animation: slideUp 0.5s ease;
        border: 1px solid var(--border);
    }
    
    .auth-title {
        text-align: center;
        color: var(--accent-primary);
        margin-bottom: 2rem;
        font-size: 2rem;
        font-weight: bold;
        text-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    
    .auth-subtitle {
        text-align: center;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-size: 1rem;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, 
    .stTextInput>div>div>input:focus {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
    }
    
    .stTextInput>div>div>input::placeholder {
        color: var(--text-tertiary);
    }
    
    /* Buttons in forms */
    .stButton>button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }
    
    /* Sidebar styling - DARK */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1e2e 100%);
        border-right: 1px solid var(--border);
    }
    
    .sidebar-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--accent-primary);
        margin-bottom: 1rem;
        text-align: center;
        padding-top: 1rem;
        text-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    
    .sidebar-subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }
    
    /* Tab buttons - DARK */
    .tab-button {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
        padding: 0.8rem 1rem;
        margin: 0.2rem 0;
        border-radius: 0.8rem;
        width: 100%;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .tab-button:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: var(--accent-primary);
        transform: translateX(5px);
    }
    
    .tab-button.active {
        background: rgba(99, 102, 241, 0.3);
        border-left: 4px solid var(--accent-primary);
    }
    
    /* Chat messages - DARK */
    .user-message {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 1.2rem 1.2rem 0.2rem 1.2rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .assistant-message {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        padding: 1.2rem;
        border-radius: 1.2rem 1.2rem 1.2rem 0.2rem;
        margin: 0.5rem 0;
        max-width: 80%;
        border-left: 4px solid var(--accent-primary);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border);
    }
    
    /* Chat container */
    .chat-container {
        padding: 2rem;
        height: calc(100vh - 180px);
        overflow-y: auto;
        background: var(--bg-primary);
    }
    
    /* Input area - DARK */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-secondary);
        padding: 1rem;
        border-top: 1px solid var(--border);
        z-index: 100;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .input-wrapper {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    /* Chat input - DARK */
    .stChatInput>div>div>textarea,
    .stChatInput>div>div>textarea:focus {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 1.5rem;
        padding: 1rem 1.5rem;
    }
    
    .stChatInput>div>div>textarea::placeholder {
        color: var(--text-tertiary);
    }
    
    /* Attachment button */
    .attach-btn {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        color: white;
        border: none;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        font-size: 1.2rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .attach-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    }
    
    /* File upload dialog - DARK */
    .file-dialog {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-secondary);
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        z-index: 1000;
        min-width: 400px;
        animation: dialogAppear 0.3s ease;
        border: 1px solid var(--border);
    }
    
    .file-dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.7);
        z-index: 999;
        animation: fadeIn 0.3s ease;
    }
    
    /* Stats cards - DARK */
    .stats-card {
        background: var(--bg-secondary);
        padding: 1.2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border);
    }
    
    /* Welcome message - DARK */
    .welcome-message {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 1.5rem;
        color: var(--text-primary);
        margin: 2rem 0;
        border: 2px dashed var(--accent-primary);
        backdrop-filter: blur(10px);
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        color: var(--accent-primary);
        text-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }
    
    /* New tab button - DARK */
    .new-tab-btn {
        background: rgba(99, 102, 241, 0.1);
        border: 2px dashed var(--accent-primary);
        color: var(--accent-primary);
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 0.8rem;
        width: 100%;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .new-tab-btn:hover {
        background: rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
    }
    
    /* Empty state - DARK */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: var(--text-tertiary);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
        color: var(--accent-primary);
    }
    
    /* Expander - DARK */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border-radius: 0.5rem;
        border: 1px solid var(--border);
    }
    
    .streamlit-expanderContent {
        background: var(--bg-secondary);
        border-radius: 0 0 0.5rem 0.5rem;
        border: 1px solid var(--border);
        border-top: none;
    }
    
    /* File uploader - DARK */
    .stFileUploader>div>div {
        background: var(--bg-tertiary);
        border: 2px dashed var(--border);
        border-radius: 1rem;
    }
    
    .stFileUploader>div>div:hover {
        border-color: var(--accent-primary);
    }
    
    /* Animation for messages */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes dialogAppear {
        from {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
    }
    
    .message-animation {
        animation: fadeIn 0.3s ease;
    }
    
    /* Scrollbar - DARK */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-secondary);
    }
    
    /* Selection color */
    ::selection {
        background: rgba(99, 102, 241, 0.3);
        color: white;
    }
    
    /* Status colors */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: #f59e0b;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    /* Divider */
    hr {
        border-color: var(--border) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
def init_session_state():
    defaults = {
        'authenticated': False,
        'user_id': None,
        'username': None,
        'show_login': True,
        'show_register': False,
        'tabs': {},
        'current_tab': None,
        'chat_history': {},
        'tab_counter': 1,
        'show_file_dialog': False,
        'editing_tab': None,
        'temp_files': [],
        'first_message_sent': False,
        'default_tab_created': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Function to clear non-persistent data
def clear_temporary_data():
    st.session_state.tabs = {}
    st.session_state.current_tab = None
    st.session_state.chat_history = {}
    st.session_state.tab_counter = 1
    st.session_state.temp_files = []
    st.session_state.first_message_sent = False
    st.session_state.default_tab_created = False

# Function to create tab name from first question
def create_tab_name_from_question(question):
    question = question.strip()
    question = question.replace('?', '')
    words = question.split()[:7]
    tab_name = ' '.join(words)
    
    if len(tab_name) > 40:
        tab_name = tab_name[:40] + "..."
    
    if not tab_name:
        tab_name = "New Chat"
    
    return tab_name

# Authentication Pages - DARK THEME
def show_login():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    
    st.markdown('<div class="auth-title">🔐 MediAssist AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Your intelligent medical assistant</div>', unsafe_allow_html=True)
    
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True, type="primary"):
            if username and password:
                user_data = login_user(username, password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_data[0]
                    st.session_state.username = user_data[1]
                    
                    user_tabs = load_user_chats(user_data[0])
                    if user_tabs:
                        st.session_state.tabs = user_tabs
                        st.session_state.current_tab = list(st.session_state.tabs.keys())[0]
                    else:
                        st.session_state.tabs = {}
                        st.session_state.current_tab = None
                    
                    st.success(f"Welcome back, {user_data[1]}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please fill in all fields")
    
    with col2:
        if st.button("Register", use_container_width=True):
            st.session_state.show_login = False
            st.session_state.show_register = True
            st.rerun()
    
    st.write("---")
    if st.button("Continue as Guest 👤", use_container_width=True):
        st.session_state.authenticated = True
        st.session_state.username = "Guest"
        clear_temporary_data()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_register():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    
    st.markdown('<div class="auth-title">📝 Create Account</div>', unsafe_allow_html=True)
    
    username = st.text_input("👤 Choose Username")
    email = st.text_input("📧 Email Address")
    password = st.text_input("🔑 Choose Password", type="password")
    confirm_password = st.text_input("🔑 Confirm Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Account", use_container_width=True, type="primary"):
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if register_user(username, email, password):
                        st.success("Account created successfully! Please login.")
                        st.session_state.show_register = False
                        st.session_state.show_login = True
                        st.rerun()
                    else:
                        st.error("Username or email already exists")
            else:
                st.warning("Please fill in all fields")
    
    with col2:
        if st.button("Back to Login", use_container_width=True):
            st.session_state.show_register = False
            st.session_state.show_login = True
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Main application - DARK THEME
def main_app():
    if 'user_tabs_loaded' not in st.session_state:
        if st.session_state.authenticated and st.session_state.user_id:
            user_tabs = load_user_chats(st.session_state.user_id)
            if user_tabs:
                st.session_state.tabs = user_tabs
                st.session_state.current_tab = list(st.session_state.tabs.keys())[0]
        st.session_state.user_tabs_loaded = True
    
    # Function to save current tab data
    def save_current_tab():
        if st.session_state.authenticated and st.session_state.user_id and st.session_state.current_tab:
            save_user_chat(
                st.session_state.user_id,
                st.session_state.current_tab,
                st.session_state.tabs.get(st.session_state.current_tab, [])
            )
            current_messages = st.session_state.tabs.get(st.session_state.current_tab, [])
            if current_messages:
                last_message = current_messages[-1] if current_messages else {}
                if last_message.get("role") == "assistant":
                    save_chat_history(
                        st.session_state.user_id,
                        st.session_state.current_tab,
                        {
                            "timestamp": dt.now().isoformat(),
                            "user_message": current_messages[-2]["content"][:100] if len(current_messages) >= 2 else "",
                            "messages": current_messages.copy()
                        }
                    )
    
    # Function to create a new tab with auto-naming
    def create_new_tab(name=None, from_question=False):
        if not name:
            name = f"Chat {st.session_state.tab_counter}"
        
        if name not in st.session_state.tabs:
            st.session_state.tabs[name] = []
            st.session_state.current_tab = name
            st.session_state.tab_counter += 1
            
            if from_question:
                st.session_state.first_message_sent = True
            
            save_current_tab()
            return name
        return name
    
    # Function to rename tab
    def rename_tab(old_name, new_name):
        if new_name and new_name != old_name:
            st.session_state.tabs[new_name] = st.session_state.tabs.pop(old_name)
            
            if st.session_state.current_tab == old_name:
                st.session_state.current_tab = new_name
            
            st.session_state.editing_tab = None
            save_current_tab()
            st.rerun()
    
    # Function to delete a tab
    def delete_tab(tab_name):
        if len(st.session_state.tabs) > 1:
            del st.session_state.tabs[tab_name]
            if st.session_state.current_tab == tab_name:
                st.session_state.current_tab = list(st.session_state.tabs.keys())[0]
            save_current_tab()
            st.rerun()
    
    # Function to switch tabs
    def switch_tab(tab_name):
        st.session_state.current_tab = tab_name
        st.session_state.show_file_dialog = False
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown(f'<div class="sidebar-title">🏥 MediAssist AI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subtitle">Welcome, <strong>{st.session_state.username}</strong></div>', unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            if st.session_state.username == "Guest":
                clear_temporary_data()
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.user_tabs_loaded = False
            st.rerun()
        
        st.write("---")
        
        # New tab button
        if st.button("＋ New Chat", key="new_chat_button", use_container_width=True, 
                    help="Start a new conversation"):
            tab_name = create_new_tab()
            st.rerun()
        
        st.write("---")
        
        # Display tabs if any exist
        if st.session_state.tabs:
            st.markdown("**💬 Conversations**")
            for tab_name in list(st.session_state.tabs.keys()):
                if st.session_state.editing_tab == tab_name:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        edited_name = st.text_input("", 
                                                   value=tab_name,
                                                   key=f"edit_{tab_name}",
                                                   label_visibility="collapsed",
                                                   placeholder="Tab name")
                    with col2:
                        if st.button("✓", key=f"save_{tab_name}", help="Save", use_container_width=True):
                            if edited_name.strip():
                                rename_tab(tab_name, edited_name.strip())
                    with col3:
                        if st.button("✗", key=f"cancel_{tab_name}", help="Cancel", use_container_width=True):
                            st.session_state.editing_tab = None
                            st.rerun()
                else:
                    is_active = st.session_state.current_tab == tab_name
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        display_name = tab_name[:25] + "..." if len(tab_name) > 25 else tab_name
                        btn_label = f"● {display_name}" if is_active else f"○ {display_name}"
                        if st.button(btn_label, 
                                   key=f"btn_{tab_name}",
                                   help=f"Switch to {tab_name}",
                                   use_container_width=True):
                            switch_tab(tab_name)
                            st.rerun()
                    with col2:
                        if len(st.session_state.tabs) > 1:
                            if st.button("✏️", key=f"edit_btn_{tab_name}", help="Rename"):
                                st.session_state.editing_tab = tab_name
                                st.rerun()
        else:
            st.markdown('<div class="empty-state">', unsafe_allow_html=True)
            st.markdown('<div class="empty-state-icon">💬</div>', unsafe_allow_html=True)
            st.markdown('<div>No conversations yet</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.8rem; margin-top: 0.5rem;">Start by typing your first question!</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("---")
        
        # Chat history for current tab
        if st.session_state.current_tab and st.session_state.authenticated and st.session_state.user_id:
            st.markdown("**📜 History**")
            history = load_chat_history(st.session_state.user_id, st.session_state.current_tab)
            if history:
                for i, chat in enumerate(history):
                    with st.expander(f"Chat {len(history)-i}"):
                        st.write(f"**Q:** {chat.get('user_message', '')[:50]}...")
                        if st.button(f"Load", key=f"load_{i}_{st.session_state.current_tab}"):
                            st.session_state.tabs[st.session_state.current_tab] = chat.get('messages', [])
                            st.rerun()
            else:
                st.caption("No history yet")
        
        st.write("---")
        
        # Current tab files
        if st.session_state.current_tab and st.session_state.authenticated and st.session_state.user_id:
            files = get_user_files(st.session_state.user_id, st.session_state.current_tab)
            if files:
                st.markdown("**📎 Files**")
                for file_name, file_type in files:
                    st.caption(f"📄 {file_name[:20]}..." if len(file_name) > 20 else f"📄 {file_name}")

    # --- Main Chat Area ---
    if st.session_state.current_tab:
        st.markdown(f'<h1 style="color: var(--accent-primary); margin-bottom: 1.5rem; text-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);">{st.session_state.current_tab}</h1>', unsafe_allow_html=True)
    
    # Welcome message for empty chat
    current_messages = st.session_state.tabs.get(st.session_state.current_tab, []) if st.session_state.current_tab else []
    
    if not current_messages:
        st.markdown('''
            <div class="welcome-message">
                <div class="welcome-icon">🌙</div>
                <h2 style="color: var(--accent-primary);">Welcome to MediAssist AI</h2>
                <p style="font-size: 1.1rem; color: var(--text-secondary); margin: 1rem 0;">Your intelligent medical assistant is ready to help.</p>
                <div style="background: rgba(30, 41, 59, 0.8); padding: 1.5rem; border-radius: 1rem; margin: 1.5rem 0; text-align: left; border: 1px solid var(--border);">
                    <h4 style="color: var(--accent-primary); margin-bottom: 1rem;">💡 What you can ask:</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.8;">
                        <li>What are the symptoms of diabetes?</li>
                        <li>Explain cancer treatment options</li>
                        <li>Heart disease prevention tips</li>
                        <li>Latest medical research updates</li>
                    </ul>
                </div>
                <p style="font-weight: bold; color: var(--accent-primary);">Type your first question below to get started!</p>
            </div>
        ''', unsafe_allow_html=True)
    
    # Chat messages container
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    
    for i, message in enumerate(current_messages):
        if message["role"] == "user":
            st.markdown(f'''
                <div class="user-message message-animation">
                    <strong style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="background: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #6366f1;">👤</span>
                        You
                    </strong>
                    <div>{message["content"]}</div>
            ''', unsafe_allow_html=True)
            
            if "attachments" in message:
                attachments_html = '<div style="margin-top: 10px; font-size: 0.9em; display: flex; flex-wrap: wrap; gap: 5px;">'
                for att in message["attachments"]:
                    attachments_html += f'<div style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 12px; font-size: 0.85em;">📎 {att[:15]}{"..." if len(att) > 15 else ""}</div>'
                attachments_html += '</div>'
                st.markdown(attachments_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="assistant-message message-animation">
                    <strong style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="background: #6366f1; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white;">🏥</span>
                        MediAssist
                    </strong>
                    <div>{message["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-scroll to bottom
    st.markdown("""
    <script>
        function scrollToBottom() {
            var container = document.getElementById('chat-container');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }
        window.onload = scrollToBottom;
        setTimeout(scrollToBottom, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # --- Input Area (Fixed at bottom) ---
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
    
    # Create columns for input area
    col1, col2, col3 = st.columns([1, 12, 1])
    
    with col1:
        if st.button("📎", 
                    key="attach_button_main",
                    help="Attach files",
                    use_container_width=True,
                    disabled=not st.session_state.current_tab):
            st.session_state.show_file_dialog = True
            st.rerun()
    
    with col2:
        prompt = st.chat_input(
            "Type your medical question here...",
            key="main_chat_input"
        )
    
    with col3:
        if st.button("🗑️", 
                    key="clear_chat",
                    help="Clear current chat",
                    use_container_width=True,
                    disabled=not st.session_state.current_tab or not current_messages):
            st.session_state.tabs[st.session_state.current_tab] = []
            save_current_tab()
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- File Dialog (Modal) ---
    if st.session_state.show_file_dialog:
        st.markdown('<div class="file-dialog-overlay"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="file-dialog">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: var(--accent-primary); margin-bottom: 1.5rem;">📎 Attach Files</h3>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files to attach",
            accept_multiple_files=True,
            key=f"file_upload_dialog",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Attach Files", use_container_width=True, type="primary"):
                if uploaded_files:
                    if st.session_state.authenticated and st.session_state.user_id:
                        save_user_files(
                            st.session_state.user_id,
                            st.session_state.current_tab,
                            uploaded_files
                        )
                    
                    file_names = [f.name for f in uploaded_files]
                    st.session_state.temp_files = file_names
                    
                    st.success(f"✓ Attached {len(uploaded_files)} file(s)")
                    st.session_state.show_file_dialog = False
                    st.rerun()
                else:
                    st.warning("Please select files first")
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_file_dialog = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Process User Input ---
    if prompt:
        if not st.session_state.tabs:
            tab_name = create_tab_name_from_question(prompt)
            create_new_tab(tab_name, from_question=True)
        elif not st.session_state.current_tab:
            st.session_state.current_tab = list(st.session_state.tabs.keys())[0]
        
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": dt.now().isoformat()
        }
        
        if st.session_state.temp_files:
            user_message["attachments"] = st.session_state.temp_files.copy()
            st.session_state.temp_files = []
        
        if st.session_state.current_tab not in st.session_state.tabs:
            st.session_state.tabs[st.session_state.current_tab] = []
        st.session_state.tabs[st.session_state.current_tab].append(user_message)
        
        with st.spinner("🌙 MediAssist is thinking..."):
            if llm_available:
                response = llm.generate_response(prompt)
            else:
                response = generate_fallback_response(prompt)
        
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": dt.now().isoformat()
        }
        st.session_state.tabs[st.session_state.current_tab].append(assistant_message)
        
        save_current_tab()
        st.session_state.show_file_dialog = False
        st.rerun()
    
    # --- Stats Footer ---
    if st.session_state.current_tab:
        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            current_msgs = len(current_messages)
            st.markdown(f'''
                <div class="stats-card">
                    <div style="font-size: 0.9em; color: var(--text-secondary);">Current Tab</div>
                    <div style="font-size: 1.1em; font-weight: bold; color: var(--accent-primary); word-break: break-word;">{st.session_state.current_tab[:20]}{"..." if len(st.session_state.current_tab) > 20 else ""}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
                <div class="stats-card">
                    <div style="font-size: 0.9em; color: var(--text-secondary);">Messages</div>
                    <div style="font-size: 1.2em; font-weight: bold; color: var(--accent-primary);">{current_msgs}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
                <div class="stats-card">
                    <div style="font-size: 0.9em; color: var(--text-secondary);">Total Chats</div>
                    <div style="font-size: 1.2em; font-weight: bold; color: var(--accent-primary);">{len(st.session_state.tabs)}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

# Main application flow
def main():
    if not st.session_state.authenticated:
        if st.session_state.show_login:
            show_login()
        elif st.session_state.show_register:
            show_register()
    else:
        main_app()

if __name__ == "__main__":
    main()
