import chromadb
import os
from llm import LLMClient  # Make sure you're importing your LLM client

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
        # This should read PDFs from the data folder and add to ChromaDB
        pass
    
    def ask(self, query):
        """Main method to handle user queries"""
        try:
            # 1. Retrieve relevant documents
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            # 2. Prepare context from retrieved documents
            context = ""
            if results['documents']:
                for doc in results['documents'][0]:
                    context += doc + "\n\n"
            
            # 3. Generate answer using LLM with context
            if context:
                prompt = f"""Based on the following medical context, answer the user's question. 
                If the context doesn't contain relevant information, say so.

                Context: {context}

                Question: {query}

                Answer:"""
            else:
                prompt = f"""Answer the following medical question based on your knowledge. 
                If you're not sure, indicate that this is outside the specific research scope.

                Question: {query}

                Answer:"""
            
            # 4. Call LLM with the prompt
            answer = self.llm.generate(prompt)
            return answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
