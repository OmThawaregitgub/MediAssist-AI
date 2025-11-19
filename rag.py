# rag.py

import chromadb
from llm import GeminiLLM

class RAGPipeline:
    def __init__(self, persist_dir="./chroma_db", collection_name="my_rag"):

        self.client = chromadb.PersistentClient(path=persist_dir)

        # ALWAYS safe way to avoid corrupted collection configs
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  
            )
        except Exception:
            # If corrupted, delete and recreate
            self.client.delete_collection(collection_name)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

        self.llm = GeminiLLM()

    # ---- Add document to vector store ----
    def add_document(self, doc_id: str, text: str):
        emb = self.llm.embed(text)
        self.collection.add(
            ids=[doc_id],
            embeddings=[emb],
            documents=[text],
        )

    # ---- RAG Query ----
    def ask(self, query: str) -> str:
        q_emb = self.llm.embed(query)

        # Retrieve top matches
        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=3
        )

        retrieved_docs = results["documents"][0]

        context = "\n\n".join(retrieved_docs)

        final_prompt = f"""
You are MediAssist AI, a medical RAG assistant.

Use the context below to answer accurately and concisely.

Context:
{context}

Question:
{query}

Answer:
"""

        return self.llm.generate(final_prompt)
