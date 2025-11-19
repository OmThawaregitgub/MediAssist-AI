# llm.py (UPDATED for Streamlit Secrets)
import streamlit as st
from google import genai
from google.genai.errors import APIError
from typing import Optional, List

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        if not API_KEY:
            raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in Streamlit secrets.")
        
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
            return f"Error from LLM (Generation): Could not generate content. Check API key permissions and quota. {e}"
        except Exception as e:
            return f"An unexpected generation error occurred: {e}"

    def embed(self, text: str) -> Optional[List[float]]:
        try:
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=[text]  # Must be a list!
            )
            if hasattr(result, 'embeddings') and result.embeddings:
                return result.embeddings[0].values
            else:
                print("No embeddings found in response")
                return None
                
        except APIError as e:
            print(f"Embedding API Error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected embedding error occurred: {e}")
            return None
