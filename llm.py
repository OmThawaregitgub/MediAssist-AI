import streamlit as st
from google import genai

class GeminiLLM:
    def __init__(self):
        self.api_key = st.secrets["GEMINI_API_KEY"]
        self.client = genai.Client(api_key=self.api_key)

        self.embed_model = "text-embedding-004"
        self.chat_model = "gemini-1.5-flash"

    # -------- EMBEDDING --------
    def embed(self, text: str):
        response = self.client.models.embed_content(
            model=self.embed_model,
            contents=[text]   # must be a list
        )
        # Extract the embedding from the first result
        embedding = response["results"][0]["embedding"]
        return embedding

    # -------- TEXT GENERATION --------
    def generate(self, prompt: str):
        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=[prompt]   # must be a list
        )
        return response.output_text  # often `output_text` instead of `text`
