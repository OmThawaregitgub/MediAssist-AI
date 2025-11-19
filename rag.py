# llm.py

import os
from google import genai
from google.genai.errors import APIError

# Load environment variables from .env file
import streamlit as st
api_key = st.secrets["my_api_key"]

# Check if the API key is available


class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name
        self.embedding_model = "text-embedding-004" # Use a stable embedding model

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

    def embed(self, text: str):
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="RETRIEVAL_DOCUMENT"
            )
            return response['embedding']
        except APIError as e:
            print(f"Embedding error: {e}")
            return None # Return None on failure
        except Exception as e:
            print(f"An unexpected embedding error occurred: {e}")
            return None

