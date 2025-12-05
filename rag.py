import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class RAGPipeline:
    def __init__(self, collection_name: str = "medical_documents") -> None:
        """
        Initialize the RAGPipeline with persistent storage
        """
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Setup persistent ChromaDB
            chroma_path = "chroma_db"
            if not os.path.exists(chroma_path):
                os.makedirs(chroma_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            print("✅ RAG Pipeline Initialized")
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def add_documents(self, documents: list, metadatas: list = None, ids: list = None):
        """Add documents to the vector database"""
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Prepare metadata
            if metadatas is None:
                metadatas = [{"type": "general"}] * len(documents)
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Added {len(documents)} documents to collection")
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            raise e
    
    def search(self, query: str, top_k: int = 3):
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, meta, dist) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'text': doc,
                        'metadata': meta or {},
                        'similarity': float(1 - dist),
                        'rank': i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def count_documents(self):
        """Return the number of documents in the collection"""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"❌ Error counting documents: {e}")
            return 0
    
    def get_collection_info(self):
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return {"document_count": 0, "collection_name": "unknown"}