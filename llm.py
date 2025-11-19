# llm.py (FINAL, WORKING VERSION for Streamlit Cloud)

import os
from google import genai
from google.genai.errors import APIError
import streamlit as st
import sys
from typing import Optional, List # Added for type hinting clarity

# Note: Removed local dotenv loading for Streamlit Cloud compatibility

# --- API KEY RETRIEVAL LOGIC (Uses a safe environment variable check) ---
API_KEY: Optional[str] = None
SECRET_NAME = "GEMINI_API_KEY"

# Streamlit Cloud automatically injects secrets as environment variables.
# We fetch it directly, which is safe.
API_KEY = os.getenv(SECRET_NAME)

# 3. Final Check (Raise an exception to stop deployment if key is missing)
if not API_KEY:
    raise ValueError(f"CRITICAL ERROR: {SECRET_NAME} not found. Ensure it is set in Streamlit Cloud Secrets.")


class GeminiLLM:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # The client initialization uses the successfully retrieved API_KEY
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name
        self.embedding_model = "text-embedding-004"  # Used for vectorization

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except APIError as e:
            return f"Error from LLM (Generation): Could not generate content. Check API key permissions and quota. {e}"
        except Exception as e:
            return f"An unexpected generation error occurred: {e}"

    def embed(self, text: str) -> Optional[List[float]]:
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text,  # CORRECT: Uses 'contents'
                # REMOVED: 'task_type' is deprecated and causes the error
            )
            return response['embedding']
        except APIError as e:
            # Handle API-specific errors (e.g., invalid key, quota limit)
            print(f"Embedding API Error: {e}")
            return None
        except Exception as e:
            # Handle unexpected errors
            print(f"An unexpected embedding error occurred: {e}")
            return None
