import chromadb
import os
import shutil
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            # Clear and recreate database to avoid schema issues
            if os.path.exists(persist_directory):
                shutil.rmtree(persist_directory)
            
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.create_collection("medical_data")
            
            # Initialize LLM
            self.llm = LLMClient()
            print("✅ RAG Pipeline initialized successfully")
            
            # Load basic documents
            self.load_documents()
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load some basic medical documents"""
        try:
            documents = [
                "Intermittent fasting involves cycling between eating and fasting periods.",
                "Common fasting methods include 16:8, 5:2, and alternate-day fasting.",
                "Fasting may improve insulin sensitivity and support weight loss."
            ]
            
            self.collection.add(
                documents=documents,
                metadatas=[{"type": "fasting"} for _ in documents],
                ids=[f"doc_{i}" for i in range(len(documents))]
            )
            print("✅ Loaded basic documents")
        except Exception as e:
            print(f"Note: Could not load documents: {e}")
    
    def ask(self, query):
        """Handle ANY medical question using LLM's general knowledge"""
        try:
            print(f"🔍 User asked: {query}")
            
            # For ANY question, use the LLM with medical context
            prompt = f"""You are a medical AI assistant. Please provide a comprehensive, accurate answer to this medical question:

Question: {query}

Instructions:
1. Provide detailed, evidence-based information
2. Cover all aspects of the question thoroughly
3. Use clear, organized formatting
4. Include important medical disclaimers
5. Be helpful and informative

Please answer this question to the best of your medical knowledge:"""
            
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready to answer any health questions"
