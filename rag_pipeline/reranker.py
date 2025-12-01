import logging
from typing import List
import numpy as np
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

class RAGReranker:
    """Rerank retrieved documents using cross-encoder"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        try:
            self.model = CrossEncoder(model_name, max_length=512)
            logger.info(f"✅ Loaded reranker model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Error loading reranker: {e}")
            self.model = None
    
    def rerank(self, query: str, documents: List[str], scores: List[float] = None) -> List[float]:
        """
        Rerank documents based on relevance to query
        
        Args:
            query: User query
            documents: List of document texts
            scores: Original retrieval scores (optional)
            
        Returns:
            List of reranked scores
        """
        if not self.model or not documents:
            return scores if scores else [1.0] * len(documents)
        
        try:
            # Prepare pairs for cross-encoder
            pairs = [[query, doc] for doc in documents]
            
            # Get scores from cross-encoder
            rerank_scores = self.model.predict(pairs)
            
            # Convert to list if single score
            if isinstance(rerank_scores, np.ndarray):
                rerank_scores = rerank_scores.tolist()
            elif isinstance(rerank_scores, float):
                rerank_scores = [rerank_scores]
            
            # Combine with original scores if available
            if scores and len(scores) == len(rerank_scores):
                # Weighted combination (70% rerank, 30% original)
                combined_scores = []
                for orig, rerank in zip(scores, rerank_scores):
                    combined = 0.7 * rerank + 0.3 * orig
                    combined_scores.append(combined)
                return combined_scores
            
            return rerank_scores
            
        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            return scores if scores else [1.0] * len(documents)