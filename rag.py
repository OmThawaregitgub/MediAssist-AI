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
            
            # Initialize LLM client - THIS IS THE CRITICAL FIX
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
    
    def ask(self, query):
        """Main method to handle user queries"""
        try:
            print(f"Processing query: {query}")
            
            # 1. Check if LLM is initialized
            if not hasattr(self, 'llm') or self.llm is None:
                return "Error: AI model not properly initialized. Please refresh the page."
            
            # 2. Retrieve relevant documents from ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            # 3. Safely extract context from retrieved documents
            context = ""
            if results and 'documents' in results and results['documents']:
                documents_list = results['documents']
                if documents_list and len(documents_list) > 0:
                    retrieved_docs = documents_list[0]
                    if retrieved_docs and len(retrieved_docs) > 0:
                        for doc in retrieved_docs:
                            if doc and str(doc).strip():
                                context += str(doc) + "\n\n"
            
            print(f"Retrieved context length: {len(context)}")
            
            # 4. Create prompt with context
            if context and context.strip():
                prompt = f"""Based on the following medical research about intermittent fasting, provide a helpful and evidence-based answer to the user's question.

Medical Research Context:
{context}

User Question: {query}

Please provide a clear, accurate answer based on the research context. If the context doesn't fully address the question, acknowledge this and provide the most relevant information available."""
            else:
                # No relevant documents found
                prompt = f"""You are a medical AI assistant specializing in intermittent fasting and metabolic health. 

User Question: {query}

Please provide a helpful, evidence-based answer about intermittent fasting. If you cannot provide specific medical advice, suggest consulting a healthcare professional."""

            # 5. Generate answer using LLM
            print("Generating response with LLM...")
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            print(f"Error in ask method: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try again or rephrase your question."
