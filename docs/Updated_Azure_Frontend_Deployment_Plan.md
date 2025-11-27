# Azure Frontend Deployment Plan - AI Healthcare App
## Enhanced with PreVisit.ai & Appoint-Ready Features

## Project Overview
This document provides comprehensive instructions for deploying the frontend of the AI Healthcare App with PreVisit.ai and Appoint-Ready functionality. The deployment follows a **local-first approach** using Docker for testing before Azure cloud deployment.

## New Features Integration

### PreVisit.ai Capabilities
- **Pre-appointment questionnaires** with dynamic form generation
- **Symptom checker** with AI-powered triage
- **Patient history collection** with FHIR integration
- **Insurance verification** and eligibility checks
- **Appointment preparation checklist** customized per visit type
- **Medical history timeline** visualization
- **Medication reconciliation** interface
- **Risk assessment** algorithms

### Appoint-Ready Features (Google Health AI)
- **Appointment context preparation** from patient records
- **Visit summary generation** from EHR data
- **Clinical decision support** recommendations
- **Patient context cards** with key information
- **Pre-visit risk stratification** scoring
- **Care gap identification** and alerts
- **Relevant test results** highlighting
- **Medication interaction checking**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Patient    │  │   Provider   │  │    Admin     │      │
│  │  Dashboard   │  │  Dashboard   │  │  Dashboard   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                           │                                  │
│         ┌─────────────────┴─────────────────┐                │
│         │                                   │                │
│  ┌──────▼──────┐                    ┌──────▼──────┐         │
│  │  PreVisit   │                    │Appoint-Ready│         │
│  │  Features   │                    │  Features   │         │
│  ├─────────────┤                    ├─────────────┤         │
│  │ • Symptoms  │                    │ • Context   │         │
│  │ • History   │                    │ • Summaries │         │
│  │ • Forms     │                    │ • Risks     │         │
│  │ • Checklist │                    │ • Gaps      │         │
│  └─────────────┘                    └─────────────┘         │
│         │                                   │                │
│         └───────────────┬───────────────────┘                │
│                         │                                    │
│              ┌──────────▼──────────┐                         │
│              │   Core Services     │                         │
│              ├─────────────────────┤                         │
│              │ • Auth (Azure AD B2C)│                        │
│              │ • Real-time (SignalR)│                        │
│              │ • Storage (Blob)     │                        │
│              │ • AI (OpenAI)        │                        │
│              │ • Speech Services    │                        │
│              │ • FHIR Integration   │                        │
│              └─────────────────────┘                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Development Approach: Local First, Then Azure

### Phase 0: Local Docker Development (Weeks 1-3)
Build and test everything locally using Docker containers before Azure deployment.

### Phase 1: Azure Migration (Week 4)
Deploy tested application to Azure Static Web Apps.

## Project Structure

```
azure-healthcare-frontend/
├── docker/
│   ├── Dockerfile                  # Frontend container
│   ├── docker-compose.yml          # Local development stack
│   ├── docker-compose.azure.yml    # Azure testing configuration
│   └── nginx.conf                  # Production nginx config
├── src/
│   ├── app/
│   │   ├── (auth)/                # Authentication routes
│   │   ├── (patient)/             # Patient portal
│   │   │   ├── dashboard/
│   │   │   ├── previsit/         # PreVisit.ai features
│   │   │   │   ├── symptoms/
│   │   │   │   ├── history/
│   │   │   │   ├── questionnaire/
│   │   │   │   ├── checklist/
│   │   │   │   └── insurance/
│   │   │   ├── appointments/
│   │   │   └── records/
│   │   ├── (provider)/           # Provider portal
│   │   │   ├── dashboard/
│   │   │   ├── appoint-ready/    # Appoint-Ready features
│   │   │   │   ├── context/
│   │   │   │   ├── summaries/
│   │   │   │   ├── risk-assessment/
│   │   │   │   ├── care-gaps/
│   │   │   │   └── clinical-support/
│   │   │   ├── patients/
│   │   │   ├── notes/
│   │   │   └── transcription/
│   │   └── (admin)/              # Admin portal
│   ├── components/
│   │   ├── previsit/             # PreVisit components
│   │   │   ├── SymptomChecker.tsx
│   │   │   ├── MedicalHistoryForm.tsx
│   │   │   ├── InsuranceVerification.tsx
│   │   │   ├── AppointmentChecklist.tsx
│   │   │   └── TimelineVisualization.tsx
│   │   ├── appoint-ready/        # Appoint-Ready components
│   │   │   ├── PatientContextCard.tsx
│   │   │   ├── VisitSummary.tsx
│   │   │   ├── RiskStratification.tsx
│   │   │   ├── CareGapAlert.tsx
│   │   │   └── ClinicalDecisionSupport.tsx
│   │   └── shared/               # Shared UI components
│   ├── lib/
│   │   ├── previsit/            # PreVisit services
│   │   │   ├── symptom-analyzer.ts
│   │   │   ├── questionnaire-generator.ts
│   │   │   ├── insurance-validator.ts
│   │   │   └── triage-engine.ts
│   │   ├── appoint-ready/       # Appoint-Ready services
│   │   │   ├── context-builder.ts
│   │   │   ├── summary-generator.ts
│   │   │   ├── risk-calculator.ts
│   │   │   ├── care-gap-detector.ts
│   │   │   └── decision-support.ts
│   │   └── fhir/                # FHIR integration
│   │       ├── fhir-client.ts
│   │       ├── resource-mapper.ts
│   │       └── terminology-service.ts
│   ├── hooks/
│   │   ├── usePreVisit.ts
│   │   ├── useAppointReady.ts
│   │   └── useFHIR.ts
│   └── types/
│       ├── previsit.types.ts
│       ├── appoint-ready.types.ts
│       └── fhir.types.ts
├── public/
├── tests/
│   ├── e2e/                     # Playwright E2E tests
│   ├── integration/             # Integration tests
│   └── unit/                    # Unit tests
├── .azure/
│   └── static-web-apps/        # Azure SWA config
├── terraform/                   # IaC for Azure
└── docs/
    ├── previsit-api.md
    ├── appoint-ready-api.md
    └── docker-guide.md
```

## Phase 0: Local Docker Development

### Step 0.1: Docker Environment Setup

**File to Create**: `docker/Dockerfile`
```dockerfile
# Multi-stage build for Next.js application
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Development image
FROM base AS development
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Enable hot reload
ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true

EXPOSE 3000
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build with environment variables
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_AZURE_CLIENT_ID
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_AZURE_CLIENT_ID=$NEXT_PUBLIC_AZURE_CLIENT_ID

RUN npm run build

# Production image
FROM base AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**File to Create**: `docker/docker-compose.yml`
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: development
    container_name: healthcare-frontend
    ports:
      - "3000:3000"
    volumes:
      - ../src:/app/src
      - ../public:/app/public
      - ../package.json:/app/package.json
      - /app/node_modules
      - /app/.next
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - NEXT_PUBLIC_AZURE_AUTHORITY=${AZURE_AUTHORITY}
      - NEXT_PUBLIC_SIGNALR_URL=http://backend:8000/signalr
      - NEXT_PUBLIC_ENABLE_PREVISIT=true
      - NEXT_PUBLIC_ENABLE_APPOINT_READY=true
    networks:
      - healthcare-network
    depends_on:
      - backend
      - mock-fhir
    command: npm run dev

  backend:
    image: healthcare-backend:latest
    container_name: healthcare-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/healthcare
      - REDIS_URL=redis://redis:6379
      - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - FHIR_SERVER_URL=http://mock-fhir:8080/fhir
    networks:
      - healthcare-network
    depends_on:
      - postgres
      - redis

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

  redis:
    image: redis:7-alpine
    container_name: healthcare-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - healthcare-network

  mock-fhir:
    image: hapiproject/hapi:latest
    container_name: healthcare-fhir
    ports:
      - "8080:8080"
    environment:
      - hapi.fhir.version=R4
      - hapi.fhir.server_address=http://mock-fhir:8080/fhir
    volumes:
      - fhir-data:/data/hapi
    networks:
      - healthcare-network

  mock-azure-openai:
    image: ghcr.io/azure-samples/openai-test-server:latest
    container_name: mock-azure-openai
    ports:
      - "8081:8080"
    environment:
      - OPENAI_API_KEY=mock-key-for-local-dev
    networks:
      - healthcare-network

networks:
  healthcare-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  fhir-data:
```

**File to Create**: `.env.local`
```bash
# Local Development Environment Variables
NODE_ENV=development

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SIGNALR_URL=http://localhost:8000/signalr

# Feature Flags
NEXT_PUBLIC_ENABLE_PREVISIT=true
NEXT_PUBLIC_ENABLE_APPOINT_READY=true
NEXT_PUBLIC_ENABLE_FHIR=true

# Azure AD B2C (Mock for local dev)
NEXT_PUBLIC_AZURE_CLIENT_ID=mock-client-id
NEXT_PUBLIC_AZURE_AUTHORITY=http://localhost:3000/mock-auth
NEXT_PUBLIC_AZURE_TENANT_DOMAIN=localhost
NEXT_PUBLIC_REDIRECT_URI=http://localhost:3000/auth/callback
NEXT_PUBLIC_POST_LOGOUT_URI=http://localhost:3000

# FHIR Server
NEXT_PUBLIC_FHIR_SERVER_URL=http://localhost:8080/fhir

# Mock Services
USE_MOCK_AUTH=true
USE_MOCK_FHIR=true
USE_MOCK_OPENAI=true
```

**Commands to Execute**:
```bash
# Create project structure
mkdir -p docker src/app/{patient,provider,admin} src/components/{previsit,appoint-ready} src/lib/{previsit,appoint-ready,fhir}

# Start local development environment
cd docker
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop environment
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

### Step 0.2: PreVisit.ai Features Implementation

**File to Create**: `src/lib/previsit/symptom-analyzer.ts`
```typescript
import { OpenAI } from '@azure/openai';

export interface Symptom {
  name: string;
  severity: 'mild' | 'moderate' | 'severe';
  duration: string;
  onset: Date;
  description: string;
}

export interface SymptomAnalysis {
  urgency: 'low' | 'moderate' | 'high' | 'emergency';
  possibleConditions: string[];
  recommendations: string[];
  triageLevel: number; // 1-5
  requiresImmediateAttention: boolean;
  suggestedSpecialty: string[];
}

export class SymptomAnalyzer {
  private openai: OpenAI;

  constructor(apiKey: string, endpoint: string) {
    this.openai = new OpenAI({ apiKey, endpoint });
  }

  async analyzeSymptoms(symptoms: Symptom[]): Promise<SymptomAnalysis> {
    const prompt = this.buildSymptomPrompt(symptoms);
    
    const response = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `You are a medical triage assistant. Analyze symptoms and provide urgency assessment, 
          possible conditions, and recommendations. Always err on the side of caution for patient safety.
          Format your response as JSON with fields: urgency, possibleConditions, recommendations, 
          triageLevel, requiresImmediateAttention, suggestedSpecialty.`
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.3,
      response_format: { type: 'json_object' }
    });

    const analysis = JSON.parse(response.choices[0].message.content);
    return analysis;
  }

  private buildSymptomPrompt(symptoms: Symptom[]): string {
    const symptomDescriptions = symptoms.map(s => 
      `${s.name} (${s.severity}) for ${s.duration}, started ${s.onset.toDateString()}: ${s.description}`
    ).join('\n');

    return `Patient presents with the following symptoms:\n${symptomDescriptions}\n\n
    Please analyze these symptoms and provide a triage assessment.`;
  }

  async generateQuestionnaire(chiefComplaint: string): Promise<QuestionnaireItem[]> {
    const response = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `Generate a medical questionnaire for the given chief complaint. 
          Create relevant follow-up questions to gather comprehensive information.
          Format as JSON array of questions with: id, text, type, options (if applicable), required.`
        },
        {
          role: 'user',
          content: `Chief complaint: ${chiefComplaint}`
        }
      ],
      temperature: 0.5,
      response_format: { type: 'json_object' }
    });

    const result = JSON.parse(response.choices[0].message.content);
    return result.questions;
  }
}

export interface QuestionnaireItem {
  id: string;
  text: string;
  type: 'text' | 'select' | 'multiselect' | 'number' | 'date' | 'boolean';
  options?: string[];
  required: boolean;
  conditionalOn?: string; // ID of question this depends on
}
```

**File to Create**: `src/components/previsit/SymptomChecker.tsx`
```typescript
'use client';

import { useState } from 'react';
import { Symptom, SymptomAnalysis } from '@/lib/previsit/symptom-analyzer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Clock, Activity } from 'lucide-react';

export function SymptomChecker() {
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [analysis, setAnalysis] = useState<SymptomAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  const addSymptom = (symptom: Symptom) => {
    setSymptoms([...symptoms, symptom]);
  };

  const analyzeSymptoms = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/previsit/analyze-symptoms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms })
      });
      
      const result = await response.json();
      setAnalysis(result);
    } catch (error) {
      console.error('Failed to analyze symptoms:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      moderate: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      emergency: 'bg-red-100 text-red-800'
    };
    return colors[urgency] || colors.low;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Symptom Checker
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Symptom Input Form */}
            <SymptomInputForm onAddSymptom={addSymptom} />
            
            {/* Current Symptoms List */}
            {symptoms.length > 0 && (
              <div className="space-y-2">
                <h3 className="font-semibold">Current Symptoms:</h3>
                {symptoms.map((symptom, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <span className="font-medium">{symptom.name}</span>
                      <Badge className="ml-2">{symptom.severity}</Badge>
                      <span className="text-sm text-gray-600 ml-2">
                        for {symptom.duration}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSymptoms(symptoms.filter((_, i) => i !== index))}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}

            <Button
              onClick={analyzeSymptoms}
              disabled={symptoms.length === 0 || loading}
              className="w-full"
            >
              {loading ? 'Analyzing...' : 'Analyze Symptoms'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Urgency Alert */}
            <Alert className={getUrgencyColor(analysis.urgency)}>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Urgency Level: {analysis.urgency.toUpperCase()}</AlertTitle>
              <AlertDescription>
                Triage Score: {analysis.triageLevel}/5
                {analysis.requiresImmediateAttention && (
                  <span className="block mt-2 font-semibold">
                    ⚠️ Immediate medical attention recommended
                  </span>
                )}
              </AlertDescription>
            </Alert>

            {/* Possible Conditions */}
            <div>
              <h3 className="font-semibold mb-2">Possible Conditions:</h3>
              <ul className="list-disc list-inside space-y-1">
                {analysis.possibleConditions.map((condition, index) => (
                  <li key={index} className="text-sm">{condition}</li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div>
              <h3 className="font-semibold mb-2">Recommendations:</h3>
              <ul className="list-disc list-inside space-y-1">
                {analysis.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm">{rec}</li>
                ))}
              </ul>
            </div>

            {/* Suggested Specialty */}
            <div>
              <h3 className="font-semibold mb-2">Suggested Specialists:</h3>
              <div className="flex flex-wrap gap-2">
                {analysis.suggestedSpecialty.map((specialty, index) => (
                  <Badge key={index} variant="outline">{specialty}</Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

### Step 0.3: Appoint-Ready Features Implementation

**File to Create**: `src/lib/appoint-ready/context-builder.ts`
```typescript
import { FHIRClient } from '../fhir/fhir-client';
import { OpenAI } from '@azure/openai';

export interface PatientContext {
  patientId: string;
  demographics: PatientDemographics;
  activeMedications: Medication[];
  recentVisits: Visit[];
  chronicConditions: Condition[];
  allergies: Allergy[];
  recentLabResults: LabResult[];
  careGaps: CareGap[];
  riskScore: RiskAssessment;
  visitPreparation: VisitPreparation;
}

export interface VisitPreparation {
  appointmentType: string;
  chiefComplaint?: string;
  relevantHistory: string[];
  anticipatedNeeds: string[];
  requiredDocuments: string[];
  prepTime: string;
  complexity: 'simple' | 'moderate' | 'complex';
}

export class AppointReadyContextBuilder {
  constructor(
    private fhirClient: FHIRClient,
    private openai: OpenAI
  ) {}

  async buildPatientContext(
    patientId: string,
    appointmentId: string
  ): Promise<PatientContext> {
    // Fetch all relevant FHIR resources in parallel
    const [
      patient,
      medications,
      conditions,
      observations,
      encounters,
      allergies,
      appointment
    ] = await Promise.all([
      this.fhirClient.getPatient(patientId),
      this.fhirClient.getMedications(patientId),
      this.fhirClient.getConditions(patientId),
      this.fhirClient.getObservations(patientId, { recent: true }),
      this.fhirClient.getEncounters(patientId, { limit: 5 }),
      this.fhirClient.getAllergies(patientId),
      this.fhirClient.getAppointment(appointmentId)
    ]);

    // Transform FHIR resources
    const demographics = this.transformDemographics(patient);
    const activeMedications = this.transformMedications(medications);
    const recentVisits = this.transformEncounters(encounters);
    const chronicConditions = this.transformConditions(conditions);
    const patientAllergies = this.transformAllergies(allergies);
    const recentLabResults = this.transformObservations(observations);

    // Detect care gaps
    const careGaps = await this.detectCareGaps(
      patientId,
      chronicConditions,
      recentLabResults,
      medications
    );

    // Calculate risk score
    const riskScore = await this.calculateRiskScore({
      demographics,
      conditions: chronicConditions,
      medications: activeMedications,
      recentVisits
    });

    // Generate visit preparation
    const visitPreparation = await this.generateVisitPreparation(
      appointment,
      demographics,
      chronicConditions,
      activeMedications,
      careGaps
    );

    return {
      patientId,
      demographics,
      activeMedications,
      recentVisits,
      chronicConditions,
      allergies: patientAllergies,
      recentLabResults,
      careGaps,
      riskScore,
      visitPreparation
    };
  }

  private async generateVisitPreparation(
    appointment: any,
    demographics: PatientDemographics,
    conditions: Condition[],
    medications: Medication[],
    careGaps: CareGap[]
  ): Promise<VisitPreparation> {
    const prompt = `Generate visit preparation for:
    Appointment Type: ${appointment.appointmentType?.text || 'General Visit'}
    Patient Age: ${demographics.age}
    Active Conditions: ${conditions.map(c => c.name).join(', ')}
    Active Medications: ${medications.map(m => m.name).join(', ')}
    Care Gaps: ${careGaps.map(g => g.description).join(', ')}

    Provide:
    1. Relevant history points to review
    2. Anticipated needs (tests, referrals, etc.)
    3. Required documents
    4. Estimated prep time
    5. Visit complexity assessment`;

    const response = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: 'You are a medical assistant preparing context for a patient visit. Be thorough but concise.'
        },
        { role: 'user', content: prompt }
      ],
      temperature: 0.3,
      response_format: { type: 'json_object' }
    });

    const preparation = JSON.parse(response.choices[0].message.content);
    return {
      appointmentType: appointment.appointmentType?.text || 'General Visit',
      chiefComplaint: appointment.reasonCode?.[0]?.text,
      relevantHistory: preparation.relevantHistory || [],
      anticipatedNeeds: preparation.anticipatedNeeds || [],
      requiredDocuments: preparation.requiredDocuments || [],
      prepTime: preparation.prepTime || '5-10 minutes',
      complexity: preparation.complexity || 'moderate'
    };
  }

  private async detectCareGaps(
    patientId: string,
    conditions: Condition[],
    labResults: LabResult[],
    medications: Medication[]
  ): Promise<CareGap[]> {
    const gaps: CareGap[] = [];

    // Check for preventive care gaps
    const preventiveGaps = await this.checkPreventiveCare(patientId);
    gaps.push(...preventiveGaps);

    // Check for condition-specific gaps
    for (const condition of conditions) {
      const conditionGaps = await this.checkConditionGuidelines(
        condition,
        labResults,
        medications
      );
      gaps.push(...conditionGaps);
    }

    // Check medication adherence
    const medicationGaps = await this.checkMedicationAdherence(medications);
    gaps.push(...medicationGaps);

    return gaps;
  }

  private async calculateRiskScore(data: {
    demographics: PatientDemographics;
    conditions: Condition[];
    medications: Medication[];
    recentVisits: Visit[];
  }): Promise<RiskAssessment> {
    // Implement risk stratification algorithm
    // Consider: age, comorbidities, polypharmacy, recent hospitalizations
    
    let score = 0;
    const factors: string[] = [];

    // Age factor
    if (data.demographics.age > 65) {
      score += 2;
      factors.push('Advanced age');
    }

    // Comorbidity factor
    if (data.conditions.length >= 3) {
      score += 3;
      factors.push('Multiple chronic conditions');
    }

    // Polypharmacy factor
    if (data.medications.length >= 5) {
      score += 2;
      factors.push('Polypharmacy');
    }

    // Recent hospitalization
    const recentHospitalization = data.recentVisits.some(
      v => v.type === 'inpatient' && 
      new Date(v.date) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
    );
    if (recentHospitalization) {
      score += 4;
      factors.push('Recent hospitalization');
    }

    return {
      score,
      level: score >= 7 ? 'high' : score >= 4 ? 'medium' : 'low',
      factors,
      recommendations: this.getRiskRecommendations(score)
    };
  }

  private getRiskRecommendations(score: number): string[] {
    if (score >= 7) {
      return [
        'Consider comprehensive care management',
        'Schedule follow-up within 2 weeks',
        'Review all medications for interactions',
        'Ensure care coordination across specialists'
      ];
    } else if (score >= 4) {
      return [
        'Monitor closely for changes',
        'Review care plan',
        'Schedule regular follow-ups'
      ];
    }
    return ['Continue routine care', 'Annual wellness visit recommended'];
  }
}

export interface RiskAssessment {
  score: number;
  level: 'low' | 'medium' | 'high';
  factors: string[];
  recommendations: string[];
}

export interface CareGap {
  type: 'preventive' | 'condition-management' | 'medication' | 'follow-up';
  description: string;
  priority: 'high' | 'medium' | 'low';
  dueDate?: Date;
  action: string;
}
```

**File to Create**: `src/components/appoint-ready/PatientContextCard.tsx`
```typescript
'use client';

import { PatientContext } from '@/lib/appoint-ready/context-builder';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  User, Calendar, Pill, Activity, AlertTriangle, 
  Clock, FileText, TrendingUp 
} from 'lucide-react';

interface PatientContextCardProps {
  context: PatientContext;
}

export function PatientContextCard({ context }: PatientContextCardProps) {
  const getRiskColor = (level: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800'
    };
    return colors[level] || colors.low;
  };

  return (
    <div className="space-y-4">
      {/* Patient Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <User className="w-5 h-5" />
              {context.demographics.name}
            </span>
            <Badge className={getRiskColor(context.riskScore.level)}>
              Risk: {context.riskScore.level.toUpperCase()}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Age</p>
              <p className="font-semibold">{context.demographics.age} years</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Gender</p>
              <p className="font-semibold">{context.demographics.gender}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Visit Preparation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Visit Preparation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <p className="text-sm font-semibold">Appointment Type</p>
            <p>{context.visitPreparation.appointmentType}</p>
          </div>
          
          {context.visitPreparation.chiefComplaint && (
            <div>
              <p className="text-sm font-semibold">Chief Complaint</p>
              <p>{context.visitPreparation.chiefComplaint}</p>
            </div>
          )}

          <div>
            <p className="text-sm font-semibold">Prep Time Needed</p>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{context.visitPreparation.prepTime}</span>
              <Badge>{context.visitPreparation.complexity}</Badge>
            </div>
          </div>

          {context.visitPreparation.relevantHistory.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-1">Relevant History</p>
              <ul className="list-disc list-inside text-sm space-y-1">
                {context.visitPreparation.relevantHistory.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {context.visitPreparation.anticipatedNeeds.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-1">Anticipated Needs</p>
              <ul className="list-disc list-inside text-sm space-y-1">
                {context.visitPreparation.anticipatedNeeds.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Active Conditions */}
      {context.chronicConditions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Active Conditions ({context.chronicConditions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {context.chronicConditions.map((condition, i) => (
                <div key={i} className="flex items-center justify-between p-2 border rounded">
                  <span>{condition.name}</span>
                  <span className="text-sm text-gray-600">
                    Since {new Date(condition.onsetDate).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Medications */}
      {context.activeMedications.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Pill className="w-5 h-5" />
              Current Medications ({context.activeMedications.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {context.activeMedications.map((med, i) => (
                <div key={i} className="p-2 border rounded">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{med.name}</span>
                    <span className="text-sm">{med.dosage}</span>
                  </div>
                  <p className="text-sm text-gray-600">{med.instructions}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Care Gaps */}
      {context.careGaps.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              Care Gaps ({context.careGaps.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {context.careGaps.map((gap, i) => (
                <Alert key={i} variant={gap.priority === 'high' ? 'destructive' : 'default'}>
                  <AlertDescription>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold">{gap.description}</p>
                        <p className="text-sm mt-1">{gap.action}</p>
                      </div>
                      <Badge variant={gap.priority === 'high' ? 'destructive' : 'secondary'}>
                        {gap.priority}
                      </Badge>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Risk Assessment */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Risk Assessment
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <p className="text-sm font-semibold mb-2">Risk Factors</p>
            <div className="space-y-1">
              {context.riskScore.factors.map((factor, i) => (
                <div key={i} className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                  <span className="text-sm">{factor}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-semibold mb-2">Recommendations</p>
            <ul className="list-disc list-inside text-sm space-y-1">
              {context.riskScore.recommendations.map((rec, i) => (
                <li key={i}>{rec}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Step 0.4: Local Testing Scripts

**File to Create**: `docker/scripts/test-local.sh`
```bash
#!/bin/bash

# Test script for local Docker environment

echo "🚀 Starting Healthcare App Local Tests..."

# Start services
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
echo "🏥 Running health checks..."

# Frontend health check
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ $FRONTEND_STATUS -eq 200 ]; then
  echo "✅ Frontend: Healthy"
else
  echo "❌ Frontend: Unhealthy (Status: $FRONTEND_STATUS)"
  exit 1
fi

# Backend health check
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $BACKEND_STATUS -eq 200 ]; then
  echo "✅ Backend: Healthy"
else
  echo "❌ Backend: Unhealthy (Status: $BACKEND_STATUS)"
  exit 1
fi

# FHIR server health check
FHIR_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/fhir/metadata)
if [ $FHIR_STATUS -eq 200 ]; then
  echo "✅ FHIR Server: Healthy"
else
  echo "❌ FHIR Server: Unhealthy (Status: $FHIR_STATUS)"
  exit 1
fi

# Run integration tests
echo "🧪 Running integration tests..."
cd .. && npm run test:integration

# Run E2E tests
echo "🎭 Running E2E tests..."
npm run test:e2e

echo "✅ All tests passed!"
echo "🌐 Application available at: http://localhost:3000"
```

**File to Create**: `docker/scripts/migrate-to-azure.sh`
```bash
#!/bin/bash

# Script to prepare for Azure migration

echo "🔄 Preparing for Azure migration..."

# Build production images
echo "🏗️  Building production Docker images..."
docker build -t healthcare-frontend:prod --target production -f docker/Dockerfile ..

# Tag images for Azure Container Registry
ACR_NAME="aihealthcareregistry"
docker tag healthcare-frontend:prod ${ACR_NAME}.azurecr.io/healthcare-frontend:latest

# Login to Azure
echo "🔐 Logging into Azure..."
az login
az acr login --name ${ACR_NAME}

# Push images to ACR
echo "📤 Pushing images to Azure Container Registry..."
docker push ${ACR_NAME}.azurecr.io/healthcare-frontend:latest

# Apply Terraform for Azure infrastructure
echo "☁️  Deploying Azure infrastructure..."
cd ../terraform
terraform init
terraform plan -var-file="environments/prod.tfvars" -out=tfplan
terraform apply tfplan

echo "✅ Azure migration preparation complete!"
echo "📋 Next steps:"
echo "1. Configure Azure Static Web Apps deployment"
echo "2. Set up Azure AD B2C tenant"
echo "3. Configure custom domain and SSL"
echo "4. Enable Application Insights monitoring"
```

## Phase 1: Azure Cloud Migration

### Step 1.1: Azure Infrastructure Deployment

**File to Create**: `terraform/frontend-azure.tf`
```hcl
# Updated Terraform with PreVisit and Appoint-Ready support

resource "azurerm_resource_group" "frontend" {
  name     = "ai-healthcare-frontend-${var.environment}-rg"
  location = var.location

  tags = {
    Environment = var.environment
    Project     = "AI-Healthcare"
    Component   = "Frontend"
    Features    = "PreVisit,AppointReady,FHIR"
  }
}

# Azure Static Web Apps with enhanced features
resource "azurerm_static_site" "main" {
  name                = "ai-healthcare-${var.environment}-static"
  resource_group_name = azurerm_resource_group.frontend.name
  location           = azurerm_resource_group.frontend.location
  sku_tier           = "Standard"
  sku_size           = "Standard"

  tags = azurerm_resource_group.frontend.tags
}

# Application Insights for monitoring
resource "azurerm_application_insights" "frontend" {
  name                = "ai-healthcare-${var.environment}-insights"
  location           = azurerm_resource_group.frontend.location
  resource_group_name = azurerm_resource_group.frontend.name
  application_type    = "web"

  tags = azurerm_resource_group.frontend.tags
}

# Azure API Management for FHIR proxy (optional)
resource "azurerm_api_management" "fhir_proxy" {
  name                = "ai-healthcare-${var.environment}-apim"
  location           = azurerm_resource_group.frontend.location
  resource_group_name = azurerm_resource_group.frontend.name
  publisher_name      = "AI Healthcare"
  publisher_email     = var.publisher_email
  sku_name           = "Developer_1"

  tags = azurerm_resource_group.frontend.tags
}

# Outputs for configuration
output "static_web_app_default_hostname" {
  value = azurerm_static_site.main.default_host_name
}

output "app_insights_instrumentation_key" {
  value     = azurerm_application_insights.frontend.instrumentation_key
  sensitive = true
}

output "app_insights_connection_string" {
  value     = azurerm_application_insights.frontend.connection_string
  sensitive = true
}
```

### Step 1.2: CI/CD Pipeline with Docker

**File to Create**: `.github/workflows/deploy-azure.yml`
```yaml
name: Build and Deploy to Azure

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18.x'
  DOCKER_REGISTRY: aihealthcareregistry.azurecr.io
  FRONTEND_IMAGE: healthcare-frontend

jobs:
  test-local:
    name: Test in Docker
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker-compose -f docker/docker-compose.yml build
      
      - name: Start services
        run: |
          docker-compose -f docker/docker-compose.yml up -d
          sleep 30
      
      - name: Run health checks
        run: |
          bash docker/scripts/test-local.sh
      
      - name: Run tests
        run: |
          docker-compose -f docker/docker-compose.yml exec -T frontend npm run test:ci
      
      - name: Stop services
        run: |
          docker-compose -f docker/docker-compose.yml down

  build-and-push:
    name: Build and Push to ACR
    runs-on: ubuntu-latest
    needs: test-local
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./docker/Dockerfile
          target: production
          push: true
          tags: |
            ${{ env.DOCKER_REGISTRY }}/${{ env.FRONTEND_IMAGE }}:latest
            ${{ env.DOCKER_REGISTRY }}/${{ env.FRONTEND_IMAGE }}:${{ github.sha }}
          build-args: |
            NEXT_PUBLIC_API_URL=${{ secrets.AZURE_API_URL }}
            NEXT_PUBLIC_AZURE_CLIENT_ID=${{ secrets.AZURE_CLIENT_ID }}

  deploy-azure:
    name: Deploy to Azure
    runs-on: ubuntu-latest
    needs: build-and-push
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Azure Static Web Apps
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/"
          output_location: "out"
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.AZURE_API_URL }}
          NEXT_PUBLIC_ENABLE_PREVISIT: true
          NEXT_PUBLIC_ENABLE_APPOINT_READY: true
```

## Progress Tracking

### Local Development Checklist (Weeks 1-3)
- [ ] Docker environment setup
  - [ ] Frontend container configured
  - [ ] Backend container integrated
  - [ ] PostgreSQL database running
  - [ ] Redis cache running
  - [ ] Mock FHIR server running
- [ ] PreVisit.ai features
  - [ ] Symptom checker implemented
  - [ ] Medical history forms
  - [ ] Insurance verification
  - [ ] Appointment checklist
  - [ ] Dynamic questionnaire generator
- [ ] Appoint-Ready features
  - [ ] Patient context builder
  - [ ] Visit summary generator
  - [ ] Risk stratification
  - [ ] Care gap detection
  - [ ] Clinical decision support
- [ ] FHIR integration
  - [ ] FHIR client library
  - [ ] Resource mappers
  - [ ] Terminology services
- [ ] Local testing
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] E2E tests passing
  - [ ] Performance benchmarks met

### Azure Migration Checklist (Week 4)
- [ ] Azure infrastructure
  - [ ] Terraform applied
  - [ ] Static Web Apps deployed
  - [ ] CDN configured
  - [ ] App Insights enabled
- [ ] CI/CD pipeline
  - [ ] GitHub Actions configured
  - [ ] Docker build working
  - [ ] ACR push successful
  - [ ] Azure deployment automated
- [ ] Production features
  - [ ] Azure AD B2C authentication
  - [ ] Real FHIR server integration
  - [ ] Azure OpenAI services
  - [ ] SignalR real-time features
- [ ] Compliance & Security
  - [ ] HIPAA compliance validated
  - [ ] Security headers configured
  - [ ] Encryption enabled
  - [ ] Audit logging active

## Quick Start Commands

```bash
# Initial setup
git clone <repository>
cd azure-healthcare-frontend

# Start local development
cd docker
cp ../.env.example ../.env.local
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Run tests
docker-compose exec frontend npm test

# Stop environment
docker-compose down

# Migrate to Azure (after local testing)
bash scripts/migrate-to-azure.sh
```

## Key Benefits of This Approach

1. **Local-First Development**: Test everything in Docker before Azure costs
2. **PreVisit.ai Features**: Comprehensive pre-appointment preparation
3. **Appoint-Ready Features**: AI-powered visit context and preparation
4. **FHIR Integration**: Full healthcare interoperability
5. **Easy Testing**: Complete stack in Docker Compose
6. **Smooth Migration**: Docker images move directly to Azure
7. **Cost Effective**: No Azure costs during initial development
8. **Production Ready**: Same containers in dev and production

This plan allows you to build and test the complete application locally using AI agents and Docker, then seamlessly migrate to Azure when ready!
