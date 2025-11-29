# Nuclear Reset Script - Complete Database Wipe
# Use this when normal reset doesn't work due to persistent database state

Write-Host "`n=== NUCLEAR RESET - Complete Database Wipe ===" -ForegroundColor Red
Write-Host "This will completely destroy all Docker containers, volumes, and networks" -ForegroundColor Yellow
Write-Host "Use this only if the normal reset script fails`n" -ForegroundColor Yellow

$confirmation = Read-Host "Are you SURE you want to continue? Type 'RESET' to confirm"
if ($confirmation -ne 'RESET') {
    Write-Host "Aborted." -ForegroundColor Red
    exit
}

Set-Location backend\docker

Write-Host "`n[1/10] Stopping all containers..." -ForegroundColor Yellow
docker-compose down
Write-Host "✅ Stopped`n" -ForegroundColor Green

Write-Host "[2/10] Removing all project containers..." -ForegroundColor Yellow
docker-compose rm -f -v
Write-Host "✅ Removed`n" -ForegroundColor Green

Write-Host "[3/10] Removing all volumes..." -ForegroundColor Yellow
docker volume rm docker_postgres_data 2>$null
docker volume rm docker_redis_data 2>$null
docker volume rm docker_azurite_data 2>$null
Write-Host "✅ Volumes removed`n" -ForegroundColor Green

Write-Host "[4/10] Removing network..." -ForegroundColor Yellow
docker network rm docker_healthcare-network 2>$null
Write-Host "✅ Network removed`n" -ForegroundColor Green

Write-Host "[5/10] Pruning Docker system..." -ForegroundColor Yellow
docker system prune -f
Write-Host "✅ Pruned`n" -ForegroundColor Green

Write-Host "[6/10] Rebuilding API container..." -ForegroundColor Yellow
docker-compose build --no-cache api
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ API rebuilt`n" -ForegroundColor Green

Write-Host "[7/10] Starting database..." -ForegroundColor Yellow
docker-compose up -d postgres redis
Write-Host "⏳ Waiting 25 seconds for database to fully initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 25

# Verify postgres is actually ready
$retries = 0
$maxRetries = 10
$ready = $false

while (-not $ready -and $retries -lt $maxRetries) {
    $status = docker-compose exec -T postgres pg_isready -U healthcare_user 2>$null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        Write-Host "✅ Database is ready`n" -ForegroundColor Green
    } else {
        $retries++
        Write-Host "⏳ Database not ready yet, waiting... (attempt $retries/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}

if (-not $ready) {
    Write-Host "❌ Database failed to start properly" -ForegroundColor Red
    Write-Host "Check logs: docker-compose logs postgres" -ForegroundColor Yellow
    exit 1
}

Write-Host "[8/10] Starting API..." -ForegroundColor Yellow
docker-compose up -d api
Write-Host "⏳ Waiting 15 seconds for API to start..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# Verify API is healthy
$apiHealthy = $false
$retries = 0
while (-not $apiHealthy -and $retries -lt 10) {
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($health.StatusCode -eq 200) {
            $apiHealthy = $true
            Write-Host "✅ API is healthy`n" -ForegroundColor Green
        }
    } catch {
        $retries++
        Write-Host "⏳ API not ready yet, waiting... (attempt $retries/10)" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}

if (-not $apiHealthy) {
    Write-Host "⚠️  API may not be fully ready, but continuing anyway..." -ForegroundColor Yellow
}

Write-Host "[9/10] Running database migrations..." -ForegroundColor Yellow
Write-Host "⏳ Waiting 5 more seconds to ensure DNS is ready..." -ForegroundColor Gray
Start-Sleep -Seconds 5

docker-compose exec -T api alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Migration failed!" -ForegroundColor Red
    Write-Host "`nDiagnostics:" -ForegroundColor Cyan

    Write-Host "`n1. Check if API can connect to database:" -ForegroundColor Yellow
    docker-compose exec -T api python -c "import socket; print('Resolving postgres:', socket.gethostbyname('postgres'))" 2>$null

    Write-Host "`n2. Database status:" -ForegroundColor Yellow
    docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -c "SELECT 1;" 2>$null

    Write-Host "`n3. Recent API logs:" -ForegroundColor Yellow
    docker-compose logs api --tail 20

    Write-Host "`n4. If you see DNS errors, try:" -ForegroundColor Cyan
    Write-Host "   - Restart Docker Desktop completely" -ForegroundColor White
    Write-Host "   - Run this script again" -ForegroundColor White
    Write-Host "   - Or try: docker-compose restart api && Start-Sleep 10 && docker-compose exec api alembic upgrade head" -ForegroundColor White

    exit 1
}
Write-Host "✅ Migrations completed successfully`n" -ForegroundColor Green

Write-Host "[10/10] Verifying migration..." -ForegroundColor Yellow
docker-compose exec -T api alembic current
Write-Host ""

Write-Host "=== Service Status ===" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n=== ✅ Nuclear Reset Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Database is completely fresh and migrations are applied." -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create a user: http://localhost:8000/docs (POST /api/auth/register)" -ForegroundColor White
Write-Host "2. Start frontend: cd ..\..\frontend && npm run dev" -ForegroundColor White
Write-Host "3. Login at: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
