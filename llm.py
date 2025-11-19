# llm.py

import os
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv
import streamlit as st
import sys

# Load .env variables for local development only
if "streamlit" not in sys.modules:
    load_dotenv()

# --- API KEY RETRIEVAL LOGIC ---
API_KEY = None
SECRET_NAME = "GEMINI_API_KEY"

# 1. Try Streamlit Secrets (Recommended for Streamlit Cloud)
if SECRET_NAME in st.secrets:
    API_KEY = st.secrets['GEMINI_API_KEY']

# 2. Fallback to Environment Variables (Works for Streamlit Cloud secrets too)
if API_KEY is None:
    API_KEY = os.getenv(SECRET_NAME)

# 3. Final Check
if not API_KEY:
    # Raise error if key is still missing
    raise ValueError(f"{SECRET_NAME} not found. Please ensure it is set in Streamlit Cloud Secrets or your local .env file.")

class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash"):
        # The client initialization uses the successfully retrieved API_KEY
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name
        self.embedding_model = "text-embedding-004" 

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
            return None
        except Exception as e:
            print(f"An unexpected embedding error occurred: {e}")
            return None




