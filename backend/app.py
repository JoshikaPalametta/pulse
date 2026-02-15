from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
from symptom_analyzer import SymptomAnalyzer
from hospital_service import HospitalService
from chatbot import MedicalChatbot

app = Flask(__name__)
CORS(app)

# Initialize services
symptom_analyzer = SymptomAnalyzer()
hospital_service = HospitalService()
chatbot = MedicalChatbot()

# Session storage (in production, use Redis or database)
sessions = {}

@app.route('/api/find-hospitals', methods=['POST'])
def find_hospitals():
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        symptoms = data.get('symptoms')
        language = data.get('language', 'en')
        session_id = data.get('session_id')
        
        if not all([latitude, longitude, symptoms]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Analyze symptoms using lightweight AI
        analysis = symptom_analyzer.analyze(symptoms, language)
        
        # Find nearby hospitals
        hospitals = hospital_service.find_nearby_hospitals(
            latitude, 
            longitude, 
            analysis['specialty'],
            analysis['priority']
        )
        
        # Score and rank hospitals
        ranked_hospitals = hospital_service.score_hospitals(
            hospitals,
            latitude,
            longitude,
            analysis
        )
        
        # Store in session
        if session_id:
            sessions[session_id] = {
                'symptoms': symptoms,
                'analysis': analysis,
                'hospitals': ranked_hospitals,
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'hospitals': ranked_hospitals[:10]  # Top 10 results
        })
        
    except Exception as e:
        print(f"Error in find_hospitals: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emergency-hospitals', methods=['POST'])
def emergency_hospitals():
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not all([latitude, longitude]):
            return jsonify({'success': False, 'error': 'Missing coordinates'}), 400
        
        # Find hospitals with 24/7 emergency services
        hospitals = hospital_service.find_emergency_hospitals(latitude, longitude)
        
        return jsonify({
            'success': True,
            'hospitals': hospitals[:15]  # Top 15 emergency hospitals
        })
        
    except Exception as e:
        print(f"Error in emergency_hospitals: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospital/<int:hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    try:
        language = request.args.get('language', 'en')
        hospital = hospital_service.get_hospital_by_id(hospital_id)
        
        if not hospital:
            return jsonify({'success': False, 'error': 'Hospital not found'}), 404
        
        return jsonify({
            'success': True,
            'hospital': hospital
        })
        
    except Exception as e:
        print(f"Error in get_hospital_details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot_response():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        response = chatbot.get_response(message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Hospital Finder API is running successfully 🚀',
        'status': 'online',
        'endpoints': {
            'health': '/health',
            'find_hospitals': '/api/find-hospitals',
            'emergency_hospitals': '/api/emergency-hospitals',
            'hospital_details': '/api/hospital/<id>',
            'chatbot': '/api/chatbot'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'symptom_analyzer': 'ready',
            'hospital_service': 'ready',
            'chatbot': 'ready'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
