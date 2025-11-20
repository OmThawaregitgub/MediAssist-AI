import chromadb
import os
import shutil
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Get or create collection - handle existing collection properly
            try:
                self.collection = self.client.get_collection("medical_data")
                print("✅ Loaded existing collection")
            except Exception as e:
                print(f"🔄 Creating new collection: {e}")
                self.collection = self.client.create_collection("medical_data")
                print("✅ Created new collection")
            
            # Initialize LLM client
            self.llm = LLMClient()
            print("✅ LLM client initialized successfully")
            
            # Load documents if collection is empty
            if self.collection.count() == 0:
                print("📚 Loading documents...")
                self.load_documents()
            else:
                print(f"📊 Collection already has {self.collection.count()} documents")
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load sample medical documents"""
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
            print(f"✅ Loaded {len(documents)} documents")
        except Exception as e:
            print(f"⚠️ Could not load documents: {e}")
    
    def ask(self, query):
        """Handle ANY medical question using LLM's general knowledge"""
        try:
            print(f"🔍 User asked: {query}")
            
            # Use LLM directly for all questions - no restrictions
            prompt = f"""You are a medical AI assistant. Please provide a comprehensive, accurate answer to this medical question:

Question: {query}

Please provide:
1. Detailed, evidence-based information
2. Clear, organized formatting
3. Important medical disclaimers
4. Comprehensive coverage of the topic

Answer:"""
            
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            return f"Error processing your question: {str(e)}"
    
    def get_collection_info(self):
        """Get collection info for UI"""
        try:
            count = self.collection.count()
            return f"🩺 Medical AI Assistant - Ready to help (Database: {count} docs)"
        except:
            return "🩺 Medical AI Assistant - Ready to help"
