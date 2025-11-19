# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS

class RAGPipeline:
    def __init__(self, collection_name="knowledge_base"):
        # Use in-memory client for Streamlit Cloud
        self.client = chromadb.EphemeralClient()
        
        # Let ChromaDB handle embeddings automatically
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "General knowledge database"}
        )

        self.llm = GeminiLLM()
        
        # Initialize with PubMed data
        self._initialize_pubmed_data()

    def _initialize_pubmed_data(self):
        """Add PubMed data for medical questions"""
        try:
            if self.collection.count() == 0:
                documents = []
                metadatas = []
                ids = []
                
                for record in RECORDS:
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
                        "source": "pubmed",
                        "category": "medical"
                    })
                    ids.append(f"pubmed_{record['pmid']}")
                
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
        except Exception as e:
            print(f"Note: {e}")

    def ask(self, query: str) -> str:
        try:
            # ALWAYS pass the query to LLM, no hardcoded responses
            # Check if it's a medical-related question
            is_medical = self._is_medical_question(query.lower())
            
            if is_medical:
                # Use RAG for medical questions - search our database
                results = self.collection.query(
                    query_texts=[query],
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

                    # Pass both the query and research context to LLM
                    final_prompt = f"""User Question: {query}

I have found some relevant medical research that might help answer this question:

RESEARCH CONTEXT:
{context}

Please provide a helpful answer to the user's question. You can reference the research above if it's helpful."""

                    answer = self.llm.generate(final_prompt)
                    return answer + sources_info
            
            # For non-medical questions or when no relevant medical context found
            # Directly pass the user query to LLM
            return self.llm.generate(query)
                
        except Exception as e:
            # If anything fails, still pass to LLM
            return self.llm.generate(query)

    def _is_medical_question(self, query: str) -> bool:
        """Check if the question is medical-related"""
        medical_keywords = [
            'cancer', 'medical', 'health', 'disease', 'treatment', 'symptom',
            'diagnosis', 'patient', 'clinical', 'therapy', 'drug', 'medicine',
            'hospital', 'doctor', 'nurse', 'surgery', 'prescription', 'vaccine',
            'infection', 'virus', 'bacteria', 'pain', 'fever', 'blood', 'heart',
            'lung', 'liver', 'kidney', 'brain', 'diabetes', 'covid', 'tumor',
            'chemotherapy', 'radiation', 'breast', 'prostate', 'lung', 'colon',
            'leukemia', 'lymphoma', 'melanoma', 'pancreatic', 'ovarian'
        ]
        
        return any(keyword in query for keyword in medical_keywords)

    def get_collection_info(self):
        """Check how many documents are in the collection"""
        try:
            count = self.collection.count()
            return f"Knowledge base loaded with {count} documents"
        except Exception as e:
            return "AI assistant is ready"
