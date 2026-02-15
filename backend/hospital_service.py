import math
import json
from typing import List, Dict, Tuple
from geopy.distance import geodesic
import sqlite3
import os

class HospitalService:
    """
    Hospital search and ranking service with accurate geolocation
    """
    
    def __init__(self, db_path='data/hospitals.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists with sample data"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create hospitals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                rating REAL DEFAULT 0,
                total_reviews INTEGER DEFAULT 0,
                has_emergency BOOLEAN DEFAULT 0,
                has_ambulance BOOLEAN DEFAULT 1,
                specialties TEXT,
                facilities TEXT,
                open_247 BOOLEAN DEFAULT 0
            )
        ''')
        
        # Check if we have data
        cursor.execute('SELECT COUNT(*) FROM hospitals')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert sample hospitals for Visakhapatnam and surrounding areas
            sample_hospitals = [
                # Visakhapatnam - Major Hospitals
                ('Seven Hills Hospital', 17.7231, 83.3008, 'Rockdale Layout, Visakhapatnam, AP 530002', 
                 '+91-891-2790000', 'info@sevenhillshospital.com', 4.5, 1250, 1, 1,
                 'Cardiology,Neurology,Orthopedics,Emergency Medicine,ICU,Oncology,Gastroenterology', 
                 'ICU,CT Scan,MRI,24/7 Lab,Pharmacy,Blood Bank,Ambulance', 1),
                
                ('Queen\'s NRI Hospital', 17.7456, 83.3161, 'Health City, Visakhapatnam, AP 530013',
                 '+91-891-6677000', 'contact@queensnrihospital.com', 4.6, 2100, 1, 1,
                 'Cardiology,Neurosurgery,Orthopedics,Nephrology,Gastroenterology,Oncology,Emergency Medicine',
                 'ICU,NICU,Cath Lab,CT Scan,MRI,24/7 Pharmacy,Blood Bank', 1),
                
                ('Visakha Institute of Medical Sciences (VIMS)', 17.7133, 83.3123, 'Near Steel Plant, Visakhapatnam, AP 530017',
                 '+91-891-2714141', 'info@vimshospital.com', 4.3, 980, 1, 1,
                 'Emergency Medicine,General Medicine,Surgery,Orthopedics,Pediatrics,Obstetrics & Gynecology',
                 'Emergency,ICU,Operation Theater,X-Ray,Ultrasound,Lab,Pharmacy', 1),
                
                ('Apollo Hospitals', 17.7523, 83.3231, 'Waltair Main Road, Visakhapatnam, AP 530002',
                 '+91-891-2777000', 'vizag@apollohospitals.com', 4.7, 3200, 1, 1,
                 'Cardiology,Neurology,Oncology,Orthopedics,Gastroenterology,Nephrology,Emergency Medicine,Pediatrics',
                 'ICU,NICU,PICU,Cath Lab,CT Scan,MRI,PET Scan,24/7 Lab,Blood Bank,Ambulance', 1),
                
                ('KIMS ICON Hospital', 17.7312, 83.3034, 'Visakhapatnam, AP 530002',
                 '+91-891-6699000', 'info@kimsicon.com', 4.4, 1560, 1, 1,
                 'Cardiology,Neurology,Orthopedics,Oncology,Nephrology,Gastroenterology,Pulmonology',
                 'ICU,CT Scan,MRI,Dialysis,24/7 Emergency,Pharmacy,Blood Bank', 1),
                
                ('Care Hospital', 17.7189, 83.3045, 'Ramnagar, Visakhapatnam, AP 530002',
                 '+91-891-6689999', 'vizag@carehospitals.com', 4.5, 1890, 1, 1,
                 'Cardiology,Neurology,Orthopedics,Gastroenterology,Pulmonology,Emergency Medicine',
                 'ICU,CCU,Operation Theater,CT Scan,MRI,Lab,Pharmacy,Ambulance', 1),
                
                ('Medicover Hospitals', 17.7289, 83.3156, 'MVP Colony, Visakhapatnam, AP 530017',
                 '+91-891-4888999', 'vizag@medicoverhospitals.in', 4.3, 1120, 1, 1,
                 'General Medicine,Surgery,Orthopedics,Pediatrics,Obstetrics & Gynecology,ENT,Dermatology',
                 'ICU,Operation Theater,X-Ray,Ultrasound,Lab,Pharmacy,24/7 Emergency', 1),
                
                ('Ramesh Hospitals', 17.7412, 83.3201, 'Visakhapatnam, AP 530013',
                 '+91-891-2577777', 'info@rameshhospitals.com', 4.2, 890, 1, 1,
                 'Cardiology,Neurology,Nephrology,Urology,Gastroenterology,Pulmonology,Diabetology',
                 'ICU,Dialysis,CT Scan,Lab,Pharmacy,Emergency,Ambulance', 1),
                
                # Smaller/Specialty Hospitals
                ('Indus Hospital', 17.7201, 83.3189, 'Siripuram, Visakhapatnam, AP 530003',
                 '+91-891-2566666', 'contact@indushospital.com', 4.1, 670, 1, 1,
                 'General Medicine,Surgery,Orthopedics,Pediatrics,ENT,Ophthalmology',
                 'Emergency,X-Ray,Ultrasound,Lab,Pharmacy', 1),
                
                ('Kalyani Hospital', 17.7378, 83.3267, 'Akkayyapalem, Visakhapatnam, AP 530016',
                 '+91-891-2755555', 'info@kalyanihospital.com', 4.0, 550, 1, 1,
                 'General Medicine,Pediatrics,Obstetrics & Gynecology,Orthopedics,ENT',
                 'Emergency,X-Ray,Ultrasound,Lab,Pharmacy,Maternity Ward', 1),
                
                ('Sunrise Hospital', 17.7156, 83.2989, 'Maddilapalem, Visakhapatnam, AP 530013',
                 '+91-891-2888777', 'info@sunrisehospital.in', 4.2, 780, 1, 1,
                 'General Medicine,Surgery,Orthopedics,Pediatrics,Dermatology',
                 'Emergency,ICU,Operation Theater,X-Ray,Lab,Pharmacy', 1),
                
                ('Aditya Hospital', 17.7445, 83.3089, 'Seethammadhara, Visakhapatnam, AP 530013',
                 '+91-891-2733333', 'contact@adityahospital.com', 4.3, 920, 1, 1,
                 'Cardiology,Neurology,Orthopedics,General Medicine,Emergency Medicine',
                 'ICU,CT Scan,X-Ray,Ultrasound,Lab,24/7 Emergency,Pharmacy', 1),
                
                # Government Hospitals
                ('King George Hospital (KGH)', 17.7123, 83.3234, 'KGH, Visakhapatnam, AP 530002',
                 '+91-891-2734567', 'kgh@ap.gov.in', 3.9, 1540, 1, 1,
                 'General Medicine,Surgery,Orthopedics,Pediatrics,Obstetrics & Gynecology,Emergency Medicine,Infectious Disease',
                 'Emergency,ICU,Operation Theater,X-Ray,Lab,Pharmacy,Blood Bank', 1),
                
                ('Government Hospital for Chest and Communicable Diseases', 17.7098, 83.3178, 'Visakhapatnam, AP 530002',
                 '+91-891-2745678', 'chesthospital@ap.gov.in', 3.7, 430, 1, 1,
                 'Pulmonology,Infectious Disease,General Medicine,Emergency Medicine',
                 'X-Ray,Lab,Pharmacy,Isolation Wards', 1),
                
                # Specialty Centers
                ('Visakha Eye Hospital', 17.7267, 83.3123, 'Visakhapatnam, AP 530002',
                 '+91-891-2799999', 'info@visakhaeye.com', 4.4, 1240, 0, 0,
                 'Ophthalmology,Eye Surgery,Retina,Glaucoma,Pediatric Ophthalmology',
                 'Operation Theater,Advanced Eye Testing,Optical Shop', 0),
                
                ('Star Hospital - Multispeciality', 17.7334, 83.3145, 'Dwaraka Nagar, Visakhapatnam, AP 530016',
                 '+91-891-2766666', 'info@starhospitalvizag.com', 4.2, 980, 1, 1,
                 'Cardiology,Orthopedics,Neurology,General Surgery,Pediatrics,Obstetrics & Gynecology',
                 'ICU,Operation Theater,CT Scan,X-Ray,Lab,Pharmacy,Emergency', 1)
            ]
            
            cursor.executemany('''
                INSERT INTO hospitals (name, latitude, longitude, address, phone, email, 
                                     rating, total_reviews, has_emergency, has_ambulance, 
                                     specialties, facilities, open_247)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_hospitals)
            
            conn.commit()
            print(f"Initialized database with {len(sample_hospitals)} hospitals")
        
        conn.close()
    
    def find_nearby_hospitals(self, latitude: float, longitude: float, 
                             specialty: str = None, priority: str = 'normal',
                             max_distance_km: float = 50) -> List[Dict]:
        """
        Find hospitals near the given location
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            specialty: Required specialty (optional)
            priority: Priority level (critical, urgent, normal)
            max_distance_km: Maximum search radius in kilometers
        
        Returns:
            List of hospitals with distance and travel time
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Base query
        query = 'SELECT * FROM hospitals'
        params = []
        
        # For critical/emergency cases, only show 24/7 emergency hospitals
        if priority == 'critical':
            query += ' WHERE has_emergency = 1 AND open_247 = 1'
        elif priority == 'urgent':
            query += ' WHERE has_emergency = 1'
        
        cursor.execute(query, params)
        all_hospitals = cursor.fetchall()
        conn.close()
        
        # Calculate distances and filter
        hospitals_with_distance = []
        user_location = (latitude, longitude)
        
        for hospital in all_hospitals:
            hospital_location = (hospital['latitude'], hospital['longitude'])
            distance_km = geodesic(user_location, hospital_location).kilometers
            
            if distance_km <= max_distance_km:
                # Convert to dict
                hospital_dict = dict(hospital)
                hospital_dict['distance_km'] = round(distance_km, 2)
                hospital_dict['travel_time_minutes'] = self._calculate_travel_time(distance_km)
                
                # Convert comma-separated strings to lists
                hospital_dict['specialties'] = hospital_dict['specialties'].split(',') if hospital_dict['specialties'] else []
                hospital_dict['facilities'] = hospital_dict['facilities'].split(',') if hospital_dict['facilities'] else []
                
                # Check specialty match
                if specialty:
                    specialty_match = any(specialty.lower() in s.lower() for s in hospital_dict['specialties'])
                    hospital_dict['specialty_match'] = specialty_match
                else:
                    hospital_dict['specialty_match'] = True
                
                hospitals_with_distance.append(hospital_dict)
        
        # Sort by distance initially
        hospitals_with_distance.sort(key=lambda x: x['distance_km'])
        
        return hospitals_with_distance
    
    def find_emergency_hospitals(self, latitude: float, longitude: float,
                                max_distance_km: float = 30) -> List[Dict]:
        """Find emergency hospitals (24/7 emergency services)"""
        return self.find_nearby_hospitals(
            latitude, longitude, 
            priority='critical',
            max_distance_km=max_distance_km
        )
    
    def score_hospitals(self, hospitals: List[Dict], user_lat: float, 
                       user_lng: float, analysis: Dict) -> List[Dict]:
        """
        Score and rank hospitals based on multiple factors
        
        Scoring criteria:
        - Specialty match: 40 points
        - Distance: 30 points (closer is better)
        - Rating: 20 points
        - Emergency availability: 10 points
        """
        scored_hospitals = []
        
        for hospital in hospitals:
            score = 0
            
            # 1. Specialty Match (40 points)
            if hospital.get('specialty_match', False):
                score += 40
            else:
                # Partial credit for general medicine
                if 'General Medicine' in hospital['specialties']:
                    score += 20
            
            # 2. Distance Score (30 points)
            distance = hospital['distance_km']
            if distance <= 5:
                score += 30
            elif distance <= 10:
                score += 25
            elif distance <= 20:
                score += 15
            elif distance <= 30:
                score += 10
            else:
                score += 5
            
            # 3. Rating Score (20 points)
            rating = hospital.get('rating', 0)
            score += (rating / 5.0) * 20
            
            # 4. Emergency/Priority Match (10 points)
            priority = analysis.get('priority', 'normal')
            if priority in ['critical', 'urgent']:
                if hospital.get('has_emergency'):
                    score += 10
                if hospital.get('has_ambulance'):
                    score += 5
            
            hospital['total_score'] = round(score, 1)
            scored_hospitals.append(hospital)
        
        # Sort by total score (descending)
        scored_hospitals.sort(key=lambda x: x['total_score'], reverse=True)
        
        return scored_hospitals
    
    def get_hospital_by_id(self, hospital_id: int) -> Dict:
        """Get detailed information about a specific hospital"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM hospitals WHERE id = ?', (hospital_id,))
        hospital = cursor.fetchone()
        conn.close()
        
        if hospital:
            hospital_dict = dict(hospital)
            hospital_dict['specialties'] = hospital_dict['specialties'].split(',') if hospital_dict['specialties'] else []
            hospital_dict['facilities'] = hospital_dict['facilities'].split(',') if hospital_dict['facilities'] else []
            return hospital_dict
        
        return None
    
    def _calculate_travel_time(self, distance_km: float) -> int:
        """
        Calculate estimated travel time in minutes
        Assumes average city traffic speed of 25 km/h
        """
        avg_speed_kmh = 25
        travel_time_hours = distance_km / avg_speed_kmh
        travel_time_minutes = int(travel_time_hours * 60)
        return max(travel_time_minutes, 5)  # Minimum 5 minutes


# Test the service
if __name__ == '__main__':
    service = HospitalService()
    
    # Test finding hospitals
    print("\n=== Testing Hospital Service ===\n")
    
    # Visakhapatnam coordinates
    test_lat, test_lng = 17.6868, 83.2185
    
    hospitals = service.find_nearby_hospitals(test_lat, test_lng, max_distance_km=20)
    print(f"Found {len(hospitals)} hospitals within 20km\n")
    
    for h in hospitals[:5]:
        print(f"{h['name']}")
        print(f"  Distance: {h['distance_km']} km ({h['travel_time_minutes']} min)")
        print(f"  Rating: {h['rating']}/5.0")
        print(f"  Emergency: {'Yes' if h['has_emergency'] else 'No'}")
        print()