import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['API_KEY']
            
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            print(f"🔑 API Key found: {api_key[:15]}...")
            
            # Configure with the same settings as your working module
            genai.configure(api_key=api_key)
            
            # Try the exact same approach as your working module
            # Most common working configuration:
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Using gemini-pro model")
            
            # Test the connection
            print("🔄 Testing API connection...")
            test_response = self.model.generate_content("Hello")
            
            if hasattr(test_response, 'text') and test_response.text:
                print(f"✅ API Test Successful: {test_response.text}")
            else:
                raise Exception("API test failed - no response text")
            
            print("✅ LLM initialized successfully")
            
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            print(f"📞 API Call: {prompt[:100]}...")
            
            response = self.model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                print(f"✅ Response received: {len(response.text)} chars")
                return response.text
            else:
                return "I apologize, but I couldn't generate a proper response."
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ API Call Error: {error_msg}")
            return f"API Error: {error_msg}"
