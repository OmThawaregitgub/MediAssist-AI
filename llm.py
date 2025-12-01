import google.generativeai as genai
import streamlit as st
import os


class LLMClient:
    """
    Initialize the LLMClient by configuring the Google Generative AI model.
    """
    
    def __init__(self) -> None:
        try:
            # Get API key from environment variable
            api_key = st.secrets["GEMINI_API_KEY"]
            if not api_key:
                # Try to get from Streamlit secrets if running in Streamlit
                try:
                    api_key = st.secrets["GEMINI_API_KEY"]
                except:
                    raise ValueError("GOOGLE_API_KEY not found in environment variables or Streamlit secrets")
            
            genai.configure(api_key=api_key)
            
            # Use a specific model
            model_name = "gemini-pro"
            self.model = genai.GenerativeModel(model_name)
            
            # Test the model
            try:
                test_response = self.model.generate_content("Test")
                if test_response.text:
                    print(f"✅ Using model: {model_name}")
            except Exception as e:
                print(f"❌ Model test failed: {e}")
                # Fallback to any available model
                for model in genai.list_models():
                    if 'generateContent' in model.supported_generation_methods:
                        try:
                            self.model = genai.GenerativeModel(model.name)
                            print(f"✅ Fallback to model: {model.name}")
                            break
                        except:
                            continue
                else:
                    raise Exception("No working models found")
                
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise e
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response using the selected LLM model.

        Parameters:
            prompt (str): The input text prompt to generate a response for.

        Returns:
            str: The generated text response, or a user-friendly error message
                 if generation fails.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "I couldn't generate a response."
        except Exception as e:
            return f"Error: {str(e)}"

        

