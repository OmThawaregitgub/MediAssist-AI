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

    def _discover_working_model(self):
        """Discover which model works with the current API"""
        model_candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-1.0-pro",
        ]
        
        for model_name in model_candidates:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                if response.text:
                    return model_name
            except Exception:
                continue
                
        return "gemini-1.5-flash"

    def generate(self, prompt: str) -> str:
        try:
            model = genai.GenerativeModel(self.model_name)
            
            # Simply pass the prompt to the LLM - no hardcoded responses
            # The LLM will handle greetings, questions, and conversations naturally
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            # If LLM fails, provide a simple fallback
            return f"I encountered an error while processing your request. Please try again with your question: '{prompt}'"

    def get_model_info(self):
        return f"Using model: {self.model_name}"
