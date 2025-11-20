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
        """Handle queries with smart prompting"""
        try:
            query_lower = query.lower().strip()
            
            # For simple greetings - VERY SIMPLE PROMPT
            if any(word in query_lower for word in ["hi", "hello", "hey", "how are you"]):
                prompt = f"Say hello back to this greeting in a friendly way: '{query}'"
                
            # For medical questions - SIMPLE MEDICAL PROMPT  
            elif any(word in query_lower for word in ["cancer", "fasting", "diabet", "treatment", "health"]):
                prompt = f"Answer this medical question clearly and helpfully: '{query}'"
                
            # For everything else - SIMPLE GENERAL PROMPT
            else:
                prompt = f"Respond to this in a helpful way: '{query}'"
            
            response = self.llm.generate(prompt)
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready to help"
