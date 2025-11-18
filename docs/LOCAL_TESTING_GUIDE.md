# Local Development & Testing Guide

This guide provides step-by-step instructions for setting up and testing the Healthcare AI Application locally.

## 1. Prerequisites

Ensure the following tools are installed and running on your system.

| Tool | Recommended Version | Verification Command |
| :--- | :--- | :--- |
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.5+ | `docker-compose --version` |
| Node.js | 18.x or 20.x | `node --version` |
| Python | 3.10+ | `python --version` or `python3 --version` |
| Git | 2.30+ | `git --version` |

## 2. Repository Setup & Configuration

First, clone the repository and configure the necessary environment variables.

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd azure-healthcare-app
    ```

2.  **Configure Backend Environment:**
    The backend `.env` file should already exist. If not, create one:
    ```bash
    cp backend/.env.example backend/.env
    ```
    Review `backend/.env` and ensure the variables are suitable for local development. The defaults are typically pre-configured for the Docker setup.

3.  **Configure Frontend Environment:**
    The frontend `.env.local` file should already exist. Verify it:
    ```bash
    cat frontend/.env.local
    ```
    Ensure `NEXT_PUBLIC_API_BASE_URL` points to your local FastAPI backend:
    ```ini
    # frontend/.env.local
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
    ```

## 3. Starting All Services

The project uses Docker Compose to orchestrate all backend services.

### Backend Services (Docker Compose)

1.  **Start Backend Services:**
    From the `/backend/docker` directory:
    ```bash
    cd backend/docker
    docker-compose up -d
    ```

    This starts:
    - PostgreSQL database (port 5432)
    - Redis cache (port 6379)
    - FHIR server (port 8080)
    - Azurite storage emulator (port 10000)
    - FastAPI backend (port 8000)

2.  **Check Backend Logs:**
    ```bash
    docker-compose logs -f api
    ```

### Frontend (Next.js Development Server)

1.  **Install Dependencies:**
    From the `/frontend` directory:
    ```bash
    cd ../../frontend  # From backend/docker
    npm install
    ```

2.  **Start Frontend:**
    ```bash
    npm run dev
    ```

    The frontend will start on `http://localhost:3000` (or 3001/3002 if 3000 is occupied)

## 4. Verifying Services

### Check Backend Services

1.  **Check Container Status:**
    ```bash
    cd backend/docker
    docker-compose ps
    ```
    All services should show as `Up` or `running`.

2.  **Test Backend API:**
    ```bash
    curl http://localhost:8000/health
    ```
    Expected response:
    ```json
    {
      "status": "healthy",
      "service": "AI Healthcare API",
      "version": "1.0.0"
    }
    ```

3.  **Access API Documentation:**
    Open `http://localhost:8000/docs` in your browser to see the interactive Swagger UI.

### Check Frontend

Open your browser to the frontend URL (check the terminal output, usually `http://localhost:3002`)

## 5. Feature Testing Walkthrough

### 5.1. Authentication Flow

1.  **Patient Login:**
    - Navigate to `http://localhost:3002/login`
    - Enter credentials:
      - **Username**: `newpatient`
      - **Password**: `SecurePass123!`
    - **Expected Result**: Successful login and redirection to `/demo` page

2.  **Doctor Login:**
    - Log out (click logout button in header)
    - Navigate to `http://localhost:3002/login`
    - Enter credentials:
      - **Username**: `drjane2`
      - **Password**: `SecurePass123!`
    - **Expected Result**: Successful login and redirection to `/demo` page with Appoint-Ready access

### 5.2. PreVisit.ai Features (Available to All Users)

**Test Symptom Checker:**

1. Log in as `newpatient`
2. Go to the "Symptom Checker" tab
3. Add symptoms:
   - Click "Add Symptom"
   - Enter: Name: "Headache", Severity: "moderate", Duration: "2 days", Description: "Frontal headache"
   - Click "Add Symptom" button
4. Click "Analyze Symptoms"
5. **Expected Result**:
   - AI analysis showing urgency level
   - Triage level
   - Possible conditions
   - Recommendations
   - Red flags (if any)

**Test Medical History Form:**

1. Click the "Medical History" tab
2. Step through the 6-step form:
   - **Step 1**: Add allergies (e.g., "Penicillin", "Peanuts")
   - **Step 2**: Add chronic conditions (e.g., "Diabetes Type 2")
   - **Step 3**: Add medications (e.g., "Metformin 500mg twice daily")
   - **Step 4**: Add past surgeries (e.g., "Appendectomy (2015)")
   - **Step 5**: Add family history (e.g., "Father: Heart disease (age 60)")
   - **Step 6**: Add additional notes
3. Click "Complete" on the final step
4. **Expected Result**: Success toast notification, data saved to database

### 5.3. Appoint-Ready Features (Doctor Role Only)

1.  **Log in as `drjane2`**
2.  **Patient Context:**
    - Click the "Appoint-Ready" tab
    - **Expected Result**: View patient demographics, contact info, PreVisit data, alerts
3.  **Risk Assessment:**
    - Scroll down to the Risk Stratification section
    - **Expected Result**: See risk scores with visual bars, risk factors, recommendations
4.  **Care Gaps:**
    - Scroll down to the Care Gaps section
    - **Expected Result**: See identified care gaps (screenings, vaccinations) with priority badges

### 5.4. Test Role-Based Access Control

1. Log in as `newpatient`
2. Try to access the "Appoint-Ready" tab
3. **Expected Result**: Tab is disabled/grayed out for patients

## 6. Testing via API (Optional)

You can also test the backend directly using curl:

```bash
# Login as patient
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"newpatient","password":"SecurePass123!"}'

# Save the access_token from the response, then use it:
TOKEN="<your-access-token>"

# Analyze symptoms
curl -X POST http://localhost:8000/api/previsit/analyze-symptoms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symptoms": [
      {
        "name": "headache",
        "severity": "moderate",
        "duration": "2 days",
        "description": "Frontal headache"
      }
    ]
  }'
```

## 7. Troubleshooting Common Issues

### Port Conflicts

**Issue**: Service fails with "port is already allocated"

**Solution**:
```bash
# Find what's using the port
lsof -i :8000  # or :3000, :5432, etc.

# Kill the process or change the port in docker-compose.yml
```

### Backend Cannot Connect to Database

**Issue**: Backend logs show connection errors

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check environment variables match
cat backend/.env | grep POSTGRES
docker-compose config | grep POSTGRES
```

### Frontend Shows CORS/API Errors

**Issue**: Browser console shows CORS errors or 404s

**Solution**:
1. Check `frontend/.env.local` has correct API URL
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check browser console for the exact error

### Database Migration Issues

**Issue**: Backend shows "table does not exist" errors

**Solution**:
```bash
# Access the backend container
docker-compose exec api bash

# Run migrations
alembic upgrade head
```

### Clean Slate Reset

**Solution**:
```bash
cd backend/docker
docker-compose down -v  # Remove volumes to reset database
docker-compose up -d --build  # Rebuild and restart
```

## 8. Stopping Services

### Stop Frontend

Press `Ctrl+C` in the terminal running `npm run dev`

### Stop Backend Services

```bash
cd backend/docker
docker-compose down
```

### Stop and Remove All Data (Clean Reset)

```bash
docker-compose down -v
```

## 9. Development Workflow

1. **Make Code Changes**
   - Backend: Edit files in `/backend/src/`
   - Frontend: Edit files in `/frontend/`

2. **See Changes**
   - Backend: Restart the API container: `docker-compose restart api`
   - Frontend: Hot reload is automatic (Next.js dev server)

3. **Test Changes**
   - Use the browser or curl commands to test
   - Check logs: `docker-compose logs -f api`

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push
   ```

## 10. Quick Reference

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Patient | newpatient | SecurePass123! |
| Doctor | drjane2 | SecurePass123! |

### Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3002 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| FHIR Server | http://localhost:8080 |

### Useful Commands

```bash
# View all container logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Access container shell
docker-compose exec api bash

# Check service status
docker-compose ps

# Stop everything
docker-compose down

# Nuclear option (reset everything)
docker-compose down -v && docker-compose up -d --build
```

---

**Ready to Test!** Start with section 3 to get everything running, then follow section 5 for feature testing.
