import google.generativeai as genai
import os
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            # Use the correct secret name - either 'API_KEY' or 'GEMINI_API_KEY'
            api_key = st.secrets['API_KEY']  # Change this if you used different name
            
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
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
            return "I'm experiencing technical difficulties. Please try again in a moment."
