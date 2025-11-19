# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS

class RAGPipeline:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("medical_data")
        self.llm = GeminiLLM()
        self._load_data()

    def _load_data(self):
        for record in RECORDS:
            abstract_text = " ".join(record['abstract'].values()) if isinstance(record['abstract'], dict) else record['abstract']
            doc_text = f"Title: {record['title']}\nAbstract: {abstract_text}"
            
            self.collection.add(
                documents=[doc_text],
                metadatas=[{"title": record['title'], "year": record['publication_date']}],
                ids=[f"doc_{record['pmid']}"]
            )

    def ask(self, query: str) -> str:
        try:
            # Always try to use medical research for relevant questions
            if any(word in query.lower() for word in ['cancer', 'medical', 'treatment']):
                results = self.collection.query(query_texts=[query], n_results=2)
                if results['documents']:
                    context = "\n".join(results['documents'][0])
                    sources = "\n\n📚 Sources:\n" + "\n".join([f"- {m['title']}" for m in results['metadatas'][0]])
                    prompt = f"Question: {query}\nContext: {context}\nAnswer:"
                    answer = self.llm.generate(prompt)
                    return answer + sources
            
            # For all other questions, use LLM directly
            return self.llm.generate(query)
            
        except:
            return self.llm.generate(query)

    def get_collection_info(self):
        return "Medical assistant ready"
