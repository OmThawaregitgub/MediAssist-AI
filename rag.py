import chromadb
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            try:
                self.collection = self.client.get_collection("medical_data")
                print("✅ Loaded existing collection")
            except:
                self.collection = self.client.create_collection("medical_data")
                print("✅ Created new collection")
            
            self.llm = LLMClient()
            print("✅ Medical Assistant Ready")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            raise e
    
    def ask(self, query):
        """Handle all types of queries appropriately"""
        try:
            query_lower = query.lower().strip()
            
            # For greetings and simple questions, use simple prompt
            if any(word in query_lower for word in ["hi", "hello", "hey", "how are you", "good morning", "good afternoon"]):
                prompt = "Respond to this greeting in a friendly, welcoming way as a medical AI assistant. Keep it warm and brief: " + query
                
            # For medical questions, use detailed medical prompt
            elif any(word in query_lower for word in ["cancer", "fasting", "diabet", "treatment", "symptom", "disease", "health", "medical"]):
                prompt = f"""You are a helpful medical AI assistant. The user asked: "{query}"

Please provide a clear, helpful answer. Format it in an easy-to-read way with bullet points or sections if appropriate.

Remember to include a brief medical disclaimer about consulting healthcare professionals."""
                
            # For other questions
            else:
                prompt = f"""Respond helpfully to this question: "{query}"

If it's medical-related, provide useful information. If it's not medical, respond appropriately as an AI assistant."""
            
            return self.llm.generate(prompt)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready to help"
