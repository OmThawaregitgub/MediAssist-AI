# llm.py
import streamlit as st
import google.generativeai as genai

class GeminiLLM:
    def __init__(self):
        try:
            # Get API key from Streamlit secrets
            API_KEY = st.secrets["GEMINI_API_KEY"]
            
            if not API_KEY:
                st.error("GEMINI_API_KEY not found in secrets")
                self.model = None
                return
            
            # Configure the API
            genai.configure(api_key=API_KEY)
            
            # Find available models
            self.model_name = self._find_working_model()
            
            if self.model_name:
                self.model = genai.GenerativeModel(self.model_name)
                st.sidebar.success(f"✅ Using: {self.model_name}")
            else:
                self.model = None
                st.sidebar.error("❌ No working model found")
                
        except Exception as e:
            st.error(f"Initialization error: {e}")
            self.model = None

    def _find_working_model(self):
        """Find a working Gemini model"""
        try:
            # Get list of available models
            models = list(genai.list_models())
            
            # Try these model names in order
            preferred_models = [
                "gemini-1.5-flash",
                "gemini-1.5-pro", 
                "gemini-1.0-pro-001",
                "gemini-pro"
            ]
            
            # First try preferred models
            for model_name in preferred_models:
                try:
                    # Check if model exists and supports generateContent
                    for model_info in models:
                        if model_name in model_info.name and 'generateContent' in model_info.supported_generation_methods:
                            # Test the model
                            test_model = genai.GenerativeModel(model_name)
                            response = test_model.generate_content("Hello")
                            if response.text:
                                return model_name
                except:
                    continue
            
            # If no preferred models work, try any available model
            for model_info in models:
                if 'generateContent' in model_info.supported_generation_methods:
                    try:
                        model_name = model_info.name
                        test_model = genai.GenerativeModel(model_name)
                        response = test_model.generate_content("Test")
                        if response.text:
                            return model_name
                    except:
                        continue
            
            return None
            
        except Exception as e:
            st.sidebar.error(f"Model discovery failed: {e}")
            return None

    def generate(self, prompt: str) -> str:
        # If model initialization failed, use fallback
        if self.model is None:
            return self._fallback_response(prompt)
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            # Use fallback if generation fails
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Provide intelligent fallback responses"""
        prompt_lower = prompt.lower().strip()
        
        # Greetings
        if any(word in prompt_lower for word in ['hi', 'hello', 'hey', 'hola']):
            return "Hello! 👋 I'm your AI assistant. I can help you with various topics including medical research. What would you like to know?"
        
        # Medical questions
        elif any(word in prompt_lower for word in ['cancer', 'medical', 'treatment', 'health', 'disease']):
            return "I can help answer medical questions using our research database. Please ask specific questions about cancer treatments, symptoms, or related medical topics."
        
        # General questions
        elif '?' in prompt or any(word in prompt_lower for word in ['what', 'how', 'why', 'when', 'where']):
            return f"I'd be happy to help with: '{prompt}'. Please try asking your question again."
        
        # Default response
        else:
            return "I'm here to help! Feel free to ask me anything."
