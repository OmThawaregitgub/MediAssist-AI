# rag.py
import chromadb
from llm import GeminiLLM

class RAGPipeline:
    def __init__(self, persist_dir="./chroma_db", collection_name="my_rag"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)
        self.llm = GeminiLLM()

    def ask(self, query: str) -> str:
        results = self.collection.query(
            query_texts=[query],
            n_results=3
        )

        docs = results.get("documents", [[]])[0]
        context = "\n\n".join(docs) if docs else "No relevant context found."

        prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question: {query}

Answer clearly and concisely:
"""

        return self.llm.generate(prompt)
