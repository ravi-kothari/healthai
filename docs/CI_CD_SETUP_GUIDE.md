# CI/CD Pipeline Setup Guide

This guide outlines a CI/CD strategy using GitHub Actions for automated testing, building, and deployment to Azure.

## 1. CI/CD Strategy Overview

- **Platform**: GitHub Actions
- **Workflow**: Automated linting, testing, and Docker image creation with deployments to `staging` and `production`
- **Artifacts**: Versioned Docker images pushed to Azure Container Registry (ACR)
- **Environments**: Local → Staging → Production

## 2. Branching Strategy

We use a GitFlow-like branching model:

- **`main`**: Production environment. Protected branch. Merges only from `develop`
- **`develop`**: Integration branch for features. Deployed to staging
- **`feature/*`**: New features. Merged to `develop` via Pull Request
- **`hotfix/*`**: Urgent production fixes. Merged to both `main` and `develop`

### Branch Protection Rules

Configure in GitHub Settings → Branches:

**For `main`:**
- ✅ Require pull request reviews (1+ approvals)
- ✅ Require status checks to pass (all CI tests)
- ✅ Require branches to be up to date
- ✅ Include administrators
- ✅ Restrict who can push (only admins)

**For `develop`:**
- ✅ Require pull request reviews
- ✅ Require status checks to pass

## 3. Pre-commit Hooks Setup

Maintain code quality before commits using `pre-commit`.

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### Configuration

Create `.pre-commit-config.yaml` at project root:

```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: check-yaml
    -   id: end-of-file-fixer
    -   id: trailing-whitespace
    -   id: check-added-large-files
    -   id: check-merge-conflict

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        args: [backend/]

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: [backend/]

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        args: [backend/, --max-line-length=100]

-   repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
    -   id: prettier
        files: ^frontend/
        types_or: [javascript, jsx, ts, tsx, json, css]
```

### Usage

```bash
# Run on all files
pre-commit run --all-files

# Automatic run on git commit
git commit -m "your message"  # pre-commit runs automatically
```

## 4. Automated Testing Setup

### Backend Testing (pytest)

**Install dependencies:**
```bash
cd backend
pip install pytest pytest-cov pytest-asyncio httpx
```

**Create `backend/pytest.ini`:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    --cov=src
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    -v
```

**Run tests:**
```bash
pytest backend/ --cov=backend/src --cov-report=xml
```

### Frontend Testing (Jest + React Testing Library)

**Install dependencies:**
```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom
```

**Create `frontend/jest.config.js`:**
```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
}

module.exports = createJestConfig(customJestConfig)
```

**Create `frontend/jest.setup.js`:**
```javascript
import '@testing-library/jest-dom'
```

**Run tests:**
```bash
npm test -- --coverage
```

### E2E Testing (Playwright)

**Install Playwright:**
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install
```

**Create `frontend/playwright.config.ts`:**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3002',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3002',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Run E2E tests:**
```bash
npx playwright test
```

## 5. GitHub Actions Workflows

Create `.github/workflows/` directory in project root.

### 5.1. PR Validation Workflow

**`.github/workflows/ci.yml`:**

```yaml
name: CI Validation

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit
        run: pre-commit run --all-files

  backend-tests:
    name: Backend Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: healthcare_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/healthcare_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend

  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js 20.x
        uses: actions/setup-node@v3
        with:
          node-version: '20.x'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend

  e2e-tests:
    name: E2E Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: |
          cd backend/docker
          docker-compose up -d
          sleep 10

      - name: Use Node.js 20.x
        uses: actions/setup-node@v3
        with:
          node-version: '20.x'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Run Playwright tests
        run: |
          cd frontend
          npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/

  docker-build:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [lint, backend-tests, frontend-tests]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build Backend Image
        uses: docker/build-push-action@v4
        with:
          context: .
          file: backend/docker/Dockerfile.api
          push: false
          tags: backend:test
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build Frontend Image
        uses: docker/build-push-action@v4
        with:
          context: frontend
          file: frontend/Dockerfile
          push: false
          tags: frontend:test
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 5.2. Staging Deployment Workflow

**`.github/workflows/deploy-staging.yml`:**

```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

env:
  ACR_NAME: yourhealthcareacr
  AZURE_WEBAPP_NAME_BACKEND: healthcare-api-staging
  AZURE_WEBAPP_NAME_FRONTEND: healthcare-web-staging

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Log in to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Log in to ACR
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.ACR_NAME }}.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push backend image
        run: |
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }} \
            -t ${{ env.ACR_NAME }}.azurecr.io/backend:staging \
            -f backend/docker/Dockerfile.api .
          docker push ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }}
          docker push ${{ env.ACR_NAME }}.azurecr.io/backend:staging

      - name: Build and push frontend image
        run: |
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }} \
            -t ${{ env.ACR_NAME }}.azurecr.io/frontend:staging \
            -f frontend/Dockerfile frontend/
          docker push ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }}
          docker push ${{ env.ACR_NAME }}.azurecr.io/frontend:staging

      - name: Deploy Backend to Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME_BACKEND }}
          images: ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }}

      - name: Deploy Frontend to Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME_FRONTEND }}
          images: ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }}
```

### 5.3. Production Deployment Workflow

**`.github/workflows/deploy-production.yml`:**

```yaml
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Git SHA or tag to deploy'
        required: true
        type: string

env:
  ACR_NAME: yourhealthcareacr
  AZURE_WEBAPP_NAME_BACKEND: healthcare-api-prod
  AZURE_WEBAPP_NAME_FRONTEND: healthcare-web-prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.inputs.version }}

      - name: Log in to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS_PROD }}

      - name: Deploy Backend
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME_BACKEND }}
          images: ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.event.inputs.version }}

      - name: Deploy Frontend
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME_FRONTEND }}
          images: ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.event.inputs.version }}

      - name: Run health checks
        run: |
          sleep 30
          curl -f https://${{ env.AZURE_WEBAPP_NAME_BACKEND }}.azurewebsites.net/health || exit 1
          curl -f https://${{ env.AZURE_WEBAPP_NAME_FRONTEND }}.azurewebsites.net || exit 1
```

## 6. GitHub Secrets Configuration

Add these secrets in GitHub Settings → Secrets and variables → Actions:

### Required Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `AZURE_CREDENTIALS` | Azure service principal | `az ad sp create-for-rbac --sdk-auth` |
| `AZURE_CREDENTIALS_PROD` | Production service principal | Separate SP for prod |
| `ACR_USERNAME` | ACR username | Azure Portal → ACR → Access keys |
| `ACR_PASSWORD` | ACR password | Azure Portal → ACR → Access keys |

### Creating Azure Service Principal

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-healthcare" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth

# Copy the JSON output to AZURE_CREDENTIALS secret
```

## 7. Environment Variables Management

### Local Development

- Use `.env` files (already configured)
- Never commit `.env` files

### GitHub Actions

- Use repository secrets for sensitive values
- Use environment variables in workflow files for non-sensitive config

### Azure Deployment

Configure in Azure App Service → Configuration → Application settings:

```bash
# Using Azure CLI
az webapp config appsettings set \
  --name healthcare-api-staging \
  --resource-group healthcare-rg \
  --settings \
    DATABASE_URL="postgresql://..." \
    REDIS_URL="redis://..." \
    AZURE_OPENAI_API_KEY="@Microsoft.KeyVault(SecretUri=...)"
```

### Azure Key Vault Integration

For production secrets:

```bash
# Create Key Vault
az keyvault create \
  --name healthcare-kv \
  --resource-group healthcare-rg

# Add secret
az keyvault secret set \
  --vault-name healthcare-kv \
  --name "OpenAIApiKey" \
  --value "your-secret-value"

# Reference in App Service
# Use: @Microsoft.KeyVault(SecretUri=https://healthcare-kv.vault.azure.net/secrets/OpenAIApiKey)
```

## 8. Monitoring and Rollback

### Application Insights Setup

```bash
# Create Application Insights
az monitor app-insights component create \
  --app healthcare-insights \
  --location eastus \
  --resource-group healthcare-rg

# Get instrumentation key
az monitor app-insights component show \
  --app healthcare-insights \
  --resource-group healthcare-rg \
  --query instrumentationKey
```

### Rollback Procedure

**Option 1: Redeploy Previous Version**

1. Go to GitHub Actions
2. Click "Deploy to Production" workflow
3. Click "Run workflow"
4. Enter the previous Git SHA
5. Click "Run workflow"

**Option 2: Azure Portal Deployment Slots**

```bash
# Swap staging slot to production
az webapp deployment slot swap \
  --name healthcare-api-prod \
  --resource-group healthcare-rg \
  --slot staging \
  --target-slot production
```

### Monitoring Dashboards

Configure in Azure Portal → Application Insights → Dashboards:

- **API Performance**: Response times, request rates
- **Errors**: Exception rates, failed requests
- **Availability**: Uptime, health check status
- **Dependencies**: Database, Redis, external API health

## 9. Development Workflow Example

### Feature Development

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/medical-history-export

# 2. Make changes and test locally
# ... code changes ...
npm run dev  # frontend
docker-compose up  # backend

# 3. Run tests
cd backend && pytest
cd frontend && npm test

# 4. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add medical history export functionality"

# 5. Push and create PR
git push origin feature/medical-history-export

# 6. Create PR on GitHub (targets 'develop')
# CI workflow runs automatically

# 7. After approval and merge
# Staging deployment workflow runs automatically
```

### Hotfix Workflow

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-auth-bug

# 2. Fix and test
# ... fix the bug ...

# 3. Create PR to main
git push origin hotfix/critical-auth-bug

# 4. After merge to main
# Manually trigger production deployment

# 5. Merge back to develop
git checkout develop
git merge hotfix/critical-auth-bug
git push origin develop
```

## 10. Best Practices

### Code Quality

- ✅ Always run pre-commit hooks
- ✅ Write tests for new features (80%+ coverage)
- ✅ Use type hints (Python) and TypeScript
- ✅ Follow linting rules (Black, Prettier, ESLint)

### Security

- ✅ Never commit secrets or API keys
- ✅ Use Azure Key Vault for production secrets
- ✅ Rotate credentials regularly
- ✅ Enable branch protection rules
- ✅ Require PR reviews

### Deployment

- ✅ Test in staging before production
- ✅ Use semantic versioning for releases
- ✅ Tag production deployments
- ✅ Monitor after deployment
- ✅ Have rollback plan ready

### CI/CD

- ✅ Keep workflows fast (<10 min)
- ✅ Use caching for dependencies
- ✅ Fail fast on critical errors
- ✅ Send notifications on failures

---

**Next Steps:**
1. Set up GitHub repository
2. Configure branch protection rules
3. Add GitHub secrets
4. Create and test workflows
5. Set up Azure resources
6. Configure monitoring
