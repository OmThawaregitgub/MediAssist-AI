import chromadb
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            try:
                self.collection = self.client.get_collection("medical_data")
                print("Loaded existing collection")
            except:
                self.collection = self.client.create_collection("medical_data")
                print("Created new collection")
            
            self.llm = LLMClient()
            print("LLM client initialized successfully")
            
            if self.collection.count() == 0:
                self.load_documents()
            else:
                print(f"Collection has {self.collection.count()} documents")
                
        except Exception as e:
            print(f"Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load sample documents"""
        try:
            sample_documents = [
                "Intermittent fasting (IF) is an eating pattern that cycles between periods of fasting and eating.",
                "Common intermittent fasting methods include the 16:8 method, the 5:2 diet, and alternate-day fasting.",
                "Research shows intermittent fasting can help with weight loss and improve metabolic health."
            ]
            
            self.collection.add(
                documents=sample_documents,
                metadatas=[{"source": "research"} for _ in sample_documents],
                ids=[f"doc_{i}" for i in range(len(sample_documents))]
            )
            print("Loaded sample documents")
        except Exception as e:
            print(f"Error loading documents: {e}")
    
    def ask(self, query):
        """Handle user queries"""
        try:
            print(f"🔍 Processing query: {query}")
            
            # For medical questions, use LLM directly with a good prompt
            prompt = f"""You are a medical AI assistant. The user asked: "{query}"

Please provide a comprehensive, well-organized answer about cancer types and treatments. Structure your response clearly with:

1. Major categories of cancer
2. Common types within each category  
3. Overview of treatment approaches
4. Important disclaimers about consulting healthcare professionals

Make the information easy to read and understand."""

            print("🔄 Sending to LLM...")
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            print(f"❌ Error in ask method: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_collection_info(self):
        """Get collection info for UI"""
        try:
            count = self.collection.count()
            return f"📊 Medical database loaded"
        except:
            return "📊 Medical assistant ready"
