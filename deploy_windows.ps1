# Windows Deployment Script for Healthcare App
# Prerequisites: Docker Desktop for Windows (with WSL2 backend recommended)

Write-Host "Starting Healthcare App Deployment..." -ForegroundColor Cyan

# 1. Check if Docker is running
Write-Host "Checking Docker status..."
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "Docker is running." -ForegroundColor Green

# 2. Build Containers
Write-Host "Building Docker containers (this may take a while)..." -ForegroundColor Yellow
docker-compose -f backend/docker/docker-compose.yml build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to build containers." -ForegroundColor Red
    exit 1
}
Write-Host "Build complete." -ForegroundColor Green

# 3. Start Containers
Write-Host "Starting containers..." -ForegroundColor Yellow
docker-compose -f backend/docker/docker-compose.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start containers." -ForegroundColor Red
    exit 1
}
Write-Host "Containers started." -ForegroundColor Green

# 4. Wait for Database
Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
$retries = 30
$connected = $false
for ($i = 0; $i -lt $retries; $i++) {
    docker exec healthcare-postgres pg_isready -U healthcare_user -d healthcare_db > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $connected = $true
        break
    }
    Start-Sleep -Seconds 2
    Write-Host "." -NoNewline
}
Write-Host ""

if (-not $connected) {
    Write-Host "Error: Database failed to start in time." -ForegroundColor Red
    exit 1
}
Write-Host "Database is ready." -ForegroundColor Green

# 5. Seed Data
Write-Host "Seeding test data..." -ForegroundColor Yellow
docker exec healthcare-api python src/api/scripts/seed_test_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Data seeding encountered an issue (or data already exists)." -ForegroundColor Yellow
} else {
    Write-Host "Data seeded successfully." -ForegroundColor Green
}

# 6. Summary
Write-Host "`nDeployment Complete!" -ForegroundColor Cyan
Write-Host "----------------------------------------"
Write-Host "Frontend:   http://localhost:3000"
Write-Host "Backend API: http://localhost:8000/docs"
Write-Host "FHIR Server: http://localhost:8081"
Write-Host "----------------------------------------"
Write-Host "Login Credentials:"
Write-Host "  Provider: doctor@healthai.com / password123"
Write-Host "  Admin:    admin@healthai.com / admin123"
Write-Host "----------------------------------------"
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
