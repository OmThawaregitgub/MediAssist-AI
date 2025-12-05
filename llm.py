import google.generativeai as genai
import os
from dotenv import load_dotenv
from typer import prompt
from model_list import model_list

load_dotenv()

class LLMClient:
    
    def __init__(self):
        self.model = None
        self.initialized = False
        self.demo_mode = False
    
    def initialize(self, api_key: str = None) -> bool:
        """Initialize the Gemini model with robust error handling"""
        print(f"🚀 LLMClient.initialize() STARTING")
        print(f"   - Current self.initialized: {self.initialized}")
        print(f"   - Current self.demo_mode: {self.demo_mode}")
        print(f"   - Current self.model: {'Exists' if self.model else 'None'}")
        
        try:
            # Get API key
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY")
            
            print(f"🔑 API Key check: {'Present' if api_key else 'Missing'}")
            
            # THIS IS CRITICAL: Set initialized to True IMMEDIATELY
            self.initialized = True
            print(f"✅ SET self.initialized = True (Line 1)")
            
            if not api_key or api_key.strip() == "":
                print("⚠️ No valid API key found. Running in DEMO MODE.")
                self.demo_mode = True
                print(f"✅ RETURNING True (no API key)")
                return True
            
            # Configure
            genai.configure(api_key=api_key)
            
            # List of models to try
            models_to_try = model_list(api_key)

            success = False
            for model_name in models_to_try:
                try:
                    print(f"   ⚙️ Trying model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Simple test
                    response = self.model.generate_content("Say hello")
                    if response and response.text:
                        print(f"✅ Connected to: {model_name}")
                        success = True
                        break

                except Exception as e:
                    error_msg = str(e)
                    print(f"   ⚠️ Error with {model_name}: {error_msg[:80]}")
            
            if success:
                self.demo_mode = False
                print(f"✅ Real model connected, demo_mode = False")
            else:
                print("⚠️ All models failed. Running in DEMO MODE.")
                self.demo_mode = True
            
            print(f"🚀 LLMClient.initialize() COMPLETED")
            print(f"   - Final self.initialized: {self.initialized}")
            print(f"   - Final self.demo_mode: {self.demo_mode}")
            print(f"   - Final self.model: {'Exists' if self.model else 'None'}")
            return True
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            print("⚠️ Running in DEMO MODE due to error.")
            self.demo_mode = True
            self.initialized = True  # STILL MARK AS INITIALIZED!
            print(f"✅ SET self.initialized = True (exception handler)")
            return True
        
    def generate(self, prompt: str) -> str:
        """Generate a response - with fallback to demo responses"""
    
        print(f"\n" + "="*50)
        print(f"🎯 llm.generate() called")
        print(f"   Query: '{prompt[:50]}...'")
        print(f"   self.model: {'EXISTS' if self.model else 'NONE'}")
        print(f"   self.demo_mode: {self.demo_mode}")
        print(f"   self.initialized: {self.initialized}")
        
        if not prompt or prompt.strip() == "":
            return "Please provide a question or message."
        
        # Always mark as initialized if we have a model
        if self.model is not None:
            self.initialized = True
            self.demo_mode = False
            print(f"   ✅ Model exists, setting demo_mode=False")
        
        # If in demo mode OR model is None, use demo responses
        if self.demo_mode or self.model is None:
            print(f"   ⚠️ Using demo response (demo_mode={self.demo_mode}, model={self.model})")
            return self._get_demo_response(prompt)
        
        # Try to generate with real model
        try:
            print(f"   🔄 Attempting real Gemini model generation...")
            response = self.model.generate_content(prompt)
            if response and response.text:
                print(f"   ✅ Gemini response successful!")
                print(f"   Response preview: {response.text[:100]}...")
                return response.text
            else:
                print("   ⚠️ Empty response from model, using demo response")
                return self._get_demo_response(prompt)
            
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_demo_response(prompt)
            
    def _get_demo_response(self, prompt: str) -> str:
        """Get a demo response when real AI is not available"""
        prompt_lower = prompt.lower().strip()
        
        # Medical responses
        if "cancer" in prompt_lower:
            return """**Understanding Cancer** 🎗️

Cancer is a group of diseases involving abnormal cell growth with the potential to invade or spread to other parts of the body.

**Common Types:**
- **Breast Cancer** - Most common in women
- **Lung Cancer** - Often linked to smoking
- **Prostate Cancer** - Common in older men
- **Colorectal Cancer** - Affects colon or rectum
- **Skin Cancer** - Often caused by UV exposure

**Key Points:**
- Early detection improves outcomes
- Treatment options include surgery, chemotherapy, radiation
- Lifestyle factors can reduce risk
- Regular screenings are important

**⚠️ Important:** This is general information. Always consult healthcare professionals for personalized medical advice."""

        elif "fasting" in prompt_lower:
            return """**Intermittent Fasting Overview** ⏰

Intermittent fasting (IF) is an eating pattern that cycles between periods of fasting and eating.

**Popular Methods:**
- **16:8 Method** - Fast for 16 hours, eat during 8-hour window
- **5:2 Diet** - Eat normally 5 days, restrict calories 2 days
- **Eat-Stop-Eat** - 24-hour fast once or twice weekly

**Potential Benefits:**
- May support weight loss
- Can improve insulin sensitivity
- May promote cellular repair (autophagy)
- Could reduce inflammation

**⚠️ Important:** Consult a healthcare provider before starting any fasting regimen."""

        elif "diabet" in prompt_lower:
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

**⚠️ Important:** Diabetes management should be supervised by healthcare professionals."""

        elif any(word in prompt_lower for word in ["hello", "hi", "hey", "how are you"]):
            return "Hello! 👋 I'm MediAssist AI. I'm currently running in demo mode. For full AI capabilities, please configure a valid Gemini API key."

        elif "summary" in prompt_lower or "summarize" in prompt_lower:
            return "I can help summarize medical information. In demo mode, please ask specific questions about cancer, fasting, or diabetes."

        # General medical response
        elif any(word in prompt_lower for word in ["medical", "health", "doctor", "hospital", "treatment"]):
            return f"""I understand you're asking about: **{prompt}**

As a medical AI assistant, I provide educational information. For accurate medical advice:

1. **Consult healthcare professionals**
2. **Use verified medical sources**
3. **Never self-diagnose**
4. **Follow prescribed treatments**

**Current Status:** Running in demo mode. Configure API key for full AI responses."""

        # Default response
        return f"""I received your question: **"{prompt}"**

**MediAssist AI Demo Mode:**
- I can provide general medical information
- For specific conditions: ask about cancer, diabetes, or fasting
- For accurate advice: consult healthcare professionals
- For full AI: add a Gemini API key to your .env file

**Try asking:**
- "Tell me about cancer"
- "What is intermittent fasting?"
- "Explain diabetes types" """

    def generate_with_context(self, context: str, query: str) -> str:
        """Generate response with context"""
        if self.demo_mode or not self.model:
            return self._get_demo_response(query)
        
        prompt = f"""Based on this context: {context}

Answer this question: {query}

Provide a clear, accurate response."""
        
        return self.generate(prompt)