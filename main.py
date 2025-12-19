# llm.py
from dotenv import load_dotenv
import os
import streamlit as st
from google import genai
from reg import RegPipeline as RP

# Load environment variables
load_dotenv()

class LargeLanguageModel:
    def __init__(self) -> None:
        # Extract the Gemini API key from environment variables
        self.API_key = os.getenv("Gemini_Api_Key")
        self.client = None
        self.initialized = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            if not self.API_key:
                st.error("❌ Gemini API key not found in environment variables")
                return
            
            self.client = genai.Client(api_key=self.API_key)
            self.initialized = True
            
        except Exception as e:
            st.error(f"❌ Failed to initialize Gemini client: {e}")
    
    @staticmethod
    def remove_extra_space(prompt: str) -> str:
        """Remove extra spaces from prompt"""
        return ' '.join(prompt.strip().split())
    
    def test_connection(self, model: str = "gemini-1.5-flash") -> bool:
        """Test connection to Gemini API"""
        if not self.initialized:
            return False
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents="Connection test"
            )
            return response.text is not None
        except Exception as e:
            st.warning(f"Model {model} not available: {e}")
            return False
    
    @staticmethod
    def gather_information_from_rag(query: str, top_k: int = 5) -> list:
        """
        Gather relevant information from the RAG pipeline
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Initialize RAG pipeline
            rag_pipeline = RP()
            
            # Search for relevant documents
            results = rag_pipeline.search_all(query=query, top_k=top_k)
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    'document': result.get('document', ''),
                    'metadata': result.get('metadata', {}),
                    'source': result.get('source', 'unknown'),
                    'relevance_score': result.get('distance', 0)
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            st.error(f"❌ Error gathering information from RAG: {e}")
            return []
    
    def generate_response(self, prompt: str, model: str = "gemini-1.5-flash") -> str:
        """
        Generate response using Gemini LLM with RAG context
        
        Args:
            prompt: User query
            model: Gemini model to use
            
        Returns:
            Generated response
        """
        # Check if client is initialized
        if not self.initialized:
            return "⚠️ LLM service is not available. Please check your API key."
        
        # Get context from RAG
        rag_results = self.gather_information_from_rag(query=prompt)
        
        # Prepare context
        context = "No relevant medical research found."
        sources_info = []
        
        if rag_results:
            context_parts = []
            for result in rag_results:
                doc_text = result['document'][:500] + "..." if len(result['document']) > 500 else result['document']
                context_parts.append(f"Source: {result.get('source', 'unknown')}\nContent: {doc_text}")
                
                # Collect source metadata for citation
                if 'metadata' in result and 'title' in result['metadata']:
                    sources_info.append(result['metadata']['title'][:100])
            
            context = "\n\n".join(context_parts)
        
        # Clean prompt
        clean_prompt = self.remove_extra_space(prompt)
        
        # Build system prompt
        system_prompt = f"""You are MediAssist AI, a specialized medical research assistant.

Your capabilities:
1. Answer medical questions based on the provided research context
2. Provide evidence-based information
3. Format responses appropriately (tables, lists, paragraphs) as requested
4. Cite sources when available
5. Acknowledge limitations when information is incomplete
6. Always recommend consulting healthcare professionals for medical advice

Important guidelines:
- DO NOT provide specific drug dosages or treatment plans
- DO NOT diagnose medical conditions
- DO NOT provide emergency medical advice
- ALWAYS suggest consulting qualified medical professionals
- Use clear, professional language
- Present information in an organized manner

Research Context:
{context}

User Question: {clean_prompt}

Please provide a helpful, accurate, and well-structured response:"""
        
        try:
            # Test connection with selected model
            if not self.test_connection(model):
                # Try fallback models
                fallback_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                for fallback_model in fallback_models:
                    if fallback_model != model and self.test_connection(fallback_model):
                        model = fallback_model
                        st.info(f"⚠️ Switched to model: {model}")
                        break
                else:
                    return "⚠️ No working Gemini model found. Please check your API configuration."
            
            # Generate response
            response = self.client.models.generate_content(
                model=model,
                contents=system_prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            if response.text:
                # Add source citations if available
                if sources_info:
                    response_text = response.text
                    response_text += f"\n\n**Sources:**\n"
                    for i, source in enumerate(sources_info[:3], 1):
                        response_text += f"{i}. {source}\n"
                    return response_text
                return response.text
            else:
                return "⚠️ No response generated. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                return "⚠️ The selected model is not available. Please try a different model."
            elif "429" in error_msg:
                return "⚠️ Rate limit exceeded. Please try again later."
            elif "401" in error_msg:
                return "⚠️ Invalid API key. Please check your configuration."
            else:
                return f"⚠️ Error generating response: {error_msg}"
    
    def get_available_models(self):
        """Get list of available Gemini models"""
        if not self.initialized:
            return []
        
        try:
            models = list(self.client.models.list())
            available_models = []
            for model_info in models:
                if 'generateContent' in model_info.supported_generation_methods:
                    available_models.append(model_info.name)
            return available_models
        except:
            return []
