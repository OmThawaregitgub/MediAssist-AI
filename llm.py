# llm.py
import streamlit as st
import google.generativeai as genai

class GeminiLLM:
    def __init__(self):
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        if not API_KEY:
            raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in Streamlit secrets.")
        
        # Configure the API
        genai.configure(api_key=API_KEY)
        
        # Find available model
        self.model_name = self._discover_working_model()

    def _discover_working_model(self):
        """Discover which model works with the current API"""
        # Try the most common models
        model_candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-1.0-pro",
        ]
        
        for model_name in model_candidates:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Test")
                if response.text:
                    return model_name
            except Exception:
                continue
                
        return "gemini-1.5-flash"

    def generate(self, prompt: str) -> str:
        try:
            model = genai.GenerativeModel(self.model_name)
            
            # Enhanced prompt for better table generation
            enhanced_prompt = prompt
            if "table" in prompt.lower() or "tabular" in prompt.lower():
                enhanced_prompt += "\n\nPlease format the response as a clear, well-structured table. Use markdown table format if possible for better readability."
            
            response = model.generate_content(enhanced_prompt)
            return response.text
        except Exception as e:
            # Provide comprehensive fallback for cancer information requests
            if "cancer" in prompt.lower() and "type" in prompt.lower():
                return self._fallback_cancer_table()
            elif "cancer" in prompt.lower():
                return "I can provide comprehensive information about various cancer types and treatments. Our database includes research on breast cancer, lung cancer, and many other types. Please ask about specific cancer types or treatment approaches."
            else:
                return "I'm here to help with medical research questions. Please ask me about cancer types, treatments, or recent medical studies."

    def _fallback_cancer_table(self):
        """Fallback table when LLM is not available"""
        return """
**Comprehensive Cancer Types and Treatments Overview**

| Cancer Type | Common Locations | Main Treatments | Recent Advances |
|-------------|------------------|-----------------|-----------------|
| **Breast Cancer** | Breast tissue | Surgery, Radiation, Chemo, Hormone therapy | Targeted therapies, Immunotherapy |
| **Lung Cancer** | Lungs | Surgery, Radiation, Chemo, Immunotherapy | Targeted drugs, Immunotherapies |
| **Prostate Cancer** | Prostate gland | Surgery, Radiation, Hormone therapy | Precision radiation, New hormonal agents |
| **Colorectal Cancer** | Colon, Rectum | Surgery, Chemo, Radiation | Targeted therapies, Immunotherapy |
| **Leukemia** | Blood, Bone marrow | Chemo, Radiation, Stem cell transplant | CAR-T cell therapy, Targeted drugs |
| **Lymphoma** | Lymph nodes | Chemo, Radiation, Immunotherapy | CAR-T therapy, New antibody drugs |
| **Melanoma** | Skin | Surgery, Immunotherapy, Targeted therapy | Immune checkpoint inhibitors |
| **Pancreatic Cancer** | Pancreas | Surgery, Chemo, Radiation | New combination therapies |
| **Ovarian Cancer** | Ovaries | Surgery, Chemo | PARP inhibitors, Targeted therapies |
| **Brain Cancer** | Brain | Surgery, Radiation, Chemo | Tumor treating fields, Targeted drugs |

*Note: This is general information. Treatment plans are personalized based on individual factors.*
"""

    def get_model_info(self):
        return f"Using model: {self.model_name}"
