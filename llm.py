import streamlit as st
from google import genai
from google.genai.errors import APIError

class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.embedding_model = "text-embedding-004"
        self.client = genai.Client(api_key=self.get_api_key())

    def get_api_key(self):
        # Safe retrieval at runtime
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found! "
                "Set it in Streamlit Cloud Secrets or your local .env file."
            )
        return api_key

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],  # Must be a list
            )
            return response.text
        except APIError as e:
            return f"LLM API error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def embed(self, text: str):
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=[text],  # Must be a list
                task_type="RETRIEVAL_DOCUMENT",
            )
            return response.embeddings[0]
        except APIError as e:
            print(f"Embedding error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected embedding error: {e}")
            return None
