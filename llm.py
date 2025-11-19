# llm.py
import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

class GeminiLLM:
    def __init__(self, model_name="gemini-flash-latest"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in .env")

        

        self.client = Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
