import logging
from typing import Dict, Any, List
from llm import LLMClient

logger = logging.getLogger(__name__)

class QueryAgent:
    """Agent for processing queries with reasoning and verification"""
    
    def __init__(self, llm: LLMClient, memory=None, hallucination_checker=None):
        self.llm = llm
        self.memory = memory
        self.hallucination_checker = hallucination_checker
    
    def process_query(self, query: str, context: str, relevant_docs: List[Dict]) -> Dict[str, Any]:
        """
        Process query with agentic reasoning
        
        Args:
            query: User query
            context: Retrieved context
            relevant_docs: Source documents
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Step 1: Analyze query and context
            analysis_prompt = f"""
            Analyze the following medical query and context:
            
            QUERY: {query}
            
            CONTEXT (from medical literature):
            {context}
            
            Provide a brief analysis of:
            1. What the user is asking
            2. What information is available in the context
            3. What might be missing
            4. Confidence level (0.0 to 1.0)
            
            Keep this analysis concise.
            """
            
            analysis = self.llm.generate(analysis_prompt)
            
            # Step 2: Generate answer
            answer_prompt = f"""
            Based on the following medical context, answer the user's query.
            
            USER QUERY: {query}
            
            MEDICAL CONTEXT (from research articles):
            {context}
            
            IMPORTANT INSTRUCTIONS:
            1. Base your answer ONLY on the provided context
            2. If information is not in the context, say "Based on the available information, I cannot confirm..."
            3. Be precise and cite specific information from the context
            4. Use medical terminology appropriately
            5. Add disclaimers about consulting healthcare professionals
            
            ANSWER:
            """
            
            answer = self.llm.generate(answer_prompt)
            
            # Step 3: Self-verify answer
            verification_prompt = f"""
            Verify if the following answer is fully supported by the context:
            
            QUERY: {query}
            
            CONTEXT:
            {context}
            
            PROPOSED ANSWER:
            {answer}
            
            Provide verification in this format:
            SUPPORTED: [Yes/Partially/No]
            CONFIDENCE: [0.0 to 1.0]
            ISSUES: [List any unsupported claims or issues]
            
            Only return these three lines.
            """
            
            verification = self.llm.generate(verification_prompt)
            
            # Parse verification
            supported = "Partially"
            confidence = 0.7
            issues = ""
            
            lines = verification.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('SUPPORTED:'):
                    supported = line.split(':', 1)[-1].strip()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[-1].strip())
                    except:
                        pass
                elif line.startswith('ISSUES:'):
                    issues = line.split(':', 1)[-1].strip()
            
            # Adjust answer if not fully supported
            if supported != "Yes":
                answer = f"{answer}\n\n⚠️ Note: This information is based on available sources but may not be comprehensive. {issues}"
            
            return {
                'answer': answer,
                'analysis': analysis,
                'verification': {
                    'supported': supported,
                    'confidence': confidence,
                    'issues': issues
                },
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error in query agent: {e}")
            return {
                'answer': f"I apologize, but I encountered an error processing your query: {str(e)}",
                'analysis': "Error in analysis",
                'verification': {
                    'supported': 'No',
                    'confidence': 0.0,
                    'issues': 'Processing error'
                },
                'confidence': 0.0
            }