import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        try:
            api_key = os.getenv("API_KEY")
            if not api_key:
                raise ValueError("API_KEY not found in environment variables")
            
            print("Configuring Gemini API...")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("Gemini model initialized successfully")
            
        except Exception as e:
            print(f"Error initializing LLMClient: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            print(f"Sending prompt to LLM (length: {len(prompt)})")
            response = self.model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
                
        except Exception as e:
            error_msg = f"Error in LLM generation: {str(e)}"
            print(error_msg)
            return "I'm experiencing technical difficulties. Please try again in a moment."
