# PROJECT MANAGEMENT GUIDE

**For**: Claude Code Agent & Development Team
**Purpose**: Effective project and code management practices
**Last Updated**: [Current Date]

---

## 📋 Daily Workflow

### Every Coding Session

1. **START**: Check Current Status
   ```bash
   # 1. Pull latest changes
   git pull origin develop
   
   # 2. Check progress tracker
   cat PROJECT_PROGRESS.md | grep "In Progress\|Not Started" | head -n 5
   
   # 3. Review relevant documentation
   # Example: If working on PreVisit features:
   grep -A 30 "PreVisit.ai" Updated_Azure_Backend_Deployment_Plan.md
   ```

2. **WORK**: Implement Feature
   - Follow the exact structure in deployment plans
   - Reference CLAUDE.md for patterns and examples
   - Write tests as you code (TDD approach)
   - Run tests frequently

3. **TEST**: Verify Implementation
   ```bash
   # Unit tests
   pytest tests/unit/test_feature.py -v
   
   # Integration tests
   pytest tests/integration/test_feature_integration.py -v
   
   # Manual testing
   curl http://localhost:8000/api/endpoint
   ```

4. **COMMIT**: Save Progress
   ```bash
   # Stage changes
   git add .
   
   # Commit with meaningful message
   git commit -m "feat(previsit): implement symptom analyzer service
   
   - Add SymptomAnalyzer class with analyze_symptoms method
   - Integrate Azure OpenAI for medical analysis
   - Add unit tests with 85% coverage
   - Update PROJECT_PROGRESS.md Task 0.2.2"
   
   # Push to feature branch
   git push origin feature/previsit-symptom-analyzer
   ```

5. **UPDATE**: Track Progress
   ```bash
   # Update PROJECT_PROGRESS.md
   # Mark task as complete
   # Add notes about implementation
   # Document any decisions or blockers
   ```

---

## 🗂️ File Organization Best Practices

### Backend Structure Rules

```
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py              # Package initialization
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Configuration management
│   │   ├── dependencies.py          # Dependency injection
│   │   │
│   │   ├── routers/                 # API endpoints (one file per resource)
│   │   │   ├── __init__.py
│   │   │   ├── patients.py         # Patient CRUD endpoints
│   │   │   ├── appointments.py     # Appointment endpoints
│   │   │   ├── previsit.py         # PreVisit.ai endpoints
│   │   │   └── appoint_ready.py    # Appoint-Ready endpoints
│   │   │
│   │   ├── services/                # Business logic (organized by feature)
│   │   │   ├── __init__.py
│   │   │   ├── previsit/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── symptom_analyzer.py
│   │   │   │   ├── triage_engine.py
│   │   │   │   └── questionnaire_generator.py
│   │   │   ├── appoint_ready/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── context_builder.py
│   │   │   │   ├── risk_calculator.py
│   │   │   │   └── care_gap_detector.py
│   │   │   ├── fhir/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py
│   │   │   │   └── validator.py
│   │   │   └── ai/
│   │   │       ├── __init__.py
│   │   │       ├── openai_service.py
│   │   │       └── speech_service.py
│   │   │
│   │   ├── models/                  # Database models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base model class
│   │   │   ├── patient.py
│   │   │   ├── appointment.py
│   │   │   ├── user.py
│   │   │   └── previsit.py
│   │   │
│   │   ├── schemas/                 # Pydantic schemas (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── patient_schemas.py
│   │   │   ├── previsit_schemas.py
│   │   │   └── appoint_ready_schemas.py
│   │   │
│   │   └── middleware/              # Custom middleware
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── audit_logging.py
│   │       └── error_handling.py
│   │
│   └── functions/                   # Azure Functions
│       ├── audio_processor/
│       ├── note_generator/
│       └── shared/
│
├── tests/                           # Test files mirror src/ structure
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration and fixtures
│   ├── unit/
│   │   ├── test_symptom_analyzer.py
│   │   └── test_triage_engine.py
│   ├── integration/
│   │   └── test_previsit_flow.py
│   └── e2e/
│       └── test_user_journeys.py
│
├── docker/                          # Docker configuration
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── pytest.ini                       # Pytest configuration
├── .env.example                     # Example environment variables
└── README.md                        # Backend-specific documentation
```

### Frontend Structure Rules

```
frontend/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Home page
│   │   ├── (auth)/                # Auth route group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (patient)/             # Patient portal (route group)
│   │   │   ├── dashboard/
│   │   │   ├── appointments/
│   │   │   └── previsit/
│   │   │       ├── symptoms/
│   │   │       ├── history/
│   │   │       ├── questionnaire/
│   │   │       └── checklist/
│   │   └── (provider)/            # Provider portal
│   │       ├── dashboard/
│   │       ├── patients/
│   │       └── appoint-ready/
│   │           ├── context/
│   │           ├── risk-assessment/
│   │           └── care-gaps/
│   │
│   ├── components/                # React components
│   │   ├── ui/                   # Base UI components (Radix UI)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── previsit/             # PreVisit-specific components
│   │   │   ├── SymptomChecker.tsx
│   │   │   ├── MedicalHistoryForm.tsx
│   │   │   └── AppointmentChecklist.tsx
│   │   ├── appoint-ready/        # Appoint-Ready components
│   │   │   ├── PatientContextCard.tsx
│   │   │   ├── RiskStratification.tsx
│   │   │   └── CareGapAlert.tsx
│   │   └── shared/               # Shared components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── LoadingSpinner.tsx
│   │
│   ├── lib/                      # Utility functions and services
│   │   ├── previsit/
│   │   │   ├── symptom-analyzer.ts
│   │   │   └── questionnaire-generator.ts
│   │   ├── appoint-ready/
│   │   │   ├── context-builder.ts
│   │   │   └── risk-calculator.ts
│   │   ├── fhir/
│   │   │   └── fhir-client.ts
│   │   ├── auth/
│   │   │   └── jwt-handler.ts
│   │   └── utils/
│   │       ├── api-client.ts
│   │       └── formatters.ts
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── usePreVisit.ts
│   │   ├── useAppointReady.ts
│   │   └── useFHIR.ts
│   │
│   ├── types/                    # TypeScript type definitions
│   │   ├── patient.types.ts
│   │   ├── previsit.types.ts
│   │   ├── appoint-ready.types.ts
│   │   └── fhir.types.ts
│   │
│   └── styles/                   # Global styles
│       └── globals.css
│
├── tests/                        # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── public/                       # Static assets
├── docker/                       # Docker configuration
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── .env.example
└── README.md
```

---

## 💾 Git Workflow

### Branch Strategy

```
main (production)
  â†'
develop (integration)
  â†'
feature/feature-name (your work)
```

### Branch Naming Convention

```bash
# Features
feature/previsit-symptom-checker
feature/appoint-ready-context-builder

# Bug fixes
fix/symptom-analyzer-null-check
fix/api-timeout-issue

# Documentation
docs/update-deployment-guide
docs/add-api-examples

# Refactoring
refactor/optimize-database-queries
refactor/simplify-auth-flow

# Testing
test/add-integration-tests
test/improve-coverage
```

### Commit Message Format

Follow Conventional Commits:

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Build process or tooling changes

**Examples:**

```bash
# Good commit messages
git commit -m "feat(previsit): add symptom analyzer with AI integration

- Implement SymptomAnalyzer class
- Integrate Azure OpenAI GPT-4o
- Add triage level assessment
- Include unit tests with 85% coverage

Closes #42"

git commit -m "fix(auth): resolve JWT token expiration issue

The token expiration was not properly checked,
causing unexpected logouts. Added proper validation.

Fixes #58"

git commit -m "test(appoint-ready): add unit tests for risk calculator

- Test age-based risk factors
- Test comorbidity assessment
- Test edge cases
- Achieve 90% coverage"

# Bad commit messages (avoid these)
git commit -m "updated stuff"
git commit -m "fix bug"
git commit -m "changes"
```

### Pull Request Workflow

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature
   ```

2. **Make Changes and Commit**
   ```bash
   # Make changes
   git add .
   git commit -m "feat: implement feature"
   ```

3. **Keep Branch Updated**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/new-feature
   git rebase develop
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/new-feature
   # Create PR on GitHub/GitLab
   ```

5. **PR Checklist**
   - [ ] All tests passing
   - [ ] Code coverage maintained or improved
   - [ ] Documentation updated
   - [ ] PROJECT_PROGRESS.md updated
   - [ ] No merge conflicts
   - [ ] Security scan passed
   - [ ] Manual testing completed

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \    E2E Tests (Few, Slow, Expensive)
      /    \   - Test complete user journeys
     /──────\  - Use Playwright
    /        \ 
   /   Integration Tests (Some, Medium Speed)
  /     - Test service interactions
 /      - Test API endpoints
/────────────────────\
Integration Tests
/                    \
/  Unit Tests (Many, Fast, Cheap)
/   - Test individual functions
/   - Mock external dependencies
────────────────────────
```

### Test Coverage Goals

- **Backend**: 80%+ overall, 90%+ for critical services
- **Frontend**: 70%+ overall, 80%+ for business logic

### Testing Commands

```bash
# Backend testing
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_symptom_analyzer.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run with markers
pytest -m "not slow" -v

# Frontend testing
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e

# Run E2E in headed mode (see browser)
npm run test:e2e -- --headed
```

---

## 📝 Code Review Guidelines

### When Requesting Review

**Include in PR Description:**
1. **What**: Brief description of changes
2. **Why**: Reason for the changes
3. **How**: Implementation approach
4. **Testing**: How you tested it
5. **Screenshots**: For UI changes
6. **Related Issues**: Link to tickets/issues

**Example PR Description:**
```markdown
## What
Implements PreVisit.ai symptom analyzer service

## Why
Needed to provide AI-powered symptom analysis for patients before appointments

## How
- Created SymptomAnalyzer class using Azure OpenAI
- Implemented triage engine for urgency assessment
- Added questionnaire generation based on symptoms

## Testing
- Added unit tests (85% coverage)
- Added integration tests for API endpoints
- Manual testing with various symptom combinations

## Screenshots
[Include relevant screenshots]

## Related Issues
Closes #42
Related to #38
```

### When Reviewing Code

**Check For:**
- [ ] Code follows project structure
- [ ] Functions have docstrings
- [ ] Type hints present (Python) or types defined (TypeScript)
- [ ] No hardcoded values (use environment variables)
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] Tests included and passing
- [ ] No security vulnerabilities
- [ ] Performance considerations
- [ ] Documentation updated if needed

**Review Comments Format:**
```
🔴 CRITICAL: Security issue - API key exposed
🟡 SUGGESTION: Consider using async/await here
🟢 MINOR: Typo in comment
💡 IDEA: Could refactor this for better readability
âś… APPROVED: Looks good!
```

---

## 🔍 Code Quality Tools

### Automated Checks

```bash
# Backend (Python)

# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/
pylint src/

# Type checking
mypy src/

# Security
bandit -r src/
safety check

# Frontend (TypeScript)

# Code formatting
npm run format

# Linting
npm run lint

# Type checking
npm run type-check

# Security
npm audit
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

Install:
```bash
pip install pre-commit
pre-commit install
```

---

## 📊 Monitoring Progress

### Daily Standup Questions

Answer these daily in PROJECT_PROGRESS.md:

1. **What did I complete yesterday?**
   - List completed tasks with task IDs
   
2. **What will I work on today?**
   - Identify next tasks from progress tracker
   
3. **Any blockers?**
   - Document in Blockers section
   
4. **Any decisions made?**
   - Add to Decisions Log

### Weekly Review

Every week, review and update:

1. **Phase Progress**
   - Update percentage complete
   - Adjust timeline if needed

2. **Metrics**
   - Test coverage numbers
   - Performance metrics
   - Code quality scores

3. **Risks**
   - Identify potential issues
   - Document mitigation plans

4. **Lessons Learned**
   - What went well
   - What could improve
   - Actions for next week

---

## 🚨 Troubleshooting Common Issues

### Docker Issues

**Problem**: Services won't start
```bash
# Solution 1: Check logs
docker-compose logs -f service-name

# Solution 2: Rebuild containers
docker-compose down
docker-compose up -d --build

# Solution 3: Clean slate
docker-compose down -v  # Removes volumes
docker-compose up -d --build
```

**Problem**: Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Issues

**Problem**: Migration fails
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec api alembic upgrade head
```

**Problem**: Can't connect to database
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Verify connection string
docker-compose exec api python -c "import os; print(os.getenv('DATABASE_URL'))"
```

### Test Issues

**Problem**: Tests failing locally but pass in CI
```bash
# Ensure clean environment
docker-compose down -v
docker-compose up -d
docker-compose exec api pytest tests/ -v
```

**Problem**: Import errors in tests
```bash
# Check PYTHONPATH
docker-compose exec api python -c "import sys; print(sys.path)"

# Reinstall dependencies
docker-compose exec api pip install -r requirements.txt
```

---

## 📚 Documentation Standards

### Code Documentation

**Python (Docstrings):**
```python
def analyze_symptoms(
    self,
    symptoms: List[Symptom],
    patient_age: int,
    patient_gender: str
) -> SymptomAnalysis:
    """
    Analyze patient symptoms using AI to provide triage assessment.
    
    This method uses Azure OpenAI to analyze symptoms and generate
    a comprehensive assessment including urgency level, possible
    conditions, and recommendations.
    
    Args:
        symptoms: List of Symptom objects containing patient symptoms
        patient_age: Patient's age in years
        patient_gender: Patient's gender ('male', 'female', 'other')
        
    Returns:
        SymptomAnalysis object containing:
            - urgency: Urgency level (low/moderate/high/emergency)
            - triage_level: Triage score 1-5
            - possible_conditions: List of possible diagnoses
            - recommendations: Treatment recommendations
            - requires_immediate_attention: Boolean flag
            
    Raises:
        ValueError: If symptoms list is empty
        OpenAIError: If AI service is unavailable
        
    Example:
        >>> analyzer = SymptomAnalyzer(openai_client)
        >>> symptoms = [Symptom(name="headache", severity="moderate")]
        >>> result = await analyzer.analyze_symptoms(
        ...     symptoms=symptoms,
        ...     patient_age=45,
        ...     patient_gender="female"
        ... )
        >>> print(result.urgency)
        "moderate"
    """
```

**TypeScript (JSDoc):**
```typescript
/**
 * Analyzes patient symptoms and returns AI-powered assessment
 * 
 * @param symptoms - Array of symptom objects
 * @param patientAge - Patient's age in years
 * @param patientGender - Patient's gender
 * @returns Promise resolving to symptom analysis
 * @throws {Error} If API request fails
 * 
 * @example
 * ```typescript
 * const result = await analyzeSymptoms(
 *   [{ name: "headache", severity: "moderate" }],
 *   45,
 *   "female"
 * );
 * console.log(result.urgency); // "moderate"
 * ```
 */
async function analyzeSymptoms(
  symptoms: Symptom[],
  patientAge: number,
  patientGender: string
): Promise<SymptomAnalysis> {
  // Implementation
}
```

### API Documentation

Use OpenAPI/Swagger for API documentation:

```python
@router.post(
    "/analyze-symptoms",
    response_model=SymptomAnalysis,
    summary="Analyze patient symptoms",
    description="""
    Analyzes patient symptoms using AI to provide triage assessment,
    possible conditions, and recommendations.
    
    **Requires authentication**: Yes
    **Rate limit**: 10 requests per minute
    """,
    responses={
        200: {
            "description": "Successful analysis",
            "content": {
                "application/json": {
                    "example": {
                        "urgency": "moderate",
                        "triage_level": 3,
                        "possible_conditions": ["tension headache", "migraine"],
                        "recommendations": ["rest", "hydration"]
                    }
                }
            }
        },
        400: {"description": "Invalid input"},
        401: {"description": "Not authenticated"},
        429: {"description": "Rate limit exceeded"}
    }
)
async def analyze_symptoms(...):
    ...
```

---

## ✅ Definition of Done

A task is considered "done" when:

### Code
- [ ] Implementation matches specification in deployment plans
- [ ] Code follows project structure and conventions
- [ ] All functions have docstrings/JSDoc comments
- [ ] Type hints (Python) or types (TypeScript) present
- [ ] No hardcoded values (uses environment variables)
- [ ] Error handling implemented
- [ ] Input validation added
- [ ] Logging added for debugging

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing (if applicable)
- [ ] Manual testing completed
- [ ] Edge cases tested
- [ ] Error scenarios tested
- [ ] Code coverage meets targets

### Documentation
- [ ] Code comments added where needed
- [ ] API documentation updated (if API changes)
- [ ] README updated (if setup changes)
- [ ] PROJECT_PROGRESS.md updated

### Quality
- [ ] Code reviewed (or self-reviewed if solo)
- [ ] No linting errors
- [ ] Security scan passed
- [ ] Performance acceptable
- [ ] No console errors/warnings

### Git
- [ ] Committed with proper message format
- [ ] Pushed to feature branch
- [ ] PR created (if applicable)
- [ ] CI/CD checks passing

---

## 🎯 Quick Reference Checklist

**Before Starting Work:**
- [ ] Check PROJECT_PROGRESS.md for next task
- [ ] Read relevant documentation section
- [ ] Ensure Docker environment is running
- [ ] Create/checkout feature branch

**During Work:**
- [ ] Follow file structure from deployment plans
- [ ] Reference CLAUDE.md for patterns
- [ ] Write tests alongside code
- [ ] Run tests frequently
- [ ] Commit small, logical changes

**After Completing Feature:**
- [ ] All tests passing
- [ ] Manual testing done
- [ ] Code reviewed/self-reviewed
- [ ] Documentation updated
- [ ] PROJECT_PROGRESS.md updated
- [ ] Git commit with proper message
- [ ] Push to remote

**Weekly:**
- [ ] Review progress
- [ ] Update metrics
- [ ] Document lessons learned
- [ ] Plan next week's work

---

## 🆘 Getting Help

1. **Check Documentation First**
   - CLAUDE.md for patterns
   - Deployment plans for specifications
   - PROJECT_PROGRESS.md for context

2. **Search Existing Issues**
   - GitHub issues
   - Stack Overflow
   - Azure documentation

3. **Ask Specific Questions**
   - Include error messages
   - Share relevant code
   - Describe what you've tried

4. **Document the Solution**
   - Update troubleshooting section
   - Add to lessons learned
   - Share with team

---

**Remember**: Good project management is about consistent, incremental progress with clear communication and documentation. Update the tracker, commit often, test thoroughly, and don't skip steps!
