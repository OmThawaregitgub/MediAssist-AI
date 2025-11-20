import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['API_KEY']
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            
            # List all available models and use the first one that supports generateContent
            print("🔍 Searching for available models...")
            available_models = []
            
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"✅ Found available model: {model.name}")
            
            if not available_models:
                raise Exception("No models with generateContent support found")
            
            # Try each available model until one works
            for model_name in available_models:
                try:
                    print(f"🔄 Trying model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Test the model
                    test_response = self.model.generate_content("Hello")
                    if hasattr(test_response, 'text') and test_response.text:
                        print(f"🎉 Successfully loaded and tested model: {model_name}")
                        break
                    else:
                        print(f"❌ Model {model_name} test failed")
                        continue
                        
                except Exception as model_error:
                    print(f"❌ Failed to load {model_name}: {model_error}")
                    continue
            else:
                raise Exception("All available models failed to load")
            
            print("✅ Gemini API connected successfully")
            
        except Exception as e:
            print(f"❌ Gemini API connection failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            response = self.model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a proper response."
                
        except Exception as e:
            print(f"LLM Generation Error: {str(e)}")
            return f"I'm experiencing technical difficulties: {str(e)}"
