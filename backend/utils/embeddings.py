import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Union

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manage text embeddings with caching"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize embedding model"""
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.embedding_cache = {}  # Simple cache for embeddings
            
            logger.info(f"✅ Loaded embedding model: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            raise e
    
    def get_embedding(self, text: Union[str, List[str]], use_cache: bool = True):
        """
        Get embedding for text(s)
        
        Args:
            text: Single text string or list of texts
            use_cache: Whether to use caching
            
        Returns:
            Embedding vector(s)
        """
        if isinstance(text, str):
            texts = [text]
            single_input = True
        else:
            texts = text
            single_input = False
        
        # Check cache
        embeddings = []
        texts_to_encode = []
        indices_to_encode = []
        
        for i, t in enumerate(texts):
            cache_key = hash(t)
            if use_cache and cache_key in self.embedding_cache:
                embeddings.append(self.embedding_cache[cache_key])
            else:
                texts_to_encode.append(t)
                indices_to_encode.append(i)
                embeddings.append(None)  # Placeholder
        
        # Encode texts not in cache
        if texts_to_encode:
            new_embeddings = self.model.encode(
                texts_to_encode,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            # Update cache and place embeddings
            for idx, text_idx in enumerate(indices_to_encode):
                embedding = new_embeddings[idx]
                
                # Cache the embedding
                cache_key = hash(texts_to_encode[idx])
                self.embedding_cache[cache_key] = embedding
                
                # Place in result
                embeddings[text_idx] = embedding
        
        # Convert list to single array if needed
        if single_input:
            return embeddings[0]
        else:
            return np.array(embeddings)
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        # Ensure numpy arrays
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        # Normalize
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)
        
        # Cosine similarity
        similarity = np.dot(emb1_norm, emb2_norm)
        
        return float(similarity)