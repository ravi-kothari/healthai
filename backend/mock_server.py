"""
Quick mock server for testing frontend login
Run with: python3 mock_server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import jwt

import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-local-development-secret-change-in-production")

# Mock users database
USERS = {
    "doctor@example.com": {
        "id": "doctor-123",
        "email": "doctor@example.com",
        "username": "doctor",
        "password": "password123",  # In real app, this would be hashed
        "full_name": "Dr. John Smith",
        "role": "doctor"
    },
    "provider@example.com": {
        "id": "provider-456",
        "email": "provider@example.com",
        "username": "provider",
        "password": "password123",
        "full_name": "Dr. Jane Doe",
        "role": "doctor"
    },
    "patient@example.com": {
        "id": "patient-789",
        "email": "patient@example.com",
        "username": "patient",
        "password": "password123",
        "full_name": "John Patient",
        "role": "patient"
    }
}

class MockAPIHandler(BaseHTTPRequestHandler):

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
            self.handle_login()
        elif self.path == '/api/auth/register':
            self.handle_register()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Not found"}).encode())

    def do_GET(self):
        if self.path == '/api/auth/me':
            self.handle_me()
        elif self.path == '/health':
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        elif self.path.startswith('/api/appointments/next'):
            self.handle_next_appointment()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Not found"}).encode())

    def handle_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        username = data.get('username')
        password = data.get('password')

        # Find user
        user = None
        for email, user_data in USERS.items():
            if user_data['username'] == username or user_data['email'] == username:
                if user_data['password'] == password:
                    user = user_data
                    break

        if user:
            # Create token
            token = jwt.encode({
                'sub': user['id'],
                'email': user['email'],
                'role': user['role'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')

            self._set_headers(200)
            response = {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "username": user['username'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(401)
            self.wfile.write(json.dumps({"detail": "Invalid credentials"}).encode())

    def handle_register(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        # For mock, just return success
        user_id = f"user-{len(USERS) + 1}"
        token = jwt.encode({
            'sub': user_id,
            'email': data.get('email'),
            'role': data.get('role', 'patient'),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')

        self._set_headers(201)
        response = {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": data.get('email'),
                "username": data.get('username'),
                "full_name": data.get('full_name'),
                "role": data.get('role', 'patient')
            }
        }
        self.wfile.write(json.dumps(response).encode())

    def handle_me(self):
        # Extract token from Authorization header
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self._set_headers(401)
            self.wfile.write(json.dumps({"detail": "Not authenticated"}).encode())
            return

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            # Find user by ID
            user_id = payload.get('sub')
            user = None
            for user_data in USERS.values():
                if user_data['id'] == user_id:
                    user = user_data
                    break

            if user:
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "id": user['id'],
                    "email": user['email'],
                    "username": user['username'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": "User not found"}).encode())
        except jwt.ExpiredSignatureError:
            self._set_headers(401)
            self.wfile.write(json.dumps({"detail": "Token expired"}).encode())
        except jwt.InvalidTokenError:
            self._set_headers(401)
            self.wfile.write(json.dumps({"detail": "Invalid token"}).encode())

    def handle_next_appointment(self):
        self._set_headers(200)
        # Return mock appointment data
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

    def log_message(self, format, *args):
        # Custom logging
        print(f"{self.address_string()} - [{self.log_date_time_string()}] {format % args}")

def run(server_class=HTTPServer, handler_class=MockAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting mock API server on port {port}...')
    print(f'\nTest credentials:')
    print(f'  Provider: username=doctor, password=password123')
    print(f'  Patient:  username=patient, password=password123')
    print(f'\nAPI available at: http://localhost:{port}')
    print(f'Frontend should connect automatically\n')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
