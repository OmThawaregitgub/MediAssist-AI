# llm.py (UPDATED with correct model names)
import streamlit as st
from google import genai
from google.genai.errors import APIError

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        if not API_KEY:
            raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in Streamlit secrets.")
        
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except APIError as e:
            # Try fallback models if the primary one fails
            return self._try_fallback_models(prompt, str(e))
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def _try_fallback_models(self, prompt: str, original_error: str) -> str:
        """Try different model names if the primary one fails"""
        fallback_models = [
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-pro",
            "models/gemini-1.5-pro",
            "models/gemini-pro"
        ]
        
        for model in fallback_models:
            if model != self.model_name:  # Skip the one that already failed
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                    print(f"✅ Successfully used model: {model}")
                    return response.text
                except Exception:
                    continue
        
        return f"Error: All models failed. Original error: {original_error}"
