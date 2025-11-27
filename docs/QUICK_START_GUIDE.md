# QUICK START GUIDE FOR CLAUDE CODE

**⚡ Fast-track guide to start building immediately**

---

## 🚀 Step 1: Initial Setup (5 minutes)

### Create Project Structure
```bash
# Create main directories
mkdir -p azure-healthcare-app/{backend,frontend,docs}
cd azure-healthcare-app

# Initialize git
git init
git checkout -b develop

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
.env
.env.local
venv/
*.egg-info/

# Node
node_modules/
.next/
out/
*.log

# Docker
*.env

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

git add .gitignore
git commit -m "chore: initial project setup"
```

---

## 🐳 Step 2: Backend Docker Setup (10 minutes)

### Create Backend Structure
```bash
cd backend
mkdir -p {src/api/{routers,services,models,schemas,middleware},tests/{unit,integration},docker/init-scripts}
touch src/api/{__init__.py,main.py,config.py,dependencies.py}
```

### Create docker-compose.yml
```bash
cat > docker/docker-compose.yml << 'EOF'
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
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/healthcare
      - REDIS_URL=redis://redis:6379
      - FHIR_SERVER_URL=http://fhir-server:8080/fhir
      - JWT_SECRET_KEY=dev-secret-key-change-in-production
      - LOG_LEVEL=DEBUG
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
    networks:
      - healthcare-network

  redis:
    image: redis:7-alpine
    container_name: healthcare-redis
    ports:
      - "6379:6379"
    networks:
      - healthcare-network

  fhir-server:
    image: hapiproject/hapi:latest
    container_name: healthcare-fhir
    ports:
      - "8080:8080"
    environment:
      - hapi.fhir.version=R4
    networks:
      - healthcare-network

networks:
  healthcare-network:
    driver: bridge

volumes:
  postgres-data:
EOF
```

### Create Dockerfile
```bash
cat > docker/Dockerfile.api << 'EOF'
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base as development

COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF
```

### Create requirements.txt
```bash
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
openai==1.3.5
httpx==0.25.1
python-dotenv==1.0.0
EOF

cat > requirements-dev.txt << 'EOF'
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1
EOF
```

### Create .env.local
```bash
cat > .env.local << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthcare
REDIS_URL=redis://localhost:6379
FHIR_SERVER_URL=http://localhost:8080/fhir
AZURE_OPENAI_ENDPOINT=http://localhost:8081
AZURE_OPENAI_API_KEY=mock-key-for-local-dev
JWT_SECRET_KEY=dev-secret-key-please-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=DEBUG
ENVIRONMENT=development
EOF
```

---

## 🎯 Step 3: First Backend Code (15 minutes)

### Create main.py
```bash
cat > src/api/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Healthcare API",
    description="Healthcare application with PreVisit.ai and Appoint-Ready features",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Healthcare API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api",
        "environment": "development"
    }

@app.get("/info")
async def info():
    """API information"""
    return {
        "title": "AI Healthcare API",
        "description": "PreVisit.ai and Appoint-Ready features",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

### Create config.py
```bash
cat > src/api/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # FHIR
    FHIR_SERVER_URL: str
    
    # Azure Services
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env.local"
        case_sensitive = True

settings = Settings()
EOF
```

---

## ✅ Step 4: Test Your Setup (5 minutes)

### Start Docker services
```bash
cd docker
docker-compose up -d

# Wait for services to start
sleep 10

# Check service health
docker-compose ps
docker-compose logs api
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"api","environment":"development"}

# API info
curl http://localhost:8000/info

# Open API docs in browser
# http://localhost:8000/docs
```

### Verify all services
```bash
# PostgreSQL
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping

# FHIR Server
curl http://localhost:8080/fhir/metadata
```

---

## 📋 Step 5: First Commit (2 minutes)

```bash
cd ..  # Back to project root
git add .
git commit -m "feat: initial backend setup with Docker

- Add FastAPI application with health check
- Configure Docker Compose with PostgreSQL, Redis, FHIR
- Set up development environment
- Add basic configuration management

Task 0.1.1, 0.1.2, 0.1.3, 0.1.4 complete"

git push origin develop
```

---

## 🎯 Step 6: Update Progress Tracker (1 minute)

Update PROJECT_PROGRESS.md:
```markdown
- [x] **Task 0.1.1**: Create project repository structure
  - Status: Complete (2024-01-15)
  - Notes: Created backend, frontend, docs directories
  
- [x] **Task 0.1.2**: Set up Docker Compose for local development
  - Status: Complete (2024-01-15)
  - Notes: All services running and healthy
  
- [x] **Task 0.1.3**: Configure environment variables
  - Status: Complete (2024-01-15)
  
- [x] **Task 0.1.4**: Initialize FastAPI application
  - Status: Complete (2024-01-15)
  - Notes: Health check endpoint working
```

---

## 🚀 What's Next?

You're ready to build! Follow this sequence:

### Immediate Next Steps (Today):
1. **Task 0.1.5**: Set up database with SQLAlchemy
   - Reference: CLAUDE.md - Database setup section
   - Create models in `src/api/models/`

2. **Task 0.1.6**: Implement authentication (JWT)
   - Reference: CLAUDE.md - Authentication section
   - Create `src/api/auth/jwt_handler.py`

3. **Task 0.1.7**: Implement Patient CRUD
   - Create `src/api/routers/patients.py`

### This Week:
- Complete Week 1 tasks in PROJECT_PROGRESS.md
- Focus on backend foundation
- Write tests for each feature

### Daily Routine:
1. Check PROJECT_PROGRESS.md for next task
2. Read relevant section in deployment plans
3. Implement feature following CLAUDE.md patterns
4. Write tests
5. Run tests: `docker-compose exec api pytest tests/ -v`
6. Commit with proper message
7. Update progress tracker

---

## 📚 Key Files to Reference

**When coding backend:**
- `Updated_Azure_Backend_Deployment_Plan.md` - Detailed implementation steps
- `CLAUDE.md` - Code patterns and examples
- `PROJECT_PROGRESS.md` - Track your progress

**When coding frontend (later):**
- `Updated_Azure_Frontend_Deployment_Plan.md` - Frontend implementation
- `CLAUDE.md` - React patterns and components

**For project management:**
- `PROJECT_MANAGEMENT_GUIDE.md` - Best practices
- `PROJECT_PROGRESS.md` - Task tracking

---

## 🆘 Quick Troubleshooting

**Services won't start:**
```bash
docker-compose down
docker-compose up -d --build
docker-compose logs -f
```

**API not responding:**
```bash
docker-compose logs api
docker-compose exec api python -c "from api.main import app; print(app)"
```

**Database connection error:**
```bash
docker-compose exec postgres pg_isready
docker-compose exec api python -c "import os; print(os.getenv('DATABASE_URL'))"
```

**Port already in use:**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

---

## ✨ Success Checklist

After completing these steps, you should have:
- [x] Project structure created
- [x] Docker Compose running all services
- [x] FastAPI application responding to requests
- [x] Health check endpoint working
- [x] API documentation accessible at /docs
- [x] All services healthy (postgres, redis, fhir-server)
- [x] First commit pushed to git
- [x] Progress tracker updated

**You're ready to build! Start with Task 0.1.5 in PROJECT_PROGRESS.md** 🎉

---

## 💡 Pro Tips

1. **Run tests frequently**: After every feature implementation
2. **Commit small changes**: Don't wait until end of day
3. **Update progress tracker**: After completing each task
4. **Read the plans**: Don't guess, follow the detailed specifications
5. **Test in Docker**: Always test in the Docker environment
6. **Ask when stuck**: Check documentation first, then ask
7. **Document decisions**: Update PROJECT_PROGRESS.md with notes

**Remember**: Local development first, Azure migration later. Build it right, then deploy it!

Good luck! 🚀
