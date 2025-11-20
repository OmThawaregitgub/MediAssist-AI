import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets.get('API_KEY')
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            print(f"🔑 API Key found: {api_key[:10]}...")
            
            genai.configure(api_key=api_key)
            
            # Try different model names
            model_names = ['gemini-pro', 'models/gemini-pro']
            
            for model_name in model_names:
                try:
                    print(f"🔄 Trying model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Simple test
                    test_response = self.model.generate_content("Hello")
                    if hasattr(test_response, 'text') and test_response.text:
                        print(f"🎉 Model {model_name} works!")
                        break
                    else:
                        print(f"❌ Model {model_name} returned empty response")
                        continue
                        
                except Exception as model_error:
                    print(f"❌ Model {model_name} failed: {str(model_error)}")
                    continue
            else:
                raise Exception("No working models found")
            
            print("✅ LLM initialized successfully")
            
        except Exception as e:
            print(f"❌ LLM initialization failed: {str(e)}")
            raise e
    
    def generate(self, prompt):
        try:
            print(f"📝 Generating response for prompt (first 200 chars): {prompt[:200]}...")
            
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            response = self.model.generate_content(prompt)
            print(f"✅ Response received: {response.text[:100] if hasattr(response, 'text') else 'No text attribute'}")
            
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a proper response."
                
        except Exception as e:
            error_msg = f"LLM Generation Error: {str(e)}"
            print(f"❌ {error_msg}")
            return f"I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
