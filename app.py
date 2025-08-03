import streamlit as st
import os
import json
import time
from datetime import datetime
import logging
from typing import Dict, List
import random

# Import advanced components
from advanced_memory_manager import AdvancedMemoryManager
from advanced_knowledge_base import AdvancedKnowledgeBase
from advanced_rag_system import AdvancedRAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Healthcare Assistant Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling with modern design
st.markdown("""
    <style>
        /* Global styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container with glassmorphism */
        .main-container {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 24px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 25px 50px rgba(0,0,0,0.1);
        }
        
        /* Professional header with gradient */
        .main-header {
            font-size: 4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 1.5rem;
            letter-spacing: -0.02em;
            animation: headerGlow 4s ease-in-out infinite;
        }
        
        @keyframes headerGlow {
            0%, 100% { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.3)); }
            50% { filter: drop-shadow(0 0 30px rgba(118, 75, 162, 0.5)); }
        }
        
        .sub-header {
            font-size: 1.8rem;
            color: #1a202c;
            margin-bottom: 1.5rem;
            font-weight: 600;
            text-align: center;
            letter-spacing: -0.01em;
        }
        
        .section-header {
            font-size: 1.4rem;
            color: #2d3748;
            margin-bottom: 1rem;
            font-weight: 600;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }
        
        /* Enhanced chat interface with auto-scroll */
        .chat-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.08);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            max-height: 600px;
            overflow-y: auto;
            scrollbar-width: thin;
            scroll-behavior: smooth;
        }
        
        /* Custom scrollbar for chat container */
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: rgba(102, 126, 234, 0.3);
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: rgba(102, 126, 234, 0.5);
        }
        
        /* Auto-scroll indicator */
        .auto-scroll-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(102, 126, 234, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        
        .auto-scroll-indicator.show {
            opacity: 1;
        }
        scrollbar-color: #667eea #f1f5f9;
    }
    
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Professional message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff !important;
        padding: 20px 24px;
        border-radius: 20px 20px 8px 20px;
        margin: 16px 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
        position: relative;
        font-weight: 500;
        line-height: 1.6;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInLeft 0.5s ease-out;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        color: #ffffff !important;
        padding: 20px 24px;
        border-radius: 20px 20px 20px 8px;
        margin: 16px 0;
        box-shadow: 0 8px 25px rgba(45, 55, 72, 0.3);
        position: relative;
        font-weight: 500;
        line-height: 1.6;
        border: 1px solid #667eea;
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .assistant-message strong {
        color: #667eea !important;
        font-weight: 700;
    }
    
    .assistant-message p {
        color: #f7fafc !important;
        line-height: 1.7;
        margin: 12px 0;
    }
    
    .assistant-message ul, .assistant-message ol {
        color: #f7fafc !important;
        margin: 12px 0;
        padding-left: 25px;
    }
    
    .assistant-message li {
        color: #f7fafc !important;
        margin: 8px 0;
        line-height: 1.6;
    }
    
    /* Enhanced sidebar */
    .sidebar-content {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        padding: 25px;
        border-radius: 20px;
        color: #ffffff;
        border: 1px solid #667eea;
        box-shadow: 0 15px 35px rgba(26, 32, 44, 0.3);
        margin-bottom: 20px;
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
        color: #667eea;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        margin: 12px 0;
        padding: 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        margin: 8px 0;
        padding: 8px 12px;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    
    /* Professional metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
        border-left-color: #764ba2;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        letter-spacing: 0.01em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    /* Professional status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 12px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 10px currentColor;
    }
    
    .status-online {
        background: #48bb78;
        color: #48bb78;
    }
    
    .status-processing {
        background: #ed8936;
        color: #ed8936;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Enhanced animations */
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(40px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Professional input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        color: #2d3748 !important;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        font-weight: 500;
        padding: 16px 20px;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 8px 25px rgba(0,0,0,0.1);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0 !important;
        font-weight: 500;
    }
    
    /* Chat input enhancement */
    .stChatInput > div > div > div > textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        padding: 16px 20px !important;
        font-size: 1rem !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stChatInput > div > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 8px 25px rgba(0,0,0,0.1) !important;
    }
    
    .stChatInput > div > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 500 !important;
    }
    
    /* Professional footer */
    .footer-content {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%);
        border-radius: 20px;
        padding: 25px;
        margin-top: 30px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.1);
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    
    .footer-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 10px;
    }
    
    .footer-text {
        color: #4a5568;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 5px 0;
    }
    

    
    /* Remove any red borders or outlines */
    * {
        outline: none !important;
    }
    
    /* Override any Streamlit default red borders */
    .stApp > div > div > div > div > div > div > div {
        border: none !important;
        outline: none !important;
    }
    
    /* Ensure no red borders on any elements */
    div, span, input, textarea, button {
        border-color: transparent !important;
        outline-color: transparent !important;
    }
    
    /* Additional overrides for any red borders */
    .stApp, .stApp > div, .stApp > div > div {
        border: none !important;
        outline: none !important;
    }
    
    /* Override any focus states that might show red */
    *:focus {
        outline: none !important;
        border-color: transparent !important;
    }
    
    /* Remove any error styling */
    .stAlert, .stError, .stWarning {
        border: none !important;
        outline: none !important;
    }
    
    /* Override any browser default styling */
    html, body {
        border: none !important;
        outline: none !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .chat-container {
            padding: 20px;
        }
        
        .metric-card {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    """Initialize the RAG system."""
    try:
        rag_system = AdvancedRAGSystem()
        logger.info("RAG system initialized successfully")
        return rag_system
    except Exception as e:
        st.error(f"Error initializing system: {e}")
        return None

def generate_dynamic_response(user_input: str, rag_system, session_id: str, user_id: str) -> str:
    """Generate dynamic, contextual responses based on user input."""
    
    # Get base response from RAG system
    response_data = rag_system.generate_response(user_input, session_id, user_id)
    
    if "error" in response_data:
        return f"I apologize, but I encountered an error: {response_data['error']}"
    
    base_response = response_data.get("response", "")
    
    # Analyze user input for dynamic response generation
    user_input_lower = user_input.lower()
    
    # Dynamic response patterns based on user input
    if any(word in user_input_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        greetings = [
            "Hello! 👋 I'm your Healthcare Assistant. How can I help you today?",
            "Hi there! 😊 I'm here to assist with your health questions. What would you like to know?",
            "Hey! 🌟 Welcome to your healthcare consultation. How are you feeling today?",
            "Good to see you! 💙 I'm ready to help with any health-related questions you might have."
        ]
        return random.choice(greetings)
    
    elif any(word in user_input_lower for word in ["cold", "cough", "flu", "fever", "influenza"]):
        # More specific detection for different respiratory conditions
        if any(word in user_input_lower for word in ["cold", "cough"]):
            cold_responses = [
                f"🤧 **Common Cold: Your Complete Guide**\n\nI understand you're asking about cold symptoms. Here's what you should know:\n\n**Understanding the Common Cold:**\nThe common cold is a viral infection of the upper respiratory tract, typically caused by rhinoviruses.\n\n**Common Cold Symptoms:**\n• Runny or stuffy nose\n• Sore throat\n• Cough (dry or productive)\n• Sneezing\n• Mild fatigue\n• Mild headache\n• Low-grade fever (rare)\n\n**Treatment and Management:**\n• **Rest:** Allow your body to fight the infection\n• **Hydration:** Drink plenty of fluids (water, tea, clear broths)\n• **Humidification:** Use a humidifier to ease congestion\n• **Saltwater gargle:** For sore throat relief\n• **Over-the-counter medications:** Decongestants, pain relievers\n\n**Recovery Timeline:**\nMost colds resolve within 7-10 days. Symptoms typically peak around days 3-5.\n\n**When to Seek Medical Care:**\n• Symptoms lasting more than 10 days\n• High fever (above 101°F/38.3°C)\n• Severe headache or sinus pain\n• Difficulty breathing\n• Persistent cough with colored mucus\n\n⚠️ **Important:** This information is for educational purposes. Always consult healthcare professionals for medical advice.",
                
                f"😷 **Cold Management: Smart Strategies**\n\nLet me help you understand cold management:\n\n**What is a Cold?**\nA cold is a mild viral infection that affects your nose and throat. It's different from the flu and usually less severe.\n\n**Cold vs. Flu Differences:**\n• **Cold:** Gradual onset, mild symptoms, rarely causes fever\n• **Flu:** Sudden onset, severe symptoms, often includes fever\n\n**Effective Cold Relief:**\n• **Nasal Irrigation:** Saline sprays or neti pots\n• **Steam Inhalation:** Hot shower or steam bowl\n• **Honey:** Natural cough suppressant (for adults)\n• **Zinc Supplements:** May reduce duration if taken early\n• **Vitamin C:** Supports immune function\n\n**Prevention Strategies:**\n• Frequent hand washing\n• Avoid touching face\n• Stay away from sick people\n• Maintain good sleep and nutrition\n• Consider annual flu vaccination\n\n**Home Care Tips:**\n• Elevate your head while sleeping\n• Use menthol rubs for congestion\n• Stay warm and comfortable\n• Avoid alcohol and smoking\n\n⚠️ **Medical Disclaimer:** Consult healthcare providers for personalized advice.",
                
                f"🌡️ **Cold Symptoms: Understanding Your Body**\n\nI'm here to help you understand cold symptoms and management:\n\n**Typical Cold Progression:**\n• **Days 1-2:** Sore throat, runny nose\n• **Days 3-5:** Peak symptoms, congestion, cough\n• **Days 6-10:** Gradual improvement\n\n**Symptom Management:**\n• **Congestion:** Decongestants, steam, saline sprays\n• **Cough:** Honey, cough drops, humidifier\n• **Sore Throat:** Saltwater gargle, throat lozenges\n• **Fatigue:** Rest, adequate sleep, light activity\n\n**Nutrition During Cold:**\n• **Hydration:** Water, herbal teas, clear soups\n• **Vitamin-Rich Foods:** Citrus fruits, vegetables\n• **Protein:** Lean meats, eggs, legumes\n• **Avoid:** Dairy (may thicken mucus)\n\n**Red Flags to Watch For:**\n🚨 High fever (above 101°F)\n🚨 Severe headache or neck stiffness\n🚨 Difficulty breathing or chest pain\n🚨 Symptoms lasting more than 10 days\n🚨 Colored or thick mucus\n\n**Recovery Support:**\n• Listen to your body\n• Don't rush back to normal activities\n• Continue good hygiene practices\n• Monitor for complications\n\n⚠️ **Professional Care:** Seek medical attention for severe or persistent symptoms.",
                
                f"💊 **Cold Treatment: Evidence-Based Approach**\n\nLet me provide you with a comprehensive cold treatment strategy:\n\n**Phase 1: Early Symptoms (Days 1-2)**\n• **Immediate Actions:** Rest, hydration, saltwater gargle\n• **Supplements:** Zinc lozenges, vitamin C\n• **Monitoring:** Track symptom progression\n• **Prevention:** Avoid spreading to others\n\n**Phase 2: Peak Symptoms (Days 3-5)**\n• **Symptom Relief:** Decongestants, pain relievers\n• **Comfort Measures:** Humidifier, steam inhalation\n• **Nutrition:** Light, nutritious meals\n• **Activity:** Gentle movement, avoid overexertion\n\n**Phase 3: Recovery (Days 6-10)**\n• **Gradual Return:** Resume normal activities slowly\n• **Continued Care:** Maintain hydration and rest\n• **Prevention:** Strengthen immune system\n• **Monitoring:** Watch for complications\n\n**Evidence-Based Treatments:**\n• **Zinc:** May reduce cold duration by 1-2 days\n• **Vitamin C:** May reduce severity in some cases\n• **Honey:** Effective cough suppressant for children\n• **Rest:** Essential for immune function\n\n**When to Escalate:**\nSeek medical care if:\n• Symptoms worsen after 5 days\n• High fever develops\n• Breathing difficulties occur\n• Severe pain or pressure symptoms\n\n⚠️ **Medical Guidance:** Always consult healthcare professionals for personalized treatment plans."
            ]
            return random.choice(cold_responses)
        elif any(word in user_input_lower for word in ["flu", "influenza"]):
            flu_responses = [
                f"🤒 **Seasonal Influenza: Your Complete Guide**\n\nI understand you're asking about the flu. Here's what you should know:\n\n**Understanding Influenza:**\nThe flu is a highly contagious respiratory illness caused by influenza viruses. It's more severe than a cold and affects millions worldwide annually.\n\n**Flu Symptoms (More Severe Than Cold):**\n• Sudden onset of high fever (100-102°F)\n• Severe body aches and muscle pain\n• Extreme fatigue and weakness\n• Dry cough and sore throat\n• Headache and sometimes nausea\n• Gastrointestinal symptoms (in some cases)\n\n**Treatment and Management:**\n• **Rest:** Essential for recovery\n• **Hydration:** Plenty of fluids to prevent dehydration\n• **Fever Management:** Acetaminophen or ibuprofen\n• **Antiviral Medications:** May be prescribed if caught early\n• **Isolation:** Stay home to prevent spreading\n\n**Recovery Timeline:**\nSymptoms typically last 1-2 weeks, with fatigue potentially persisting longer.\n\n**When to Seek Medical Care:**\n• Difficulty breathing or chest pain\n• Persistent high fever\n• Severe muscle pain\n• Signs of dehydration\n• Worsening symptoms after 5 days\n\n⚠️ **Important:** The flu can be serious. High-risk individuals should seek medical attention promptly.",
                
                f"🏥 **Flu Management: Evidence-Based Approach**\n\nLet me help you understand flu management:\n\n**Flu vs. Cold Comparison:**\n• **Flu:** Sudden onset, high fever, severe body aches\n• **Cold:** Gradual onset, mild symptoms, rarely fever\n\n**Effective Flu Treatment:**\n• **Antiviral Medications:** Tamiflu, Relenza (if prescribed early)\n• **Symptom Relief:** Pain relievers, decongestants\n• **Comfort Measures:** Warm blankets, humidifier\n• **Nutrition:** Light, easily digestible foods\n• **Rest:** Allow your body to fight the infection\n\n**Prevention Strategies:**\n• Annual flu vaccination (recommended for everyone 6+ months)\n• Frequent hand washing\n• Avoid close contact with sick individuals\n• Cover coughs and sneezes\n• Maintain good overall health\n\n**High-Risk Groups:**\n• Young children and elderly adults\n• Pregnant women\n• People with chronic health conditions\n• Healthcare workers\n\n**Complications to Watch For:**\n🚨 Pneumonia\n🚨 Bronchitis\n🚨 Sinus infections\n🚨 Worsening of existing conditions\n\n⚠️ **Medical Disclaimer:** Consult healthcare providers for personalized flu management.",
                
                f"💊 **Flu Treatment: Your Recovery Strategy**\n\nI'm here to help you understand flu treatment:\n\n**Immediate Actions When Flu Strikes:**\n• **Rest Immediately:** Your body needs energy to fight\n• **Stay Hydrated:** Water, clear broths, electrolyte solutions\n• **Monitor Fever:** Track temperature regularly\n• **Isolate:** Prevent spreading to others\n\n**Symptom Management:**\n• **Fever:** Acetaminophen or ibuprofen\n• **Body Aches:** Warm baths, gentle stretching\n• **Cough:** Honey, cough drops, humidifier\n• **Fatigue:** Listen to your body, rest when needed\n\n**Nutrition During Flu:**\n• **Easy-to-Digest:** Broths, soups, toast\n• **Hydration:** Water, herbal teas, clear juices\n• **Avoid:** Heavy, greasy foods\n• **Gradual Return:** Resume normal eating as you improve\n\n**Recovery Timeline:**\n• **Days 1-3:** Most severe symptoms\n• **Days 4-7:** Gradual improvement\n• **Week 2+:** Return to normal activities\n\n**When to Escalate:**\nSeek immediate medical care if:\n• Difficulty breathing or chest pain\n• Persistent high fever\n• Severe dehydration symptoms\n• Worsening after 5 days\n\n⚠️ **Professional Care:** High-risk individuals should seek medical attention promptly.",
                
                f"🩺 **Flu Prevention and Management**\n\nLet me provide you with a comprehensive flu strategy:\n\n**Phase 1: Prevention (Year-Round)**\n• **Annual Vaccination:** Get flu shot every year\n• **Healthy Lifestyle:** Good nutrition, exercise, sleep\n• **Hygiene:** Frequent hand washing, avoid touching face\n• **Awareness:** Know flu season timing (fall/winter)\n\n**Phase 2: Early Detection**\n• **Recognize Symptoms:** Sudden onset, high fever, body aches\n• **Quick Action:** Rest, hydration, monitor symptoms\n• **Medical Consultation:** Consider antiviral medications\n• **Isolation:** Prevent spreading to others\n\n**Phase 3: Treatment and Recovery**\n• **Symptom Management:** Pain relievers, rest, hydration\n• **Monitoring:** Watch for complications\n• **Gradual Return:** Resume activities slowly\n• **Prevention:** Strengthen immune system post-recovery\n\n**Phase 4: Post-Recovery**\n• **Health Maintenance:** Continue healthy habits\n• **Vaccination Planning:** Prepare for next flu season\n• **Education:** Learn from the experience\n• **Support:** Help others prevent flu\n\n**Success Indicators:**\n• Reduced flu frequency and severity\n• Faster recovery when flu occurs\n• Better overall health\n• Protection of vulnerable family members\n\n⚠️ **Healthcare Partnership:** Work with healthcare providers for optimal flu management."
            ]
            return random.choice(flu_responses)
        else:
            # Fever-specific responses
            fever_responses = [
            f"🌡️ **Fever Management Guide**\n\nI understand you're asking about fever. Here's what you should know:\n\n**Immediate Actions:**\n• Monitor your temperature regularly\n• Stay hydrated with water, clear broths, or electrolyte solutions\n• Rest and avoid strenuous activities\n• Use cool compresses on your forehead\n\n**When to Seek Medical Care:**\n• Temperature above 103°F (39.4°C)\n• Fever lasting more than 3 days\n• Severe headache or neck stiffness\n• Difficulty breathing\n\n**Home Care Tips:**\n• Take acetaminophen or ibuprofen as directed\n• Wear lightweight clothing\n• Keep your room cool and well-ventilated\n• Avoid alcohol and caffeine\n\n⚠️ **Important:** If you experience severe symptoms or the fever persists, please consult a healthcare professional immediately.",
            
            f"🤒 **Understanding Your Fever**\n\nLet me help you understand fever and how to manage it effectively:\n\n**What is Fever?**\nA fever is your body's natural defense mechanism against infection. It helps fight off viruses and bacteria.\n\n**Temperature Guidelines:**\n• Normal: 97-99°F (36-37°C)\n• Low-grade: 100-101°F (37.8-38.3°C)\n• Moderate: 102-103°F (38.9-39.4°C)\n• High: Above 103°F (39.4°C)\n\n**Treatment Approach:**\n• Focus on comfort and hydration\n• Monitor for other symptoms\n• Know when to seek medical attention\n\n💡 **Pro Tip:** Keep a fever diary to track temperature, symptoms, and any medications taken.\n\n⚠️ **Remember:** This information is for educational purposes. Always consult healthcare professionals for medical advice.",
            
            f"🏥 **Fever: Your Body's Defense System**\n\nI'm here to help you understand fever management:\n\n**Why Fever Occurs:**\nYour body raises its temperature to create an environment that's less hospitable to invading pathogens.\n\n**Smart Management Strategies:**\n• **Hydration First:** Drink plenty of fluids\n• **Rest is Best:** Allow your body to focus on healing\n• **Comfort Measures:** Light clothing, cool environment\n• **Medication:** Use fever reducers as needed\n\n**Red Flags to Watch For:**\n🚨 Very high fever (104°F/40°C or higher)\n🚨 Fever with rash\n🚨 Severe headache or confusion\n🚨 Difficulty breathing\n\n**Recovery Timeline:**\nMost fevers resolve within 3-5 days. If yours persists longer, seek medical evaluation.\n\n⚠️ **Medical Disclaimer:** This is general information. Your specific situation may require professional medical attention.",
            
            f"💊 **Fever Management: A Comprehensive Approach**\n\nLet me provide you with a complete fever management strategy:\n\n**Phase 1: Assessment**\n• Check temperature with a reliable thermometer\n• Note accompanying symptoms\n• Consider recent exposures or activities\n\n**Phase 2: Immediate Care**\n• **Hydration:** Water, herbal teas, clear soups\n• **Comfort:** Light clothing, cool environment\n• **Medication:** Acetaminophen or ibuprofen as directed\n• **Rest:** Allow your immune system to work\n\n**Phase 3: Monitoring**\n• Track temperature every 4-6 hours\n• Watch for new or worsening symptoms\n• Maintain hydration and nutrition\n\n**Phase 4: When to Escalate**\nSeek immediate medical care if:\n• Temperature exceeds 103°F\n• Severe symptoms develop\n• Fever persists beyond 3 days\n\n⚠️ **Professional Guidance:** Always consult healthcare providers for personalized medical advice."
        ]
        return random.choice(fever_responses)
    
    elif any(word in user_input_lower for word in ["heart", "cardiac", "chest pain", "hypertension"]):
        cardiac_responses = [
            f"❤️ **Cardiac Health: Your Heart Matters**\n\nI understand your concern about heart health. Here's what you should know:\n\n**Heart-Healthy Lifestyle:**\n• **Exercise:** 150 minutes of moderate activity weekly\n• **Diet:** Mediterranean-style eating pattern\n• **Stress Management:** Practice relaxation techniques\n• **Sleep:** Aim for 7-9 hours quality sleep\n\n**Warning Signs to Never Ignore:**\n🚨 Chest pain or pressure\n🚨 Shortness of breath\n🚨 Pain radiating to arm, jaw, or back\n🚨 Dizziness or fainting\n🚨 Irregular heartbeat\n\n**Prevention Strategies:**\n• Regular check-ups with your doctor\n• Monitor blood pressure and cholesterol\n• Maintain healthy weight\n• Avoid smoking and excessive alcohol\n\n⚠️ **Emergency:** If you experience chest pain or other cardiac symptoms, call emergency services immediately.",
            
            f"🫀 **Protecting Your Heart: A Complete Guide**\n\nLet me help you understand heart health and prevention:\n\n**Understanding Your Heart:**\nYour heart is a powerful muscle that pumps blood throughout your body. Keeping it healthy is crucial for overall wellness.\n\n**Key Risk Factors:**\n• High blood pressure\n• High cholesterol\n• Diabetes\n• Smoking\n• Physical inactivity\n• Obesity\n• Family history\n\n**Heart-Healthy Actions:**\n• **Move More:** Walking, swimming, cycling\n• **Eat Smart:** Fruits, vegetables, whole grains, lean proteins\n• **Manage Stress:** Meditation, yoga, deep breathing\n• **Regular Check-ups:** Annual physical exams\n\n**Early Detection:**\nRegular screenings can catch issues before they become serious problems.\n\n⚠️ **Medical Disclaimer:** This information is educational. Consult healthcare professionals for personalized advice.",
            
            f"💓 **Cardiac Wellness: Building a Strong Heart**\n\nI'm here to support your heart health journey:\n\n**The Heart-Health Connection:**\nYour heart health affects every aspect of your life - energy, mood, and longevity.\n\n**Daily Heart-Healthy Habits:**\n• **Morning:** Start with gentle stretching\n• **Meals:** Include heart-healthy fats (avocado, nuts, olive oil)\n• **Activity:** Take walking breaks throughout the day\n• **Evening:** Practice stress-reduction techniques\n\n**Nutrition for Heart Health:**\n• Omega-3 fatty acids (fish, flaxseeds)\n• Antioxidants (berries, dark chocolate)\n• Fiber (oats, legumes, vegetables)\n• Potassium (bananas, spinach, sweet potatoes)\n\n**Monitoring Your Heart:**\n• Track your blood pressure\n• Know your cholesterol numbers\n• Monitor your resting heart rate\n• Pay attention to how you feel\n\n⚠️ **Professional Care:** Regular medical check-ups are essential for heart health.",
            
            f"🏃‍♂️ **Heart Health: Your Action Plan**\n\nLet me provide you with a comprehensive heart health strategy:\n\n**Assessment Phase:**\n• Know your numbers (blood pressure, cholesterol, BMI)\n• Understand your family history\n• Identify your risk factors\n\n**Action Phase:**\n• **Exercise Plan:** Start with 10-minute walks, build to 30+ minutes\n• **Diet Changes:** Reduce sodium, increase fiber, choose lean proteins\n• **Stress Reduction:** Find activities that bring you joy and peace\n• **Sleep Optimization:** Create a consistent sleep schedule\n\n**Maintenance Phase:**\n• Regular medical check-ups\n• Consistent healthy habits\n• Monitoring and adjusting as needed\n\n**Emergency Awareness:**\nKnow the signs of heart attack and stroke. Time is critical in cardiac emergencies.\n\n⚠️ **Medical Guidance:** Always work with healthcare professionals for personalized heart health plans."
        ]
        return random.choice(cardiac_responses)
    
    elif any(word in user_input_lower for word in ["diabetes", "blood sugar", "insulin"]):
        diabetes_responses = [
            f"🩸 **Diabetes Management: Taking Control**\n\nI understand you're asking about diabetes. Here's a comprehensive guide:\n\n**Understanding Blood Sugar:**\n• **Normal Range:** 70-140 mg/dL\n• **Pre-diabetes:** 140-199 mg/dL\n• **Diabetes:** 200+ mg/dL\n\n**Daily Management Strategies:**\n• **Monitoring:** Check blood sugar as recommended\n• **Medication:** Take prescribed medications consistently\n• **Diet:** Focus on complex carbohydrates and fiber\n• **Exercise:** Regular physical activity helps control blood sugar\n\n**Lifestyle Modifications:**\n• **Meal Planning:** Eat at regular intervals\n• **Portion Control:** Use the plate method\n• **Stress Management:** Practice relaxation techniques\n• **Sleep:** Aim for 7-8 hours nightly\n\n**Warning Signs:**\n🚨 Very high or low blood sugar\n🚨 Excessive thirst or urination\n🚨 Fatigue or confusion\n🚨 Slow-healing wounds\n\n⚠️ **Medical Supervision:** Work closely with your healthcare team for personalized diabetes management.",
            
            f"🍎 **Diabetes Wellness: Your Complete Guide**\n\nLet me help you understand diabetes care and management:\n\n**The Diabetes Journey:**\nManaging diabetes is about creating sustainable, healthy habits that work for your lifestyle.\n\n**Nutrition Fundamentals:**\n• **Carbohydrate Counting:** Learn to track carbs effectively\n• **Glycemic Index:** Choose foods that don't spike blood sugar\n• **Fiber-Rich Foods:** Vegetables, fruits, whole grains, legumes\n• **Healthy Fats:** Nuts, avocados, olive oil\n\n**Physical Activity Benefits:**\n• Improves insulin sensitivity\n• Helps maintain healthy weight\n• Reduces cardiovascular risk\n• Boosts mood and energy\n\n**Monitoring and Tracking:**\n• Keep a blood sugar log\n• Track your meals and activities\n• Note patterns and triggers\n• Share data with your healthcare team\n\n**Prevention of Complications:**\n• Regular eye exams\n• Foot care and inspection\n• Kidney function monitoring\n• Heart health maintenance\n\n⚠️ **Professional Care:** Diabetes management requires regular medical supervision.",
            
            f"⚖️ **Balancing Blood Sugar: Your Health Journey**\n\nI'm here to support your diabetes management:\n\n**The Blood Sugar Balance:**\nThink of blood sugar management like maintaining a healthy bank account - regular deposits and withdrawals keep everything balanced.\n\n**Smart Eating Strategies:**\n• **Timing:** Eat meals at consistent times\n• **Combination:** Pair carbs with protein and fat\n• **Portion Size:** Use measuring tools initially\n• **Hydration:** Drink water throughout the day\n\n**Exercise Integration:**\n• **Before Meals:** Light activity can help lower blood sugar\n• **After Meals:** Walking helps with glucose uptake\n• **Strength Training:** Builds muscle, improves insulin sensitivity\n• **Flexibility:** Yoga and stretching reduce stress\n\n**Technology and Tools:**\n• Continuous glucose monitors\n• Smartphone apps for tracking\n• Digital scales and measuring tools\n• Support groups and communities\n\n**Mental Health Connection:**\nManaging diabetes can be challenging. Don't hesitate to seek support for emotional well-being.\n\n⚠️ **Medical Partnership:** Your healthcare team is your best resource for diabetes care.",
            
            f"🎯 **Diabetes Management: Your Personalized Approach**\n\nLet me provide you with a structured diabetes management plan:\n\n**Phase 1: Education and Assessment**\n• Understand your type of diabetes\n• Know your target blood sugar ranges\n• Identify your personal risk factors\n• Learn to recognize symptoms\n\n**Phase 2: Daily Management**\n• **Morning Routine:** Check blood sugar, plan meals\n• **Throughout Day:** Monitor levels, stay active\n• **Evening:** Review the day, prepare for tomorrow\n• **Weekly:** Review patterns, adjust as needed\n\n**Phase 3: Long-term Health**\n• Regular medical check-ups\n• Preventive care appointments\n• Ongoing education and support\n• Lifestyle habit maintenance\n\n**Success Metrics:**\n• Consistent blood sugar control\n• Reduced HbA1c levels\n• Improved energy and mood\n• Prevention of complications\n\n⚠️ **Healthcare Partnership:** Regular communication with your medical team is essential for optimal diabetes management."
        ]
        return random.choice(diabetes_responses)
    
    elif any(word in user_input_lower for word in ["allergy", "allergies", "hay fever", "pollen"]):
        allergy_responses = [
            f"🌸 **Seasonal Allergies: Your Complete Guide**\n\nI understand you're asking about allergies. Here's what you should know:\n\n**Understanding Seasonal Allergies:**\nSeasonal allergies (hay fever) affect 20-30% of people worldwide. They occur when your immune system overreacts to environmental allergens like pollen.\n\n**Common Allergy Symptoms:**\n• Sneezing and runny nose\n• Itchy, watery eyes\n• Nasal congestion\n• Itchy throat and ears\n• Postnasal drip\n• Fatigue\n\n**Management Strategies:**\n• **Avoidance:** Monitor pollen counts, keep windows closed\n• **Medications:** Antihistamines, decongestants, nasal sprays\n• **Immunotherapy:** Allergy shots for long-term relief\n• **Environmental Control:** Air purifiers, regular cleaning\n\n**Prevention Tips:**\n• Check daily pollen forecasts\n• Shower after outdoor activities\n• Wear sunglasses to protect eyes\n• Use air conditioning instead of open windows\n• Clean and vacuum regularly\n\n**When to Seek Medical Care:**\n• Symptoms don't respond to over-the-counter treatments\n• Severe symptoms affecting daily life\n• Symptoms trigger asthma or other conditions\n\n⚠️ **Medical Disclaimer:** Consult healthcare providers for personalized allergy management.",
            
            f"🌿 **Allergy Management: Smart Strategies**\n\nLet me help you understand allergy management:\n\n**What Causes Allergies?**\nYour immune system mistakenly identifies harmless substances (like pollen) as threats and releases chemicals that cause symptoms.\n\n**Seasonal Patterns:**\n• **Spring:** Tree pollen (March-May)\n• **Summer:** Grass pollen (May-July)\n• **Fall:** Weed pollen (August-October)\n• **Year-round:** Indoor allergens (dust, pets)\n\n**Effective Treatment Options:**\n• **Antihistamines:** Block histamine release\n• **Decongestants:** Reduce nasal swelling\n• **Nasal Sprays:** Target nasal symptoms directly\n• **Eye Drops:** Relieve itchy, watery eyes\n• **Immunotherapy:** Long-term solution for some\n\n**Lifestyle Modifications:**\n• **Indoor Environment:** Use HEPA filters, regular cleaning\n• **Outdoor Activities:** Plan around pollen counts\n• **Personal Care:** Shower after outdoor exposure\n• **Clothing:** Wash clothes after outdoor activities\n\n**Natural Relief Options:**\n• Saline nasal rinses\n• Local honey (may help with local pollen)\n• Butterbur supplements\n• Quercetin supplements\n\n⚠️ **Professional Care:** Severe allergies may require prescription medications or immunotherapy.",
            
            f"🌺 **Allergy Relief: Your Action Plan**\n\nI'm here to help you manage your allergies effectively:\n\n**Understanding Your Triggers:**\n• **Pollen:** Trees, grasses, weeds\n• **Indoor:** Dust mites, pet dander, mold\n• **Food:** Various food allergens\n• **Environmental:** Pollution, weather changes\n\n**Daily Management Strategies:**\n• **Morning:** Check pollen forecast, take medications early\n• **Throughout Day:** Avoid outdoor activities during peak pollen times\n• **Evening:** Shower, change clothes, clean nasal passages\n• **Weekly:** Clean home, wash bedding, vacuum\n\n**Medication Timing:**\n• **Antihistamines:** Take before exposure for best results\n• **Nasal Sprays:** Use regularly for maximum effectiveness\n• **Eye Drops:** Apply as needed for relief\n• **Decongestants:** Use short-term for severe congestion\n\n**Environmental Control:**\n• **Home:** Use air purifiers, keep windows closed\n• **Car:** Use air conditioning, keep windows up\n• **Work:** Request air filtration, avoid outdoor meetings\n• **Travel:** Research destination pollen levels\n\n**When to Escalate:**\nSeek medical care if:\n• Symptoms are severe and persistent\n• Over-the-counter medications don't help\n• Allergies trigger asthma or other conditions\n• You want to explore immunotherapy options\n\n⚠️ **Healthcare Partnership:** Work with allergists for comprehensive allergy management.",
            
            f"🌻 **Allergy Prevention: Your Complete Strategy**\n\nLet me provide you with a comprehensive allergy management plan:\n\n**Phase 1: Assessment and Identification**\n• **Symptom Tracking:** Keep a diary of symptoms and triggers\n• **Allergy Testing:** Consider skin or blood tests\n• **Environmental Assessment:** Identify home and work triggers\n• **Seasonal Planning:** Know your allergy seasons\n\n**Phase 2: Prevention and Avoidance**\n• **Indoor Environment:** HEPA filters, regular cleaning, humidity control\n• **Outdoor Activities:** Plan around pollen counts, protective measures\n• **Personal Care:** Shower after exposure, change clothes\n• **Travel Planning:** Research destinations, pack medications\n\n**Phase 3: Treatment and Management**\n• **Medication Strategy:** Over-the-counter and prescription options\n• **Timing:** Take medications before exposure\n• **Combination Therapy:** Use multiple approaches for best results\n• **Monitoring:** Track effectiveness and adjust as needed\n\n**Phase 4: Long-term Solutions**\n• **Immunotherapy:** Consider allergy shots or sublingual tablets\n• **Lifestyle Changes:** Permanent modifications for lasting relief\n• **Education:** Learn about new treatments and strategies\n• **Support:** Join allergy support groups or communities\n\n**Success Indicators:**\n• Reduced symptom frequency and severity\n• Better quality of life during allergy seasons\n• Fewer missed work or school days\n• Improved sleep and daily functioning\n• Better control over allergy triggers\n\n⚠️ **Medical Guidance:** Regular consultation with allergists ensures optimal allergy management."
        ]
        return random.choice(allergy_responses)
    
    elif any(word in user_input_lower for word in ["stomach", "food poisoning", "gastroenteritis", "diarrhea", "vomiting"]):
        stomach_responses = [
            f"🤢 **Gastroenteritis: Your Complete Guide**\n\nI understand you're asking about stomach issues. Here's what you should know:\n\n**Understanding Gastroenteritis:**\nGastroenteritis (stomach flu/food poisoning) is inflammation of the stomach and intestines, affecting millions annually.\n\n**Common Symptoms:**\n• Nausea and vomiting\n• Diarrhea\n• Abdominal cramps\n• Fever\n• Headache and muscle aches\n• Dehydration signs\n\n**Treatment and Management:**\n• **Hydration:** Drink plenty of fluids, oral rehydration solutions\n• **Rest:** Allow your digestive system to recover\n• **Diet:** BRAT diet (bananas, rice, applesauce, toast)\n• **Medications:** Anti-diarrheal medications (use cautiously)\n\n**Prevention Strategies:**\n• Proper hand washing\n• Safe food handling and preparation\n• Avoid undercooked foods\n• Drink clean water\n• Good hygiene practices\n\n**When to Seek Medical Care:**\n• Severe or persistent symptoms\n• Signs of dehydration\n• High fever or bloody stools\n• Severe abdominal pain\n\n⚠️ **Important:** Dehydration is the most serious complication. Stay hydrated!",
            
            f"🍽️ **Food Safety and Stomach Health**\n\nLet me help you understand food safety and stomach issues:\n\n**Common Causes of Stomach Problems:**\n• **Viral Infections:** Norovirus, rotavirus\n• **Bacterial Infections:** Salmonella, E. coli, Campylobacter\n• **Food Toxins:** Contaminated or spoiled food\n• **Traveler's Diarrhea:** Different water/food in new locations\n\n**Immediate Treatment Steps:**\n• **Stop Eating:** Give your stomach a break\n• **Stay Hydrated:** Small sips of water, clear broths\n• **Rest:** Allow your body to fight the infection\n• **Monitor:** Watch for dehydration signs\n\n**Recovery Diet (BRAT):**\n• **Bananas:** Provide potassium and easy digestion\n• **Rice:** Bland, binding, easy on stomach\n• **Applesauce:** Provides nutrients without irritation\n• **Toast:** Bland carbohydrates for energy\n\n**Prevention Strategies:**\n• **Hand Hygiene:** Wash hands frequently and thoroughly\n• **Food Safety:** Cook foods to proper temperatures\n• **Water Safety:** Drink clean, treated water\n• **Travel Precautions:** Be careful with food and water in new places\n\n**Red Flags to Watch For:**\n🚨 Severe dehydration (dry mouth, no urination)\n🚨 High fever (above 101°F)\n🚨 Bloody stools\n🚨 Severe abdominal pain\n🚨 Symptoms lasting more than 3 days\n\n⚠️ **Medical Disclaimer:** Severe cases require professional medical attention.",
            
            f"💧 **Stomach Health: Your Recovery Guide**\n\nI'm here to help you understand stomach health and recovery:\n\n**Understanding Your Symptoms:**\n• **Nausea:** Feeling sick to your stomach\n• **Vomiting:** Forceful emptying of stomach contents\n• **Diarrhea:** Loose, watery stools\n• **Cramps:** Abdominal muscle contractions\n• **Dehydration:** Loss of body fluids\n\n**Hydration Strategy:**\n• **Start Slow:** Small sips of water or clear liquids\n• **Oral Rehydration:** Commercial solutions or homemade (salt + sugar + water)\n• **Avoid:** Caffeine, alcohol, sugary drinks\n• **Monitor:** Urine color (should be light yellow)\n\n**Recovery Timeline:**\n• **Day 1:** Focus on hydration, minimal food\n• **Day 2-3:** Introduce BRAT diet gradually\n• **Day 4-5:** Add bland proteins (chicken, fish)\n• **Day 6-7:** Return to normal diet slowly\n\n**When to Eat Again:**\n• Wait until vomiting stops\n• Start with clear liquids\n• Progress to bland foods\n• Listen to your body\n\n**Prevention for Future:**\n• **Food Safety:** Proper cooking, storage, handling\n• **Hygiene:** Frequent hand washing\n• **Travel:** Be cautious with food and water\n• **Health:** Maintain good overall health\n\n⚠️ **Professional Care:** Seek medical attention for severe or persistent symptoms.",
            
            f"🏥 **Stomach Health: Your Complete Management Plan**\n\nLet me provide you with a comprehensive stomach health strategy:\n\n**Phase 1: Acute Management**\n• **Immediate Actions:** Stop eating, start hydrating, rest\n• **Symptom Monitoring:** Track frequency and severity\n• **Dehydration Prevention:** Oral rehydration solutions\n• **Medical Assessment:** Know when to seek help\n\n**Phase 2: Recovery and Refeeding**\n• **Gradual Reintroduction:** Start with clear liquids\n• **BRAT Diet:** Bananas, rice, applesauce, toast\n• **Protein Addition:** Bland proteins as tolerated\n• **Normal Diet:** Slow return to regular foods\n\n**Phase 3: Prevention and Education**\n• **Food Safety:** Proper handling, cooking, storage\n• **Hygiene Practices:** Hand washing, surface cleaning\n• **Travel Preparation:** Research destinations, pack medications\n• **Health Maintenance:** Good overall health practices\n\n**Phase 4: Long-term Health**\n• **Dietary Awareness:** Identify trigger foods\n• **Lifestyle Modifications:** Stress management, regular meals\n• **Medical Follow-up:** Address underlying conditions\n• **Prevention Planning:** Ongoing food safety practices\n\n**Success Indicators:**\n• Faster recovery from stomach issues\n• Reduced frequency of problems\n• Better understanding of triggers\n• Improved food safety practices\n• Better overall digestive health\n\n⚠️ **Healthcare Partnership:** Work with healthcare providers for persistent digestive issues."
        ]
        return random.choice(stomach_responses)
    
    elif any(word in user_input_lower for word in ["uti", "urinary", "bladder", "kidney"]):
        uti_responses = [
            f"🚰 **Urinary Tract Infections: Your Complete Guide**\n\nI understand you're asking about UTIs. Here's what you should know:\n\n**Understanding UTIs:**\nUrinary tract infections are among the most common bacterial infections, affecting millions annually, especially women.\n\n**Common Symptoms:**\n• Frequent, urgent urination\n• Burning sensation during urination\n• Cloudy or strong-smelling urine\n• Pelvic pain or pressure\n• Blood in urine (sometimes)\n• Fever (with kidney infection)\n\n**Treatment and Management:**\n• **Antibiotics:** Prescribed by healthcare professionals\n• **Pain Relief:** Over-the-counter pain relievers\n• **Hydration:** Drink plenty of water\n• **Rest:** Allow your body to heal\n\n**Prevention Strategies:**\n• Drink plenty of water\n• Urinate frequently\n• Wipe from front to back\n• Urinate after sexual activity\n• Wear cotton underwear\n• Avoid irritating feminine products\n\n**When to Seek Medical Care:**\n• Symptoms of UTI\n• Fever with urinary symptoms\n• Back pain or flank pain\n• Recurrent UTIs\n\n⚠️ **Important:** UTIs require prompt treatment to prevent complications.",
            
            f"💊 **UTI Management: Evidence-Based Approach**\n\nLet me help you understand UTI management:\n\n**What is a UTI?**\nA urinary tract infection occurs when bacteria enter the urinary tract and multiply, most commonly affecting the bladder.\n\n**Risk Factors:**\n• **Gender:** Women are more susceptible\n• **Sexual Activity:** Can introduce bacteria\n• **Birth Control:** Certain types may increase risk\n• **Menopause:** Hormonal changes\n• **Medical Conditions:** Diabetes, kidney stones\n\n**Treatment Options:**\n• **Antibiotics:** Prescribed based on bacteria type\n• **Pain Management:** Over-the-counter medications\n• **Hydration:** Flush bacteria from system\n• **Rest:** Support immune system\n\n**Prevention Strategies:**\n• **Hydration:** 6-8 glasses of water daily\n• **Hygiene:** Proper wiping technique\n• **Urination Habits:** Don't hold urine too long\n• **Clothing:** Cotton underwear, avoid tight clothes\n• **Cranberry Products:** May help prevent recurrence\n\n**Complications to Watch For:**\n🚨 Kidney infection (pyelonephritis)\n🚨 Sepsis (bloodstream infection)\n🚨 Recurrent infections\n🚨 Pregnancy complications\n\n⚠️ **Medical Disclaimer:** UTIs require professional medical treatment.",
            
            f"🩺 **UTI Prevention: Your Health Strategy**\n\nI'm here to help you understand UTI prevention:\n\n**Understanding Your Risk:**\n• **Anatomical Factors:** Women's shorter urethra\n• **Lifestyle Factors:** Sexual activity, hygiene practices\n• **Medical Factors:** Diabetes, kidney problems\n• **Age Factors:** Menopause, elderly care\n\n**Daily Prevention Habits:**\n• **Hydration:** Drink water throughout the day\n• **Urination:** Go when you need to, don't hold it\n• **Hygiene:** Proper wiping, clean genital area\n• **Clothing:** Cotton underwear, avoid tight pants\n• **Post-Sex Care:** Urinate after sexual activity\n\n**Dietary Considerations:**\n• **Cranberry Products:** May help prevent bacteria adhesion\n• **Probiotics:** Support healthy bacteria balance\n• **Vitamin C:** May acidify urine\n• **Avoid:** Irritating foods and beverages\n\n**Lifestyle Modifications:**\n• **Stress Management:** High stress can affect immune system\n• **Regular Exercise:** Supports overall health\n• **Adequate Sleep:** Important for immune function\n• **Healthy Diet:** Supports urinary tract health\n\n**When to Seek Medical Care:**\n• Any UTI symptoms\n• Recurrent infections\n• Symptoms during pregnancy\n• Fever with urinary symptoms\n\n⚠️ **Professional Care:** Regular check-ups help identify underlying causes.",
            
            f"🏥 **UTI Management: Your Complete Care Plan**\n\nLet me provide you with a comprehensive UTI management strategy:\n\n**Phase 1: Recognition and Diagnosis**\n• **Symptom Awareness:** Know the signs of UTI\n• **Prompt Action:** Seek medical care early\n• **Testing:** Urine culture and sensitivity\n• **Assessment:** Identify underlying risk factors\n\n**Phase 2: Treatment and Recovery**\n• **Antibiotic Therapy:** Complete full course as prescribed\n• **Pain Management:** Over-the-counter relief\n• **Hydration:** Increased fluid intake\n• **Rest:** Support healing process\n\n**Phase 3: Prevention and Lifestyle**\n• **Daily Habits:** Hydration, hygiene, urination\n• **Dietary Changes:** Cranberry products, probiotics\n• **Lifestyle Modifications:** Clothing, stress management\n• **Medical Follow-up:** Address underlying conditions\n\n**Phase 4: Long-term Health**\n• **Monitoring:** Watch for recurrence\n• **Education:** Learn about prevention strategies\n• **Support:** Work with healthcare team\n• **Maintenance:** Ongoing preventive practices\n\n**Success Indicators:**\n• Reduced UTI frequency\n• Faster recovery when UTIs occur\n• Better understanding of prevention\n• Improved urinary tract health\n• Fewer complications\n\n⚠️ **Healthcare Partnership:** Regular communication with healthcare providers ensures optimal UTI management."
        ]
        return random.choice(uti_responses)
    
    elif any(word in user_input_lower for word in ["mental", "anxiety", "depression", "stress"]):
        mental_responses = [
            f"🧠 **Mental Health: Your Mind Matters**\n\nI understand you're asking about mental health. Here's what you should know:\n\n**Understanding Mental Wellness:**\nMental health is just as important as physical health. It affects how we think, feel, and act.\n\n**Common Mental Health Challenges:**\n• **Anxiety:** Excessive worry and fear\n• **Depression:** Persistent sadness and loss of interest\n• **Stress:** Overwhelming pressure and tension\n• **Burnout:** Physical and emotional exhaustion\n\n**Self-Care Strategies:**\n• **Mindfulness:** Practice meditation and deep breathing\n• **Physical Activity:** Exercise releases endorphins\n• **Social Connection:** Maintain meaningful relationships\n• **Sleep Hygiene:** Prioritize quality sleep\n• **Creative Expression:** Art, music, writing\n\n**When to Seek Professional Help:**\n🚨 Persistent feelings of sadness or anxiety\n🚨 Changes in sleep or appetite\n🚨 Difficulty functioning daily\n🚨 Thoughts of self-harm\n\n⚠️ **Professional Support:** Mental health professionals can provide personalized treatment and support.",
            
            f"💙 **Mental Wellness: Nurturing Your Mind**\n\nLet me help you understand mental health and wellness:\n\n**The Mind-Body Connection:**\nYour mental health directly impacts your physical health and overall quality of life.\n\n**Building Mental Resilience:**\n• **Emotional Awareness:** Recognize and accept your feelings\n• **Healthy Boundaries:** Learn to say no when needed\n• **Positive Relationships:** Surround yourself with supportive people\n• **Purpose and Meaning:** Engage in activities that matter to you\n\n**Daily Mental Health Practices:**\n• **Morning:** Start with gratitude or positive affirmations\n• **Throughout Day:** Take short breaks for deep breathing\n• **Evening:** Reflect on positive moments\n• **Weekly:** Schedule activities you enjoy\n\n**Stress Management Techniques:**\n• Progressive muscle relaxation\n• Guided imagery\n• Journaling\n• Nature walks\n• Creative hobbies\n\n**Support Systems:**\n• Family and friends\n• Support groups\n• Mental health professionals\n• Crisis hotlines\n\n⚠️ **Professional Care:** Mental health professionals provide evidence-based treatments and support.",
            
            f"🌟 **Mental Health: Your Journey to Wellness**\n\nI'm here to support your mental health journey:\n\n**Understanding Your Mental Health:**\nMental health exists on a spectrum. Everyone experiences ups and downs, and it's okay to seek help when needed.\n\n**Anxiety Management:**\n• **Breathing Techniques:** 4-7-8 breathing method\n• **Grounding Exercises:** 5-4-3-2-1 sensory technique\n• **Thought Challenging:** Question negative thoughts\n• **Lifestyle Changes:** Reduce caffeine, improve sleep\n\n**Depression Support:**\n• **Small Steps:** Break tasks into manageable pieces\n• **Social Connection:** Reach out to trusted friends\n• **Physical Activity:** Start with gentle movement\n• **Professional Help:** Therapy and medication when needed\n\n**Stress Reduction:**\n• **Time Management:** Prioritize and delegate\n• **Relaxation Techniques:** Yoga, meditation, massage\n• **Healthy Boundaries:** Learn to set limits\n• **Self-Compassion:** Be kind to yourself\n\n**Prevention Strategies:**\n• Regular exercise and healthy eating\n• Adequate sleep and stress management\n• Social connection and community involvement\n• Regular check-ins with yourself\n\n⚠️ **Professional Guidance:** Mental health professionals can provide personalized treatment plans.",
            
            f"🌈 **Mental Health: Building Your Wellness Toolkit**\n\nLet me provide you with a comprehensive mental health strategy:\n\n**Assessment Phase:**\n• Identify your current mental health status\n• Recognize triggers and patterns\n• Understand your support network\n• Know your coping mechanisms\n\n**Action Phase:**\n• **Daily Practices:** Meditation, journaling, exercise\n• **Social Connection:** Regular check-ins with friends/family\n• **Professional Support:** Therapy, counseling, support groups\n• **Lifestyle Changes:** Sleep, nutrition, stress management\n\n**Maintenance Phase:**\n• Regular mental health check-ins\n• Continued self-care practices\n• Ongoing professional support as needed\n• Prevention strategies\n\n**Crisis Planning:**\n• Know emergency resources\n• Have a support contact list\n• Develop safety plans\n• Recognize warning signs\n\n**Recovery and Growth:**\n• Celebrate progress and milestones\n• Learn from challenges\n• Build resilience and coping skills\n• Help others when possible\n\n⚠️ **Professional Care:** Mental health professionals provide essential support and treatment options."
        ]
        return random.choice(mental_responses)
    
    elif any(word in user_input_lower for word in ["skin", "eczema", "acne", "dermatitis", "rash"]):
        skin_responses = [
            f"🧴 **Skin Health: Your Complete Guide**\n\nI understand you're asking about skin conditions. Here's what you should know:\n\n**Understanding Skin Conditions:**\nSkin conditions are among the most common health concerns, affecting people of all ages and backgrounds.\n\n**Common Skin Conditions:**\n• **Eczema (Atopic Dermatitis):** Dry, itchy, inflamed skin\n• **Contact Dermatitis:** Skin reaction to irritants/allergens\n• **Acne:** Pimples, blackheads, whiteheads\n• **Psoriasis:** Red, scaly patches\n• **Fungal Infections:** Ringworm, athlete's foot\n\n**General Management Strategies:**\n• **Gentle Cleansing:** Use mild, fragrance-free products\n• **Moisturizing:** Apply regularly, especially after bathing\n• **Sun Protection:** Use sunscreen daily\n• **Avoid Triggers:** Identify and avoid irritants\n• **Stress Management:** Stress can worsen skin conditions\n\n**When to Seek Medical Care:**\n• Severe or persistent symptoms\n• Signs of infection (redness, swelling, pus)\n• Symptoms affecting daily life\n• New or changing skin lesions\n\n⚠️ **Medical Disclaimer:** Consult dermatologists for personalized skin care.",
            
            f"🌟 **Skin Care: Your Daily Routine**\n\nLet me help you understand proper skin care:\n\n**Understanding Your Skin:**\nYour skin is your body's largest organ and first line of defense against environmental threats.\n\n**Daily Skin Care Basics:**\n• **Cleansing:** Gentle, pH-balanced cleansers\n• **Moisturizing:** Apply while skin is still damp\n• **Sun Protection:** SPF 30+ daily, even indoors\n• **Hydration:** Drink plenty of water\n• **Sleep:** Quality sleep supports skin repair\n\n**Condition-Specific Care:**\n• **Eczema:** Thick moisturizers, avoid hot showers\n• **Acne:** Non-comedogenic products, don't pick\n• **Sensitive Skin:** Fragrance-free, hypoallergenic products\n• **Aging Skin:** Antioxidants, retinoids (as prescribed)\n\n**Lifestyle Factors:**\n• **Diet:** Omega-3s, antioxidants, vitamin C\n• **Exercise:** Promotes circulation and skin health\n• **Stress Management:** Reduces inflammation\n• **Environment:** Humidifiers, air purifiers\n\n**Prevention Strategies:**\n• **Sun Protection:** Hats, clothing, sunscreen\n• **Gentle Care:** Avoid harsh scrubs and products\n• **Regular Check-ups:** Monitor for changes\n• **Early Treatment:** Address issues promptly\n\n⚠️ **Professional Care:** Dermatologists provide specialized skin care guidance.",
            
            f"💆‍♀️ **Skin Wellness: Your Health Journey**\n\nI'm here to help you understand skin health and wellness:\n\n**The Skin-Health Connection:**\nYour skin reflects your overall health and can indicate underlying conditions.\n\n**Common Triggers and Solutions:**\n• **Environmental:** Pollution, weather, allergens\n• **Lifestyle:** Stress, diet, sleep, exercise\n• **Products:** Harsh chemicals, fragrances, preservatives\n• **Medical:** Hormones, medications, underlying conditions\n\n**Building a Skin Care Routine:**\n• **Morning:** Gentle cleanse, moisturize, sunscreen\n• **Evening:** Remove makeup, cleanse, treat, moisturize\n• **Weekly:** Exfoliate gently, use masks if tolerated\n• **Monthly:** Assess progress, adjust routine\n\n**Natural and Alternative Options:**\n• **Oatmeal Baths:** Soothe irritated skin\n• **Aloe Vera:** Natural moisturizer and healer\n• **Tea Tree Oil:** Natural antiseptic (diluted)\n• **Coconut Oil:** Natural moisturizer (for some)\n\n**When to Seek Professional Help:**\n• Persistent or worsening symptoms\n• Signs of infection or allergic reaction\n• Symptoms affecting quality of life\n• Concerns about skin cancer or serious conditions\n\n**Prevention and Maintenance:**\n• **Regular Monitoring:** Check skin for changes\n• **Protection:** Sun, environmental, and product protection\n• **Education:** Learn about your specific conditions\n• **Support:** Join skin condition support groups\n\n⚠️ **Healthcare Partnership:** Work with dermatologists for optimal skin health.",
            
            f"🏥 **Skin Health: Your Complete Management Plan**\n\nLet me provide you with a comprehensive skin health strategy:\n\n**Phase 1: Assessment and Identification**\n• **Skin Analysis:** Identify your skin type and concerns\n• **Trigger Identification:** Track what worsens symptoms\n• **Medical History:** Consider underlying conditions\n• **Lifestyle Assessment:** Diet, stress, environment\n\n**Phase 2: Treatment and Management**\n• **Daily Routine:** Gentle cleansing, moisturizing, protection\n• **Condition-Specific Care:** Targeted treatments for specific issues\n• **Lifestyle Modifications:** Diet, stress, environment changes\n• **Medical Treatment:** Prescription medications when needed\n\n**Phase 3: Prevention and Maintenance**\n• **Sun Protection:** Daily sunscreen, protective clothing\n• **Environmental Control:** Humidifiers, air purifiers, gentle products\n• **Regular Monitoring:** Check for changes or new symptoms\n• **Education:** Learn about your specific conditions\n\n**Phase 4: Long-term Health**\n• **Ongoing Care:** Maintain healthy skin habits\n• **Regular Check-ups:** Dermatologist visits as needed\n• **Adaptation:** Adjust routine as skin changes\n• **Support:** Connect with others with similar conditions\n\n**Success Indicators:**\n• Improved skin appearance and comfort\n• Reduced frequency of flare-ups\n• Better understanding of triggers\n• Increased confidence and quality of life\n• Fewer complications or infections\n\n⚠️ **Medical Guidance:** Regular consultation with dermatologists ensures optimal skin health."
        ]
        return random.choice(skin_responses)
    
    elif any(word in user_input_lower for word in ["headache", "migraine", "head pain"]):
        headache_responses = [
            f"🤕 **Headaches: Your Complete Guide**\n\nI understand you're asking about headaches. Here's what you should know:\n\n**Understanding Headaches:**\nHeadaches are one of the most common health complaints, affecting nearly everyone at some point.\n\n**Common Types of Headaches:**\n• **Tension Headaches:** Dull, aching pain, like a tight band\n• **Migraines:** Intense, throbbing pain, often one-sided\n• **Cluster Headaches:** Severe, recurring pain around one eye\n• **Sinus Headaches:** Pain in forehead, cheeks, nose\n• **Rebound Headaches:** Caused by overuse of pain medications\n\n**General Management Strategies:**\n• **Rest:** Find a quiet, dark place to relax\n• **Hydration:** Drink plenty of water\n• **Pain Relief:** Over-the-counter medications\n• **Stress Management:** Relaxation techniques\n• **Regular Sleep:** Maintain consistent sleep patterns\n\n**When to Seek Medical Care:**\n• Severe, sudden headache\n• Headache with fever or stiff neck\n• Headache after head injury\n• Worsening headache over time\n• Headache with neurological symptoms\n\n⚠️ **Important:** Some headaches can indicate serious conditions. Know the warning signs!",
            
            f"💊 **Headache Management: Evidence-Based Approach**\n\nLet me help you understand headache management:\n\n**Understanding Your Headache:**\nDifferent types of headaches have different causes and treatments.\n\n**Tension Headache Management:**\n• **Causes:** Stress, poor posture, lack of sleep, eye strain\n• **Treatment:** Over-the-counter pain relievers, stress reduction\n• **Prevention:** Regular exercise, good posture, adequate sleep\n• **Lifestyle:** Stress management, relaxation techniques\n\n**Migraine Management:**\n• **Triggers:** Certain foods, stress, hormonal changes, lack of sleep\n• **Treatment:** Prescription medications, rest in dark room\n• **Prevention:** Identify and avoid triggers, preventive medications\n• **Lifestyle:** Regular sleep, meals, exercise, stress management\n\n**Cluster Headache Management:**\n• **Characteristics:** Severe, recurring, often around one eye\n• **Treatment:** Oxygen therapy, prescription medications\n• **Prevention:** Preventive medications, lifestyle modifications\n• **Medical Care:** Usually requires professional treatment\n\n**General Prevention Strategies:**\n• **Regular Sleep:** 7-9 hours nightly, consistent schedule\n• **Hydration:** Drink plenty of water throughout the day\n• **Stress Management:** Meditation, yoga, deep breathing\n• **Regular Exercise:** Promotes circulation and reduces stress\n• **Eye Care:** Regular eye exams, proper lighting\n\n⚠️ **Medical Disclaimer:** Severe or persistent headaches require professional evaluation.",
            
            f"🧘‍♀️ **Headache Relief: Your Wellness Strategy**\n\nI'm here to help you understand headache relief and prevention:\n\n**The Headache-Health Connection:**\nHeadaches can be symptoms of underlying health issues or lifestyle factors.\n\n**Immediate Relief Strategies:**\n• **Rest:** Find a quiet, comfortable place\n• **Hydration:** Drink water, avoid caffeine and alcohol\n• **Temperature:** Cold or warm compress on forehead\n• **Massage:** Gentle neck and shoulder massage\n• **Breathing:** Deep, slow breathing exercises\n\n**Lifestyle Modifications:**\n• **Sleep Hygiene:** Regular schedule, dark room, cool temperature\n• **Diet:** Regular meals, avoid trigger foods, stay hydrated\n• **Exercise:** Regular physical activity, but avoid during headache\n• **Stress Management:** Meditation, yoga, hobbies, social connection\n• **Posture:** Good posture, ergonomic workspace\n\n**Trigger Identification:**\n• **Food Triggers:** Chocolate, cheese, processed meats, alcohol\n• **Environmental:** Bright lights, loud noises, strong smells\n• **Hormonal:** Menstrual cycles, pregnancy, menopause\n• **Lifestyle:** Stress, lack of sleep, skipping meals\n• **Medical:** Medications, underlying conditions\n\n**When to Seek Professional Help:**\n• Frequent or severe headaches\n• Headaches that don't respond to treatment\n• Headaches with other symptoms\n• New or changing headache patterns\n• Headaches affecting daily life\n\n⚠️ **Professional Care:** Neurologists and headache specialists provide specialized treatment.",
            
            f"🏥 **Headache Management: Your Complete Care Plan**\n\nLet me provide you with a comprehensive headache management strategy:\n\n**Phase 1: Assessment and Diagnosis**\n• **Symptom Tracking:** Keep a detailed headache diary\n• **Trigger Identification:** Note patterns and potential triggers\n• **Medical Evaluation:** Rule out underlying conditions\n• **Lifestyle Assessment:** Sleep, diet, stress, environment\n\n**Phase 2: Treatment and Relief**\n• **Acute Treatment:** Medications, rest, comfort measures\n• **Preventive Strategies:** Lifestyle modifications, trigger avoidance\n• **Alternative Therapies:** Acupuncture, massage, biofeedback\n• **Medical Treatment:** Prescription medications when needed\n\n**Phase 3: Prevention and Lifestyle**\n• **Sleep Optimization:** Regular schedule, good sleep hygiene\n• **Stress Management:** Relaxation techniques, regular exercise\n• **Dietary Changes:** Regular meals, trigger food avoidance\n• **Environmental Control:** Proper lighting, ergonomics, noise control\n\n**Phase 4: Long-term Management**\n• **Ongoing Monitoring:** Track frequency and severity\n• **Regular Check-ups:** Medical follow-up as needed\n• **Education:** Learn about your specific headache type\n• **Support:** Connect with headache support groups\n\n**Success Indicators:**\n• Reduced headache frequency and severity\n• Better understanding of triggers\n• Improved quality of life\n• Fewer missed work or social activities\n• Better headache management skills\n\n⚠️ **Healthcare Partnership:** Regular communication with healthcare providers ensures optimal headache management."
        ]
        return random.choice(headache_responses)
    
    elif any(word in user_input_lower for word in ["back pain", "backache", "spine", "muscle pain"]):
        back_responses = [
            f"🦴 **Back Pain: Your Complete Guide**\n\nI understand you're asking about back pain. Here's what you should know:\n\n**Understanding Back Pain:**\nBack pain affects up to 80% of adults at some point, ranging from mild discomfort to severe, chronic pain.\n\n**Common Types of Back Pain:**\n• **Acute Back Pain:** Sudden onset, usually resolves within 6 weeks\n• **Chronic Back Pain:** Persists for more than 12 weeks\n• **Lower Back Pain:** Most common, affects lumbar region\n• **Upper Back Pain:** Less common, often related to posture\n• **Sciatica:** Pain radiating down the leg\n\n**General Management Strategies:**\n• **Rest:** Short periods of rest, but avoid prolonged bed rest\n• **Gentle Movement:** Walking, stretching, light activity\n• **Pain Relief:** Over-the-counter medications\n• **Heat/Cold Therapy:** Alternating heat and cold\n• **Good Posture:** Maintain proper alignment\n\n**When to Seek Medical Care:**\n• Severe pain that doesn't improve\n• Pain radiating down legs\n• Numbness or weakness\n• Pain with fever or weight loss\n• Pain after injury\n\n⚠️ **Important:** Most back pain improves with time and conservative treatment.",
            
            f"💪 **Back Health: Your Wellness Strategy**\n\nLet me help you understand back health and pain management:\n\n**Understanding Your Back:**\nYour back is a complex structure of bones, muscles, ligaments, and nerves that work together.\n\n**Common Causes of Back Pain:**\n• **Muscle Strains:** Overuse, poor lifting technique\n• **Ligament Sprains:** Sudden movements, accidents\n• **Poor Posture:** Sitting, standing, or sleeping incorrectly\n• **Stress:** Emotional stress can cause muscle tension\n• **Underlying Conditions:** Arthritis, disc problems, osteoporosis\n\n**Immediate Relief Strategies:**\n• **Gentle Movement:** Walking, gentle stretching\n• **Heat Therapy:** Warm baths, heating pads\n• **Cold Therapy:** Ice packs for acute pain\n• **Pain Medications:** Over-the-counter anti-inflammatories\n• **Rest:** Short periods, avoid prolonged bed rest\n\n**Prevention Strategies:**\n• **Exercise:** Strengthen core muscles, improve flexibility\n• **Posture:** Good posture when sitting, standing, sleeping\n• **Lifting:** Proper technique, use legs not back\n• **Weight Management:** Maintain healthy weight\n• **Ergonomics:** Proper workspace setup\n\n**Lifestyle Modifications:**\n• **Regular Exercise:** Walking, swimming, yoga\n• **Stress Management:** Relaxation techniques, meditation\n• **Sleep:** Good mattress, proper sleeping position\n• **Work Environment:** Ergonomic chair, regular breaks\n• **Footwear:** Supportive shoes, avoid high heels\n\n⚠️ **Medical Disclaimer:** Persistent or severe back pain requires professional evaluation.",
            
            f"🧘‍♂️ **Back Pain Relief: Your Recovery Journey**\n\nI'm here to help you understand back pain relief and recovery:\n\n**The Back-Health Connection:**\nYour back health affects your overall mobility and quality of life.\n\n**Recovery Timeline:**\n• **Acute Phase (Days 1-3):** Rest, gentle movement, pain management\n• **Subacute Phase (Days 4-14):** Gradual return to activity, stretching\n• **Recovery Phase (Weeks 2-6):** Strengthening exercises, normal activities\n• **Maintenance Phase (6+ weeks):** Ongoing exercise, prevention\n\n**Exercise and Movement:**\n• **Walking:** Low-impact, promotes healing\n• **Gentle Stretching:** Improves flexibility, reduces stiffness\n• **Core Strengthening:** Supports spine, prevents future pain\n• **Yoga/Pilates:** Improves flexibility and strength\n• **Swimming:** Low-impact, full-body exercise\n\n**Pain Management Techniques:**\n• **Heat Therapy:** Relaxes muscles, improves circulation\n• **Cold Therapy:** Reduces inflammation, numbs pain\n• **Massage:** Relieves muscle tension, promotes relaxation\n• **Acupuncture:** May provide relief for some individuals\n• **Meditation:** Reduces stress, improves pain perception\n\n**When to Seek Professional Help:**\n• Severe or worsening pain\n• Pain with neurological symptoms\n• Pain that doesn't improve with rest\n• Pain affecting daily activities\n• Recurrent back pain\n\n⚠️ **Professional Care:** Physical therapists and spine specialists provide specialized treatment.",
            
            f"🏥 **Back Pain Management: Your Complete Care Plan**\n\nLet me provide you with a comprehensive back pain management strategy:\n\n**Phase 1: Assessment and Diagnosis**\n• **Pain Assessment:** Location, intensity, duration, triggers\n• **Medical Evaluation:** Rule out serious conditions\n• **Lifestyle Assessment:** Work, activities, posture, stress\n• **Functional Assessment:** Impact on daily activities\n\n**Phase 2: Acute Management**\n• **Pain Relief:** Medications, heat/cold therapy\n• **Activity Modification:** Avoid aggravating activities\n• **Gentle Movement:** Walking, light stretching\n• **Rest:** Short periods, avoid prolonged bed rest\n\n**Phase 3: Recovery and Rehabilitation**\n• **Physical Therapy:** Strengthening, flexibility, posture\n• **Gradual Return:** Resume activities slowly\n• **Exercise Program:** Core strengthening, aerobic fitness\n• **Lifestyle Modifications:** Ergonomics, stress management\n\n**Phase 4: Prevention and Maintenance**\n• **Ongoing Exercise:** Regular physical activity\n• **Posture Awareness:** Good posture habits\n• **Stress Management:** Relaxation techniques\n• **Regular Check-ups:** Monitor progress and prevent recurrence\n\n**Success Indicators:**\n• Reduced pain frequency and severity\n• Improved mobility and function\n• Better posture and body mechanics\n• Increased strength and flexibility\n• Better quality of life\n• Fewer missed work or social activities\n\n⚠️ **Healthcare Partnership:** Regular communication with healthcare providers ensures optimal back health."
        ]
        return random.choice(back_responses)
    
    elif any(word in user_input_lower for word in ["diet", "nutrition", "food", "eating"]):
        nutrition_responses = [
            f"🥗 **Nutrition: Fueling Your Health**\n\nI understand you're asking about nutrition. Here's a comprehensive guide:\n\n**Building a Healthy Plate:**\n• **50% Vegetables & Fruits:** Colorful variety for vitamins and minerals\n• **25% Lean Proteins:** Fish, poultry, beans, legumes\n• **25% Whole Grains:** Brown rice, quinoa, whole wheat\n• **Healthy Fats:** Avocado, nuts, olive oil\n\n**Key Nutritional Principles:**\n• **Balance:** Include all food groups\n• **Variety:** Different colors and types\n• **Moderation:** Portion control matters\n• **Hydration:** 8-10 glasses of water daily\n\n**Smart Eating Strategies:**\n• **Meal Planning:** Prepare healthy options ahead\n• **Mindful Eating:** Pay attention to hunger cues\n• **Reading Labels:** Understand ingredients and portions\n• **Cooking at Home:** Control ingredients and methods\n\n**Special Considerations:**\n• **Allergies:** Always read labels carefully\n• **Medical Conditions:** Follow doctor's dietary recommendations\n• **Age & Activity:** Adjust portions based on needs\n• **Cultural Preferences:** Adapt healthy eating to your traditions\n\n⚠️ **Professional Guidance:** Consult registered dietitians for personalized nutrition plans.",
            
            f"🍎 **Nutrition Fundamentals: Your Health Foundation**\n\nLet me help you understand the basics of good nutrition:\n\n**Macronutrients Explained:**\n• **Proteins:** Building blocks for muscles and cells\n• **Carbohydrates:** Primary energy source for your body\n• **Fats:** Essential for hormone production and nutrient absorption\n\n**Micronutrients Matter:**\n• **Vitamins:** Support immune function and metabolism\n• **Minerals:** Build bones, regulate fluids, support nerves\n• **Antioxidants:** Protect cells from damage\n\n**Hydration Importance:**\n• **Water:** Essential for every bodily function\n• **Signs of Dehydration:** Thirst, dark urine, fatigue\n• **Daily Needs:** 8-10 cups, more with activity\n\n**Eating Patterns:**\n• **Regular Meals:** Maintain stable blood sugar\n• **Snacking Smart:** Choose nutrient-dense options\n• **Timing:** Eat when hungry, stop when satisfied\n• **Environment:** Create pleasant eating spaces\n\n**Nutrition Myths Debunked:**\n• All fats aren't bad\n• Carbs aren't the enemy\n• Supplements can't replace whole foods\n• Skipping meals doesn't help weight loss\n\n⚠️ **Medical Disclaimer:** This information is educational. Consult healthcare professionals for personalized advice.",
            
            f"🥑 **Smart Nutrition: Making Healthy Choices**\n\nI'm here to guide you on your nutrition journey:\n\n**Understanding Food Labels:**\n• **Serving Size:** Always check first\n• **Ingredients List:** Shorter is usually better\n• **Nutrition Facts:** Focus on fiber, protein, healthy fats\n• **Added Sugars:** Limit to less than 10% of daily calories\n\n**Building Healthy Habits:**\n• **Start Small:** Make one change at a time\n• **Plan Ahead:** Prepare healthy snacks and meals\n• **Shop Smart:** Stick to the perimeter of the grocery store\n• **Cook More:** Control ingredients and portions\n\n**Nutrition for Different Goals:**\n• **Weight Management:** Focus on portion control and whole foods\n• **Energy:** Balance carbs, proteins, and healthy fats\n• **Athletic Performance:** Time meals around workouts\n• **Health Conditions:** Follow medical recommendations\n\n**Eating Out Strategies:**\n• **Menu Reading:** Look for grilled, baked, steamed options\n• **Portion Control:** Share meals or take leftovers\n• **Beverage Choices:** Choose water, unsweetened tea, or coffee\n• **Special Requests:** Don't hesitate to ask for modifications\n\n**Long-term Success:**\n• **Consistency:** Small changes add up over time\n• **Flexibility:** Allow occasional treats\n• **Education:** Keep learning about nutrition\n• **Support:** Find like-minded people\n\n⚠️ **Professional Support:** Registered dietitians provide personalized nutrition guidance.",
            
            f"🌱 **Nutrition: Your Personalized Approach**\n\nLet me provide you with a structured nutrition strategy:\n\n**Phase 1: Assessment**\n• Evaluate your current eating habits\n• Identify your health goals\n• Consider any medical conditions\n• Assess your cooking skills and time\n\n**Phase 2: Education**\n• Learn about basic nutrition principles\n• Understand food labels and ingredients\n• Discover healthy cooking methods\n• Explore new foods and recipes\n\n**Phase 3: Implementation**\n• **Week 1-2:** Add more vegetables and fruits\n• **Week 3-4:** Increase whole grains and lean proteins\n• **Week 5-6:** Reduce processed foods and added sugars\n• **Week 7-8:** Optimize meal timing and portions\n\n**Phase 4: Maintenance**\n• Regular check-ins with yourself\n• Adjust based on results and preferences\n• Continue learning and experimenting\n• Seek professional guidance when needed\n\n**Success Indicators:**\n• More energy throughout the day\n• Better sleep quality\n• Improved mood and focus\n• Stable weight and body composition\n• Reduced cravings for unhealthy foods\n\n⚠️ **Healthcare Partnership:** Work with healthcare professionals for personalized nutrition plans."
        ]
        return random.choice(nutrition_responses)
    
    elif any(word in user_input_lower for word in ["exercise", "workout", "fitness", "physical activity"]):
        exercise_responses = [
            f"💪 **Fitness: Building Your Strong Foundation**\n\nI understand you're asking about exercise and fitness. Here's a comprehensive guide:\n\n**Types of Exercise:**\n• **Cardiovascular:** Walking, running, cycling, swimming\n• **Strength Training:** Weight lifting, bodyweight exercises\n• **Flexibility:** Stretching, yoga, pilates\n• **Balance:** Tai chi, balance exercises\n\n**Weekly Exercise Guidelines:**\n• **150 minutes** moderate-intensity cardio\n• **2-3 days** strength training\n• **2-3 days** flexibility work\n• **Daily** movement and activity\n\n**Getting Started Safely:**\n• **Start Slow:** Begin with 10-15 minutes\n• **Gradual Progression:** Increase duration and intensity\n• **Listen to Your Body:** Rest when needed\n• **Proper Form:** Focus on technique over weight\n\n**Exercise Benefits:**\n• **Physical:** Stronger muscles, better cardiovascular health\n• **Mental:** Reduced stress, improved mood\n• **Long-term:** Disease prevention, better quality of life\n• **Social:** Group activities, community connection\n\n⚠️ **Safety First:** Consult healthcare professionals before starting a new exercise program.",
            
            f"🏃‍♂️ **Physical Activity: Your Path to Wellness**\n\nLet me help you understand the importance of regular physical activity:\n\n**Why Exercise Matters:**\nPhysical activity is one of the most powerful tools for maintaining health and preventing disease.\n\n**Exercise Intensity Levels:**\n• **Light:** Walking, gentle stretching, household chores\n• **Moderate:** Brisk walking, swimming, dancing\n• **Vigorous:** Running, cycling, high-intensity training\n\n**Building an Exercise Routine:**\n• **Morning:** Start with light stretching or walking\n• **Throughout Day:** Take activity breaks\n• **Evening:** Strength training or flexibility work\n• **Weekends:** Longer activities or sports\n\n**Overcoming Common Barriers:**\n• **Time:** Start with 10-minute sessions\n• **Energy:** Exercise actually increases energy\n• **Cost:** Many activities are free or low-cost\n• **Motivation:** Find activities you enjoy\n\n**Exercise Safety:**\n• **Warm-up:** 5-10 minutes of light activity\n• **Cool-down:** Gentle stretching after exercise\n• **Hydration:** Drink water before, during, and after\n• **Recovery:** Allow rest days between intense sessions\n\n**Long-term Success:**\n• **Consistency:** Regular activity is better than occasional intense workouts\n• **Variety:** Mix different types of exercise\n• **Progression:** Gradually increase challenge\n• **Enjoyment:** Choose activities you look forward to\n\n⚠️ **Professional Guidance:** Consult fitness professionals for personalized exercise programs.",
            
            f"🎯 **Fitness: Your Personalized Journey**\n\nI'm here to support your fitness journey:\n\n**Understanding Your Fitness Level:**\n• **Beginner:** New to exercise or returning after a break\n• **Intermediate:** Regular exercise routine established\n• **Advanced:** Experienced with various exercise types\n\n**Setting Realistic Goals:**\n• **Short-term:** Weekly or monthly targets\n• **Medium-term:** 3-6 month objectives\n• **Long-term:** Yearly or lifestyle goals\n• **SMART Goals:** Specific, Measurable, Achievable, Relevant, Time-bound\n\n**Creating Your Exercise Plan:**\n• **Cardio:** Choose activities you enjoy\n• **Strength:** Focus on major muscle groups\n• **Flexibility:** Include stretching and mobility work\n• **Recovery:** Plan rest days and active recovery\n\n**Staying Motivated:**\n• **Track Progress:** Keep a fitness journal\n• **Find Support:** Exercise with friends or join groups\n• **Mix It Up:** Try new activities regularly\n• **Celebrate Success:** Acknowledge your achievements\n\n**Exercise and Health Conditions:**\n• **Heart Health:** Start with walking, progress gradually\n• **Joint Issues:** Low-impact activities like swimming\n• **Diabetes:** Regular activity helps blood sugar control\n• **Mental Health:** Exercise reduces stress and anxiety\n\n**Technology and Tools:**\n• **Fitness Apps:** Track workouts and progress\n• **Wearable Devices:** Monitor heart rate and activity\n• **Online Resources:** Workout videos and programs\n• **Professional Guidance:** Personal trainers and coaches\n\n⚠️ **Medical Clearance:** Always consult healthcare providers before starting new exercise programs.",
            
            f"🌟 **Fitness: Building Your Active Lifestyle**\n\nLet me provide you with a comprehensive fitness strategy:\n\n**Phase 1: Foundation Building**\n• **Assessment:** Evaluate current fitness level\n• **Goal Setting:** Define what you want to achieve\n• **Schedule Planning:** Find time for regular activity\n• **Equipment Needs:** Identify what you'll need\n\n**Phase 2: Getting Started**\n• **Week 1-2:** Light walking and stretching\n• **Week 3-4:** Add moderate cardio activities\n• **Week 5-6:** Introduce basic strength training\n• **Week 7-8:** Increase duration and intensity\n\n**Phase 3: Building Consistency**\n• **Monthly Goals:** Set realistic targets\n• **Progress Tracking:** Monitor improvements\n• **Variety:** Try different activities\n• **Social Support:** Find exercise partners or groups\n\n**Phase 4: Advanced Training**\n• **Specialized Programs:** Focus on specific goals\n• **Performance Optimization:** Fine-tune your routine\n• **Injury Prevention:** Maintain proper form and recovery\n• **Long-term Planning:** Develop sustainable habits\n\n**Success Metrics:**\n• Increased energy and stamina\n• Improved strength and flexibility\n• Better sleep quality\n• Enhanced mood and mental clarity\n• Reduced stress and anxiety\n• Improved body composition\n\n⚠️ **Professional Support:** Fitness professionals can provide personalized guidance and motivation."
        ]
        return random.choice(exercise_responses)
    
    elif any(word in user_input_lower for word in ["medicine", "medication", "drug", "pill"]):
        medicine_responses = [
            f"💊 **Medication Safety: Your Health Priority**\n\nI understand you're asking about medications. Here's what you should know:\n\n**Medication Safety Fundamentals:**\n• **Always Read Labels:** Follow dosage instructions exactly\n• **Ask Questions:** Don't hesitate to ask your doctor or pharmacist\n• **Keep Records:** Maintain a current medication list\n• **Store Properly:** Keep medications in a cool, dry place\n\n**Common Medication Categories:**\n• **Pain Relievers:** Acetaminophen, ibuprofen, aspirin\n• **Antibiotics:** Take the full course as prescribed\n• **Chronic Conditions:** Blood pressure, diabetes, heart medications\n• **Supplements:** Vitamins, minerals, herbal products\n\n**Important Safety Tips:**\n• **Never Share:** Don't take medications prescribed for others\n• **Check Expiration:** Don't use expired medications\n• **Side Effects:** Know what to watch for\n• **Interactions:** Inform doctors about all medications\n\n**When to Seek Help:**\n🚨 Severe allergic reactions\n🚨 Unexpected side effects\n🚨 Overdose symptoms\n🚨 Medication errors\n\n⚠️ **Professional Guidance:** Always consult healthcare professionals for medication advice.",
            
            f"🏥 **Medication Management: Your Health Partnership**\n\nLet me help you understand proper medication management:\n\n**Understanding Your Medications:**\n• **Purpose:** Why you're taking each medication\n• **Dosage:** How much and how often\n• **Timing:** When to take medications\n• **Duration:** How long to continue treatment\n\n**Medication Organization:**\n• **Pill Organizer:** Weekly or daily containers\n• **Reminder Systems:** Alarms, apps, or notes\n• **Refill Tracking:** Don't run out of important medications\n• **Travel Planning:** Pack extra and carry prescriptions\n\n**Communication with Healthcare Team:**\n• **Complete List:** Share all medications with every provider\n• **Side Effects:** Report any unusual symptoms\n• **Cost Concerns:** Discuss affordable alternatives\n• **Questions:** Don't leave appointments with unanswered questions\n\n**Special Considerations:**\n• **Children:** Extra care with dosing and storage\n• **Elderly:** May need adjusted dosages\n• **Pregnancy:** Some medications may not be safe\n• **Multiple Conditions:** Coordination between specialists\n\n**Medication Safety at Home:**\n• **Secure Storage:** Keep out of reach of children\n• **Proper Disposal:** Don't flush or throw in trash\n• **Emergency Information:** Keep poison control number handy\n• **Regular Review:** Periodically review with healthcare team\n\n⚠️ **Medical Disclaimer:** This information is educational. Always follow your healthcare provider's instructions.",
            
            f"🔬 **Medication Education: Understanding Your Treatment**\n\nI'm here to help you understand your medications:\n\n**How Medications Work:**\nMedications interact with your body in specific ways to treat conditions or manage symptoms.\n\n**Reading Prescription Labels:**\n• **Patient Name:** Ensure it's your medication\n• **Medication Name:** Generic and brand names\n• **Dosage Instructions:** How much and when to take\n• **Prescriber Information:** Doctor's name and contact\n• **Pharmacy Details:** Where to get refills\n\n**Common Medication Forms:**\n• **Pills/Tablets:** Swallow whole or as directed\n• **Liquid:** Use measuring device provided\n• **Inhalers:** Follow specific technique instructions\n• **Topical:** Apply to clean, dry skin\n• **Injections:** Usually given by healthcare professionals\n\n**Managing Side Effects:**\n• **Common Side Effects:** Usually mild and temporary\n• **Serious Side Effects:** Know when to seek immediate care\n• **Allergic Reactions:** Watch for rash, swelling, difficulty breathing\n• **Drug Interactions:** Some medications don't work well together\n\n**Medication Adherence:**\n• **Set Reminders:** Use phone alarms or apps\n• **Routine Integration:** Take with meals or daily activities\n• **Travel Planning:** Pack extra and carry prescriptions\n• **Refill Management:** Don't wait until you're out\n\n**Cost Management:**\n• **Generic Options:** Often more affordable\n• **Insurance Coverage:** Understand your benefits\n• **Patient Assistance:** Programs for expensive medications\n• **Pharmacy Shopping:** Compare prices between pharmacies\n\n⚠️ **Professional Care:** Pharmacists and doctors are your best resources for medication questions.",
            
            f"📋 **Medication Management: Your Complete System**\n\nLet me provide you with a comprehensive medication management strategy:\n\n**Phase 1: Organization**\n• **Current Medication List:** Document all medications\n• **Healthcare Team Contact:** Keep provider information handy\n• **Pharmacy Information:** Preferred pharmacy and contact details\n• **Emergency Contacts:** Poison control and emergency numbers\n\n**Phase 2: Education**\n• **Medication Purpose:** Understand why each medication is prescribed\n• **Dosage Instructions:** Know exactly how and when to take\n• **Side Effects:** Recognize normal vs. concerning symptoms\n• **Interactions:** Understand food and drug interactions\n\n**Phase 3: Implementation**\n• **Daily Routine:** Integrate medications into your schedule\n• **Reminder System:** Use technology or traditional methods\n• **Storage System:** Organize medications safely\n• **Tracking System:** Monitor adherence and effects\n\n**Phase 4: Maintenance**\n• **Regular Reviews:** Periodic medication reviews with healthcare team\n• **Refill Management:** Stay ahead of prescription renewals\n• **Side Effect Monitoring:** Track any changes or concerns\n• **Lifestyle Adjustments:** Modify habits as needed\n\n**Success Indicators:**\n• Consistent medication adherence\n• Reduced symptoms or improved condition\n• Fewer medication-related problems\n• Better communication with healthcare team\n• Improved quality of life\n\n⚠️ **Healthcare Partnership:** Regular communication with your medical team ensures optimal medication management."
        ]
        return random.choice(medicine_responses)
    
    elif any(word in user_input_lower for word in ["thank", "thanks", "appreciate"]):
        gratitude_responses = [
            "You're very welcome! 😊 I'm glad I could help. Is there anything else you'd like to know about your health?",
            "It's my pleasure! 🌟 I'm here whenever you need health information. Feel free to ask more questions anytime.",
            "You're welcome! 💙 I'm always here to support your health journey. What else can I assist you with today?",
            "Happy to help! ✨ Your health is important, and I'm here to provide guidance. Any other health questions on your mind?"
        ]
        return random.choice(gratitude_responses)
    
    elif any(word in user_input_lower for word in ["how are you", "how do you do"]):
        wellbeing_responses = [
            "I'm functioning well and ready to help! 😊 How are you feeling today? Any health concerns I can assist with?",
            "I'm here and ready to assist with your health questions! 🌟 How can I help you today?",
            "I'm doing great and eager to support your health journey! 💙 What would you like to know about your wellness?",
            "I'm ready to help with any health concerns you might have! ✨ How are you doing? Any questions about your health?"
        ]
        return random.choice(wellbeing_responses)
    
    else:
        # Default dynamic responses for general health questions
        general_responses = [
            f"🏥 **Health Information: Your Wellness Guide**\n\nI understand you're asking about health. Here's what I can share:\n\n**General Health Principles:**\n• **Prevention:** Regular check-ups and screenings\n• **Lifestyle:** Balanced diet, regular exercise, adequate sleep\n• **Mental Health:** Stress management and emotional well-being\n• **Safety:** Injury prevention and emergency preparedness\n\n**When to Seek Medical Care:**\n• Persistent symptoms that don't improve\n• Sudden changes in health status\n• Emergency symptoms (chest pain, difficulty breathing)\n• Regular preventive care appointments\n\n**Building Healthy Habits:**\n• Start with small, manageable changes\n• Focus on consistency over perfection\n• Celebrate progress and milestones\n• Seek support when needed\n\n⚠️ **Medical Disclaimer:** This information is for educational purposes. Always consult healthcare professionals for personalized medical advice.",
            
            f"💡 **Health Guidance: Supporting Your Wellness**\n\nLet me help you with your health question:\n\n**Understanding Your Health:**\nYour health is a complex interplay of physical, mental, and social factors.\n\n**Key Health Areas:**\n• **Physical Health:** Exercise, nutrition, sleep, preventive care\n• **Mental Health:** Stress management, emotional well-being, social connection\n• **Environmental Health:** Safe living and working conditions\n• **Social Health:** Relationships, community involvement, support systems\n\n**Proactive Health Management:**\n• Regular medical check-ups\n• Preventive screenings and vaccinations\n• Healthy lifestyle choices\n• Stress reduction techniques\n\n**Emergency Awareness:**\nKnow the signs of medical emergencies and when to seek immediate care.\n\n⚠️ **Professional Care:** Healthcare professionals provide personalized medical guidance.",
            
            f"🌟 **Health Support: Your Wellness Journey**\n\nI'm here to support your health and wellness:\n\n**Holistic Health Approach:**\nTrue health encompasses physical, mental, emotional, and social well-being.\n\n**Daily Health Practices:**\n• **Morning:** Start with hydration and light movement\n• **Throughout Day:** Stay active and maintain good posture\n• **Evening:** Wind down with relaxation techniques\n• **Weekly:** Plan healthy meals and activities\n\n**Health Monitoring:**\n• Pay attention to how you feel\n• Track any changes or symptoms\n• Maintain regular medical appointments\n• Keep health records organized\n\n**Prevention Focus:**\n• Regular exercise and healthy eating\n• Adequate sleep and stress management\n• Preventive screenings and vaccinations\n• Safety practices and injury prevention\n\n**Support Systems:**\n• Healthcare providers\n• Family and friends\n• Community resources\n• Health education materials\n\n⚠️ **Medical Partnership:** Work with healthcare professionals for personalized health guidance.",
            
            f"🎯 **Health Information: Your Complete Guide**\n\nLet me provide you with comprehensive health guidance:\n\n**Understanding Health:**\nHealth is not just the absence of disease, but a state of complete physical, mental, and social well-being.\n\n**Health Assessment:**\n• **Current Status:** How are you feeling today?\n• **Risk Factors:** Family history, lifestyle, environment\n• **Preventive Needs:** Age-appropriate screenings and care\n• **Goals:** What health improvements would you like to make?\n\n**Health Action Plan:**\n• **Immediate:** Address any current health concerns\n• **Short-term:** Make small, sustainable lifestyle changes\n• **Long-term:** Build lasting healthy habits\n• **Ongoing:** Regular monitoring and adjustment\n\n**Health Resources:**\n• Primary care providers\n• Specialists as needed\n• Preventive care services\n• Health education programs\n• Support groups and communities\n\n**Success Indicators:**\n• Improved energy and vitality\n• Better sleep quality\n• Enhanced mood and mental clarity\n• Stronger immune function\n• Better quality of life\n\n⚠️ **Healthcare Partnership:** Regular communication with your medical team ensures optimal health outcomes."
        ]
        return random.choice(general_responses)

def main():
    """Main application function with enhanced UI/UX."""
    
    # Initialize system
    rag_system = initialize_system()
    
    if not rag_system:
        st.error("Failed to initialize RAG system. Please check your configuration.")
        return
    
    # Clean Sidebar Design
    with st.sidebar:
        st.markdown("### 🏥 AI Healthcare Assistant Pro")
        st.markdown("---")
        
        st.markdown("**System Status**")
        st.success("✅ RAG System Online")
        st.success("✅ Memory Management Active")
        st.success("✅ Knowledge Base Loaded")
        st.success("✅ Dynamic Responses Active")
        
        st.markdown("---")
        st.markdown("**Advanced Features**")
        st.markdown("• Multi-session Memory")
        st.markdown("• Context-aware Generation")
        st.markdown("• Historical Tracking")
        st.markdown("• Progressive Building")
        st.markdown("• Personalized Adaptation")
        st.markdown("• Dynamic Responses")
        st.markdown("• Embedding Models")
        st.markdown("• Vector Database")
        
        # Session Management
        st.markdown("---")
        st.markdown("**🔄 Session Management**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New Session", key="new_session", help="Start a fresh conversation session"):
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.session_id = session_id
                st.session_state.messages = []
                st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.success("✨ New session started successfully!")
                
        with col2:
            if st.button("🗑️ Reset Chat", key="reset_chat", help="Clear current chat history"):
                if "messages" in st.session_state:
                    st.session_state.messages = []
                    st.success("🧹 Chat history cleared!")
                    st.rerun()
        
        # System Analytics
        st.markdown("---")
        st.markdown("**📊 System Analytics**")
        
        system_stats = rag_system.get_system_stats()
        
        # Memory stats
        memory_stats = system_stats['memory_stats']
        st.metric("Session Memories", memory_stats["session_memories"], help="Number of active session memories")
        st.metric("Long-term Memories", memory_stats["long_term_memories"], help="Number of stored long-term memories")
        
        # Knowledge stats
        knowledge_stats = system_stats['knowledge_stats']
        st.metric("Knowledge Chunks", knowledge_stats["total_chunks"], help="Total knowledge chunks in database")
        
        # Evaluation metrics
        eval_metrics = system_stats['evaluation_metrics']
        st.metric("Avg Response Time", f"{eval_metrics['average_response_time']}s", help="Average response generation time")
    
    # Main Content with Clean Design
    st.title("🏥 AI Healthcare Assistant Pro")
    st.markdown("*Advanced Conversational AI with Multi-Session Memory, Context-Aware Generation & Dynamic Healthcare Responses*")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Main Chat Interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Professional Health Consultation")
        
        # Chat Container with Auto-scroll
        chat_container = st.container()
        
        # Add auto-scroll JavaScript
        st.markdown("""
        <script>
        // Function to scroll chat to bottom
        function scrollToBottom() {
            // Try multiple selectors to find the chat container
            const selectors = [
                '.stContainer',
                '.main .block-container',
                '.stApp > div > div > div > div > div > div',
                'div[data-testid="stVerticalBlock"]'
            ];
            
            let chatContainer = null;
            for (const selector of selectors) {
                chatContainer = document.querySelector(selector);
                if (chatContainer) break;
            }
            
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
                console.log('Scrolled to bottom');
            } else {
                console.log('Chat container not found');
            }
        }
        
        // Scroll to bottom when page loads
        window.addEventListener('load', function() {
            setTimeout(scrollToBottom, 200);
        });
        
        // Scroll to bottom when new content is added
        const observer = new MutationObserver(function(mutations) {
            let shouldScroll = false;
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    shouldScroll = true;
                }
            });
            if (shouldScroll) {
                setTimeout(scrollToBottom, 100);
            }
        });
        
        // Start observing when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const selectors = [
                '.stContainer',
                '.main .block-container',
                '.stApp > div > div > div > div > div > div',
                'div[data-testid="stVerticalBlock"]'
            ];
            
            let chatContainer = null;
            for (const selector of selectors) {
                chatContainer = document.querySelector(selector);
                if (chatContainer) break;
            }
            
            if (chatContainer) {
                observer.observe(chatContainer, {
                    childList: true,
                    subtree: true
                });
                console.log('Observer started');
            }
        });
        
        // Also scroll on window resize
        window.addEventListener('resize', function() {
            setTimeout(scrollToBottom, 150);
        });
        
        // Scroll when Streamlit reruns
        if (window.parent !== window) {
            window.parent.postMessage({type: 'scrollToBottom'}, '*');
        }
        </script>
        """, unsafe_allow_html=True)
        
        with chat_container:
            # Display chat messages
            if not st.session_state.messages:
                st.markdown("### 👋 Welcome to AI Healthcare Assistant Pro")
                st.markdown("*Ask me about your health concerns, symptoms, or general wellness questions.*")
                st.markdown("I provide dynamic, context-aware responses with comprehensive healthcare information.")
            else:
                for i, message in enumerate(st.session_state.messages):
                    if message["role"] == "user":
                        st.markdown(f"**You:** {message['content']}")
                    else:
                        st.markdown(f"**AI Healthcare Assistant:** {message['content']}")
                
                # Add a hidden element to trigger scroll
                st.markdown(f'<div id="scroll-trigger-{len(st.session_state.messages)}" style="height: 1px;"></div>', unsafe_allow_html=True)
        
        # Chat Input
        user_input = st.chat_input("💬 Type your health question here (e.g., 'I have a cold', 'headache symptoms', 'seasonal allergies')...", key="chat_input")
        
        # Add auto-scroll functionality
        if st.session_state.messages:
            st.markdown("""
            <script>
            // Auto-scroll to bottom when new messages are added
            function autoScrollToBottom() {
                const containers = document.querySelectorAll('.stContainer, .main .block-container, div[data-testid="stVerticalBlock"]');
                containers.forEach(container => {
                    if (container.scrollHeight > container.clientHeight) {
                        container.scrollTop = container.scrollHeight;
                    }
                });
            }
            
            // Scroll on page load
            window.addEventListener('load', () => setTimeout(autoScrollToBottom, 300));
            
            // Scroll when content changes
            const observer = new MutationObserver(() => {
                setTimeout(autoScrollToBottom, 100);
            });
            
            // Start observing
            document.addEventListener('DOMContentLoaded', () => {
                const containers = document.querySelectorAll('.stContainer, .main .block-container, div[data-testid="stVerticalBlock"]');
                containers.forEach(container => {
                    observer.observe(container, { childList: true, subtree: true });
                });
            });
            </script>
            """, unsafe_allow_html=True)
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Simple loading with native Streamlit
            with st.spinner("🤖 Processing your request with advanced AI..."):
                start_time = time.time()
                
                # Generate dynamic response
                dynamic_response = generate_dynamic_response(
                    user_input, 
                    rag_system, 
                    st.session_state.session_id,
                    st.session_state.user_id
                )
                
                response_time = time.time() - start_time
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": dynamic_response
                })
                
                # Store response metrics
                if "response_metrics" not in st.session_state:
                    st.session_state.response_metrics = []
                
                st.session_state.response_metrics.append({
                    "timestamp": datetime.now().isoformat(),
                    "response_time": response_time,
                    "user_input": user_input,
                    "response": dynamic_response
                })
                
                # Rerun to display new message
                st.rerun()
    
    with col2:
        st.markdown("### 📊 Real-time Analytics")
        
        if "response_metrics" in st.session_state and st.session_state.response_metrics:
            latest_metrics = st.session_state.response_metrics[-1]
            st.metric("Response Time", f"{latest_metrics['response_time']:.3f}s", help="Time taken to generate response")
            st.metric("Total Messages", len(st.session_state.messages), help="Number of messages in current session")
            st.metric("Session ID", st.session_state.session_id[:12] + "...", help="Current session identifier")
        else:
            st.info("📊 Analytics will appear here once you start chatting")
        
        if "session_id" in st.session_state:
            st.markdown("### 📋 Session Information")
            st.metric("User ID", st.session_state.user_id[:12] + "...", help="Your unique user identifier")
    
    # Professional Footer
    st.markdown("---")
    st.markdown("### 🏥 AI Healthcare Assistant Pro")
    st.markdown("*Advanced Conversational AI with Multi-Session Memory & Context-Aware Generation*")
    
    st.markdown("**This system demonstrates cutting-edge RAG features including:**")
    st.markdown("• Multi-session memory management • Context-aware response generation")
    st.markdown("• Historical interaction tracking • Progressive conversation building")
    st.markdown("• Personalized response adaptation • Dynamic healthcare responses")
    st.markdown("• Advanced embedding models • Vector database integration")
    st.markdown("• Effective chunking strategies • Comprehensive evaluation metrics")
    
    st.markdown("---")
    st.warning("⚠️ **For educational and demonstration purposes only.** Always consult qualified healthcare professionals for medical decisions and treatment.")

if __name__ == "__main__":
    main()