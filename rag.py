import chromadb
from llm import GeminiLLM # <-- Must successfully import this now

class RAGPipeline:
    def __init__(self, collection_name="my_rag"):

        # Use in-memory client for Streamlit Cloud (NO local disk)
        self.client = chromadb.Client()

        # Safe collection creation
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.llm = GeminiLLM()

    # ---- Add document to vector store ----
    def add_document(self, doc_id: str, text: str):
        # We must use the LLM to create an embedding first
        emb = self.llm.embed(text) 
        if emb:
            self.collection.add(
                ids=[doc_id],
                embeddings=[emb],
                documents=[text],
            )

    # ---- RAG Query ----
    def ask(self, query: str) -> str:
        q_emb = self.llm.embed(query)
        
        # Guard clause if embedding fails
        if q_emb is None:
            return "Error: Could not generate embedding for the query."

        results = self.collection.query(
            query_embeddings=[q_emb],
            n_results=3
        )

        retrieved_docs = results["documents"][0] if results["documents"] else []

        context = "\n\n".join(retrieved_docs)

        final_prompt = f"""
Use the following context to answer accurately and concisely.

Context:
{context}

Question:
{query}

Answer:
"""

        return self.llm.generate(final_prompt)
