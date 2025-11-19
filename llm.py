# llm.py

import os
import google.genai as genai
import streamlit as st

class GeminiLLM:
    def __init__(self):

        # Load API key from Streamlit Secrets (Cloud) or .env/local
        if "GEMINI_API_KEY" in st.secrets:
            self.api_key = st.secrets["GEMINI_API_KEY"]
        else:
            self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets or .env")

        genai.configure(api_key=self.api_key)
        self.client = genai.Client(api_key=self.api_key)

        # Models
        self.chat_model = "models/gemini-2.0-flash"
        self.embedding_model = "models/text-embedding-004"

    # ---- Generate text ----
    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.chat_model,
            content=prompt
        )
        return response.text

    # ---- Generate embeddings ----
    def embed(self, text: str):
        response = self.client.models.embed_content(
            model=self.embedding_model,
            content=text
        )
        return response.embedding
