import google.generativeai as genai
import os
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            api_key = st.secrets['GEMINI_API_KEY']
            if not api_key:
                raise ValueError("API_KEY not found in environment variables. Please check your Streamlit Cloud secrets or .env file.")
            
            # Check if API key looks valid (starts with AIza)
            if not api_key.startswith('AIza'):
                raise ValueError("Invalid API key format. Google Gemini keys usually start with 'AIza'")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
            # Test the connection
            test_response = self.model.generate_content("Hello")
            if not hasattr(test_response, 'text'):
                raise ValueError("API key test failed - no response from Gemini")
                
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
                return "I apologize, but I couldn't generate a proper response. The API returned an empty response."
                
        except Exception as e:
            error_msg = f"API Error: {str(e)}"
            print(f"LLM Generation Error: {error_msg}")
            return "I'm experiencing technical difficulties with the AI service. Please check your API key and try again."
