# rag.py - Updated version
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class RAGPipeline:
    def __init__(self, collection_name: str = "medical_documents") -> None:
        """
        Initialize the RAGPipeline with multiple vector databases
        """
        try:
            # Initialize embedding model for new documents
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Setup persistent ChromaDB for user-uploaded documents
            chroma_path = "chroma_db"
            if not os.path.exists(chroma_path):
                os.makedirs(chroma_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection for user documents
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize PubMed vector database client
            self.pubmed_client = None
            self.pubmed_collection = None
            
            # Check if PubMed database exists
            pubmed_path = "./chroma_pubmed"
            if os.path.exists(pubmed_path):
                try:
                    self.pubmed_client = chromadb.PersistentClient(
                        path=pubmed_path,
                        settings=Settings(anonymized_telemetry=False)
                    )
                    
                    # Get PubMed collection
                    self.pubmed_collection = self.pubmed_client.get_collection(
                        name="pubmed_articles"
                    )
                    
                    pubmed_count = self.pubmed_collection.count()
                    print(f"✅ PubMed Database Initialized: {pubmed_count} articles")
                    
                except Exception as e:
                    print(f"⚠️ PubMed database not accessible: {e}")
            
            print("✅ RAG Pipeline Initialized with multiple databases")
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    # In rag.py, add this method to the RAGPipeline class:
    def search_all(self, query: str, top_k: int = 3):
        """
        Search across ALL available databases
        Returns combined results from PubMed and user documents
        """
        all_results = []
        
        # 1. Search PubMed database (if available)
        pubmed_results = self.search_pubmed(query, top_k)
        if pubmed_results:
            all_results.extend(pubmed_results)
            print(f"🔍 Found {len(pubmed_results)} PubMed results")
        
        # 2. Search user documents database
        user_results = self.search_user_docs(query, top_k)
        if user_results:
            all_results.extend(user_results)
            print(f"🔍 Found {len(user_results)} user document results")
        
        # Sort all results by similarity score (highest first)
        all_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Return top_k combined results
        return all_results[:top_k]

    def search_pubmed(self, query: str, top_k: int = 3):
        """Search specifically in PubMed database"""
        if not self.pubmed_collection:
            return []
        
        try:
            # Search in PubMed collection
            results = self.pubmed_collection.query(
                query_texts=[query],
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
                        'rank': i + 1,
                        'source': 'pubmed'
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ PubMed search error: {e}")
            return []

    def search_user_docs(self, query: str, top_k: int = 3):
        """Search in user documents database"""
        try:
            # Generate query embedding for user docs
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in user collection
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
                        'rank': i + 1,
                        'source': 'user_docs'
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ User docs search error: {e}")
            return []
        
        
    
    def search_user_docs(self, query: str, top_k: int = 3):
        """Search in user documents database"""
        try:
            # Generate query embedding for user docs
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in user collection
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
                        'rank': i + 1,
                        'source': 'user_docs'
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ User docs search error: {e}")
            return []
    
    def add_documents(self, documents: list, metadatas: list = None, ids: list = None):
        """Add documents to the user vector database"""
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
            
            print(f"✅ Added {len(documents)} documents to user collection")
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            raise e
    
    def search(self, query: str, top_k: int = 3):
        """Legacy search - searches all databases"""
        return self.search_all(query, top_k)
    
    def count_documents(self):
        """Return total documents count from all databases"""
        total_count = 0
        db_info = {}
        
        # Count user documents
        try:
            user_count = self.collection.count()
            total_count += user_count
            db_info['user_docs'] = user_count
        except:
            db_info['user_docs'] = 0
        
        # Count PubMed documents
        try:
            if self.pubmed_collection:
                pubmed_count = self.pubmed_collection.count()
                total_count += pubmed_count
                db_info['pubmed'] = pubmed_count
            else:
                db_info['pubmed'] = 0
        except:
            db_info['pubmed'] = 0
        
        db_info['total'] = total_count
        return db_info
    
    def get_collection_info(self):
        """Get information about all collections"""
        db_counts = self.count_documents()
        
        return {
            "total_documents": db_counts['total'],
            "pubmed_articles": db_counts.get('pubmed', 0),
            "user_documents": db_counts.get('user_docs', 0),
            "has_pubmed": db_counts.get('pubmed', 0) > 0
        }