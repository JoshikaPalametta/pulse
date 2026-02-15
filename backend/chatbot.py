import random
import re
from typing import Dict, List

class MedicalChatbot:
    """
    Simple, lightweight rule-based medical chatbot for basic queries
    """
    
    def __init__(self):
        self.responses = self._load_responses()
        self.context = {}
    
    def _load_responses(self) -> Dict:
        """Load response templates for different query types"""
        return {
            'greeting': [
                "Hello! I'm here to help you find the right hospital. How can I assist you today?",
                "Hi! I can help you with medical queries and finding hospitals. What's bothering you?",
                "Welcome! I'm your medical assistant. How may I help you?"
            ],
            
            'symptom_query': [
                "I understand you're experiencing {symptoms}. For an accurate diagnosis, I recommend visiting a hospital. Would you like me to find nearby hospitals for you?",
                "Based on what you've told me, it would be best to consult with a medical professional. Shall I help you find appropriate hospitals nearby?",
                "I can help you find hospitals that specialize in treating {symptoms}. What's your location?"
            ],
            
            'emergency': [
                "This sounds like an emergency! Please call emergency services (108 in India) immediately or visit the nearest emergency room. Would you like me to find emergency hospitals near you?",
                "⚠️ For urgent medical issues, please seek immediate medical attention. Call 108 or go to the nearest hospital. I can help you find emergency hospitals nearby.",
                "This requires immediate medical attention. Please call an ambulance (108) or have someone take you to the emergency room right away."
            ],
            
            'location_query': [
                "To find the best hospitals for you, I'll need your location. Can you share your city or allow location access?",
                "I can search for hospitals near you. What city are you in?",
                "Please share your location so I can find nearby hospitals that can help you."
            ],
            
            'hospital_info': [
                "I can provide information about hospitals including their specialties, ratings, distance from you, and contact details. What would you like to know?",
                "I have detailed information about hospitals in your area. Would you like to know about specific hospitals or search by specialty?",
                "I can help you compare hospitals based on distance, ratings, specialties, and emergency services. What's most important to you?"
            ],
            
            'thanks': [
                "You're welcome! Take care and get well soon. Feel free to ask if you need anything else.",
                "Happy to help! Wishing you good health. Don't hesitate to reach out if you have more questions.",
                "Glad I could assist! Stay safe and feel better soon."
            ],
            
            'unknown': [
                "I'm not sure I understood that. Could you rephrase your question? I can help you find hospitals or answer basic medical queries.",
                "I didn't quite catch that. I specialize in helping you find hospitals and understand symptoms. How can I help?",
                "Could you please provide more details? I'm here to help you find the right hospital for your needs."
            ],
            
            'general_advice': [
                "While I can provide general information, it's important to consult with a healthcare professional for proper diagnosis and treatment. Would you like me to find doctors or hospitals near you?",
                "For medical advice, it's best to speak with a qualified doctor. I can help you find the right hospital or specialist. Shall I search for you?",
                "I recommend getting a professional medical opinion. I can help you find appropriate healthcare providers nearby."
            ]
        }
    
    def get_response(self, message: str) -> str:
        """
        Generate response based on message content
        
        Args:
            message: User's message
        
        Returns:
            Bot response string
        """
        message_lower = message.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(message_lower)
        
        # Emergency keywords
        emergency_keywords = ['emergency', 'urgent', 'severe', 'critical', 'heart attack', 
                            'stroke', 'bleeding', 'unconscious', 'can\'t breathe', 'accident']
        
        # Check for emergency
        if any(keyword in message_lower for keyword in emergency_keywords):
            return random.choice(self.responses['emergency'])
        
        # Greetings
        if intent == 'greeting':
            return random.choice(self.responses['greeting'])
        
        # Thanks
        elif intent == 'thanks':
            return random.choice(self.responses['thanks'])
        
        # Symptom-related
        elif intent == 'symptom':
            symptoms = self._extract_symptoms(message_lower)
            response = random.choice(self.responses['symptom_query'])
            return response.format(symptoms=symptoms if symptoms else "your symptoms")
        
        # Location query
        elif intent == 'location':
            return random.choice(self.responses['location_query'])
        
        # Hospital info
        elif intent == 'hospital':
            return random.choice(self.responses['hospital_info'])
        
        # General medical advice
        elif intent == 'medical_advice':
            return random.choice(self.responses['general_advice'])
        
        # Default
        else:
            return random.choice(self.responses['unknown'])
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        
        # Greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(pattern in message for pattern in greeting_patterns):
            return 'greeting'
        
        # Thanks patterns
        thanks_patterns = ['thank', 'thanks', 'appreciate']
        if any(pattern in message for pattern in thanks_patterns):
            return 'thanks'
        
        # Symptom patterns
        symptom_keywords = ['pain', 'ache', 'fever', 'cough', 'headache', 'sick', 'ill', 
                          'dizzy', 'nausea', 'vomit', 'diarrhea', 'symptom', 'feel']
        if any(keyword in message for keyword in symptom_keywords):
            return 'symptom'
        
        # Location patterns
        location_keywords = ['where', 'location', 'near', 'nearby', 'close', 'around']
        if any(keyword in message for keyword in location_keywords):
            return 'location'
        
        # Hospital info patterns
        hospital_keywords = ['hospital', 'clinic', 'doctor', 'emergency', 'specialist']
        if any(keyword in message for keyword in hospital_keywords):
            return 'hospital'
        
        # Medical advice patterns
        medical_keywords = ['what should i do', 'what can i do', 'advice', 'recommend', 'suggest']
        if any(keyword in message for keyword in medical_keywords):
            return 'medical_advice'
        
        return 'unknown'
    
    def _extract_symptoms(self, message: str) -> str:
        """Extract symptom mentions from message"""
        symptom_words = ['pain', 'ache', 'fever', 'cough', 'headache', 'dizzy', 
                        'nausea', 'vomit', 'diarrhea', 'weakness', 'fatigue']
        
        found_symptoms = [word for word in symptom_words if word in message]
        
        if found_symptoms:
            return ', '.join(found_symptoms)
        
        return "your condition"


# Test the chatbot
if __name__ == '__main__':
    chatbot = MedicalChatbot()
    
    test_messages = [
        "Hello!",
        "I have a severe headache and fever",
        "Where can I find a hospital near me?",
        "I'm having chest pain and difficulty breathing",
        "Thank you for your help"
    ]
    
    print("\n=== Testing Medical Chatbot ===\n")
    for msg in test_messages:
        response = chatbot.get_response(msg)
        print(f"User: {msg}")
        print(f"Bot: {response}\n")