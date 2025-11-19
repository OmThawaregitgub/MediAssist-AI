# 🏥 MediAssist AI
### AI-Powered Healthcare Q&A System Using RAG, ChromaDB & LLaMA

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![VectorDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-lightgreen)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MediAssist AI is an intelligent **Healthcare Question-Answering system** designed for doctors, clinicians, and medical researchers. It provides **quick, evidence-based summaries** on *Intermittent Fasting (IF)* and related metabolic disorders using **Retrieval-Augmented Generation (RAG)**.

This tool helps clinicians access **reliable medical information instantly**, reducing research time and improving decision-making.

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

## 🏗 Architecture Diagram (ASCII)

            ┌───────────────────────────┐
            │       User Query          │
            └─────────────┬─────────────┘
                          │
                   (1) Retrieve
                          │
            ┌─────────────▼─────────────┐
            │     ChromaDB Vector DB    │
            │  (Stores medical research)│
            └─────────────┬─────────────┘
                          │
                    (2) Context
                          │
            ┌─────────────▼─────────────┐
            │   LLM (LLaMA / Gemini)    │
            │ Generates evidence-based  │
            │ summaries & answers       │
            └─────────────┬─────────────┘
                          │
                   (3) Final Answer
                          │
            ┌─────────────▼─────────────┐
            │     Streamlit Chat UI     │
            └───────────────────────────┘