[file name]: README.md
[file content begin]
# 🏥 MediAssist AI

### AI-Powered Healthcare Q&A System Using RAG, ChromaDB & LLaMA

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![VectorDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-lightgreen)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MediAssist AI is an intelligent **Healthcare Question-Answering system** designed for doctors, clinicians, and medical researchers. It provides **quick, evidence-based summaries** on *Intermittent Fasting (IF)* and related metabolic disorders using **Retrieval-Augmented Generation (RAG)**.

This tool helps clinicians access **reliable medical information instantly**, reducing research time and improving decision-making.

---

## 💻 App Demonstration

Check out the live application or see the interface below!

🔗 **Live Demo Link**

👉 [Click here to test the MediAssist AI App!](https://mediassist-ai-zasupw7hcgypimctpdtcyr.streamlit.app/)

## 📸 Screenshots

### 1. Main Chat Interface
The initial interface showing the welcoming message and the chat layout.
![Main Chat Interface](https://github.com/OmThawaregitgub/MediAssist-AI/blob/master/Images/Screenshot%20(419).png?raw=true)

### 2. RAG-Powered Answer
A demonstration of the system successfully retrieving context and generating a grounded response.
![RAG-Powered Answer Example](https://github.com/OmThawaregitgub/MediAssist-AI/blob/master/Images/Screenshot%20(420).png?raw=true)

---

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

---

## 💡 Proposed Solution — MediAssist AI

MediAssist AI solves these problems by providing:
* ✔ Evidence-based answers
* ✔ Context-aware summaries
* ✔ Fast retrieval from a vector database
* ✔ Easy-to-use chat-based interface

The system combines **AI generation + research retrieval** for trustworthy medical insights.

---

## 🧠 System Architecture

### 🔹 Core Components
| Component | Role |
| :--- | :--- |
| **RAG (Retrieval-Augmented Generation)** | Ensures answers are grounded in real medical research. |
| **ChromaDB (Vector Database)** | Stores & retrieves embedded medical literature. |
| **LLaMA / Gemini / Any LLM** | Generates clear explanations and summaries based on context. |
| **Streamlit Chat UI** | Provides a simple interface showing previous questions/answers and an input box. |

---

## 🏗 Architecture Diagram

```
                ┌───────────────────────────┐
                │       User Query           │
                └─────────────┬─────────────┘
                              │
                       (1) Retrieve
                              │
                ┌─────────────▼─────────────┐
                │     ChromaDB Vector DB     │
                │  (Stores medical research) │
                └─────────────┬─────────────┘
                              │
                        (2) Context
                              │
                ┌─────────────▼─────────────┐
                │   LLM (LLaMA / Gemini)     │
                │ Generates evidence-based   │
                │ summaries & answers        │
                └─────────────┬─────────────┘
                              │
                       (3) Final Answer
                              │
                ┌─────────────▼─────────────┐
                │     Streamlit Chat UI      │
                └───────────────────────────┘
```

---

## 🚀 Features

* ✔ AI-Generated clinical summaries
* ✔ Grounded using real research (RAG)
* ✔ Stores literature using vector embeddings
* ✔ Chat interface with visible history
* ✔ Session-based chat (clears when browser closes)
* ✔ Fast & lightweight Streamlit UI

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/MediAssist-AI.git
cd MediAssist-AI
```

### 2️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Add your API key
The system requires an API key for the LLM (Google Gemini).

Create a file named `.env` in the project's root directory:
```env
# Put your Google Gemini API Key here
API_KEY=YOUR_GEMINI_API_KEY_HERE
```

---

## ▶️ Run the Application

Start the Streamlit server from the terminal:
```bash
streamlit run streamlit_app.py
```

---

## 📁 Project Structure

Make sure you have an images folder for the screenshots and a data folder for your medical research files.

```
MediAssist-AI/
│── streamlit_app.py       # Main Streamlit Chat UI
│── rag.py                 # RAG pipeline logic (vector store setup, retrieval)
│── llm.py                 # LLM wrapper (Gemini/LLaMA integration)
│── data/                  # Directory for source PDFs or research papers
│── images/
│   ├── Screenshot (419).png # Main Chat Interface
│   └── Screenshot (420).png # Example Answer
│── .env                   # API key (excluded from Git via .gitignore)
│── .gitignore
│── requirements.txt
└── README.md              # This file
```

---

## 🧪 How It Works

1. User asks a medical question.
2. The system retrieves relevant research data from ChromaDB using vector search.
3. The relevant documents are passed as context to the LLM (LLaMA or Gemini).
4. The LLM generates a grounded, evidence-based summary.
5. The final answer appears on the Streamlit screen with the chat history.

---

## 📘 Example Use Cases

* "Does 16:8 fasting help improve insulin sensitivity?"
* "Is intermittent fasting safe for Type 2 diabetic patients?"
* "Which IF method is best for weight loss?"

---

## 🙌 Acknowledgments

* **ChromaDB** for powerful and easy-to-use vector storage.
* **LLaMA / Meta AI** and **Google Gemini** for providing flexible LLM options.
* **Streamlit** for the rapid development of the interactive chat UI.

---

## 📜 License

This project is open-source under the **MIT License**.
[file content end]
