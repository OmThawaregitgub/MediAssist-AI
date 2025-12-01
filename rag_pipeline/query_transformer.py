import logging
from typing import List
from llm import LLMClient

logger = logging.getLogger(__name__)

class QueryTransformer:
    """Transform and expand user queries for better retrieval"""
    
    def __init__(self):
        self.llm = LLMClient()
    
    def transform(self, query: str) -> List[str]:
        """
        Transform query into multiple variations
        
        Args:
            query: Original user query
            
        Returns:
            List of query variations
        """
        try:
            prompt = f"""
            Transform the following medical query into 3 different variations that might help retrieve relevant information.
            
            Original Query: {query}
            
            Provide the variations in this format:
            1. [Variation 1]
            2. [Variation 2]
            3. [Variation 3]
            
            Make the variations diverse but semantically related.
            """
            
            response = self.llm.generate(prompt)
            
            # Parse response
            variations = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering/bullets
                    variation = line.split('.', 1)[-1].strip()
                    variation = variation.lstrip('-• ').strip()
                    if variation:
                        variations.append(variation)
            
            # Always include original query
            if query not in variations:
                variations.insert(0, query)
            
            return variations[:4]  # Return up to 4 variations
            
        except Exception as e:
            logger.error(f"Error transforming query: {e}")
            return [query]  # Fallback to original query