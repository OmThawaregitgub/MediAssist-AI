import chromadb
import os
from llm import LLMClient

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("medical_data")
        except:
            self.collection = self.client.create_collection("medical_data")
        
        # Initialize LLM client
        self.llm = LLMClient()
        
        # Check if collection has documents, if not, load them
        if self.collection.count() == 0:
            self.load_documents()
    
    def load_documents(self):
        """Load documents into the vector database"""
        # Add your document loading logic here
        # For now, we'll add some placeholder text
        try:
            # Example documents - replace with your actual document loading
            sample_documents = [
                "Intermittent fasting (IF) is an eating pattern that cycles between periods of fasting and eating.",
                "Time-restricted feeding involves daily fasting periods, typically 16-18 hours.",
                "Studies show intermittent fasting may improve insulin sensitivity in prediabetic individuals.",
                "Common IF methods include 16:8, 5:2, and alternate-day fasting protocols.",
                "Research indicates IF can lead to weight loss and improved metabolic markers."
            ]
            
            sample_metadatas = [{"source": "medical_research"} for _ in sample_documents]
            sample_ids = [f"doc_{i}" for i in range(len(sample_documents))]
            
            self.collection.add(
                documents=sample_documents,
                metadatas=sample_metadatas,
                ids=sample_ids
            )
            print(f"Loaded {len(sample_documents)} sample documents")
        except Exception as e:
            print(f"Error loading documents: {e}")
    
    def ask(self, query):
        """Main method to handle user queries"""
        try:
            # 1. Retrieve relevant documents from ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            # Debug: Print results to understand structure
            print("ChromaDB results:", results)
            
            # 2. Safely extract context from retrieved documents
            context = ""
            if results and 'documents' in results:
                documents_list = results['documents']
                if documents_list and len(documents_list) > 0:
                    retrieved_docs = documents_list[0]
                    if retrieved_docs and len(retrieved_docs) > 0:
                        for doc in retrieved_docs:
                            if doc:  # Check if document is not None or empty
                                context += str(doc) + "\n\n"
            
            # 3. Create prompt with context
            if context and context.strip():  # Check if context is not empty
                prompt = f"""Based on the following medical research context, provide a helpful answer to the user's question. 
If the context doesn't contain enough information to answer fully, acknowledge this and provide general information.

Context:
{context}

Question: {query}

Please provide a clear, evidence-based answer:"""
            else:
                # No relevant documents found
                prompt = f"""Answer the following medical question based on your knowledge. 
Please indicate if this is outside specific research scope.

Question: {query}

Provide a helpful answer:"""
            
            # 4. Generate answer using LLM
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question. Please try again. Error: {str(e)}"
