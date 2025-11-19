# rag.py

import chromadb
from llm import GeminiLLM

class RAGPipeline:
    def __init__(self, collection_name="my_rag"):
        # ❗ Use in-memory client instead of PersistentClient
        self.client = chromadb.Client()

        # Chroma Cloud-safe collection creation
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.llm = GeminiLLM()

    def ask(self, query: str) -> str:
        # Embed query using Gemini
        emb = self.llm.embed(query)

        # Retrieve from Chroma
        results = self.collection.query(
            query_embeddings=[emb],
            n_results=3
        )

        context = "\n".join(results["documents"][0]) if len(results["documents"]) else ""

        prompt = f"""
Use the following context to answer the question:

Context:
{context}

Question:
{query}

Answer clearly and concisely.
"""

        return self.llm.generate(prompt)
