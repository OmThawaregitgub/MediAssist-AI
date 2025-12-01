import logging
from typing import List, Dict, Any
from llm import LLMClient

logger = logging.getLogger(__name__)

class HallucinationChecker:
    """Check for hallucinations in generated answers"""
    
    def __init__(self):
        self.llm = LLMClient()
    
    def check(self, answer: str, sources: List[Dict]) -> Dict[str, Any]:
        """
        Check if answer contains hallucinations
        
        Args:
            answer: Generated answer
            sources: Source documents used for generation
            
        Returns:
            Dictionary with hallucination check results
        """
        if not answer or not sources:
            return {
                'is_hallucination': False,
                'confidence': 1.0,
                'reason': 'No answer or sources provided'
            }
        
        try:
            # Extract source texts
            source_texts = [src.get('text', '') for src in sources[:3]]  # Check against top 3 sources
            
            prompt = f"""
            Analyze if the following answer contains any hallucinations (information not supported by the sources).
            
            ANSWER: {answer}
            
            SOURCES:
            {chr(10).join([f'[Source {i+1}]: {text[:500]}' for i, text in enumerate(source_texts)])}
            
            Provide your analysis in this exact format:
            IS_HALLUCINATION: [True/False]
            CONFIDENCE: [0.0 to 1.0]
            REASON: [Brief explanation]
            
            Only return these three lines.
            """
            
            response = self.llm.generate(prompt)
            
            # Parse response
            result = {
                'is_hallucination': False,
                'confidence': 1.0,
                'reason': 'Unable to parse checker response'
            }
            
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('IS_HALLUCINATION:'):
                    value = line.split(':', 1)[-1].strip().lower()
                    result['is_hallucination'] = value == 'true'
                elif line.startswith('CONFIDENCE:'):
                    try:
                        value = float(line.split(':', 1)[-1].strip())
                        result['confidence'] = max(0.0, min(1.0, value))
                    except:
                        pass
                elif line.startswith('REASON:'):
                    result['reason'] = line.split(':', 1)[-1].strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in hallucination check: {e}")
            return {
                'is_hallucination': False,
                'confidence': 0.0,
                'reason': f'Error: {str(e)}'
            }