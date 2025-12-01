That's a very detailed and well-structured `README.md`\! I will format it using Markdown headings, lists, tables, and blockquotes for excellent readability, maintaining the original content and structure.

-----

# 🏥 MediAssist AI

### AI-Powered Healthcare Q\&A System Using RAG, ChromaDB & Gemini AI

[](https://www.python.org/)
[](https://streamlit.io/)
[](https://www.trychroma.com/)
[](https://ai.google.dev/)
[](https://opensource.org/licenses/MIT)

MediAssist AI is an intelligent **Healthcare Question-Answering system** designed for doctors, clinicians, and medical researchers. It provides **quick, evidence-based summaries** on *Intermittent Fasting (IF)* and related metabolic disorders using **Retrieval-Augmented Generation (RAG)**.

This tool helps clinicians access **reliable medical information instantly**, reducing research time and improving decision-making.

-----

## 🚀 Latest Updates (December 2024)

### ✨ New Features Added:

| Feature | Description | Status |
| :--- | :--- | :--- |
| **🔐 User Authentication** | Secure login/register system with password hashing | ✅ Live |
| **💬 Multi-Conversation Management** | Create, edit, delete, and switch between conversations | ✅ Live |
| **📁 PDF Document Upload** | Upload medical PDFs for analysis and summarization | ✅ Live |
| **🤖 Enhanced Gemini AI** | Using gemini-flash-latest for faster, smarter responses | ✅ Live |
| **🎨 Dark Theme UI** | Professional dark interface with gradient accents | ✅ Live |
| **🔍 Advanced RAG Search** | Combined search across medical database + uploaded PDFs | ✅ Live |
| **📊 Conversation Summarization** | AI-powered summaries of entire conversations | ✅ Live |
| **📚 Source Citation** | View sources with similarity scores and metadata | ✅ Live |

-----

## 💻 App Demonstration

Check out the live application or see the interface below\!

🔗 **Live Demo Link**

> 👉 [Click here to test the MediAssist AI App\!](https://mediassist-ai-zasupw7hcgypimctpdtcyr.streamlit.app/)

## 📸 Screenshots

### 1\. Authentication Page

Secure login and registration with dark theme design.

### 2\. Main Chat Interface

AI-powered chat with conversation history and document upload.

### 3\. RAG-Powered Answer

Evidence-based responses with source citations.

### 4\. PDF Analysis

Upload and analyze medical documents with AI summarization.

-----

## 🔍 Background & Problem Statement

**MediInsight**, a preventive healthcare analytics company, is exploring Intermittent Fasting (IF) as a treatment approach for:

  * Obesity
  * Type 2 Diabetes
  * Metabolic Disorders

However, they face major challenges:

### ❗ Challenges

| Challenge | Description |
| :--- | :--- |
| **Conflicting Information** | IF studies are rapidly increasing, but many are inconclusive or not peer-reviewed. |
| **No Standard Guidelines** | Fasting protocols vary (16:8, 5:2, alternate-day fasting), making it hard to unify recommendations. |
| **Clinicians Lack Time** | Doctors cannot keep up with large volumes of research data. |
| **Document Management** | Medical PDFs and research papers are scattered and hard to search. |
| **Knowledge Retention** | Difficult to track and summarize conversations with patients/researchers. |

-----

## 💡 Solution — MediAssist AI

MediAssist AI solves these problems with:

### ✅ Core Features

  * **AI-Powered Medical Assistant**: Gemini Flash AI for intelligent responses
  * **RAG Search System**: Evidence-based answers with citations
  * **Multi-User System**: Secure authentication and conversation management
  * **PDF Document Analysis**: Upload and query medical research papers
  * **Conversation History**: Save, edit, and review past conversations
  * **Dark Theme UI**: Professional interface for extended use
  * **Real-time Processing**: Instant responses with live analysis

### ✅ Medical Knowledge Base

  * Intermittent Fasting protocols (16:8, 5:2, alternate-day)
  * Diabetes management and insulin sensitivity
  * Metabolic disorders research
  * Nutrition and dietetics
  * Weight management strategies
  * General medical concepts

-----

## 🧠 System Architecture

### 🔹 Core Components

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Interactive web interface with dark theme |
| **AI Model** | Google Gemini Flash | Intelligent response generation |
| **Vector Database** | ChromaDB | Medical knowledge storage and retrieval |
| **Authentication** | SHA-256 Hashing | Secure user login/registration |
| **Document Processing** | PyPDF2 | PDF text extraction and analysis |
| **Embeddings** | Sentence Transformers | Text vectorization for semantic search |
| **Conversation Storage** | JSON File System | Persistent conversation history |
| **RAG Pipeline** | Custom Implementation | Evidence-based answer generation |

-----

## 🏗 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                      MediAssist AI - Complete Architecture           ║
╚══════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────┐
│                     🌐 USER INTERFACE LAYER                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │🔐 AUTHENTICATION│ │💬 CHAT INTERFACE│  │📁 PDF UPLOADER  │       │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤       │
│  │ • Login/Register│  │ • Real-time Q&A │  │ • Upload PDFs   │       │
│  │ • SHA-256 Hash  │  │ • Multi-Conv    │  │ • Extract Text  │       │
│  │ • Session Mgmt  │  │ • Dark Theme    │  │ • Summarize     │       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘       │
│           │                  │                  │                    │
│           └──────────────────┼──────────────────┘                    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                    STREAMLIT FRONTEND                       │     │
│  │              (Single-Page Application with React-like)      │    │
│  └─────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ⚙️ BUSINESS LOGIC LAYER                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                CONVERSATION MANAGER                         │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ • Create/Edit/Delete Conversations                          │    │
│  │ • Switch Between Conversations                              │    │
│  │ • Save/Load from JSON                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                 DOCUMENT PROCESSOR                          │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ • PDF Text Extraction (PyPDF2)                              │    │
│  │ • Chunking & Preprocessing                                  │    │
│  │ • Metadata Extraction                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                🤖 AI PROCESSING & RAG PIPELINE                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐       QUERY      ┌─────────────────┐            │
│  │  🔍RETRIEVAL    │◄────────────────►│  🧠 GENERATION │            │
│  │  ENGINE         │                  │  ENGINE          │           │
│  ├─────────────────┤     CONTEXT      ├─────────────────┤            │
│  │ • Vector Search │                 │ • Gemini AI      │            │
│  │ • ChromaDB      │                 │ • Prompt Eng     │            │
│  │ • Similarity    │                 │ • Summarization  │            │
│  └─────────────────┘                 └─────────────────┘             │
│            │                              │                          │
│            └───────────────┬───────────────┘                         │
│                            │                                         │
│                ┌───────────▼───────────┐                             │
│                │      RAG ORCHESTRATOR    │                          │
│                ├─────────────────────────┤                           │
│                │ • Combine Context       │                           │
│                │ • Generate Final Answer │                           │
│                │ • Add Source Citations  │                           │
│                └─────────────────────────┘                           │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    💾 DATA STORAGE LAYER                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐                  ┌─────────────────┐            │
│  │  🗄️ VECTOR DB    │                  │  📄 FILE SYSTEM    │        │
│  ├─────────────────┤                  ├─────────────────┤            │
│  │ • ChromaDB      │                  │ • conversations │            │
│  │ • Embeddings    │                  │ • user_data     │            │
│  │ • Medical KB    │                  │ • config        │            │
│  └─────────────────┘                  └─────────────────┘            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                    KNOWLEDGE BASE                           │     │
│  ├─────────────────────────────────────────────────────────────┤     │
│  │ • Intermittent Fasting Research                             │     │
│  │ • Diabetes Management                                       │     │
│  │ • Metabolic Disorders                                       │     │
│  │ • Nutrition Studies                                         │     │
│  └─────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘
```
## 🔄 Data Flow Diagram
```
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    USER     │   │  FRONTEND   │   │   AUTH      │
  │   Input     │──►│  (Streamlit)│──►│   System    │
  └─────┬───────┘   └─────┬───────┘   └─────┬───────┘
        │                 │                 │
        │           ┌─────▼───────┐   ┌─────▼───────┐
        │           │   STATE     │   │   SESSION   │
        │           │   MANAGER   │   │   MANAGER   │
        │           └─────┬───────┘   └─────────────┘
        │                 │
        │           ┌─────▼─────────────────────────┐
        │           │        RAG PIPELINE           │
        │           │  ┌─────────────────────────┐  │
        │           │  │   1. Vector Search      │  │
        │           │  │      (ChromaDB)         │  │
        │           │  └───────────┬─────────────┘  │
        │           │              │                 │
        │           │  ┌───────────▼─────────────┐  │
        │           │  │   2. Context Building   │  │
        │           │  │   (Retrieved Docs)      │  │
        │           │  └───────────┬─────────────┘  │
        │           │              │                 │
        │           │  ┌───────────▼─────────────┐  │
        │           │  │   3. LLM Generation     │  │
        │           │  │     (Gemini AI)         │  │
        │           │  └───────────┬─────────────┘  │
        │           └───────────────┼─────────────────┘
        │                           │
        │                   ┌───────▼───────┐
        │                   │   RESPONSE    │
        │                   │   PROCESSOR   │
        │                   └───────┬───────┘
        │                           │
        │                   ┌───────▼───────┐
        │                   │    OUTPUT     │
        │                   │   (Display)   │
        │                   └───────────────┘
        │                           │
        └───────────────────────────┘
```

## 🎯 Simplified Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Query    │────►│   Authentication│────►│   Conversation  │
│   or PDF Upload │     │   & Validation  │     │   Management    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌─────────────────┐     ┌────────▼────────┐
│   Display       │◄────│   Response      │◄────│   RAG Pipeline  │
│   Results       │     │   Generation    │     │                 │
└─────────────────┘     └─────────────────┘     ├─────────────────┤
                                                 │ 1. Search DB    │
                                                 │ 2. Get Context  │
                                                 │ 3. Call LLM     │
                                                 │ 4. Format Answer│
                                                 └─────────────────┘

```
-----

## 🚀 Features

### 🤖 AI Capabilities

  * ✅ Gemini Flash Latest AI for medical Q\&A
  * ✅ RAG-powered evidence-based answers
  * ✅ Conversation summarization
  * ✅ PDF document analysis
  * ✅ Context-aware responses
  * ✅ Multi-turn conversation memory

### 🔐 User Management

  * ✅ Secure authentication (SHA-256)
  * ✅ Multi-user support
  * ✅ Personalized conversation history
  * ✅ Session management
  * ✅ User profiles

### 📁 Document Handling

  * ✅ PDF upload and processing
  * ✅ Medical document analysis
  * ✅ Text extraction and summarization
  * ✅ Vector embedding of documents
  * ✅ Cross-document search

### 💬 Conversation Features

  * ✅ Create new conversations
  * ✅ Edit conversation titles
  * ✅ Delete conversations
  * ✅ Switch between conversations
  * ✅ Save conversation history
  * ✅ Export-ready format

### 🎨 UI/UX Features

  * ✅ Dark theme interface
  * ✅ Responsive design
  * ✅ Gradient accents
  * ✅ Animated elements
  * ✅ Intuitive navigation
  * ✅ Mobile-friendly layout

-----

## 📦 Installation & Setup

### 1️⃣ Prerequisites

  * Python 3.9+
  * Google Gemini API Key
  * 2GB+ RAM

### 2️⃣ Clone & Setup

```bash
# Clone repository
git clone https://github.com/OmThawaregitgub/MediAssist-AI.git
cd MediAssist-AI

# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure API Keys

Create `.env` file in project root:

```env
# Google Gemini API Key (from https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_actual_api_key_here

# Alternative key names also supported:
# GOOGLE_API_KEY=your_key
# API_KEY=your_key
```

### 4️⃣ Run Application

```bash
# Start the application
streamlit run app.py

# Access at: http://localhost:8501
```

### 5️⃣ Default Login Credentials

```
Username: admin
Password: admin123
```

-----

## 📁 Project Structure

```
MediAssist-AI/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # API keys (not in git)
├── conversations.json             # User conversations storage
├── chroma_pubmed/                 # Vector database directory
│
├── data/                          # Medical research documents
│   ├── sample_papers/
│   └── medical_knowledge/
│
├── images/                        # Screenshots for documentation
│   ├── Screenshot (419).png      # Auth page
│   ├── Screenshot (420).png      # Main chat
│   ├── Screenshot (421).png      # RAG answer
│   └── Screenshot (422).png      # PDF analysis
│
└── README.md                      # This documentation
```

-----

## 🧪 How It Works

### 1️⃣ User Authentication

  * Users register/login with credentials
  * Passwords are hashed with SHA-256
  * Each user gets isolated conversation space

### 2️⃣ Conversation Management

  * Create unlimited conversations
  * Edit titles for easy identification
  * Switch between conversations seamlessly
  * Delete unwanted conversations

### 3️⃣ Medical Q\&A Process

```
User Question → Vector Search → Context Retrieval → AI Generation → Response
      │               │               │               │            │
      │               │               │               │            └─ Display answer with sources
      │               │               │               └─ Gemini AI processes context + question
      │               │               └─ Relevant documents from ChromaDB
      │               └─ Semantic search in vector database
      └─ Medical query input
```

### 4️⃣ PDF Document Processing

  * Upload medical PDFs via sidebar
  * Text extraction using PyPDF2
  * Content embedding into vector DB
  * AI-powered document summarization
  * Query-specific content retrieval

### 5️⃣ RAG Implementation

  * Combines retrieval (vector search) + generation (Gemini AI)
  * Provides evidence-based answers
  * Cites sources with similarity scores
  * Ensures accuracy and reliability

-----

## 📘 Example Use Cases

### 🩺 For Medical Professionals

  * "What are the latest IF protocols for type 2 diabetes?"
  * "Summarize the conversation I had about patient X"
  * "Analyze this research paper on metabolic syndrome"
  * "Compare 16:8 vs 5:2 fasting for weight loss"

### 📚 For Researchers

  * "Upload and summarize this clinical trial PDF"
  * "Find studies on IF and insulin sensitivity"
  * "What's the evidence for IF in obesity treatment?"
  * "Create a literature review on fasting benefits"

### 👨‍⚕️ For Clinicians

  * "Is intermittent fasting safe for elderly patients?"
  * "What precautions for IF with diabetes medication?"
  * "How to monitor patients during fasting periods?"
  * "Best practices for IF implementation"

### 🏋️ For Health Coaches

  * "Optimal fasting windows for muscle preservation"
  * "Nutrition strategies during eating windows"
  * "Hydration and electrolyte management"
  * "Exercise timing with fasting schedules"

-----

## 🔧 Technical Details

### **Dependencies**

```txt
streamlit==1.28.0
google-generativeai==0.3.0
chromadb==0.4.15
sentence-transformers==2.2.2
PyPDF2==3.0.1
python-dotenv==1.0.0
```

### **Performance Metrics**

  * Response time: \< 3 seconds
  * Vector search accuracy: \> 85%
  * PDF processing: \< 10 seconds per page
  * Concurrent users: 50+ (depending on API limits)
  * Storage: \~100MB for 1000 conversations

### **Security Features**

  * Password hashing (SHA-256)
  * Session-based authentication
  * API key encryption
  * File upload validation
  * Input sanitization

-----

## 🐛 Troubleshooting

### **Common Issues & Solutions**

| Issue | Solution |
| :--- | :--- |
| API Key Error | Check `.env` file and Gemini API quota |
| ChromaDB Connection | Delete `chroma_pubmed` folder and restart |
| PDF Upload Fails | Ensure PDF is not encrypted/corrupted |
| Slow Responses | Check internet connection and API status |
| Login Failure | Use default credentials or register new account |
| Memory Issues | Reduce PDF size or split into smaller documents |

### **Error Messages**

```bash
# Missing API Key
❌ No API key available. Please add GEMINI_API_KEY to .env

# Invalid API Key
❌ Invalid API Key. Check your Google AI Studio API key.

# Database Error
❌ Vector database error. Try deleting chroma_pubmed folder.

# PDF Error
⚠️ No text could be extracted from PDF. Try a different file.
```

-----

## 📈 Future Roadmap

### **Planned Features**

  * [ ] **Multi-language Support** - Spanish, French, Hindi translations
  * [ ] **Voice Input/Output** - Speech-to-text and text-to-speech
  * [ ] **Advanced Analytics** - Conversation insights and patterns
  * [ ] **Export Features** - PDF/Word export of conversations
  * [ ] **API Access** - REST API for integration with other systems
  * [ ] **Mobile App** - iOS and Android applications
  * [ ] **Team Collaboration** - Shared conversations and documents
  * [ ] **Real-time Updates** - Live medical news and research

### **Technical Enhancements**

  * [ ] **Database Migration** - SQLite/PostgreSQL for conversations
  * [ ] **Caching System** - Redis for faster responses
  * [ ] **Model Fine-tuning** - Custom medical AI model
  * [ ] **Advanced Search** - Boolean and semantic search combination
  * [ ] **Batch Processing** - Multiple PDF upload and processing

-----

## 🙌 Acknowledgments

### **Technologies Used**

  * **Google Gemini AI** - Advanced language model for medical Q\&A
  * **ChromaDB** - High-performance vector database
  * **Streamlit** - Rapid web application development
  * **Sentence Transformers** - Text embedding models
  * **PyPDF2** - PDF text extraction library

### **Research Sources**

  * PubMed Central - Medical research papers
  * Harvard Medical School - Health guidelines
  * Diabetes Care Journal - Diabetes research
  * Nutrition Research Journals - Diet studies
  * Clinical Trial Databases - Evidence-based data

### **Contributors**

  * **Om Thaware** - Project Lead & Developer
  * **Medical Professionals** - Domain expertise
  * **Open Source Community** - Libraries and tools

-----

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

## ⚠️ Disclaimer

> **MediAssist AI is for educational and research purposes only.** It does not provide medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical concerns. The information provided by this system should not be used as a substitute for professional medical advice.

-----

## 📞 Support & Contact

For issues, questions, or contributions:

  * **GitHub Issues**: [Create an issue](https://github.com/OmThawaregitgub/MediAssist-AI/issues)
  * **Email**: omthaware@example.com
  * **Documentation**: [Read the docs](https://github.com/OmThawaregitgub/MediAssist-AI/wiki)

-----

## 🎯 Quick Start Commands

```bash
# Quick install and run
git clone https://github.com/OmThawaregitgub/MediAssist-AI.git
cd MediAssist-AI
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env
streamlit run app.py

# Default login
Username: admin
Password: admin123
```

*Happy coding and stay healthy\! 🏥💙*

-----

Would you like me to highlight the key changes in the `app.py` code snippet, or is there another part of the documentation you'd like me to format or summarize?
