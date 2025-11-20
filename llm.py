import google.generativeai as genai
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['API_KEY']
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            
            # Use gemini-flash-latest model
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("✅ Using model: gemini-1.5-flash-latest")
            
            # Test the connection with a simple prompt
            test_response = self.model.generate_content("Hello")
            if hasattr(test_response, 'text') and test_response.text:
                print("✅ Model test successful")
            else:
                raise Exception("Model test failed - no response")
            
            print("✅ Gemini API connected successfully")
            
        except Exception as e:
            print(f"❌ Gemini API connection failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            print(f"Generating response for prompt: {prompt[:100]}...")
            response = self.model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                print("✅ Response generated successfully")
                return response.text
            else:
                print("❌ Empty response from model")
                return "I apologize, but I couldn't generate a proper response. Please try again."
                
        except Exception as e:
            print(f"LLM Generation Error: {str(e)}")
            return f"I'm experiencing technical difficulties: {str(e)}"
