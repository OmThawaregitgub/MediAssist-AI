from sentence_transformers import SentenceTransformer
import chromadb as v_db
from chromadb.config import Settings as setting
import os
from Fetch_data.fetch_data import store_data 
import hashlib

class Reg_pipline:
    def __init__(self, collection_name: str = "medical_documents") -> None:
        """
        Initialize the retrieval augmentation pipeline.
        """
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Set up ChromaDB client
            chroma_path = "pumed"
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
                print(f"✅ PubMed Database Initialized: {pubmed_count} articles")
            except Exception as e:
                print(f"ℹ️ PubMed collection not found: {e}")
                self.pubmed_collection = None

        except Exception as exception:
            print(f"An error occurred during initialization: {exception}")
            raise exception

    def sync_to_main_collection(self) -> int:
        """
        Sync PubMed data to main collection.
        Returns number of documents synced.
        """
        try:
            if not self.pubmed_collection or self.pubmed_collection.count() == 0:
                print("❌ No PubMed data to sync")
                return 0
            
            # Get all from PubMed
            pubmed_data = self.pubmed_collection.get()
            
            if not pubmed_data['ids']:
                print("❌ PubMed collection is empty")
                return 0
            
            # Filter out documents already in main collection
            existing_ids = set()
            if self.collection.count() > 0:
                existing_data = self.collection.get()
                existing_ids = set(existing_data['ids'])
            
            new_docs = []
            new_metas = []
            new_ids = []
            
            for i, doc_id in enumerate(pubmed_data['ids']):
                # Create a modified ID for main collection
                main_id = f"main_{doc_id}"
                
                if main_id not in existing_ids:
                    new_ids.append(main_id)
                    new_docs.append(pubmed_data['documents'][i])
                    new_metas.append(pubmed_data['metadatas'][i] if pubmed_data['metadatas'] else {})
            
            if new_ids:
                self.collection.add(
                    ids=new_ids,
                    documents=new_docs,
                    metadatas=new_metas
                )
                print(f"✅ Synced {len(new_ids)} documents to main collection")
                return len(new_ids)
            else:
                print("ℹ️ All PubMed documents already in main collection")
                return 0
                
        except Exception as e:
            print(f"❌ Error syncing to main collection: {e}")
            return 0

    def search_all(self, query: str, top_k: int = 5, use_both: bool = True) -> list:
        """
        Search across collections.
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode([query])[0]
            
            all_results = []
            
            # Search main collection
            main_count = self.collection.count()
            if main_count > 0:
                main_results = self.collection.query(
                    query_embeddings=[query_embedding],
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
                    query_embeddings=[query_embedding],
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
            
            # If no results, fetch new data
            if not all_results:
                print(f"🔍 No results found. Fetching new data for: '{query}'")
                success = self._fetch_and_store(query)
                if success:
                    # Retry search
                    return self.search_all(query, top_k, use_both)
            
            # Sort by distance and return top_k
            all_results.sort(key=lambda x: x['distance'])
            return all_results[:top_k]
            
        except Exception as e:
            print(f"❌ Error in search: {e}")
            return []

    def _fetch_and_store(self, query: str, max_results: int = 20) -> bool:
        """
        Fetch and store new PubMed data.
        """
        try:
            print(f"📥 Fetching PubMed data for: '{query}'")
            data_fetcher = store_data(search_topic=query, max_results=max_results)
            
            # Store in both collections
            success_pubmed = data_fetcher.run(collection_name="pubmed_collection")
            success_main = data_fetcher.run(collection_name="medical_documents")
            
            if success_pubmed or success_main:
                # Refresh collection references
                try:
                    self.pubmed_collection = self.client.get_collection(name="pubmed_collection")
                except:
                    pass
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
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
        except:
            pass
        
        return stats