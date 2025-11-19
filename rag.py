# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS

class RAGPipeline:
    def __init__(self, collection_name="knowledge_base"):
        self.client = chromadb.EphemeralClient()
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.llm = GeminiLLM()
        self._initialize_pubmed_data()

    def _initialize_pubmed_data(self):
        """Add PubMed data"""
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
                            "title": record['title"],
                            "journal": record['journal'], 
                            "publication_date": record['publication_date'],
                            "source": "pubmed"
                        }]
                    )
        except Exception as e:
            print(f"Database note: {e}")

    def ask(self, query: str) -> str:
        try:
            # ALWAYS pass query to LLM first for natural conversation
            # Check if it might be a medical question
            if self._is_medical_question(query.lower()):
                # Try to find relevant research
                results = self.collection.query(query_texts=[query], n_results=2)
                retrieved_docs = results["documents"][0] if results["documents"] else []
                retrieved_metadatas = results["metadatas"][0] if results["metadatas"] else []

                if retrieved_docs:
                    context = "\n\n".join(retrieved_docs)
                    sources_info = "\n\n📚 **Research Sources:**\n"
                    for meta in retrieved_metadatas:
                        sources_info += f"• {meta.get('title', 'Unknown')} ({meta.get('journal', 'Unknown journal')}, {meta.get('publication_date', 'Unknown year')})\n"
                    
                    enhanced_prompt = f"Question: {query}\n\nRelevant Research:\n{context}\n\nPlease answer the question:"
                    answer = self.llm.generate(enhanced_prompt)
                    return answer + sources_info
            
            # For non-medical or when no research found, just use LLM
            return self.llm.generate(query)
                
        except Exception as e:
            # Fallback to direct LLM
            return self.llm.generate(query)

    def _is_medical_question(self, query: str) -> bool:
        """Check if question might be medical"""
        medical_keywords = ['cancer', 'medical', 'health', 'disease', 'treatment', 'symptom', 'diagnosis', 'patient']
        return any(keyword in query for keyword in medical_keywords)

    def get_collection_info(self):
        try:
            count = self.collection.count()
            return f"Loaded {count} research articles"
        except:
            return "Assistant ready"
