# Setup Script: Run Frontend Locally on Windows
# This script sets up and starts the frontend outside Docker

Write-Host "`n=== Healthcare AI - Local Frontend Setup ===" -ForegroundColor Cyan
Write-Host "This will run the frontend locally while backend stays in Docker`n" -ForegroundColor Cyan

# Step 1: Check Node.js is installed
Write-Host "[1/5] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
    Write-Host "✅ npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    Write-Host "   Download the LTS version (18.x or higher)" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 2: Check backend services are running
Write-Host "[2/5] Checking backend services..." -ForegroundColor Yellow
Set-Location backend\docker
$services = docker-compose ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker services not running" -ForegroundColor Red
    Write-Host "   Starting backend services..." -ForegroundColor Yellow
    docker-compose up -d postgres redis api
    Start-Sleep -Seconds 10
}

# Verify API is accessible
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($health.StatusCode -eq 200) {
        Write-Host "✅ Backend API is running" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Backend API not responding. Starting services..." -ForegroundColor Yellow
    docker-compose up -d postgres redis api
    Write-Host "   Waiting for services to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
}
Write-Host ""

# Step 3: Navigate to frontend and check .env.local
Write-Host "[3/5] Checking frontend configuration..." -ForegroundColor Yellow
Set-Location ..\..\frontend

if (-not (Test-Path ".env.local")) {
    Write-Host "⚠️  .env.local not found. Creating from example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env.local
        Write-Host "✅ Created .env.local" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Creating basic .env.local..." -ForegroundColor Yellow
        @"
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Application
NEXT_PUBLIC_APP_NAME=AI Healthcare Platform
NEXT_PUBLIC_APP_VERSION=1.0.0
"@ | Out-File -FilePath .env.local -Encoding utf8
        Write-Host "✅ Created .env.local" -ForegroundColor Green
    }
} else {
    Write-Host "✅ .env.local exists" -ForegroundColor Green
}

# Verify API URL is correct
$apiUrl = Get-Content .env.local | Select-String "NEXT_PUBLIC_API_URL"
if ($apiUrl -match "http://localhost:8000") {
    Write-Host "✅ API URL configured correctly" -ForegroundColor Green
} else {
    Write-Host "⚠️  Updating API URL to http://localhost:8000..." -ForegroundColor Yellow
    (Get-Content .env.local) -replace 'NEXT_PUBLIC_API_URL=.*', 'NEXT_PUBLIC_API_URL=http://localhost:8000' | Set-Content .env.local
    Write-Host "✅ Updated API URL" -ForegroundColor Green
}
Write-Host ""

# Step 4: Install dependencies
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "   Running npm install (this may take a few minutes)..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ npm install failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
    Write-Host "   (Run 'npm install' manually if you need to update packages)" -ForegroundColor Gray
}
Write-Host ""

# Step 5: Start the frontend
Write-Host "[5/5] Starting frontend development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Frontend Starting ===" -ForegroundColor Cyan
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the frontend" -ForegroundColor Gray
Write-Host "To stop backend: cd backend\docker && docker-compose down" -ForegroundColor Gray
Write-Host ""

npm run dev
