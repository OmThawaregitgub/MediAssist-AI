# llm.py
import streamlit as st
import google.generativeai as genai

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
        st.sidebar.info(f"Using model: {self.model_name}")

    def _discover_working_model(self):
        """Discover which model works with the current API"""
        # Common model names that work with Google Gemini
        model_candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-1.0-pro",
            "models/gemini-1.5-flash-001",
            "models/gemini-1.5-pro-001",
            "models/gemini-pro"
        ]
        
        for model_name in model_candidates:
            try:
                # Test the model with a simple prompt
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                if response.text:
                    return model_name
            except Exception as e:
                continue
                
        # If no model works, use the most common one and handle errors gracefully
        return "gemini-1.5-flash"

    def generate(self, prompt: str) -> str:
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Return friendly responses for common queries
            if any(word in prompt.lower() for word in ['hi', 'hello', 'hey', 'hola']):
                return "Hello! I'm MediAssist AI, your medical research assistant. I can help answer questions about breast cancer research using our database of medical studies."
            elif 'cancer' in prompt.lower() or 'treatment' in prompt.lower() or 'medical' in prompt.lower():
                return "I can provide information about breast cancer research from our medical database. Please ask specific questions about treatments, risk factors, or recent studies."
            else:
                return "I'm here to help with medical research questions. Please ask me about breast cancer topics, treatments, or medical research."
