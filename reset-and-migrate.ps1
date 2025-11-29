# Complete Reset and Migration Script for Windows
# This script resets the entire environment and runs database migrations

Write-Host "`n=== Healthcare AI - Complete Reset & Migration ===" -ForegroundColor Cyan
Write-Host "This will reset all data and recreate the database`n" -ForegroundColor Yellow

# Confirm with user
$confirmation = Read-Host "Are you sure you want to continue? (yes/no)"
if ($confirmation -ne 'yes') {
    Write-Host "Aborted." -ForegroundColor Red
    exit
}

# Navigate to docker directory
Set-Location backend\docker

# Step 1: Stop everything
Write-Host "`n[1/8] Stopping all containers..." -ForegroundColor Yellow
docker-compose down -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to stop containers" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Containers stopped`n" -ForegroundColor Green

# Step 2: Remove network (forces recreation)
Write-Host "[2/8] Removing Docker network..." -ForegroundColor Yellow
docker network rm docker_healthcare-network 2>$null
Write-Host "✅ Network removed`n" -ForegroundColor Green

# Step 3: Rebuild API
Write-Host "[3/8] Rebuilding API container..." -ForegroundColor Yellow
docker-compose build api
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build API" -ForegroundColor Red
    exit 1
}
Write-Host "✅ API rebuilt`n" -ForegroundColor Green

# Step 4: Start database and redis
Write-Host "[4/8] Starting database and Redis..." -ForegroundColor Yellow
docker-compose up -d postgres redis
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start database" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Database and Redis starting..." -ForegroundColor Green
Write-Host "   Waiting 20 seconds for database to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 20

# Step 5: Check database is healthy
Write-Host "`n[5/8] Checking database health..." -ForegroundColor Yellow
$dbStatus = docker-compose ps postgres | Select-String "healthy"
if ($dbStatus) {
    Write-Host "✅ Database is healthy`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database may not be ready yet, waiting 10 more seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Step 6: Start API
Write-Host "[6/8] Starting API..." -ForegroundColor Yellow
docker-compose up -d api
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start API" -ForegroundColor Red
    exit 1
}
Write-Host "✅ API starting..." -ForegroundColor Green
Write-Host "   Waiting 10 seconds for API to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Step 7: Run migrations
Write-Host "`n[7/8] Running database migrations..." -ForegroundColor Yellow
docker-compose exec -T api alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Migration failed!" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Cyan
    Write-Host "1. Check API logs: docker-compose logs api --tail 50" -ForegroundColor White
    Write-Host "2. Check database logs: docker-compose logs postgres --tail 50" -ForegroundColor White
    Write-Host "3. See DATABASE_MIGRATION_FIX.md for more help" -ForegroundColor White
    exit 1
}
Write-Host "✅ Migrations completed successfully`n" -ForegroundColor Green

# Step 8: Verify migration status
Write-Host "[8/8] Verifying migration status..." -ForegroundColor Yellow
docker-compose exec -T api alembic current
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration verification successful`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  Could not verify migration status`n" -ForegroundColor Yellow
}

# Show service status
Write-Host "=== Service Status ===" -ForegroundColor Cyan
docker-compose ps

# Final instructions
Write-Host "`n=== ✅ Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create a user account:" -ForegroundColor White
Write-Host "   Open http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   Use POST /api/auth/register endpoint" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the frontend:" -ForegroundColor White
Write-Host "   cd ..\..\frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Backend:  http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
