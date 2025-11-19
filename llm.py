import openai
import os
import streamlit as st

class LLMClient:
    def __init__(self):
        try:
            # Get OpenAI key from secrets
            api_key = st.secrets['GEMINI_API_KEY']
            
            if not api_key:
                raise ValueError("OpenAI_key not found in environment variables or Streamlit secrets.")
            
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            
            print("✅ OpenAI API connected successfully")
            
        except Exception as e:
            print(f"❌ OpenAI API connection failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant specializing in intermittent fasting and metabolic health. Provide evidence-based answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            error_msg = f"OpenAI API Error: {str(e)}"
            print(f"LLM Generation Error: {error_msg}")
            return "I'm experiencing technical difficulties. Please try again in a moment."
