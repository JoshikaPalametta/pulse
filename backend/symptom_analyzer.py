import re
import json
from typing import Dict, List, Tuple

class SymptomAnalyzer:
    """
    Lightweight, accurate symptom analyzer using rule-based pattern matching
    and medical knowledge base. Fast and efficient - no heavy ML models needed.
    """
    
    def __init__(self):
        self.medical_keywords = self._load_medical_keywords()
        self.specialty_rules = self._load_specialty_rules()
        self.priority_rules = self._load_priority_rules()
    
    def _load_medical_keywords(self) -> Dict:
        """Medical symptom keywords mapped to categories"""
        return {
            # Cardiovascular
            'cardiovascular': [
                'chest pain', 'heart attack', 'cardiac', 'palpitations', 'angina',
                'shortness of breath', 'irregular heartbeat', 'heart pounding',
                'chest pressure', 'heart racing', 'cardiovascular'
            ],
            
            # Respiratory
            'respiratory': [
                'breathing', 'cough', 'asthma', 'pneumonia', 'bronchitis',
                'wheezing', 'respiratory', 'lung', 'breathless', 'dyspnea',
                'chest congestion', 'difficulty breathing'
            ],
            
            # Neurological
            'neurological': [
                'headache', 'migraine', 'seizure', 'stroke', 'paralysis',
                'numbness', 'tingling', 'dizziness', 'vertigo', 'confusion',
                'memory loss', 'neurological', 'brain', 'nerve pain'
            ],
            
            # Gastrointestinal
            'gastrointestinal': [
                'stomach pain', 'abdominal pain', 'nausea', 'vomiting', 'diarrhea',
                'constipation', 'digestive', 'gastric', 'intestinal', 'bowel',
                'food poisoning', 'indigestion', 'acid reflux'
            ],
            
            # Orthopedic
            'orthopedic': [
                'bone', 'fracture', 'joint pain', 'back pain', 'spinal',
                'arthritis', 'muscle pain', 'sprain', 'strain', 'orthopedic',
                'knee pain', 'shoulder pain', 'hip pain'
            ],
            
            # Infectious Disease
            'infectious': [
                'fever', 'infection', 'flu', 'cold', 'viral', 'bacterial',
                'malaria', 'dengue', 'typhoid', 'chills', 'sweating',
                'body ache', 'fatigue'
            ],
            
            # Emergency/Trauma
            'emergency': [
                'accident', 'injury', 'bleeding', 'trauma', 'burn', 'wound',
                'fall', 'crash', 'emergency', 'severe pain', 'unconscious',
                'heavy bleeding', 'deep cut'
            ],
            
            # Pediatric
            'pediatric': [
                'child', 'baby', 'infant', 'kid', 'pediatric', 'newborn',
                'toddler', 'childhood'
            ],
            
            # Gynecological
            'gynecological': [
                'pregnancy', 'prenatal', 'delivery', 'gynecological', 'menstrual',
                'obstetric', 'pregnant', 'labor', 'gynecology'
            ],
            
            # Dermatology
            'dermatology': [
                'skin', 'rash', 'allergy', 'itch', 'dermatology', 'acne',
                'eczema', 'psoriasis', 'skin infection', 'hives'
            ],
            
            # Ophthalmology
            'ophthalmology': [
                'eye', 'vision', 'blind', 'ophthalmology', 'visual', 'sight',
                'eye pain', 'blurred vision', 'eye infection'
            ],
            
            # ENT
            'ent': [
                'ear', 'nose', 'throat', 'ent', 'hearing', 'sinus', 'tonsil',
                'ear pain', 'sore throat', 'nasal', 'hearing loss'
            ],
            
            # General Medicine
            'general': [
                'general', 'checkup', 'consultation', 'medical', 'health',
                'wellness', 'screening'
            ]
        }
    
    def _load_specialty_rules(self) -> Dict:
        """Map categories to hospital specialties"""
        return {
            'cardiovascular': 'Cardiology',
            'respiratory': 'Pulmonology',
            'neurological': 'Neurology',
            'gastrointestinal': 'Gastroenterology',
            'orthopedic': 'Orthopedics',
            'infectious': 'Infectious Disease',
            'emergency': 'Emergency Medicine',
            'pediatric': 'Pediatrics',
            'gynecological': 'Obstetrics & Gynecology',
            'dermatology': 'Dermatology',
            'ophthalmology': 'Ophthalmology',
            'ent': 'ENT',
            'general': 'General Medicine'
        }
    
    def _load_priority_rules(self) -> Dict:
        """Critical keywords that indicate urgency"""
        return {
            'critical': [
                'heart attack', 'stroke', 'unconscious', 'heavy bleeding',
                'severe bleeding', 'can\'t breathe', 'chest pain', 'paralysis',
                'severe burns', 'head injury', 'poisoning', 'seizure'
            ],
            'urgent': [
                'severe pain', 'high fever', 'difficulty breathing', 'vomiting blood',
                'severe headache', 'abdominal pain', 'accident', 'injury',
                'deep cut', 'broken bone', 'very dizzy'
            ],
            'normal': []  # Default
        }
    
    def analyze(self, symptoms: str, language: str = 'en') -> Dict:
        """
        Analyze symptoms and return categorization
        
        Args:
            symptoms: User's symptom description
            language: Language code (en, hi, te)
        
        Returns:
            Dict with category, specialty, priority, and confidence
        """
        symptoms_lower = symptoms.lower()
        
        # Translate if needed (basic keyword translation)
        if language != 'en':
            symptoms_lower = self._translate_symptoms(symptoms_lower, language)
        
        # Detect categories
        category_scores = self._score_categories(symptoms_lower)
        
        # Determine priority
        priority = self._determine_priority(symptoms_lower)
        
        # Get top category
        if category_scores:
            top_category = max(category_scores.items(), key=lambda x: x[1])
            category = top_category[0]
            confidence = min(top_category[1] / 10.0, 1.0)  # Normalize to 0-1
        else:
            category = 'general'
            confidence = 0.5
        
        specialty = self.specialty_rules.get(category, 'General Medicine')
        
        return {
            'category': category,
            'specialty': specialty,
            'priority': priority,
            'confidence': confidence,
            'raw_scores': category_scores
        }
    
    def _score_categories(self, symptoms: str) -> Dict[str, int]:
        """Score each category based on keyword matches"""
        scores = {}
        
        for category, keywords in self.medical_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in symptoms:
                    # Exact phrase match gets higher score
                    score += 3
                elif any(word in symptoms for word in keyword.split()):
                    # Partial word match gets lower score
                    score += 1
            
            if score > 0:
                scores[category] = score
        
        return scores
    
    def _determine_priority(self, symptoms: str) -> str:
        """Determine urgency level"""
        # Check for critical keywords
        for keyword in self.priority_rules['critical']:
            if keyword in symptoms:
                return 'critical'
        
        # Check for urgent keywords
        for keyword in self.priority_rules['urgent']:
            if keyword in symptoms:
                return 'urgent'
        
        return 'normal'
    
    def _translate_symptoms(self, symptoms: str, language: str) -> str:
        """Basic keyword translation to English for analysis"""
        translations = {
            'hi': {
                'बुखार': 'fever',
                'सिरदर्द': 'headache',
                'दर्द': 'pain',
                'पेट': 'stomach',
                'खांसी': 'cough',
                'सांस': 'breathing',
                'चक्कर': 'dizziness',
                'कमजोरी': 'weakness',
                'उल्टी': 'vomiting'
            },
            'te': {
                'జ్వరం': 'fever',
                'తలనొప్పి': 'headache',
                'నొప్పి': 'pain',
                'కడుపు': 'stomach',
                'దగ్గు': 'cough',
                'శ్వాస': 'breathing',
                'తలతిరగడం': 'dizziness',
                'బలహీనత': 'weakness',
                'వాంతులు': 'vomiting'
            }
        }
        
        if language in translations:
            for native_word, english_word in translations[language].items():
                symptoms = symptoms.replace(native_word, english_word)
        
        return symptoms

# Quick test
if __name__ == '__main__':
    analyzer = SymptomAnalyzer()
    
    test_cases = [
        "I have severe chest pain and difficulty breathing",
        "My child has high fever and is vomiting",
        "I fell and my leg is swollen, can't walk",
        "Headache and blurred vision for 2 days"
    ]
    
    for test in test_cases:
        result = analyzer.analyze(test)
        print(f"\nSymptoms: {test}")
        print(f"Analysis: {result}")