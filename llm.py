import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets.get('API_KEY')
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            
            # List available models and use the first working one
            print("🔍 Finding available models...")
            available_models = []
            
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"✅ Found: {model.name}")
            
            if not available_models:
                raise Exception("No generateContent models available")
            
            # Try each available model
            working_model = None
            for model_name in available_models:
                try:
                    print(f"🔄 Testing: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    test_response = self.model.generate_content("Hello")
                    if test_response.text:
                        working_model = model_name
                        print(f"🎉 Using: {working_model}")
                        break
                except Exception as e:
                    print(f"❌ {model_name} failed: {str(e)[:100]}")
                    continue
            
            if not working_model:
                raise Exception(f"No working models from: {available_models}")
                
            print("✅ LLM initialized successfully")
            
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "I couldn't generate a response."
        except Exception as e:
            return f"LLM Error: {str(e)}"
