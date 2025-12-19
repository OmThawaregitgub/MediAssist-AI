# reg.py
import chromadb as v_db
from chromadb.config import Settings as setting
import os
import hashlib
from typing import List, Dict, Any
import numpy as np

class RegPipeline:
    def __init__(self, collection_name: str = "medical_documents") -> None:
        """
        Initialize the retrieval augmentation pipeline.
        """
        try:
            # Set up ChromaDB client
            chroma_path = "chroma_db"
            if not os.path.exists(chroma_path):
                os.makedirs(chroma_path)

            self.client = v_db.PersistentClient(
                path=chroma_path,
                settings=setting(anonymized_telemetry=False)
            )

            # Get or create main collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Try to get the PubMed collection
            try:
                self.pubmed_collection = self.client.get_collection(name="pubmed_collection")
                pubmed_count = self.pubmed_collection.count()
                print(f"✅ PubMed Database: {pubmed_count} articles")
            except Exception as e:
                print(f"ℹ️ PubMed collection not found: {e}")
                self.pubmed_collection = None

        except Exception as exception:
            print(f"An error occurred during initialization: {exception}")
            raise exception

    def search_all(self, query: str, top_k: int = 5, use_both: bool = True) -> list:
        """
        Search across collections.
        """
        try:
            # Use ChromaDB's built-in embeddings
            all_results = []
            
            # Search main collection
            main_count = self.collection.count()
            if main_count > 0:
                main_results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k if not use_both else top_k * 2
                )
                if main_results and main_results['ids']:
                    for i in range(len(main_results['ids'][0])):
                        result = {
                            'id': main_results['ids'][0][i],
                            'document': main_results['documents'][0][i],
                            'metadata': main_results['metadatas'][0][i] if main_results['metadatas'] and i < len(main_results['metadatas'][0]) else {},
                            'distance': main_results['distances'][0][i],
                            'source': 'main_collection'
                        }
                        all_results.append(result)
            
            # Search PubMed collection if enabled
            if use_both and self.pubmed_collection and self.pubmed_collection.count() > 0:
                pubmed_results = self.pubmed_collection.query(
                    query_texts=[query],
                    n_results=top_k if main_count == 0 else top_k * 2
                )
                if pubmed_results and pubmed_results['ids']:
                    for i in range(len(pubmed_results['ids'][0])):
                        result = {
                            'id': pubmed_results['ids'][0][i],
                            'document': pubmed_results['documents'][0][i],
                            'metadata': pubmed_results['metadatas'][0][i] if pubmed_results['metadatas'] and i < len(pubmed_results['metadatas'][0]) else {},
                            'distance': pubmed_results['distances'][0][i],
                            'source': 'pubmed_collection'
                        }
                        all_results.append(result)
            
            # Sort by distance (lower is better)
            all_results.sort(key=lambda x: x['distance'])
            return all_results[:top_k]
            
        except Exception as e:
            print(f"❌ Error in search: {e}")
            return []

    def add_document(self, text: str, metadata: Dict = None):
        """Add a document to the collection"""
        try:
            doc_id = f"doc_{hashlib.md5(text.encode()).hexdigest()[:16]}"
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata] if metadata else [{}]
            )
            return True
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get database statistics.
        """
        stats = {
            'main_collection': 0,
            'pubmed_collection': 0,
            'total': 0
        }
        
        try:
            stats['main_collection'] = self.collection.count()
            if self.pubmed_collection:
                stats['pubmed_collection'] = self.pubmed_collection.count()
            stats['total'] = stats['main_collection'] + stats['pubmed_collection']
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
        
        return stats
