# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS  # Import your PubMed data

class RAGPipeline:
    def __init__(self, collection_name="medical_rag"):
        # Use in-memory client for Streamlit Cloud
        self.client = chromadb.Client()
        
        # Let ChromaDB handle embeddings automatically
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        self.llm = GeminiLLM()
        
        # Initialize with PubMed data
        self._initialize_pubmed_data()

    def _initialize_pubmed_data(self):
        """Add PubMed breast cancer research data to ChromaDB"""
        if self.collection.count() == 0:  # Only add if collection is empty
            for i, record in enumerate(RECORDS):
                # Create document text from title and abstract
                abstract_text = ""
                if isinstance(record['abstract'], dict):
                    # Join all abstract sections
                    abstract_text = " ".join(record['abstract'].values())
                elif isinstance(record['abstract'], str):
                    abstract_text = record['abstract']
                
                document_text = f"Title: {record['title']}\nAbstract: {abstract_text}"
                
                # Add to ChromaDB
                self.collection.add(
                    ids=[f"pubmed_{record['pmid']}"],
                    documents=[document_text],
                    metadatas=[{
                        "pmid": record['pmid'],
                        "title": record['title'],
                        "journal": record['journal'],
                        "authors": record['authors'],
                        "publication_date": record['publication_date'],
                        "source": "pubmed"
                    }]
                )
            print(f"✅ Loaded {len(RECORDS)} PubMed articles into ChromaDB")

    def ask(self, query: str) -> str:
        try:
            # Use ChromaDB's automatic embedding generation
            results = self.collection.query(
                query_texts=[query],  # ChromaDB handles the embedding
                n_results=3
            )

            retrieved_docs = results["documents"][0] if results["documents"] else []
            retrieved_metadatas = results["metadatas"][0] if results["metadatas"] else []

            if retrieved_docs:
                context = "\n\n".join(retrieved_docs)
                
                # Create sources information
                sources_info = "\n\n📚 **Sources:**\n"
                for meta in retrieved_metadatas:
                    sources_info += f"• {meta.get('title', 'Unknown')} ({meta.get('journal', 'Unknown journal')}, {meta.get('publication_date', 'Unknown year')})\n"

                final_prompt = f"""
You are MediAssist AI, a medical research assistant specializing in breast cancer research.

Use the following research context from PubMed articles to answer the question accurately. Provide evidence-based information.

Research Context:
{context}

Question: {query}

Provide a clear, evidence-based answer citing the available research:
"""
                answer = self.llm.generate(final_prompt)
                return answer + sources_info
            else:
                # Fallback to general medical knowledge
                general_prompt = f"""
You are MediAssist AI, a helpful medical assistant. Answer this medical question based on your knowledge:

Question: {query}

Provide a helpful and accurate response. If this is about breast cancer, mention that you're using general medical knowledge since no specific research was found:
"""
                return self.llm.generate(general_prompt)
                
        except Exception as e:
            return f"Error retrieving information: {str(e)}"

    def get_collection_info(self):
        """Check how many documents are in the collection"""
        try:
            count = self.collection.count()
            return f"Medical database has {count} research articles"
        except Exception as e:
            return f"Error checking collection: {e}"
