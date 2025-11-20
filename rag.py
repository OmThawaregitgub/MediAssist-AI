import chromadb
import os
import shutil
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            # COMPLETELY remove old database to fix schema issues
            if os.path.exists(persist_directory):
                print("🔄 Removing old database due to schema conflict...")
                shutil.rmtree(persist_directory)
                print("✅ Old database removed")
            
            # Create fresh database
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.create_collection("medical_data")
            print("✅ New collection created")
            
            # Initialize LLM
            self.llm = LLMClient()
            print("✅ LLM initialized")
            
            # Load some basic documents
            self.load_documents()
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load basic medical documents"""
        try:
            documents = [
                "Intermittent fasting cycles between eating and fasting periods.",
                "Common fasting methods: 16:8, 5:2, alternate-day fasting.",
                "Fasting may improve insulin sensitivity and aid weight loss."
            ]
            
            self.collection.add(
                documents=documents,
                metadatas=[{"type": "medical"} for _ in documents],
                ids=[f"id_{i}" for i in range(len(documents))]
            )
            print("✅ Documents loaded")
        except Exception as e:
            print(f"⚠️ Could not load documents: {e}")
    
    def ask(self, query):
        """Handle user queries"""
        try:
            # Simple prompt that works
            if query.lower().strip() in ["hi", "hello", "hey"]:
                return "Hello! 👋 I'm MediAssist AI. How can I help you today?"
            
            # For other questions, use simple prompt
            prompt = f"Please answer this question: {query}"
            return self.llm.generate(prompt)
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready"
