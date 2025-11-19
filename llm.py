# llm.py
import streamlit as st
import google.generativeai as genai

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-pro"):
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        if not API_KEY:
            raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in Streamlit secrets.")
        
        # Configure the API
        genai.configure(api_key=API_KEY)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        try:
            # Use the GenerativeModel class
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
