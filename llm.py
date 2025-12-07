# llm.py
import os
from typing import Optional
import requests
import json
import streamlit as st

class LLMClient:
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "mixtral-8x7b-32768"  # Groq's fast model
        self.initialized = False
        self.demo_mode = False
        print(f"LLMClient __init__(): GROQ_API_KEY present: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
    
    def initialize(self, api_key: str = None) -> bool:
        """Initialize the Groq client"""
        print(f"🚀 LLMClient.initialize() STARTING")
        print(f"   - Current self.initialized: {self.initialized}")
        print(f"   - Current self.demo_mode: {self.demo_mode}")
        
        # Set initialized to True immediately
        self.initialized = True
        
        # Get API key
        if api_key and api_key != "demo_key":
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
        
        # Check if we have a valid API key
        if not self.api_key or self.api_key.strip() == "":
            print("⚠️ No valid Groq API key found. Running in DEMO MODE.")
            self.demo_mode = True
            return True
        
        print(f"✅ API key loaded: {self.api_key[:10]}...")
        
        # Test the API connection
        try:
            # Simple test to check if API works
            test_response = self._call_api("Hello, are you working?")
            if test_response:
                self.demo_mode = False
                print(f"✅ Connected to Groq API successfully")
                return True
            else:
                print("⚠️ API test failed. Running in DEMO MODE.")
                self.demo_mode = True
                return True
                
        except Exception as e:
            print(f"❌ API connection error: {e}")
            print("⚠️ Running in DEMO MODE due to error.")
            self.demo_mode = True
            return True
        
    def _call_api(self, prompt: str) -> Optional[str]:
        """Make API call to Groq"""
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful medical research assistant. Provide accurate, evidence-based medical information. Always mention that users should consult healthcare professionals for personalized advice."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"❌ API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return None
    
    def generate(self, prompt: str) -> str:
        """Generate a response - with fallback to demo responses"""
        
        print(f"\n" + "="*50)
        print(f"🎯 llm.generate() called")
        print(f"   Query: '{prompt[:50]}...'")
        print(f"   self.demo_mode: {self.demo_mode}")
        print(f"   self.initialized: {self.initialized}")
        
        if not prompt or prompt.strip() == "":
            return "Please provide a question or message."
        
        # If in demo mode, use demo responses
        if self.demo_mode:
            print(f"   ⚠️ Using demo response")
            return self._get_demo_response(prompt)
        
        # Try to generate with real API
        try:
            print(f"   🔄 Attempting Groq API call...")
            response = self._call_api(prompt)
            if response:
                print(f"   ✅ Groq response successful!")
                print(f"   Response preview: {response[:100]}...")
                return response
            else:
                print("   ⚠️ Empty response from API, using demo response")
                return self._get_demo_response(prompt)
            
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            return self._get_demo_response(prompt)
            
    def _get_demo_response(self, prompt: str) -> str:
        """Get a response based on vector DB context when in demo mode"""
        prompt_lower = prompt.lower().strip()
        
        # Check if this is a vector DB context prompt (contains research information)
        if "based on the following medical research information" in prompt_lower or "medical research information:" in prompt_lower:
            # Extract the actual user question from the prompt
            lines = prompt.split('\n')
            user_question = ""
            research_context = ""
            capturing_context = False
            
            for line in lines:
                if "answer the question:" in line.lower():
                    # Extract question from quotes
                    if '"' in line:
                        user_question = line.split('"')[1]
                    else:
                        # Try to extract after colon
                        parts = line.split(':')
                        if len(parts) > 1:
                            user_question = parts[1].strip()
                
                if "medical research information:" in line.lower():
                    capturing_context = True
                    continue
                    
                if capturing_context:
                    research_context += line + "\n"
            
            # Clean up the research context
            research_context = research_context.strip()
            
            if research_context and user_question:
                # Analyze the research context and provide an answer
                return self._analyze_research_context(user_question, research_context)
        
        # For general medical questions without specific context
        return self._get_general_medical_response(prompt_lower, prompt)

    def _analyze_research_context(self, question: str, research_context: str) -> str:
        """Analyze research context and directly answer the question"""
        
        # Clean up the research context
        research_context = research_context.strip()
        
        # First, try to directly answer common medical questions
        if "diabetes" in question.lower():
            return self._answer_diabetes_question(question, research_context)
        elif "cancer" in question.lower():
            return self._answer_cancer_question(question, research_context)
        elif "fasting" in question.lower():
            return self._answer_fasting_question(question, research_context)
        
        # For other questions, provide a direct analysis
        return self._general_research_analysis(question, research_context)

    def _answer_diabetes_question(self, question: str, research_context: str) -> str:
        """Specifically answer diabetes-related questions"""
        question_lower = question.lower()
        
        if "level" in question_lower or "good" in question_lower or "normal" in question_lower:
            # This is asking about diabetes levels
            answer = """**Answer: Understanding Diabetes Levels**

For diabetes management, there are no "good" or "bad" levels in terms of having diabetes. However, we measure how well diabetes is controlled through:

**Key Metrics for Diabetes Control:**

1. **HbA1c (Glycated Hemoglobin)**
   - Normal: Below 5.7%
   - Prediabetes: 5.7% to 6.4%
   - Diabetes: 6.5% or higher
   - Target for most diabetics: Below 7.0%

2. **Fasting Blood Glucose**
   - Normal: 70-99 mg/dL
   - Prediabetes: 100-125 mg/dL
   - Diabetes: 126 mg/dL or higher

3. **Postprandial (After-meal) Glucose**
   - Normal: Less than 140 mg/dL
   - Target for diabetics: Less than 180 mg/dL

**Important Notes:**
- "Good" diabetes control means maintaining blood sugar within target ranges
- Individual targets vary based on age, diabetes type, and other health factors
- Regular monitoring and medical supervision are essential

**Based on Research:**
"""
            
            # Add relevant research findings
            if "insulin sensitivity" in research_context:
                answer += "The research shows that improving insulin sensitivity through methods like intermittent fasting can help achieve better blood sugar control."
            
            answer += "\n\n**⚠️ Medical Disclaimer:** Always consult with healthcare professionals to determine your personal diabetes management goals and targets."
            return answer
        
        # For other diabetes questions
        return self._general_research_analysis(question, research_context)
    
    def _answer_cancer_question(self, question: str, research_context: str) -> str:
        """Specifically answer cancer-related questions"""
        # Add specific cancer question handling here
        return self._general_research_analysis(question, research_context)
    
    def _answer_fasting_question(self, question: str, research_context: str) -> str:
        """Specifically answer fasting-related questions"""
        # Add specific fasting question handling here
        return self._general_research_analysis(question, research_context)
    
    def _general_research_analysis(self, question: str, research_context: str) -> str:
        """General analysis of research for any question"""
        
        # Count sources in the context
        source_count = research_context.count('Source')
        
        # Extract unique information from research context
        lines = research_context.split('\n')
        unique_points = []
        seen_points = set()
        
        for line in lines:
            if line.strip() and not line.startswith('---'):
                clean_line = line.strip()
                # Only add substantial, unique content
                if len(clean_line) > 30 and clean_line not in seen_points:
                    seen_points.add(clean_line)
                    unique_points.append(clean_line[:300] + "..." if len(clean_line) > 300 else clean_line)
        
        # Limit to 3 most unique points
        unique_points = unique_points[:3]
        
        # Generate response
        response = f"""**Answer to: {question}** Based on {source_count} PubMed research 
        article{'s' if source_count != 1 else ''}:"""
        
        # Add relevant research findings if available
        if unique_points:
            response += "\n**Relevant Research Findings:**\n\n"
            for i, point in enumerate(unique_points, 1):
                response += f"{i}. {point}\n\n"
        else:
            response += "\nThe available research doesn't directly address this specific question.\n\n"
        
        # Add medical disclaimer
        response += "**⚠️ Medical Disclaimer:** I can provide information about cancer, diabetes, and other medical topics. Always consult healthcare professionals for personalized medical advice."
        
        return response


    def _get_general_medical_response(self, prompt_lower: str, original_prompt: str) -> str:
        """Get general medical response when no specific research context is found"""
        
        # Medical responses
        if "cancer" in prompt_lower:
            # ... existing cancer response ...
            pass
            
        elif "fasting" in prompt_lower:
            # ... existing fasting response ...
            pass
            
        elif "diabet" in prompt_lower:
        # Check for specific diabetes level questions
            if "level" in prompt_lower or "good" in prompt_lower or "normal" in prompt_lower:
                return """**Understanding Diabetes Levels**

                        There is no "good" level of having diabetes. Diabetes is a medical condition, not something that comes in "good" or "bad" levels. However, we measure how well diabetes is controlled:

                        **Key Control Metrics:**

        1. **HbA1c** (3-month average blood sugar):
        - Normal: < 5.7%
        - Prediabetes: 5.7-6.4%
        - Diabetes: ≥ 6.5%
        - Target for diabetics: Usually < 7.0%

        2. **Fasting Blood Sugar:**
        - Normal: 70-99 mg/dL
        - Prediabetes: 100-125 mg/dL
        - Diabetes: ≥ 126 mg/dL

        3. **Random Blood Sugar:**
        - Normal: < 140 mg/dL
        - Diabetes: ≥ 200 mg/dL with symptoms

        **What is "Good Control"?**
        - Maintaining blood sugar within target ranges
        - Preventing complications
        - Individualized targets set with your doctor

        **⚠️ Medical Disclaimer:** Always work with healthcare professionals to determine your personal diabetes management goals."""
                    
        else:
        # General diabetes response
            return """**Diabetes Information** 💉
                        Diabetes is a chronic condition affecting how your body processes glucose (sugar).
                        **Types:**
                            - **Type 1** - Autoimmune, usually diagnosed in childhood
                            - **Type 2** - Most common, often related to lifestyle
                            - **Gestational** - Occurs during pregnancy

                        **Management:**
                            - Regular blood sugar monitoring
                            - Healthy diet and exercise
                            - Medication as prescribed
                            - Regular medical check-ups     
                        **⚠️ Medical Disclaimer:** I can provide information about cancer, diabetes, and other medical topics. Always consult healthcare professionals for personalized medical advice."""
                
               