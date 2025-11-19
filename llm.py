# llm.py
import streamlit as st
import google.generativeai as genai

class GeminiLLM:
    def __init__(self):
        try:
            API_KEY = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"API configuration error: {e}")

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I'm here to help! What would you like to know? (Error: {str(e)})"
