# rag_pipeline.py
from sentence_transformers import SentenceTransformer
import chromadb as v_db
from chromadb.config import Settings as setting
import os
from Fetch_data.fetch_data import store_data
from typing import List, Dict, Any
from langchain.schema import Document
from rank_bm25 import BM25Okapi
import numpy as np
import logging

logger = logging.getLogger(__name__)

class AdvancedRAGPipeline:
    def __init__(self, collection_name: str = "medical_documents"):
        """
        Advanced RAG Pipeline with:
        - Query Transformation
        - RAG Fusion (Hybrid Search)
        - BM25 + Vector Search
        - Re-ranking
        """
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Set up ChromaDB
            chroma_path = "chroma_db"
            if not os.path.exists(chroma_path):
                os.makedirs(chroma_path)

            self.client = v_db.PersistentClient(
                path=chroma_path,
                settings=setting(anonymized_telemetry=False)
            )

            # Main collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # PubMed collection
            try:
                self.pubmed_collection = self.client.get_collection(name="pubmed_collection")
                logger.info(f"PubMed collection loaded: {self.pubmed_collection.count()} documents")
            except:
                self.pubmed_collection = None
            
            # BM25 retriever
            self.bm25_retriever = None
            self._update_bm25()
            
            logger.info("Advanced RAG Pipeline initialized")
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise

    def _update_bm25(self):
        """Update BM25 retriever with current documents"""
        try:
            # Get all documents
            all_docs = self._get_all_documents()
            if all_docs:
                documents = [doc.page_content for doc in all_docs]
                tokenized_docs = [doc.split() for doc in documents]
                self.bm25_retriever = BM25Okapi(tokenized_docs)
                self.all_documents = all_docs
        except Exception as e:
            logger.error(f"BM25 update error: {e}")

    def _get_all_documents(self) -> List[Document]:
        """Get all documents from collections"""
        documents = []
        
        # From main collection
        try:
            main_data = self.collection.get()
            if main_data['documents']:
                for i, doc in enumerate(main_data['documents']):
                    metadata = main_data['metadatas'][i] if main_data['metadatas'] else {}
                    documents.append(Document(page_content=doc, metadata=metadata))
        except:
            pass
        
        # From PubMed collection
        if self.pubmed_collection:
            try:
                pubmed_data = self.pubmed_collection.get()
                if pubmed_data['documents']:
                    for i, doc in enumerate(pubmed_data['documents']):
                        metadata = pubmed_data['metadatas'][i] if pubmed_data['metadatas'] else {}
                        documents.append(Document(page_content=doc, metadata=metadata))
            except:
                pass
        
        return documents

    def query_transformer(self, query: str) -> str:
        """Transform query for better retrieval"""
        # Simple transformation - can be enhanced with LLM
        transformations = {
            "treatment": "therapy intervention medication",
            "symptom": "sign manifestation indication",
            "diagnosis": "detection identification assessment",
            "cancer": "tumor malignancy carcinoma neoplasm"
        }
        
        transformed = query
        for word, expansion in transformations.items():
            if word in query.lower():
                transformed += f" {expansion}"
        
        logger.info(f"Query transformed: '{query}' -> '{transformed}'")
        return transformed

    def hybrid_retrieval(self, query: str, top_k: int = 5) -> List[Dict]:
        """Hybrid retrieval using BM25 and vector search"""
        try:
            # Transform query
            transformed_query = self.query_transformer(query)
            
            # Vector search
            query_embedding = self.embedding_model.encode([transformed_query])[0]
            
            all_results = []
            
            # Search main collection
            if self.collection.count() > 0:
                vector_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k * 2
                )
                self._add_to_results(all_results, vector_results, "main")
            
            # Search PubMed collection
            if self.pubmed_collection and self.pubmed_collection.count() > 0:
                pubmed_results = self.pubmed_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k * 2
                )
                self._add_to_results(all_results, pubmed_results, "pubmed")
            
            # BM25 search
            if self.bm25_retriever and self.all_documents:
                bm25_scores = self.bm25_retriever.get_scores(transformed_query.split())
                top_bm25_indices = np.argsort(bm25_scores)[-top_k*2:][::-1]
                
                for idx in top_bm25_indices:
                    if idx < len(self.all_documents):
                        doc = self.all_documents[idx]
                        all_results.append({
                            'document': doc.page_content,
                            'metadata': doc.metadata,
                            'score': float(bm25_scores[idx]),
                            'source': 'bm25'
                        })
            
            # Rerank and deduplicate
            reranked_results = self._rerank_documents(query, all_results)
            
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"Hybrid retrieval error: {e}")
            return []

    def _add_to_results(self, all_results: List, collection_results: Dict, source: str):
        """Add collection results to all results"""
        if collection_results and collection_results.get('ids'):
            for i in range(len(collection_results['ids'][0])):
                all_results.append({
                    'document': collection_results['documents'][0][i],
                    'metadata': collection_results['metadatas'][0][i] if collection_results['metadatas'] else {},
                    'score': 1 - collection_results['distances'][0][i],  # Convert distance to similarity
                    'source': source
                })

    def _rerank_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Simple reranking based on query relevance"""
        # Simple keyword matching for reranking
        query_words = set(query.lower().split())
        
        for doc in documents:
            doc_text = doc['document'].lower()
            # Calculate simple relevance score
            word_matches = sum(1 for word in query_words if word in doc_text)
            length_penalty = 1 / (1 + len(doc_text.split()) / 1000)  # Penalize very long documents
            doc['relevance_score'] = word_matches * length_penalty
        
        # Sort by relevance score
        documents.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return documents

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Main retrieval method"""
        try:
            # Check if query needs data fetching
            if self._needs_data_fetching(query):
                logger.info(f"Fetching data for query: {query}")
                self._fetch_new_data(query)
                self._update_bm25()  # Update BM25 with new data
            
            # Perform hybrid retrieval
            results = self.hybrid_retrieval(query, top_k)
            
            if not results:
                logger.warning(f"No results found for query: {query}")
                # Try direct PubMed fetch
                if self._is_medical_query(query):
                    self._fetch_new_data(query)
                    results = self.hybrid_retrieval(query, top_k)
            
            return results
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []

    def _needs_data_fetching(self, query: str) -> bool:
        """Check if we need to fetch new data"""
        # Check if query contains new medical terms
        medical_terms = ['cancer', 'treatment', 'therapy', 'diagnosis', 'symptom']
        return any(term in query.lower() for term in medical_terms)

    def _is_medical_query(self, query: str) -> bool:
        """Check if query is medical-related"""
        medical_keywords = [
            'cancer', 'medical', 'health', 'disease', 'treatment', 'symptom',
            'diagnosis', 'patient', 'clinical', 'therapy', 'drug', 'medicine'
        ]
        return any(keyword in query.lower() for keyword in medical_keywords)

    def _fetch_new_data(self, query: str, max_results: int = 10):
        """Fetch new data from PubMed"""
        try:
            data_fetcher = store_data(search_topic=query, max_results=max_results)
            
            # Store in both collections
            data_fetcher.run(collection_name="pubmed_collection")
            data_fetcher.run(collection_name="medical_documents")
            
            # Refresh collections
            try:
                self.pubmed_collection = self.client.get_collection(name="pubmed_collection")
            except:
                pass
            
            logger.info(f"Fetched new data for query: {query}")
            
        except Exception as e:
            logger.error(f"Data fetching error: {e}")

    def add_documents(self, documents: List[Document]):
        """Add new documents to the system"""
        try:
            for doc in documents:
                # Generate embedding
                embedding = self.embedding_model.encode([doc.page_content])[0]
                
                # Add to main collection
                self.collection.add(
                    ids=[f"custom_{hash(doc.page_content)}"],
                    embeddings=[embedding],
                    documents=[doc.page_content],
                    metadatas=[doc.metadata]
                )
            
            # Update BM25
            self._update_bm25()
            logger.info(f"Added {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")

    def get_stats(self) -> Dict:
        """Get system statistics"""
        stats = {
            'main_collection': self.collection.count() if self.collection else 0,
            'pubmed_collection': self.pubmed_collection.count() if self.pubmed_collection else 0,
            'bm25_documents': len(self.all_documents) if hasattr(self, 'all_documents') else 0
        }
        stats['total'] = stats['main_collection'] + stats['pubmed_collection']
        return stats
