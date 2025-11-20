import chromadb
from llm import LLMClient

class RAGPipeline:
    def __init__(self):
        try:
            # Use in-memory client with unique collection name
            self.client = chromadb.Client()
            
            # Create unique collection name to avoid conflicts
            collection_name = f"medical_data_{id(self)}"
            self.collection = self.client.create_collection(collection_name)
            
            # Initialize LLM
            self.llm = LLMClient()
            
            print("✅ MediAssist AI Initialized Successfully")
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def ask(self, query):
        """Handle user queries"""
        try:
            query_lower = query.lower().strip()
            
            # Handle greetings
            if any(word in query_lower for word in ["hi", "hello", "hey"]):
                return "Hello! 👋 I'm MediAssist AI. How can I help you with medical questions today?"
            
            if "how are you" in query_lower:
                return "I'm doing well, thank you! Ready to assist you with medical information."
            
            # Handle medical questions
            if any(word in query_lower for word in ["cancer", "fasting", "diabetes", "treatment", "medical", "health"]):
                prompt = f"Please provide clear, helpful information about: {query}"
            else:
                prompt = f"Please answer this question: {query}"
            
            return self.llm.generate(prompt)
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready to Help"
