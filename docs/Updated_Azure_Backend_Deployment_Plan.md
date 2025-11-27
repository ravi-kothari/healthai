# Azure Backend Deployment Plan - AI Healthcare App
## Enhanced with PreVisit.ai & Appoint-Ready Features

## Project Overview
This document provides comprehensive instructions for deploying the backend of the AI Healthcare App with PreVisit.ai and Appoint-Ready functionality. The deployment follows a **local-first approach** using Docker for testing before Azure cloud deployment.

## Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐         ┌────────────────┐              │
│  │  API Gateway   │         │  Azure Func    │              │
│  │  (FastAPI)     │◄───────►│  (Python)      │              │
│  └────────┬───────┘         └────────┬───────┘              │
│           │                          │                       │
│           ├──────────────┬───────────┴───────────┐           │
│           │              │                       │           │
│    ┌──────▼──────┐ ┌────▼────────┐      ┌──────▼──────┐    │
│    │  PreVisit   │ │Appoint-Ready│      │    FHIR     │    │
│    │  Services   │ │  Services   │      │  Integration│    │
│    ├─────────────┤ ├─────────────┤      ├─────────────┤    │
│    │• Symptom AI │ │• Context Gen│      │• R4 Support │    │
│    │• Triage     │ │• Risk Calc  │      │• Resources  │    │
│    │• Forms      │ │• Gap Detect │      │• Validation │    │
│    │• Insurance  │ │• Summaries  │      │• Search     │    │
│    └─────────────┘ └─────────────┘      └─────────────┘    │
│           │              │                       │           │
│           └──────────────┼───────────────────────┘           │
│                          │                                   │
│              ┌───────────▼────────────┐                      │
│              │    Data Layer          │                      │
│              ├────────────────────────┤                      │
│              │ PostgreSQL             │                      │
│              │ Redis Cache            │                      │
│              │ Blob Storage           │                      │
│              │ Azure OpenAI           │                      │
│              │ Azure Speech           │                      │
│              └────────────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
azure-healthcare-backend/
├── docker/
│   ├── Dockerfile.api              # API container
│   ├── Dockerfile.functions        # Azure Functions container
│   ├── docker-compose.yml          # Local development stack
│   ├── docker-compose.azure.yml    # Azure testing configuration
│   └── init-scripts/              # Database initialization
│       ├── 01-schema.sql
│       ├── 02-fhir-tables.sql
│       └── 03-test-data.sql
├── src/
│   ├── api/                        # FastAPI application
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── patients.py
│   │   │   ├── appointments.py
│   │   │   ├── previsit.py        # PreVisit.ai routes
│   │   │   ├── appoint_ready.py   # Appoint-Ready routes
│   │   │   ├── transcription.py
│   │   │   └── fhir.py            # FHIR routes
│   │   ├── services/
│   │   │   ├── previsit/
│   │   │   │   ├── symptom_analyzer.py
│   │   │   │   ├── triage_engine.py
│   │   │   │   ├── questionnaire_generator.py
│   │   │   │   ├── insurance_verifier.py
│   │   │   │   └── checklist_builder.py
│   │   │   ├── appoint_ready/
│   │   │   │   ├── context_builder.py
│   │   │   │   ├── summary_generator.py
│   │   │   │   ├── risk_calculator.py
│   │   │   │   ├── care_gap_detector.py
│   │   │   │   └── decision_support.py
│   │   │   ├── fhir/
│   │   │   │   ├── client.py
│   │   │   │   ├── validator.py
│   │   │   │   ├── resource_handler.py
│   │   │   │   └── search_builder.py
│   │   │   ├── ai/
│   │   │   │   ├── openai_service.py
│   │   │   │   ├── speech_service.py
│   │   │   │   └── embeddings.py
│   │   │   └── auth/
│   │   │       ├── azure_ad.py
│   │   │       └── rbac.py
│   │   ├── models/
│   │   │   ├── patient.py
│   │   │   ├── appointment.py
│   │   │   ├── previsit.py
│   │   │   ├── appoint_ready.py
│   │   │   └── fhir.py
│   │   ├── schemas/
│   │   │   ├── previsit_schemas.py
│   │   │   ├── appoint_ready_schemas.py
│   │   │   └── fhir_schemas.py
│   │   └── middleware/
│   │       ├── audit_logging.py
│   │       ├── hipaa_compliance.py
│   │       └── rate_limiting.py
│   ├── functions/                  # Azure Functions
│   │   ├── audio_processor/
│   │   │   ├── __init__.py
│   │   │   └── function_app.py
│   │   ├── note_generator/
│   │   │   ├── __init__.py
│   │   │   └── function_app.py
│   │   ├── previsit_orchestrator/  # New: PreVisit orchestration
│   │   │   ├── __init__.py
│   │   │   └── function_app.py
│   │   ├── context_builder/        # New: Appoint-Ready context
│   │   │   ├── __init__.py
│   │   │   └── function_app.py
│   │   └── shared/
│   │       ├── utils.py
│   │       └── constants.py
│   └── workers/                    # Background workers
│       ├── fhir_sync_worker.py
│       ├── care_gap_monitor.py
│       └── risk_assessment_worker.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── terraform/                      # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── backend.tf
│   ├── functions.tf
│   └── monitoring.tf
└── docs/
    ├── api-docs.md
    ├── previsit-integration.md
    ├── appoint-ready-integration.md
    └── fhir-implementation.md
```

## Phase 0: Local Docker Development (Weeks 1-4)

### Step 0.1: Docker Environment Setup

**File to Create**: `docker/Dockerfile.api`
```dockerfile
# Multi-stage build for FastAPI application
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Development stage
FROM base as development

# Install development dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY src/ ./src/

# Enable hot reload
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Install only production dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

ENV PYTHONPATH=/app/src
EXPOSE 8000

CMD ["gunicorn", "api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**File to Create**: `docker/Dockerfile.functions`
```dockerfile
# Azure Functions Python Docker image
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-functions.txt /
RUN pip install -r /requirements-functions.txt

# Copy function code
COPY src/functions /home/site/wwwroot

# Set working directory
WORKDIR /home/site/wwwroot
```

**File to Create**: `docker/docker-compose.yml`
```yaml
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile.api
      target: development
    container_name: healthcare-api
    ports:
      - "8000:8000"
    volumes:
      - ../src:/app/src
      - /app/src/__pycache__
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/healthcare
      - REDIS_URL=redis://redis:6379
      - FHIR_SERVER_URL=http://fhir-server:8080/fhir
      - AZURE_OPENAI_ENDPOINT=http://mock-openai:8081
      - AZURE_OPENAI_API_KEY=mock-key
      - AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;
      - JWT_SECRET_KEY=dev-secret-key-change-in-production
      - ENABLE_PREVISIT=true
      - ENABLE_APPOINT_READY=true
      - LOG_LEVEL=DEBUG
    networks:
      - healthcare-network
    depends_on:
      - postgres
      - redis
      - fhir-server
      - azurite
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

  functions:
    build:
      context: ..
      dockerfile: docker/Dockerfile.functions
    container_name: healthcare-functions
    ports:
      - "7071:80"
    volumes:
      - ../src/functions:/home/site/wwwroot
    environment:
      - AzureWebJobsStorage=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;
      - FUNCTIONS_WORKER_RUNTIME=python
      - AZURE_OPENAI_ENDPOINT=http://mock-openai:8081
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/healthcare
    networks:
      - healthcare-network
    depends_on:
      - azurite
      - postgres

  postgres:
    image: postgres:15-alpine
    container_name: healthcare-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=healthcare
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - healthcare-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: healthcare-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - healthcare-network
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  fhir-server:
    image: hapiproject/hapi:latest
    container_name: healthcare-fhir
    ports:
      - "8080:8080"
    environment:
      - spring.datasource.url=jdbc:postgresql://postgres:5432/fhir
      - spring.datasource.username=postgres
      - spring.datasource.password=postgres
      - spring.datasource.driverClassName=org.postgresql.Driver
      - spring.jpa.properties.hibernate.dialect=ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgres94Dialect
      - hapi.fhir.version=R4
      - hapi.fhir.fhirpath_interceptor_enabled=true
    volumes:
      - fhir-data:/data/hapi
    networks:
      - healthcare-network
    depends_on:
      postgres:
        condition: service_healthy

  azurite:
    image: mcr.microsoft.com/azure-storage/azurite
    container_name: healthcare-azurite
    ports:
      - "10000:10000"  # Blob service
      - "10001:10001"  # Queue service
      - "10002:10002"  # Table service
    volumes:
      - azurite-data:/data
    networks:
      - healthcare-network
    command: azurite --blobHost 0.0.0.0 --queueHost 0.0.0.0 --tableHost 0.0.0.0

  mock-openai:
    image: ghcr.io/azure-samples/openai-test-server:latest
    container_name: mock-azure-openai
    ports:
      - "8081:8080"
    environment:
      - OPENAI_API_KEY=mock-key-for-local-dev
    networks:
      - healthcare-network

  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile.api
      target: development
    container_name: healthcare-worker
    volumes:
      - ../src:/app/src
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/healthcare
      - REDIS_URL=redis://redis:6379
      - FHIR_SERVER_URL=http://fhir-server:8080/fhir
    networks:
      - healthcare-network
    depends_on:
      - postgres
      - redis
      - fhir-server
    command: python -m workers.care_gap_monitor

networks:
  healthcare-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  fhir-data:
  azurite-data:
```

**File to Create**: `.env.local`
```bash
# Local Development Environment Variables

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthcare
REDIS_URL=redis://localhost:6379

# FHIR Server
FHIR_SERVER_URL=http://localhost:8080/fhir
FHIR_SERVER_USERNAME=
FHIR_SERVER_PASSWORD=

# Azure Services (Mock for local dev)
AZURE_OPENAI_ENDPOINT=http://localhost:8081
AZURE_OPENAI_API_KEY=mock-key-for-local-dev
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_SPEECH_KEY=mock-speech-key
AZURE_SPEECH_REGION=eastus

# Azure Storage (Azurite)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1;

# Authentication
JWT_SECRET_KEY=dev-secret-key-please-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
ENABLE_PREVISIT=true
ENABLE_APPOINT_READY=true
ENABLE_FHIR_VALIDATION=true
ENABLE_AUDIT_LOGGING=true

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### Step 0.2: PreVisit.ai Services Implementation

**File to Create**: `src/api/services/previsit/symptom_analyzer.py`
```python
from typing import List, Dict, Optional
from datetime import datetime
from openai import AzureOpenAI
from pydantic import BaseModel
import json

class Symptom(BaseModel):
    name: str
    severity: str  # 'mild', 'moderate', 'severe'
    duration: str
    onset: datetime
    description: str
    location: Optional[str] = None
    aggravating_factors: Optional[List[str]] = None
    relieving_factors: Optional[List[str]] = None

class SymptomAnalysis(BaseModel):
    urgency: str  # 'low', 'moderate', 'high', 'emergency'
    triage_level: int  # 1-5
    possible_conditions: List[Dict[str, any]]
    recommendations: List[str]
    requires_immediate_attention: bool
    suggested_specialties: List[str]
    differential_diagnosis: List[Dict[str, str]]
    red_flags: List[str]
    follow_up_questions: List[str]

class SymptomAnalyzer:
    def __init__(self, azure_openai_client: AzureOpenAI):
        self.client = azure_openai_client
        
    async def analyze_symptoms(
        self,
        symptoms: List[Symptom],
        patient_age: int,
        patient_gender: str,
        medical_history: Optional[List[str]] = None
    ) -> SymptomAnalysis:
        """
        Analyze patient symptoms using Azure OpenAI with medical knowledge.
        """
        prompt = self._build_symptom_prompt(
            symptoms, patient_age, patient_gender, medical_history
        )
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert medical triage AI assistant.
                    Analyze symptoms and provide urgency assessment, possible conditions,
                    and recommendations. Always prioritize patient safety and err on the
                    side of caution. Use evidence-based medical knowledge.
                    
                    Provide your response in JSON format with these fields:
                    - urgency: low/moderate/high/emergency
                    - triage_level: 1-5 (1=routine, 5=life-threatening)
                    - possible_conditions: array of {name, probability, reasoning}
                    - recommendations: array of specific actions
                    - requires_immediate_attention: boolean
                    - suggested_specialties: array of medical specialties
                    - differential_diagnosis: array of {condition, likelihood, key_features}
                    - red_flags: array of concerning symptoms
                    - follow_up_questions: array of questions to gather more info
                    """
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        analysis_data = json.loads(response.choices[0].message.content)
        return SymptomAnalysis(**analysis_data)
    
    def _build_symptom_prompt(
        self,
        symptoms: List[Symptom],
        patient_age: int,
        patient_gender: str,
        medical_history: Optional[List[str]]
    ) -> str:
        """Build detailed prompt for symptom analysis."""
        
        symptom_descriptions = []
        for symptom in symptoms:
            desc = f"- {symptom.name} ({symptom.severity} severity)"
            desc += f"\n  Duration: {symptom.duration}"
            desc += f"\n  Onset: {symptom.onset.strftime('%Y-%m-%d %H:%M')}"
            desc += f"\n  Description: {symptom.description}"
            
            if symptom.location:
                desc += f"\n  Location: {symptom.location}"
            if symptom.aggravating_factors:
                desc += f"\n  Aggravated by: {', '.join(symptom.aggravating_factors)}"
            if symptom.relieving_factors:
                desc += f"\n  Relieved by: {', '.join(symptom.relieving_factors)}"
            
            symptom_descriptions.append(desc)
        
        prompt = f"""Patient Information:
Age: {patient_age} years
Gender: {patient_gender}
"""
        
        if medical_history:
            prompt += f"Medical History: {', '.join(medical_history)}\n"
        
        prompt += f"""
Presenting Symptoms:
{chr(10).join(symptom_descriptions)}

Please provide a comprehensive analysis including triage assessment,
differential diagnosis, recommendations, and any red flags that require
immediate medical attention.
"""
        return prompt

    async def generate_questionnaire(
        self,
        chief_complaint: str,
        initial_symptoms: List[Symptom]
    ) -> List[Dict]:
        """
        Generate dynamic follow-up questionnaire based on chief complaint.
        """
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """Generate a medical questionnaire to gather comprehensive
                    information about the patient's condition. Create relevant, specific
                    follow-up questions based on the chief complaint and symptoms.
                    
                    Format as JSON array of questions with:
                    - id: unique identifier
                    - text: question text
                    - type: text/select/multiselect/number/date/boolean
                    - options: array (if type is select/multiselect)
                    - required: boolean
                    - conditional_on: id of question this depends on (optional)
                    - medical_significance: why this question matters
                    """
                },
                {
                    "role": "user",
                    "content": f"""Chief Complaint: {chief_complaint}
                    
Initial Symptoms: {', '.join([s.name for s in initial_symptoms])}

Generate 8-12 relevant follow-up questions to gather comprehensive information."""
                }
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result["questions"]

class TriageEngine:
    """Implements clinical triage protocols."""
    
    TRIAGE_CATEGORIES = {
        1: {
            "name": "Emergent",
            "description": "Life-threatening",
            "max_wait_time": "0 minutes",
            "action": "Immediate medical attention - call 911"
        },
        2: {
            "name": "Urgent",
            "description": "High risk",
            "max_wait_time": "15 minutes",
            "action": "Urgent care or ER visit today"
        },
        3: {
            "name": "Semi-urgent",
            "description": "Moderate risk",
            "max_wait_time": "30-60 minutes",
            "action": "See provider within 24 hours"
        },
        4: {
            "name": "Non-urgent",
            "description": "Low risk",
            "max_wait_time": "1-2 hours",
            "action": "Schedule appointment within 2-3 days"
        },
        5: {
            "name": "Routine",
            "description": "Minimal risk",
            "max_wait_time": "Can be scheduled",
            "action": "Routine appointment appropriate"
        }
    }
    
    # Red flag symptoms that require immediate attention
    RED_FLAGS = {
        "chest_pain": ["chest pain", "chest pressure", "chest tightness"],
        "stroke": ["facial drooping", "arm weakness", "speech difficulty"],
        "severe_bleeding": ["uncontrolled bleeding", "severe bleeding"],
        "breathing": ["difficulty breathing", "shortness of breath", "cannot breathe"],
        "consciousness": ["loss of consciousness", "unresponsive", "confusion"],
        "severe_pain": ["severe pain", "worst pain ever", "10/10 pain"],
        "poisoning": ["poisoning", "overdose", "toxic ingestion"],
        "trauma": ["severe injury", "head trauma", "major trauma"]
    }
    
    def assess_triage_level(
        self,
        symptoms: List[Symptom],
        vital_signs: Optional[Dict] = None
    ) -> Dict:
        """Assess triage level based on symptoms and vital signs."""
        
        # Check for red flags
        red_flags_present = self._check_red_flags(symptoms)
        
        # If red flags present, immediately escalate
        if red_flags_present:
            return {
                "level": 1,
                "category": self.TRIAGE_CATEGORIES[1],
                "red_flags": red_flags_present,
                "immediate_action_required": True
            }
        
        # Assess based on severity
        severity_score = self._calculate_severity_score(symptoms)
        
        # Check vital signs if available
        if vital_signs:
            vital_score = self._assess_vital_signs(vital_signs)
            severity_score = max(severity_score, vital_score)
        
        # Determine triage level
        if severity_score >= 9:
            level = 1
        elif severity_score >= 7:
            level = 2
        elif severity_score >= 5:
            level = 3
        elif severity_score >= 3:
            level = 4
        else:
            level = 5
        
        return {
            "level": level,
            "category": self.TRIAGE_CATEGORIES[level],
            "severity_score": severity_score,
            "immediate_action_required": level <= 2
        }
    
    def _check_red_flags(self, symptoms: List[Symptom]) -> List[str]:
        """Check for red flag symptoms."""
        red_flags_found = []
        
        for symptom in symptoms:
            symptom_text = f"{symptom.name} {symptom.description}".lower()
            
            for flag_category, flag_keywords in self.RED_FLAGS.items():
                if any(keyword in symptom_text for keyword in flag_keywords):
                    red_flags_found.append(flag_category.replace('_', ' ').title())
        
        return list(set(red_flags_found))
    
    def _calculate_severity_score(self, symptoms: List[Symptom]) -> int:
        """Calculate severity score based on symptoms."""
        severity_map = {"mild": 1, "moderate": 3, "severe": 5}
        
        scores = []
        for symptom in symptoms:
            base_score = severity_map.get(symptom.severity.lower(), 2)
            
            # Adjust for duration
            if "sudden" in symptom.description.lower() or "acute" in symptom.description.lower():
                base_score += 2
            
            # Adjust for progression
            if "worsening" in symptom.description.lower() or "getting worse" in symptom.description.lower():
                base_score += 1
            
            scores.append(base_score)
        
        # Return highest score plus average of others
        if scores:
            return max(scores) + (sum(scores) - max(scores)) // len(scores)
        return 0
    
    def _assess_vital_signs(self, vital_signs: Dict) -> int:
        """Assess severity based on vital signs."""
        score = 0
        
        # Temperature
        temp = vital_signs.get("temperature_f")
        if temp:
            if temp > 103 or temp < 95:
                score = max(score, 8)
            elif temp > 101 or temp < 96:
                score = max(score, 5)
        
        # Heart rate
        hr = vital_signs.get("heart_rate")
        if hr:
            if hr > 120 or hr < 50:
                score = max(score, 7)
            elif hr > 100 or hr < 60:
                score = max(score, 4)
        
        # Blood pressure
        systolic = vital_signs.get("bp_systolic")
        if systolic:
            if systolic > 180 or systolic < 90:
                score = max(score, 8)
            elif systolic > 160 or systolic < 100:
                score = max(score, 5)
        
        # Oxygen saturation
        spo2 = vital_signs.get("oxygen_saturation")
        if spo2 and spo2 < 95:
            if spo2 < 90:
                score = max(score, 9)
            else:
                score = max(score, 6)
        
        return score
```

### Step 0.3: Appoint-Ready Services Implementation

**File to Create**: `src/api/services/appoint_ready/context_builder.py`
```python
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio
from fhirclient import client
from openai import AzureOpenAI

class PatientContext(BaseModel):
    patient_id: str
    appointment_id: str
    demographics: Dict
    active_medications: List[Dict]
    chronic_conditions: List[Dict]
    recent_visits: List[Dict]
    allergies: List[Dict]
    recent_labs: List[Dict]
    care_gaps: List[Dict]
    risk_assessment: Dict
    visit_preparation: Dict
    clinical_summary: str

class AppointReadyContextBuilder:
    """Build comprehensive patient context for appointment preparation."""
    
    def __init__(
        self,
        fhir_client: client.FHIRClient,
        openai_client: AzureOpenAI,
        db_session
    ):
        self.fhir = fhir_client
        self.openai = openai_client
        self.db = db_session
    
    async def build_context(
        self,
        patient_id: str,
        appointment_id: str
    ) -> PatientContext:
        """
        Build complete patient context by aggregating data from multiple sources.
        """
        
        # Fetch data in parallel for performance
        tasks = [
            self._fetch_demographics(patient_id),
            self._fetch_medications(patient_id),
            self._fetch_conditions(patient_id),
            self._fetch_recent_visits(patient_id),
            self._fetch_allergies(patient_id),
            self._fetch_recent_labs(patient_id),
            self._fetch_appointment_details(appointment_id)
        ]
        
        (demographics, medications, conditions, visits, 
         allergies, labs, appointment) = await asyncio.gather(*tasks)
        
        # Detect care gaps
        care_gaps = await self._detect_care_gaps(
            patient_id, conditions, labs, medications
        )
        
        # Calculate risk assessment
        risk_assessment = await self._calculate_risk_score(
            demographics, conditions, medications, visits
        )
        
        # Generate visit preparation
        visit_prep = await self._generate_visit_preparation(
            appointment, demographics, conditions, medications, care_gaps
        )
        
        # Generate clinical summary
        clinical_summary = await self._generate_clinical_summary(
            demographics, conditions, medications, labs, visits
        )
        
        return PatientContext(
            patient_id=patient_id,
            appointment_id=appointment_id,
            demographics=demographics,
            active_medications=medications,
            chronic_conditions=conditions,
            recent_visits=visits,
            allergies=allergies,
            recent_labs=labs,
            care_gaps=care_gaps,
            risk_assessment=risk_assessment,
            visit_preparation=visit_prep,
            clinical_summary=clinical_summary
        )
    
    async def _generate_visit_preparation(
        self,
        appointment: Dict,
        demographics: Dict,
        conditions: List[Dict],
        medications: List[Dict],
        care_gaps: List[Dict]
    ) -> Dict:
        """Generate AI-powered visit preparation recommendations."""
        
        prompt = f"""Generate visit preparation for upcoming appointment:

Appointment Type: {appointment.get('type', 'General Visit')}
Chief Complaint: {appointment.get('reason', 'N/A')}

Patient Profile:
- Age: {demographics['age']}
- Active Conditions: {', '.join([c['name'] for c in conditions])}
- Active Medications: {len(medications)} medications
- Care Gaps: {len(care_gaps)} identified

Provide:
1. Key history points to review
2. Anticipated tests or procedures
3. Expected treatment discussions
4. Documents or information patient should bring
5. Estimated preparation time needed
6. Visit complexity (simple/moderate/complex)
7. Suggested visit duration
8. Follow-up planning considerations

Format as JSON with these keys: relevant_history, anticipated_needs, 
required_documents, prep_time, complexity, duration, follow_up_planning"""

        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant preparing provider context for patient visits."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _detect_care_gaps(
        self,
        patient_id: str,
        conditions: List[Dict],
        labs: List[Dict],
        medications: List[Dict]
    ) -> List[Dict]:
        """Detect care gaps based on clinical guidelines."""
        
        gaps = []
        
        # Check preventive care
        preventive_gaps = await self._check_preventive_care(patient_id)
        gaps.extend(preventive_gaps)
        
        # Check condition-specific guidelines
        for condition in conditions:
            condition_gaps = await self._check_condition_guidelines(
                condition, labs, medications
            )
            gaps.extend(condition_gaps)
        
        # Check medication adherence
        medication_gaps = await self._check_medication_gaps(medications)
        gaps.extend(medication_gaps)
        
        # Prioritize gaps
        gaps = self._prioritize_gaps(gaps)
        
        return gaps
    
    async def _calculate_risk_score(
        self,
        demographics: Dict,
        conditions: List[Dict],
        medications: List[Dict],
        visits: List[Dict]
    ) -> Dict:
        """Calculate comprehensive risk assessment."""
        
        risk_factors = []
        score = 0
        
        # Age factor
        age = demographics['age']
        if age >= 65:
            score += 2
            risk_factors.append({
                "factor": "Advanced age",
                "weight": 2,
                "description": f"Age {age} years"
            })
        
        # Comorbidity burden
        if len(conditions) >= 3:
            score += 3
            risk_factors.append({
                "factor": "Multiple chronic conditions",
                "weight": 3,
                "description": f"{len(conditions)} active conditions"
            })
        
        # Polypharmacy
        if len(medications) >= 5:
            score += 2
            risk_factors.append({
                "factor": "Polypharmacy",
                "weight": 2,
                "description": f"{len(medications)} medications"
            })
        
        # Recent hospitalization
        recent_hosp = any(
            v['type'] == 'inpatient' and 
            datetime.fromisoformat(v['date']) > datetime.now() - timedelta(days=30)
            for v in visits
        )
        if recent_hosp:
            score += 4
            risk_factors.append({
                "factor": "Recent hospitalization",
                "weight": 4,
                "description": "Hospitalized within past 30 days"
            })
        
        # High-risk conditions
        high_risk_conditions = ['heart failure', 'copd', 'diabetes', 'ckd']
        for condition in conditions:
            if any(hrc in condition['name'].lower() for hrc in high_risk_conditions):
                score += 1
                risk_factors.append({
                    "factor": f"High-risk condition: {condition['name']}",
                    "weight": 1,
                    "description": "Requires close monitoring"
                })
        
        # Determine risk level
        if score >= 8:
            level = "high"
            recommendations = [
                "Comprehensive care management recommended",
                "Close follow-up within 1-2 weeks",
                "Consider care coordinator assignment",
                "Review all medications for interactions"
            ]
        elif score >= 5:
            level = "moderate"
            recommendations = [
                "Regular monitoring needed",
                "Follow-up within 2-4 weeks",
                "Review care plan"
            ]
        else:
            level = "low"
            recommendations = [
                "Continue routine care",
                "Annual wellness visit",
                "Age-appropriate screenings"
            ]
        
        return {
            "score": score,
            "level": level,
            "factors": risk_factors,
            "recommendations": recommendations
        }

class CareGapDetector:
    """Detect care gaps based on clinical guidelines."""
    
    # Clinical guidelines for common conditions
    GUIDELINES = {
        "diabetes": {
            "hba1c": {"frequency": 90, "name": "HbA1c"},
            "eye_exam": {"frequency": 365, "name": "Eye Exam"},
            "foot_exam": {"frequency": 365, "name": "Foot Exam"},
            "lipid_panel": {"frequency": 365, "name": "Lipid Panel"}
        },
        "hypertension": {
            "bp_check": {"frequency": 180, "name": "BP Check"},
            "lipid_panel": {"frequency": 365, "name": "Lipid Panel"},
            "creatinine": {"frequency": 365, "name": "Creatinine"}
        },
        "heart_failure": {
            "echocardiogram": {"frequency": 365, "name": "Echocardiogram"},
            "bnp": {"frequency": 90, "name": "BNP/NT-proBNP"},
            "weight_monitoring": {"frequency": 7, "name": "Weight Monitoring"}
        }
    }
    
    PREVENTIVE_CARE = {
        "mammogram": {
            "gender": "female",
            "age_start": 40,
            "frequency": 730  # 2 years
        },
        "colonoscopy": {
            "age_start": 45,
            "frequency": 3650  # 10 years
        },
        "flu_vaccine": {
            "age_start": 6,
            "frequency": 365  # Annual
        },
        "pneumococcal_vaccine": {
            "age_start": 65,
            "frequency": None  # One-time
        }
    }
    
    def detect_condition_gaps(
        self,
        condition_name: str,
        last_tests: Dict[str, datetime],
        medications: List[Dict]
    ) -> List[Dict]:
        """Detect care gaps for specific condition."""
        
        gaps = []
        condition_key = condition_name.lower().replace(" ", "_")
        
        if condition_key not in self.GUIDELINES:
            return gaps
        
        guidelines = self.GUIDELINES[condition_key]
        
        for test_key, requirements in guidelines.items():
            last_test_date = last_tests.get(test_key)
            
            if not last_test_date:
                # Never done
                gaps.append({
                    "type": "missing_test",
                    "test": requirements["name"],
                    "priority": "high",
                    "description": f"{requirements['name']} never performed",
                    "action": f"Order {requirements['name']}"
                })
            else:
                # Check if overdue
                days_since = (datetime.now() - last_test_date).days
                if days_since > requirements["frequency"]:
                    gaps.append({
                        "type": "overdue_test",
                        "test": requirements["name"],
                        "priority": "medium",
                        "description": f"{requirements['name']} overdue by {days_since - requirements['frequency']} days",
                        "action": f"Schedule {requirements['name']}"
                    })
        
        return gaps
```

### Step 0.4: API Routes

**File to Create**: `src/api/routers/previsit.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.previsit.symptom_analyzer import (
    SymptomAnalyzer, TriageEngine, Symptom, SymptomAnalysis
)
from ..dependencies import get_current_user, get_openai_client

router = APIRouter(prefix="/api/previsit", tags=["previsit"])

@router.post("/analyze-symptoms", response_model=SymptomAnalysis)
async def analyze_symptoms(
    symptoms: List[Symptom],
    patient_age: int,
    patient_gender: str,
    medical_history: List[str] = None,
    current_user = Depends(get_current_user),
    openai_client = Depends(get_openai_client)
):
    """Analyze patient symptoms and provide triage recommendations."""
    
    analyzer = SymptomAnalyzer(openai_client)
    
    analysis = await analyzer.analyze_symptoms(
        symptoms=symptoms,
        patient_age=patient_age,
        patient_gender=patient_gender,
        medical_history=medical_history
    )
    
    return analysis

@router.post("/triage-assessment")
async def triage_assessment(
    symptoms: List[Symptom],
    vital_signs: dict = None,
    current_user = Depends(get_current_user)
):
    """Perform triage assessment based on symptoms and vital signs."""
    
    triage = TriageEngine()
    assessment = triage.assess_triage_level(symptoms, vital_signs)
    
    return assessment

@router.post("/generate-questionnaire")
async def generate_questionnaire(
    chief_complaint: str,
    initial_symptoms: List[Symptom],
    current_user = Depends(get_current_user),
    openai_client = Depends(get_openai_client)
):
    """Generate dynamic follow-up questionnaire."""
    
    analyzer = SymptomAnalyzer(openai_client)
    questions = await analyzer.generate_questionnaire(
        chief_complaint, initial_symptoms
    )
    
    return {"questions": questions}
```

**File to Create**: `src/api/routers/appoint_ready.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from ..services.appoint_ready.context_builder import (
    AppointReadyContextBuilder, PatientContext
)
from ..dependencies import (
    get_current_user, get_fhir_client, 
    get_openai_client, get_db
)

router = APIRouter(prefix="/api/appoint-ready", tags=["appoint-ready"])

@router.get("/patient-context/{patient_id}/{appointment_id}")
async def get_patient_context(
    patient_id: str,
    appointment_id: str,
    current_user = Depends(get_current_user),
    fhir_client = Depends(get_fhir_client),
    openai_client = Depends(get_openai_client),
    db = Depends(get_db)
) -> PatientContext:
    """Build comprehensive patient context for appointment."""
    
    # Verify user has permission to access this patient
    if not current_user.can_access_patient(patient_id):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this patient"
        )
    
    builder = AppointReadyContextBuilder(fhir_client, openai_client, db)
    context = await builder.build_context(patient_id, appointment_id)
    
    return context

@router.get("/care-gaps/{patient_id}")
async def get_care_gaps(
    patient_id: str,
    current_user = Depends(get_current_user),
    fhir_client = Depends(get_fhir_client),
    db = Depends(get_db)
):
    """Get identified care gaps for patient."""
    
    builder = AppointReadyContextBuilder(fhir_client, None, db)
    
    # Fetch required data
    conditions = await builder._fetch_conditions(patient_id)
    labs = await builder._fetch_recent_labs(patient_id)
    medications = await builder._fetch_medications(patient_id)
    
    # Detect gaps
    gaps = await builder._detect_care_gaps(
        patient_id, conditions, labs, medications
    )
    
    return {"care_gaps": gaps}
```

### Step 0.5: Testing Scripts

**File to Create**: `docker/scripts/test-backend.sh`
```bash
#!/bin/bash

echo "🚀 Starting Backend Tests..."

# Start services
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services..."
sleep 30

# Run health checks
echo "🏥 Health Checks..."

# API health
curl -f http://localhost:8000/health || exit 1
echo "✅ API: Healthy"

# Database health
docker-compose exec -T postgres pg_isready -U postgres || exit 1
echo "✅ Database: Healthy"

# FHIR server health
curl -f http://localhost:8080/fhir/metadata || exit 1
echo "✅ FHIR Server: Healthy"

# Run tests
echo "🧪 Running tests..."
docker-compose exec -T api pytest tests/ -v

echo "✅ All tests passed!"
```

## Phase 1: Azure Cloud Migration (Week 5)

### Step 1.1: Production Terraform Configuration

**File to Create**: `terraform/backend-azure.tf`
```hcl
# Production Azure Backend Infrastructure

resource "azurerm_app_service_plan" "main" {
  name                = "ai-healthcare-${var.environment}-plan"
  location           = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind               = "Linux"
  reserved           = true

  sku {
    tier = "Premium"
    size = "P1v3"
  }
}

resource "azurerm_app_service" "api" {
  name                = "ai-healthcare-${var.environment}-api"
  location           = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  app_service_plan_id = azurerm_app_service_plan.main.id

  site_config {
    linux_fx_version = "DOCKER|${var.acr_name}.azurecr.io/healthcare-api:latest"
    always_on        = true
    
    cors {
      allowed_origins = var.allowed_origins
    }
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "DOCKER_REGISTRY_SERVER_URL"          = "https://${var.acr_name}.azurecr.io"
    "DOCKER_REGISTRY_SERVER_USERNAME"     = azurerm_container_registry.main.admin_username
    "DOCKER_REGISTRY_SERVER_PASSWORD"     = azurerm_container_registry.main.admin_password
    "DATABASE_URL"                         = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.db_url.id})"
    "AZURE_OPENAI_ENDPOINT"               = azurerm_cognitive_account.openai.endpoint
    "ENABLE_PREVISIT"                     = "true"
    "ENABLE_APPOINT_READY"                = "true"
  }
}

# Container Registry for Docker images
resource "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  sku                = "Premium"
  admin_enabled      = true
}
```

## Progress Tracking

### Local Development (Weeks 1-4)
- [ ] Docker environment setup
- [ ] PreVisit.ai services implementation
- [ ] Appoint-Ready services implementation
- [ ] FHIR integration
- [ ] API routes
- [ ] Testing suite
- [ ] Documentation

### Azure Migration (Week 5)
- [ ] Terraform infrastructure
- [ ] CI/CD pipeline
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] HIPAA compliance validation

This comprehensive backend plan enables local Docker development and testing before Azure deployment, with full PreVisit.ai and Appoint-Ready functionality!
