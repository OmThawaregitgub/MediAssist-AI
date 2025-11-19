import streamlit as st
from google import genai

import os
from google.genai.errors import APIError
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# --- FIX START ---
# Read the GEMINI_API_KEY environment variable
API_KEY = os.getenv("GEMINI_API_KEY") # <-- CHANGE IS HERE
# --- FIX END ---

# Check if the API key is available
if not API_KEY:
    # A cleaner way to handle this on Streamlit Cloud is to prompt
    # the user or stop the app, but for this context we raise an error.
    # Note: If running locally with a .env file, ensure the key is 'GEMINI_API_KEY' there too.
    raise ValueError("GEMINI_API_KEY not found in environment variables or .env file.")
    
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

