import streamlit as st
from google import genai

class GeminiLLM:
    def __init__(self):
        # Load from Streamlit Cloud secrets
        self.api_key = st.secrets["GEMINI_API_KEY"]

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets!")

        # New SDK client (NO configure())
        self.client = genai.Client(api_key=self.api_key)

        self.embed_model = "text-embedding-004"
        self.chat_model = "gemini-1.5-flash"

    # Create embeddings
    def embed(self, text: str):
        response = self.client.embed_content(
            model=self.embed_model,
            content=text
        )
        return response.embedding

    # Generate text from LLM
    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )
        return response.text
