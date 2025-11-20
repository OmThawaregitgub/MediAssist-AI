import chromadb
import shutil
import os
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            # Clear existing database to fix schema issues
            if os.path.exists(persist_directory):
                print("🔄 Clearing existing database due to schema issues...")
                shutil.rmtree(persist_directory)
            
            # Initialize ChromaDB client with fresh database
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Create new collection
            self.collection = self.client.create_collection("medical_data")
            print("✅ Created new collection")
            
            # Initialize LLM client
            self.llm = LLMClient()
            print("✅ LLM client initialized successfully")
            
            # Load documents
            print("📚 Loading documents...")
            self.load_documents()
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load medical documents about intermittent fasting"""
        try:
            # Comprehensive medical documents about intermittent fasting
            medical_documents = [
                "Intermittent fasting (IF) is an eating pattern that cycles between periods of fasting and eating, focusing on when to eat rather than what to eat.",
                "The 16:8 method involves fasting for 16 hours daily and eating within an 8-hour window, such as from 12 PM to 8 PM.",
                "The 5:2 diet involves eating normally for 5 days and restricting calories to 500-600 on 2 non-consecutive days.",
                "Alternate-day fasting involves alternating between normal eating days and fasting days or significantly reduced calorie intake.",
                "Research shows intermittent fasting can lead to 3-8% weight loss over 3-24 weeks by creating a calorie deficit and enhancing fat burning.",
                "Intermittent fasting improves insulin sensitivity and can reduce blood sugar levels, benefiting individuals with prediabetes or type 2 diabetes.",
                "Time-restricted feeding improves metabolic health markers including cholesterol levels, blood pressure, and inflammatory markers like C-reactive protein.",
                "Intermittent fasting triggers autophagy, a cellular cleanup process that removes damaged components and may have anti-aging benefits.",
                "IF is generally safe for healthy adults but may not be suitable for individuals with diabetes, eating disorders, pregnant women, or those with certain medical conditions.",
                "Common side effects during adaptation include hunger, fatigue, headaches, and irritability, which typically subside within a few weeks.",
                "Intermittent fasting may preserve muscle mass better than continuous calorie restriction when combined with resistance training.",
                "Studies suggest IF can improve brain health, enhance memory, and protect against neurodegenerative diseases through various mechanisms.",
                "The eating window in time-restricted feeding should align with circadian rhythms for optimal metabolic benefits, typically earlier in the day.",
                "Intermittent fasting protocols should be individualized based on health status, lifestyle, and personal preferences for long-term sustainability."
            ]
            
            # Add documents to collection
            self.collection.add(
                documents=medical_documents,
                metadatas=[{"source": "medical_research", "topic": "intermittent_fasting"} for _ in medical_documents],
                ids=[f"doc_{i}" for i in range(len(medical_documents))]
            )
            print(f"✅ Loaded {len(medical_documents)} medical documents")
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            raise e
    
    def ask(self, query):
        """Handle user queries with smart response generation"""
        try:
            print(f"🔍 Processing query: {query}")
            
            # For medical questions, use a combination of RAG and LLM knowledge
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            # Build context from retrieved documents
            context = ""
            if results.get('documents') and results['documents'][0]:
                for doc in results['documents'][0]:
                    if doc and str(doc).strip():
                        context += f"• {doc}\n"
            
            # Create intelligent prompt
            if context:
                prompt = f"""As a medical AI assistant, answer this question: "{query}"

Relevant medical information:
{context}

Please provide a comprehensive, evidence-based answer. If the context doesn't fully address the question, use your medical knowledge to supplement.

Structure your response clearly and include important medical disclaimers."""
            else:
                prompt = f"""As a medical AI assistant, provide a comprehensive answer to: "{query}"

Use your medical knowledge to give a helpful, evidence-based response. If discussing specific medical conditions or treatments, include appropriate disclaimers about consulting healthcare professionals.

Structure the information clearly for easy understanding."""
            
            print("🔄 Generating response...")
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            print(f"❌ Error in ask method: {e}")
            return f"I apologize, but I encountered an error processing your question. Please try again."
    
    def get_collection_info(self):
        """Get collection information for UI"""
        try:
            count = self.collection.count()
            return f"📊 Medical database loaded with {count} documents about intermittent fasting"
        except:
            return "📊 Medical AI Assistant Ready"
