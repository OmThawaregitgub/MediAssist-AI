# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS

class RAGPipeline:
    def __init__(self, collection_name="medical_rag"):
        # Use in-memory client for Streamlit Cloud (no disk storage)
        self.client = chromadb.EphemeralClient()
        
        # Let ChromaDB handle embeddings automatically with its default model
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Breast cancer research database"}
        )

        self.llm = GeminiLLM()
        
        # Initialize with PubMed data
        self._initialize_pubmed_data()

    def _initialize_pubmed_data(self):
        """Add PubMed breast cancer research data to ChromaDB"""
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                documents = []
                metadatas = []
                ids = []
                
                for record in RECORDS:
                    # Create document text from title and abstract
                    abstract_text = ""
                    if isinstance(record['abstract'], dict):
                        abstract_text = " ".join(record['abstract'].values())
                    elif isinstance(record['abstract'], str):
                        abstract_text = record['abstract']
                    
                    document_text = f"Title: {record['title']}\nAbstract: {abstract_text}"
                    
                    documents.append(document_text)
                    metadatas.append({
                        "pmid": record['pmid'],
                        "title": record['title'],
                        "journal": record['journal'], 
                        "authors": record['authors'],
                        "publication_date": record['publication_date'],
                        "source": "pubmed"
                    })
                    ids.append(f"pubmed_{record['pmid']}")
                
                # Add all documents at once
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
        except Exception as e:
            print(f"Note: {e}")

    def ask(self, query: str) -> str:
        try:
            # Handle greetings directly
            if query.lower().strip() in ['hi', 'hello', 'hey', 'hola', 'hi!', 'hello!']:
                return "Hello! 👋 I'm MediAssist AI, your medical research assistant. I specialize in breast cancer research and can help answer questions using our database of medical studies. What would you like to know about breast cancer?"
            
            # Use ChromaDB's built-in embeddings (automatic)
            results = self.collection.query(
                query_texts=[query],  # ChromaDB handles embedding internally
                n_results=3
            )

            retrieved_docs = results["documents"][0] if results["documents"] else []
            retrieved_metadatas = results["metadatas"][0] if results["metadatas"] else []

            if retrieved_docs:
                context = "\n\n".join(retrieved_docs)
                
                # Create sources information
                sources_info = "\n\n📚 **Research Sources:**\n"
                for meta in retrieved_metadatas:
                    title = meta.get('title', 'Unknown')
                    journal = meta.get('journal', 'Unknown journal')
                    year = meta.get('publication_date', 'Unknown year')
                    sources_info += f"• {title} ({journal}, {year})\n"

                final_prompt = f"""You are MediAssist AI, a medical research assistant specializing in breast cancer. 

Based on the following research context, provide a clear, evidence-based answer to the question.

RESEARCH CONTEXT:
{context}

QUESTION: {query}

Please provide a helpful, accurate answer based on the research above:"""

                answer = self.llm.generate(final_prompt)
                return answer + sources_info
            else:
                # No relevant documents found
                return self.llm.generate(f"Please answer this question about breast cancer or medical research: {query}")
                
        except Exception as e:
            # Fallback response
            return f"Hello! I'm MediAssist AI. I can help with breast cancer research questions. Please ask me about treatments, risk factors, or recent studies."

    def get_collection_info(self):
        """Check how many documents are in the collection"""
        try:
            count = self.collection.count()
            return f"Medical database loaded with {count} research articles"
        except Exception as e:
            return "Medical research database is ready"
