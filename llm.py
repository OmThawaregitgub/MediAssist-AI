import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['API_KEY']
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            print(f"🔑 API Key found: {api_key[:10]}...")  # Log first 10 chars
            
            genai.configure(api_key=api_key)
            
            # List ALL models to see what's available
            print("🔍 Listing ALL available models:")
            all_models = list(genai.list_models())
            
            if not all_models:
                raise Exception("No models returned from API - check API key validity")
            
            available_models = []
            for model in all_models:
                print(f"📋 Model: {model.name}")
                print(f"   Supported methods: {model.supported_generation_methods}")
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"   ✅ Can use for generateContent")
            
            print(f"🎯 Available generateContent models: {available_models}")
            
            if not available_models:
                raise Exception("No generateContent models available")
            
            # Try each available model
            for model_name in available_models:
                try:
                    print(f"🔄 Testing model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Simple test
                    test_response = self.model.generate_content("Say hello in one word")
                    if hasattr(test_response, 'text') and test_response.text:
                        print(f"🎉 Model {model_name} works!")
                        self.model_name = model_name
                        break
                    else:
                        print(f"❌ Model {model_name} returned empty response")
                        continue
                        
                except Exception as model_error:
                    print(f"❌ Model {model_name} failed: {model_error}")
                    continue
            else:
                raise Exception(f"No working models found from: {available_models}")
            
            print(f"✅ Successfully initialized with model: {self.model_name}")
            
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
