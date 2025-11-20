import google.generativeai as genai
import streamlit as st

class LLMClient:
    """
        Initialize the LLMClient by configuring the Google Generative AI model.

        Workflow:
            1. Retrieves the API key from Streamlit secrets.
            2. Configures the Generative AI client with the retrieved key.
            3. Scans all available models and collects those that support
               'generateContent' functionality.
            4. Iterates through the available models and selects the first one 
               that successfully generates a test response.
            5. Raises an exception if none of the models work.

        Returns:
            None

        Raises:
            ValueError: If the API_KEY is missing in Streamlit secrets.
            Exception: If no compatible or working models are found.
        """
    def __init__(self) -> None:
        try:
            api_key = st.secrets.get('API_KEY')
            if not api_key:
                raise ValueError("API_KEY not found in secrets")
            
            genai.configure(api_key=api_key)
            
            # Find and use available models
            available_models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            
            # Try models in order
            for model_name in available_models:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    # Test the model
                    test_response = self.model.generate_content("Hello")
                    if test_response.text:
                        print(f"✅ Using model: {model_name}")
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

        Behavior:
            - Sends the user's prompt to the configured LLM model.
            - Returns the model's text output when successful.
            - Gracefully handles errors and returns a simple error message instead
              of crashing the application.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "I couldn't generate a response."
        except Exception as e:
            return f"Error: {str(e)}"

