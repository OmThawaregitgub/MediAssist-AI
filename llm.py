import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets.get('API_KEY')
            if not api_key:
                raise ValueError("API_KEY not found")
            
            genai.configure(api_key=api_key)
            
            # Try available models
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except:
                # List models and use first available
                models = list(genai.list_models())
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        self.model = genai.GenerativeModel(model.name)
                        break
                else:
                    raise Exception("No working models")
            
            print("✅ LLM Ready")
            
        except Exception as e:
            print(f"❌ LLM failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "No response"
        except Exception as e:
            return f"LLM Error: {str(e)}"
