import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY not found in environment variables. Please check your .env file or Streamlit Cloud environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate(self, prompt):
        try:
            if not prompt or not prompt.strip():
                return "Please provide a valid question."
            
            response = self.model.generate_content(prompt)
            
            # Check if response is valid
            if hasattr(response, 'text'):
                return response.text
            else:
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
                
        except Exception as e:
            return f"I encountered an error while generating the response: {str(e)}. Please try again."
