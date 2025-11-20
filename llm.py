import streamlit as st
from datetime import datetime

class LLMClient:
    def __init__(self):
        try:
            print(f"✅ Medical Assistant Initialized at {datetime.now()}")
            self.call_count = 0
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise e
    
    def generate(self, prompt):
        try:
            self.call_count += 1
            print(f"📞 Call #{self.call_count}: {prompt[:50]}...")
            
            prompt_lower = prompt.lower().strip()
            
            # Greetings
            if any(word in prompt_lower for word in ["hi", "hello", "hey", "how are you"]):
                return "Hello! 👋 I'm MediAssist AI. I can provide detailed medical information about cancer types, intermittent fasting, diabetes, and general health topics. What would you like to know?"
            
            # Cancer questions
            elif "cancer" in prompt_lower:
                return self._get_cancer_info()
            
            # Fasting questions
            elif any(word in prompt_lower for word in ["fasting", "diet", "weight", "16:8", "5:2"]):
                return self._get_fasting_info()
            
            # Diabetes questions
            elif "diabet" in prompt_lower:
                return self._get_diabetes_info()
            
            # Heart health
            elif any(word in prompt_lower for word in ["heart", "blood pressure", "cholesterol"]):
                return self._get_heart_info()
            
            # General medical
            else:
                return f"""I understand you're asking about: "{prompt}"

As a medical AI assistant, I can provide information on:

🏥 **Cancer Types & Treatments**
⏰ **Intermittent Fasting Methods**
🩺 **Diabetes Management** 
❤️ **Heart Health**
💊 **General Medical Topics**

Please ask me about any specific health topic, and I'll provide comprehensive, organized information.

**Note:** For personal medical advice, always consult healthcare professionals."""

        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_cancer_info(self):
        return """**COMPREHENSIVE CANCER GUIDE**

**MAJOR CATEGORIES:**
1. **Carcinomas** (85-90% of cancers)
   - Breast, Lung, Prostate, Colorectal, Skin
   
2. **Sarcomas** (Bone & Soft Tissue)
   - Osteosarcoma, Liposarcoma
   
3. **Leukemias** (Blood Cancers)
   - ALL, AML, CLL, CML
   
4. **Lymphomas** 
   - Hodgkin, Non-Hodgkin
   
5. **Central Nervous System**
   - Brain tumors, Spinal tumors

**TREATMENT OPTIONS:**
• Surgery • Radiation • Chemotherapy
• Immunotherapy • Targeted Therapy
• Hormone Therapy • Stem Cell Transplant

**Note:** Treatment depends on cancer type, stage, and individual factors."""

    def _get_fasting_info(self):
        return """**INTERMITTENT FASTING METHODS**

**Popular Approaches:**
⏰ **16:8 Method** - Fast 16h, Eat 8h
📅 **5:2 Diet** - Normal 5 days, 500cal 2 days
🔄 **Alternate-Day** - Switch normal/fast days
🌅 **Eat-Stop-Eat** - 24h fasts 1-2x/week

**Benefits:**
• Weight loss (3-8% in 3-24 weeks)
• Improved insulin sensitivity  
• Reduced inflammation
• Cellular repair (autophagy)

**Safety:** Consult doctor if diabetic, pregnant, or have health conditions."""

    def _get_diabetes_info(self):
        return """**DIABETES MANAGEMENT**

**Types:**
• Type 1 - Autoimmune, insulin-dependent
• Type 2 - Insulin resistance, most common
• Gestational - During pregnancy
• Prediabetes - Early warning stage

**Management:**
Medication, Diet, Exercise, Monitoring

Consult endocrinologist for personalized care."""

    def _get_heart_info(self):
        return """**HEART HEALTH**

**Key Factors:**
• Blood Pressure control
• Cholesterol management
• Regular exercise
• Healthy diet
• Stress management

**Common Conditions:**
Hypertension, Coronary Artery Disease, Heart Failure

Regular check-ups with cardiologist recommended."""
