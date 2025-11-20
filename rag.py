import chromadb
from llm import LLMClient

class RAGPipeline:
    def __init__(self):
        try:
            self.client = chromadb.Client()
            self.collection = self.client.create_collection("medical_data")
            self.llm = LLMClient()
            self.load_documents()
            print("✅ MediAssist AI Ready")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise e
    
    def load_documents(self):
        """Load basic medical documents"""
        try:
            documents = [
                "Intermittent fasting cycles between eating and fasting periods.",
                "Common fasting methods: 16:8, 5:2, alternate-day fasting."
            ]
            self.collection.add(
                documents=documents,
                metadatas=[{"type": "medical"} for _ in documents],
                ids=[f"doc_{i}" for i in range(len(documents))]
            )
        except:
            pass
    
    def ask(self, query):
        """Handle user queries"""
        try:
            query_lower = query.lower().strip()
            
            # Handle greetings
            if query_lower in ["hi", "hello", "hey"]:
                return "Hello! 👋 I'm MediAssist AI. How can I help you with medical questions today?"
            
            if "how are you" in query_lower:
                return "I'm doing well, thank you! Ready to assist you with medical information."
            
            # Handle medical questions
            prompt = f"Please provide helpful medical information about: {query}"
            return self.llm.generate(prompt)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready"
