import chromadb
import os
import sys
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection("medical_data")
                print("Loaded existing collection")
            except:
                self.collection = self.client.create_collection("medical_data")
                print("Created new collection")
            
            # Initialize LLM client
            self.llm = LLMClient()
            print("LLM client initialized successfully")
            
            # Check if collection has documents, if not, load them
            if self.collection.count() == 0:
                print("Loading sample documents...")
                self.load_documents()
            else:
                print(f"Collection already has {self.collection.count()} documents")
                
        except Exception as e:
            print(f"Error initializing RAGPipeline: {e}")
            raise e
    
    def load_documents(self):
        """Load sample documents into the vector database"""
        try:
            # Sample medical documents about intermittent fasting
            sample_documents = [
                "Intermittent fasting (IF) is an eating pattern that cycles between periods of fasting and eating. It doesn't specify which foods to eat but rather when you should eat them.",
                "Common intermittent fasting methods include the 16:8 method (fasting for 16 hours, eating within an 8-hour window), the 5:2 diet (eating normally for 5 days, restricting calories for 2 days), and alternate-day fasting.",
                "Research shows intermittent fasting can help with weight loss by reducing calorie intake and increasing metabolism. Studies indicate 3-8% weight loss over 3-24 weeks.",
                "Intermittent fasting may improve insulin sensitivity and reduce blood sugar levels. Some studies show reductions in insulin resistance in prediabetic individuals.",
                "Time-restricted feeding, a form of intermittent fasting, has shown benefits for metabolic health including improved cholesterol levels, blood pressure, and inflammatory markers.",
                "Intermittent fasting appears to be safe for most healthy adults, but may not be suitable for individuals with diabetes, eating disorders, or pregnant women without medical supervision.",
                "Studies suggest intermittent fasting can trigger autophagy, a cellular cleanup process that may have anti-aging and disease-prevention benefits.",
                "The 16:8 method is one of the most popular and sustainable intermittent fasting approaches, typically involving skipping breakfast and consuming all meals within an 8-hour window like 12 pm to 8 pm."
            ]
            
            sample_metadatas = [{"source": "medical_research", "type": "fasting_info"} for _ in sample_documents]
            sample_ids = [f"doc_{i}" for i in range(len(sample_documents))]
            
            self.collection.add(
                documents=sample_documents,
                metadatas=sample_metadatas,
                ids=sample_ids
            )
            print(f"Successfully loaded {len(sample_documents)} sample documents")
            
        except Exception as e:
            print(f"Error loading documents: {e}")
    
    def is_simple_query(self, query):
        """Check if query is simple/greeting that doesn't need RAG"""
        simple_queries = [
            "hi", "hello", "hey", "good morning", "good afternoon", 
            "good evening", "how are you", "what's up", "hey there",
            "hi there", "hello there", "greetings"
        ]
        
        query_lower = query.lower().strip()
        return any(simple in query_lower for simple in simple_queries)
    
    def is_medical_query(self, query):
        """Check if query is related to medical topics"""
        medical_keywords = [
            "fasting", "diet", "weight", "diabetes", "metabolic", "insulin",
            "health", "medical", "treatment", "therapy", "symptom", "disease",
            "cancer", "blood", "cholesterol", "pressure", "fast", "obesity",
            "metabolism", "clinical", "study", "research", "patient"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in medical_keywords)
    
    def ask(self, query):
        """Main method to handle user queries"""
        try:
            print(f"Processing query: {query}")
            
            # 1. Check if LLM is initialized
            if not hasattr(self, 'llm') or self.llm is None:
                return "Error: AI model not properly initialized. Please refresh the page."
            
            # 2. Handle simple greetings directly with LLM
            if self.is_simple_query(query):
                print("Detected simple query - using LLM directly")
                prompt = f"""The user said: "{query}"
                
                Respond in a friendly, welcoming manner as a medical AI assistant. Keep it brief and warm."""
                return self.llm.generate(prompt)
            
            # 3. For ALL medical queries, use LLM with general knowledge
            if self.is_medical_query(query):
                print("Detected medical query - using LLM with general medical knowledge")
                
                # Try to get some context first, but don't rely on it
                context = ""
                try:
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=2
                    )
                    
                    if results and 'documents' in results and results['documents']:
                        documents_list = results['documents']
                        if documents_list and len(documents_list) > 0:
                            retrieved_docs = documents_list[0]
                            if retrieved_docs and len(retrieved_docs) > 0:
                                for doc in retrieved_docs:
                                    if doc and str(doc).strip():
                                        context += str(doc) + "\n\n"
                except Exception as e:
                    print(f"Error retrieving documents: {e}")
                    context = ""
                
                # Create prompt that works with or without context
                if context and context.strip():
                    prompt = f"""You are a medical AI assistant. The user asked: "{query}"

Some potentially relevant medical information:
{context}

Please provide a comprehensive, evidence-based answer. If the context above is not directly relevant to the question, rely on your general medical knowledge to provide a helpful response.

Format your answer in a clear, organized way that's easy to understand."""
                else:
                    # No relevant context found, use LLM's general knowledge
                    prompt = f"""You are a medical AI assistant specializing in healthcare information.

User Question: {query}

Please provide a comprehensive, evidence-based answer using your medical knowledge. Format the response in a clear, organized way that's easy for the user to understand.

If discussing treatments, mention that users should consult healthcare professionals for personalized medical advice."""
                
                return self.llm.generate(prompt)
            
            # 4. For non-medical queries
            print("Detected non-medical query - using LLM directly")
            prompt = f"""The user asked: "{query}"
            
            Respond as a helpful AI assistant. If this is outside your medical scope, politely mention that you specialize in healthcare information."""
            return self.llm.generate(prompt)
            
        except Exception as e:
            print(f"Error in ask method: {e}")
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def get_collection_info(self):
        """Get information about the collection for the UI"""
        try:
            count = self.collection.count()
            return f"📊 Database loaded with {count} medical documents"
        except Exception as e:
            return f"📊 Medical database loaded"
