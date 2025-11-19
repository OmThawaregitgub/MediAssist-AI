# llm.py (SIMPLIFIED - No Embeddings)
import streamlit as st
from google import genai
from google.genai.errors import APIError

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        if not API_KEY:
            raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in Streamlit secrets.")
        
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except APIError as e:
            return f"Error from LLM: Could not generate content. {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
