import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets.get('API_KEY')
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            
            # Find and use available models
            available_models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            
            # Try models in order
            for model_name in available_models:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    # Test the model
                    test_response = self.model.generate_content("Hello")
                    if test_response.text:
                        print(f"✅ Using model: {model_name}")
                        break
                except:
                    continue
            else:
                raise Exception("No working models found")
                
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "I couldn't generate a response."
        except Exception as e:
            return f"Error: {str(e)}"
