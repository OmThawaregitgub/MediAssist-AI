import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['API_KEY']
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            
            # Common working model names (in order of preference)
            model_names = [
                'gemini-1.0-pro',
                'models/gemini-1.0-pro',
                'gemini-pro',
                'models/gemini-pro'
            ]
            
            for model_name in model_names:
                try:
                    print(f"🔄 Trying model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Test the model
                    test_response = self.model.generate_content("Hello")
                    if hasattr(test_response, 'text') and test_response.text:
                        print(f"🎉 Successfully loaded: {model_name}")
                        break
                    else:
                        print(f"❌ Model {model_name} test failed")
                        continue
                        
                except Exception as model_error:
                    print(f"❌ Failed to load {model_name}: {model_error}")
                    continue
            else:
                raise Exception("No common models worked. Please check your API key and region.")
            
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
