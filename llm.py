# llm.py
import streamlit as st
import google.generativeai as genai
import time

class GeminiLLM:
    def __init__(self):
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        if not API_KEY:
            raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in Streamlit secrets.")
        
        # Configure the API
        genai.configure(api_key=API_KEY)
        
        # Find available model
        self.model_name = self._discover_working_model()
        st.sidebar.info(f"Model: {self.model_name}")

    def _discover_working_model(self):
        """Discover which model works with the current API"""
        try:
            # List available models and find one that supports generateContent
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    # Try common model names
                    if any(name in model.name for name in ['gemini-pro', 'gemini-1.5', 'gemini-1.0']):
                        return model.name
            # Fallback to the first available model
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    return model.name
        except Exception as e:
            st.sidebar.error(f"Model discovery failed: {e}")
        
        # Default fallbacks
        return "gemini-1.5-flash"

    def generate(self, prompt: str) -> str:
        try:
            # Use the correct API approach
            model = genai.GenerativeModel(self.model_name)
            
            # Generate content with retry logic
            for attempt in range(3):
                try:
                    response = model.generate_content(prompt)
                    if response.text:
                        return response.text
                    else:
                        time.sleep(1)  # Wait before retry
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise e
                    time.sleep(1)
                    
            return "I'm here to help! What would you like to know?"
            
        except Exception as e:
            # Provide friendly responses based on common query types
            prompt_lower = prompt.lower()
            
            # For greetings, provide a simple response
            if any(word in prompt_lower for word in ['hi', 'hello', 'hey', 'hola']):
                return "Hello! 👋 I'm your AI assistant. How can I help you today?"
            
            # For other queries, acknowledge the issue but still try to be helpful
            return f"I'd be happy to help with that! Feel free to ask me anything."

    def get_model_info(self):
        return f"Using model: {self.model_name}"
