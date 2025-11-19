# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS

class RAGPipeline:
    def __init__(self, collection_name="medical_rag"):
        # Use in-memory client for Streamlit Cloud
        self.client = chromadb.Client()
        
        # Let ChromaDB handle embeddings automatically
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.llm = GeminiLLM()
        
        # Initialize with PubMed data
        self._initialize_pubmed_data()

    def _initialize_pubmed_data(self):
        """Add PubMed breast cancer research data to ChromaDB"""
        try:
            if self.collection.count() == 0:
                for record in RECORDS:
                    abstract_text = ""
                    if isinstance(record['abstract'], dict):
                        abstract_text = " ".join(record['abstract'].values())
                    elif isinstance(record['abstract'], str):
                        abstract_text = record['abstract']
                    
                    document_text = f"Title: {record['title']}\nAbstract: {abstract_text}"
                    
                    self.collection.add(
                        ids=[f"pubmed_{record['pmid']}"],
                        documents=[document_text],
                        metadatas=[{
                            "pmid": record['pmid'],
                            "title": record['title'],
                            "journal": record['journal'], 
                            "authors": record['authors'],
                            "publication_date": record["publication_date"],
                            "source": "pubmed"
                        }]
                    )
                print(f"✅ Loaded {len(RECORDS)} PubMed articles")
        except Exception as e:
            print(f"Error loading PubMed data: {e}")

    def ask(self, query: str) -> str:
        try:
            # Use ChromaDB's automatic embedding
            results = self.collection.query(query_texts=[query], n_results=3)
            retrieved_docs = results["documents"][0] if results["documents"] else []
            retrieved_metadatas = results["metadatas"][0] if results["metadatas"] else []

            if retrieved_docs:
                context = "\n\n".join(retrieved_docs)
                sources_info = "\n\n📚 **Sources:**\n"
                for meta in retrieved_metadatas:
                    sources_info += f"• {meta.get('title', 'Unknown')} ({meta.get('journal', 'Unknown journal')}, {meta.get('publication_date', 'Unknown year')})\n"

                final_prompt = f"""You are MediAssist AI, a medical research assistant. Use the research context below to answer the question.

Context:
{context}

Question: {query}

Provide a clear, evidence-based answer:"""
                
                answer = self.llm.generate(final_prompt)
                return answer + sources_info
            else:
                # Direct response for general questions
                return self.llm.generate(f"Please answer this question: {query}")
                
        except Exception as e:
            return f"Error processing your question: {str(e)}"

    def get_collection_info(self):
        """Check how many documents are in the collection"""
        try:
            count = self.collection.count()
            return f"Medical database has {count} research articles"
        except Exception as e:
            return f"Error checking collection: {e}"

