import chromadb
from llm import GeminiLLM

class RAGPipeline:
    def __init__(self, collection_name="my_rag"):

        # ⭐ Use in-memory client for Streamlit Cloud (NO local disk)
        self.client = chromadb.Client()

        # ⭐ Safe collection creation (no corruption possible)
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

        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=3
        )

        retrieved_docs = results["documents"][0] if results["documents"] else []

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
