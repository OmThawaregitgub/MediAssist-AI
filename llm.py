import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['API_KEY']
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            print(f"🔑 API Key found: {api_key[:15]}...")
            
            genai.configure(api_key=api_key)
            
            # List ALL available models
            print("🔍 Listing ALL available models:")
            all_models = list(genai.list_models())
            
            if not all_models:
                raise Exception("No models returned from API")
            
            # Find models that support generateContent
            available_models = []
            for model in all_models:
                print(f"📋 Model: {model.name}")
                print(f"   Methods: {model.supported_generation_methods}")
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"   ✅ CAN USE for generateContent")
            
            print(f"🎯 Available generateContent models: {available_models}")
            
            if not available_models:
                raise Exception("No generateContent models available")
            
            # Try each available model
            working_model = None
            for model_name in available_models:
                try:
                    print(f"🔄 Testing: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Simple test
                    test_response = self.model.generate_content("Hello")
                    if hasattr(test_response, 'text') and test_response.text:
                        working_model = model_name
                        print(f"🎉 SUCCESS with model: {working_model}")
                        break
                except Exception as e:
                    print(f"   ❌ {model_name} failed: {str(e)[:100]}")
                    continue
            
            if not working_model:
                raise Exception(f"No working models found from: {available_models}")
                
            print(f"✅ LLM initialized with: {working_model}")
            
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            print(f"📞 Making API call with: {prompt[:100]}...")
            
            response = self.model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                print(f"✅ Response received: {len(response.text)} characters")
                return response.text
            else:
                return "I apologize, but I couldn't generate a proper response."
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Generation error: {error_msg}")
            return f"Error: {error_msg}"
