# llm.py - DIRECT API VERSION
import streamlit as st
import requests
import json

class GeminiLLM:
    def __init__(self):
        self.api_key = st.secrets["GEMINI_API_KEY"]
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
        
    def generate(self, prompt: str) -> str:
        try:
            # Try gemini-1.5-flash first (most common)
            return self._try_model("gemini-1.5-flash", prompt)
        except:
            try:
                # Fallback to gemini-1.5-pro
                return self._try_model("gemini-1.5-pro", prompt)
            except:
                # Final fallback
                return "Hello! I'm MediAssist AI. I can help answer questions about breast cancer research using our medical database. What would you like to know?"
    
    def _try_model(self, model_name: str, prompt: str) -> str:
        url = f"{self.base_url}{model_name}:generateContent?key={self.api_key}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Model {model_name} failed: {response.status_code}")
