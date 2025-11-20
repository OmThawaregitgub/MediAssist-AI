import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            # Get API key from secrets
            api_key = st.secrets.get('API_KEY')
            
            if not api_key:
                raise ValueError("❌ API_KEY not found in Streamlit secrets")
            
            print(f"🔑 API Key found: {api_key[:15]}...")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # List available models to see what we have
            print("🔍 Checking available models...")
            available_models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"   ✅ {model.name}")
            
            if not available_models:
                raise ValueError("❌ No generateContent models available")
            
            # Try to use a model - let's be more flexible
            working_model = None
            for model_name in available_models:
                try:
                    print(f"🔄 Testing: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    # Simple test
                    test_response = self.model.generate_content("Hello")
                    if test_response.text:
                        working_model = model_name
                        print(f"🎉 Using model: {working_model}")
                        break
                except Exception as e:
                    print(f"   ❌ {model_name} failed: {str(e)[:100]}")
                    continue
            
            if not working_model:
                raise ValueError("❌ No working models found from available list")
                
            print("✅ LLM initialized successfully")
            
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            print(f"📝 Prompt length: {len(prompt)} characters")
            print(f"📝 First 200 chars: {prompt[:200]}...")
            
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Check response
            if hasattr(response, 'text') and response.text:
                print(f"✅ Response generated: {len(response.text)} characters")
                return response.text
            else:
                print("❌ Empty response from model")
                return "I apologize, but I couldn't generate a proper response. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Generation error: {error_msg}")
            
            # Provide more specific error messages
            if "API_KEY" in error_msg:
                return "❌ API configuration error. Please check your API key."
            elif "quota" in error_msg.lower():
                return "❌ API quota exceeded. Please check your billing or try again later."
            elif "permission" in error_msg.lower():
                return "❌ API permission denied. Please check your API key permissions."
            else:
                return f"❌ I'm experiencing technical difficulties: {error_msg}"
