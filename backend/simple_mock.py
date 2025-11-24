"""
Simple mock server for testing frontend login (no external dependencies)
Run with: python3 simple_mock.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class SimpleMockHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        if self.path == '/api/auth/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            username = data.get('username')
            password = data.get('password')

            # Accept any credentials for testing
            if username and password:
                role = "doctor" if "doctor" in username.lower() or "provider" in username.lower() else "patient"

                self._set_headers(200)
                response = {
                    "access_token": f"mock-token-{username}",
                    "token_type": "bearer",
                    "user": {
                        "id": f"user-{username}",
                        "email": f"{username}@example.com",
                        "username": username,
                        "full_name": f"Test {username.capitalize()}",
                        "role": role
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({"detail": "Invalid credentials"}).encode())

        elif self.path == '/api/auth/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            self._set_headers(201)
            response = {
                "access_token": f"mock-token-{data.get('username')}",
                "token_type": "bearer",
                "user": {
                    "id": f"user-{data.get('username')}",
                    "email": data.get('email'),
                    "username": data.get('username'),
                    "full_name": data.get('full_name'),
                    "role": data.get('role', 'patient')
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Not found"}).encode())

    def do_GET(self):
        if self.path == '/api/auth/me':
            auth_header = self.headers.get('Authorization', '')
            if 'mock-token' in auth_header:
                username = auth_header.split('-')[-1] if '-' in auth_header else 'testuser'
                role = "doctor" if "doctor" in username.lower() or "provider" in username.lower() else "patient"

                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "id": f"user-{username}",
                    "email": f"{username}@example.com",
                    "username": username,
                    "full_name": f"Test {username.capitalize()}",
                    "role": role
                }).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({"detail": "Not authenticated"}).encode())

        elif self.path == '/health':
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy"}).encode())

        elif self.path.startswith('/api/appointments/next'):
            self._set_headers(200)
            response = {
                "id": "appt-123",
                "patient_id": "patient-456",
                "scheduled_start": datetime.utcnow().isoformat() + "Z",
                "chief_complaint": "Annual checkup",
                "is_today": True,
                "previsit_completed": True,
                "patient": {
                    "name": "John Doe",
                    "mrn": "MRN-123456"
                }
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/api/appoint-ready/patient-context/'):
            self._set_headers(200)
            response = {
                "patient_id": "patient-456",
                "demographics": {
                    "name": "John Doe",
                    "age": 45,
                    "gender": "male",
                    "mrn": "MRN-123456"
                },
                "active_medications": [
                    {"name": "Lisinopril 10mg", "dosage": "10mg", "frequency": "Once daily"},
                    {"name": "Metformin 500mg", "dosage": "500mg", "frequency": "Twice daily"}
                ],
                "active_conditions": [
                    {"name": "Hypertension", "onset_date": "2020-01-15"},
                    {"name": "Type 2 Diabetes", "onset_date": "2019-06-20"}
                ],
                "allergies": [
                    {"allergen": "Penicillin", "reaction": "Rash", "severity": "moderate"}
                ],
                "recent_vitals": {
                    "blood_pressure": "130/85 mmHg",
                    "heart_rate": "72 bpm",
                    "temperature": "98.6°F",
                    "weight": "180 lbs",
                    "recorded_date": "2025-11-15"
                },
                "last_visit_date": "2025-10-01",
                "upcoming_appointment": {
                    "date": datetime.utcnow().isoformat() + "Z",
                    "reason": "Annual checkup"
                }
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/api/appoint-ready/test-results/'):
            self._set_headers(200)
            response = {
                "patient_id": "patient-456",
                "test_results": [
                    {
                        "test_name": "Hemoglobin A1C",
                        "value": "7.2%",
                        "reference_range": "4.0-5.6%",
                        "status": "abnormal_high",
                        "date": "2025-11-10",
                        "category": "diabetes_monitoring",
                        "trend": "stable"
                    },
                    {
                        "test_name": "LDL Cholesterol",
                        "value": "145 mg/dL",
                        "reference_range": "<100 mg/dL",
                        "status": "abnormal_high",
                        "date": "2025-11-10",
                        "category": "lipid_panel",
                        "trend": "up"
                    },
                    {
                        "test_name": "Creatinine",
                        "value": "1.1 mg/dL",
                        "reference_range": "0.7-1.3 mg/dL",
                        "status": "normal",
                        "date": "2025-11-10",
                        "category": "renal_function",
                        "trend": "stable"
                    }
                ],
                "summary": {
                    "total_results": 3,
                    "abnormal_count": 2,
                    "critical_count": 0
                }
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/api/appoint-ready/medication-review/'):
            self._set_headers(200)
            response = {
                "patient_id": "patient-456",
                "medications": [
                    {
                        "name": "Lisinopril",
                        "dosage": "10mg",
                        "frequency": "Once daily",
                        "indication": "Hypertension",
                        "start_date": "2020-01-15"
                    },
                    {
                        "name": "Metformin",
                        "dosage": "500mg",
                        "frequency": "Twice daily",
                        "indication": "Type 2 Diabetes",
                        "start_date": "2019-06-20"
                    }
                ],
                "interactions": [
                    {
                        "drug1": "Lisinopril",
                        "drug2": "Metformin",
                        "severity": "mild",
                        "description": "May increase risk of hypoglycemia",
                        "clinical_effect": "Both medications can lower blood sugar when used together",
                        "recommendation": "Monitor blood glucose levels regularly"
                    }
                ],
                "allergies": [
                    {
                        "allergen": "Penicillin",
                        "reaction": "Rash",
                        "severity": "moderate"
                    }
                ],
                "summary": {
                    "total_medications": 2,
                    "interaction_count": 1,
                    "severe_interactions": 0
                }
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/api/appoint-ready/risk-stratification/'):
            self._set_headers(200)
            response = {
                "patient_id": "patient-456",
                "overall_risk_score": 65,
                "risk_level": "moderate",
                "risk_factors": [
                    {
                        "category": "cardiovascular",
                        "score": 70,
                        "factors": ["Hypertension", "Elevated LDL"],
                        "recommendations": ["Lifestyle modifications", "Consider statin therapy"]
                    },
                    {
                        "category": "metabolic",
                        "score": 75,
                        "factors": ["Type 2 Diabetes", "Elevated A1C"],
                        "recommendations": ["Diabetes management", "Dietary counseling"]
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/api/appoint-ready/care-gaps/'):
            self._set_headers(200)
            response = {
                "patient_id": "patient-456",
                "care_gaps": [
                    {
                        "gap_type": "preventive",
                        "description": "Annual flu vaccine",
                        "due_date": "2025-11-30",
                        "priority": "high",
                        "status": "overdue"
                    },
                    {
                        "gap_type": "screening",
                        "description": "Diabetic retinopathy screening",
                        "due_date": "2025-12-15",
                        "priority": "medium",
                        "status": "upcoming"
                    }
                ],
                "summary": {
                    "total_gaps": 2,
                    "overdue": 1,
                    "upcoming": 1
                }
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Not found"}).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleMockHandler)
    print(f'\n✅ Mock API Server Running on port {port}')
    print(f'=' * 60)
    print(f'\n📍 API URL: http://localhost:{port}')
    print(f'📍 Frontend: http://localhost:3000')
    print(f'\n🔑 Login Credentials (any work, but try these):')
    print(f'   Provider: username=doctor, password=anything')
    print(f'   Provider: username=provider, password=anything')
    print(f'   Patient:  username=patient, password=anything')
    print(f'\n💡 All credentials are accepted for testing')
    print(f'=' * 60)
    print(f'\nServer logs:\n')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
