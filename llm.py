import streamlit as st
from google import genai

class GeminiLLM:
    def __init__(self):
        # Load API key from secrets
        self.api_key = st.secrets["GEMINI_API_KEY"]
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets!")

        # Initialize client
        self.client = genai.Client(api_key=self.api_key)

        # Models
        self.embed_model = "text-embedding-004"
        self.chat_model = "gemini-1.5-flash"

    # Create embeddings
    def embed(self, text: str):
    response = self.client.embeddings.embed(
        model=self.embed_model,
        input=text
    )
    return response.data[0].embedding


    # Generate answer
    def generate(self, prompt: str):
        response = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt
        )
        return response.text

