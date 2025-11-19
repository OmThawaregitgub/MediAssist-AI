import streamlit as st
from google import genai

class GeminiLLM:
    def __init__(self):
        # Streamlit Secrets (recommended)
        self.api_key = st.secrets["GEMINI_API_KEY"]

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Models
        self.embed_model = "text-embedding-004"
        self.chat_model = "gemini-1.5-flash"

    # -------- EMBEDDING --------
    def embed(self, text: str):
        response = self.client.models.embed_content(
            model=self.embed_model,
            contents=[text]    # <-- FIXED: must be a list
        )
        return response["embedding"]

    # -------- TEXT GENERATION --------
    def generate(self, prompt: str):
        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=[prompt]   # <-- FIXED: must be a list
        )
        return response.text
