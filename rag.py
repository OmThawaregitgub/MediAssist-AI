import chromadb
from llm import LLMClient

class RAGPipeline:
    def __init__(self):
        try:
            # Use in-memory client to avoid file permission issues
            self.client = chromadb.Client()
            self.collection = self.client.create_collection("medical_data")
            print("✅ In-memory database created")
            
            # Initialize LLM
            self.llm = LLMClient()
            print("✅ LLM initialized")
            
            # Load basic documents
            self.load_documents()
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load basic medical documents"""
        try:
            documents = [
                "Intermittent fasting cycles between eating and fasting periods.",
                "Common fasting methods include 16:8, 5:2, and alternate-day fasting.",
                "Research shows intermittent fasting can help with weight loss and improve insulin sensitivity.",
                "Fasting may trigger autophagy, a cellular cleanup process.",
                "Time-restricted feeding involves eating within a specific daily window.",
                "Intermittent fasting is generally safe for healthy adults but may not be suitable for everyone.",
                "Always consult healthcare professionals before starting any fasting regimen."
            ]
            
            self.collection.add(
                documents=documents,
                metadatas=[{"type": "medical", "topic": "fasting"} for _ in documents],
                ids=[f"doc_{i}" for i in range(len(documents))]
            )
            print(f"✅ Loaded {len(documents)} medical documents")
        except Exception as e:
            print(f"⚠️ Could not load documents: {e}")
    
    def ask(self, query):
        """Handle user queries"""
        try:
            query_lower = query.lower().strip()
            
            # Simple greetings
            if query_lower in ["hi", "hello", "hey"]:
                return "Hello! 👋 I'm MediAssist AI. How can I help you with medical questions today?"
            
            if "how are you" in query_lower:
                return "I'm doing well, thank you! Ready to assist you with medical information. What would you like to know?"
            
            # For medical questions, try to use RAG first
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=2
                )
                
                # Build context if documents found
                context = ""
                if results.get('documents') and results['documents'][0]:
                    for doc in results['documents'][0]:
                        if doc:
                            context += f"• {doc}\n"
                
                if context:
                    prompt = f"""Based on this medical information:
{context}

Please answer this question: {query}

Provide a clear, helpful response."""
                else:
                    prompt = f"Please answer this medical question: {query}"
                    
            except Exception as rag_error:
                # If RAG fails, just use LLM directly
                print(f"⚠️ RAG failed, using LLM directly: {rag_error}")
                prompt = f"Please answer this question: {query}"
            
            response = self.llm.generate(prompt)
            return response
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_collection_info(self):
        return "🩺 Medical AI Assistant - Ready to Help"
