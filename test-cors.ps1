# CORS Diagnostic Script for Windows
# Run this script in PowerShell to diagnose CORS issues

Write-Host "`n=== CORS Diagnostic Tool ===" -ForegroundColor Cyan
Write-Host "Testing CORS configuration...`n" -ForegroundColor Cyan

# Test 1: Check if services are running
Write-Host "[1/6] Checking if Docker services are running..." -ForegroundColor Yellow
docker-compose ps
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker services not running. Run 'docker-compose up -d' first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker services are running`n" -ForegroundColor Green

# Test 2: Check API health
Write-Host "[2/6] Testing API health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($health.StatusCode -eq 200) {
        Write-Host "✅ API is healthy" -ForegroundColor Green
        Write-Host $health.Content
    }
} catch {
    Write-Host "❌ API health check failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 3: Check CORS configuration inside container
Write-Host "[3/6] Checking CORS configuration in container..." -ForegroundColor Yellow
$corsConfig = docker-compose exec -T api python -c "from src.api.config import settings; print(','.join(settings.CORS_ORIGINS))" 2>$null
if ($corsConfig) {
    Write-Host "✅ CORS Origins: $corsConfig" -ForegroundColor Green
    if ($corsConfig -notmatch "http://localhost:3000") {
        Write-Host "⚠️  WARNING: http://localhost:3000 not in CORS origins!" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Could not read CORS configuration" -ForegroundColor Red
}
Write-Host ""

# Test 4: Test CORS preflight (OPTIONS)
Write-Host "[4/6] Testing CORS preflight request..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = "http://localhost:3000"
        "Access-Control-Request-Method" = "POST"
        "Access-Control-Request-Headers" = "Content-Type"
    }
    $preflight = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method Options -Headers $headers -UseBasicParsing

    $allowOrigin = $preflight.Headers["Access-Control-Allow-Origin"]
    $allowCreds = $preflight.Headers["Access-Control-Allow-Credentials"]

    Write-Host "Response Headers:" -ForegroundColor Gray
    Write-Host "  Access-Control-Allow-Origin: $allowOrigin" -ForegroundColor Gray
    Write-Host "  Access-Control-Allow-Credentials: $allowCreds" -ForegroundColor Gray

    if ($allowOrigin -eq "http://localhost:3000") {
        Write-Host "✅ CORS preflight working correctly" -ForegroundColor Green
    } else {
        Write-Host "❌ CORS preflight failed - wrong origin: $allowOrigin" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ CORS preflight test failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Test actual POST request
Write-Host "[5/6] Testing actual POST request with CORS..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = "http://localhost:3000"
        "Content-Type" = "application/json"
    }
    $body = '{"username":"test","password":"test"}'

    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method Post -Headers $headers -Body $body -UseBasicParsing

    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]

    Write-Host "Response Headers:" -ForegroundColor Gray
    Write-Host "  Access-Control-Allow-Origin: $allowOrigin" -ForegroundColor Gray
    Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Gray

    if ($allowOrigin -eq "http://localhost:3000") {
        Write-Host "✅ CORS headers present in POST response" -ForegroundColor Green
    } else {
        Write-Host "❌ CORS headers missing or incorrect in POST response" -ForegroundColor Red
    }
} catch {
    # Even if the request fails (401, 422, etc.), CORS headers should be present
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "Request returned status $statusCode (expected - invalid credentials)" -ForegroundColor Gray

    if ($_.Exception.Response.Headers) {
        $allowOrigin = $_.Exception.Response.Headers["Access-Control-Allow-Origin"]
        if ($allowOrigin -eq "http://localhost:3000") {
            Write-Host "✅ CORS headers present even in error response" -ForegroundColor Green
        } else {
            Write-Host "❌ CORS headers missing in error response" -ForegroundColor Red
        }
    }
}
Write-Host ""

# Test 6: Check frontend configuration
Write-Host "[6/6] Checking frontend configuration..." -ForegroundColor Yellow
if (Test-Path "frontend/.env.local") {
    $apiUrl = Get-Content "frontend/.env.local" | Select-String "NEXT_PUBLIC_API"
    Write-Host "Frontend API URL: $apiUrl" -ForegroundColor Gray

    if ($apiUrl -match "http://localhost:8000") {
        Write-Host "✅ Frontend configured correctly" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Frontend API URL might be incorrect" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  frontend/.env.local not found" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "If all tests passed, CORS is configured correctly on the server side." -ForegroundColor White
Write-Host "If you still get CORS errors in the browser:" -ForegroundColor White
Write-Host "  1. Clear browser cache completely (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  2. Try incognito/private mode" -ForegroundColor White
Write-Host "  3. Try a different browser" -ForegroundColor White
Write-Host "  4. Disable browser extensions" -ForegroundColor White
Write-Host "  5. Check Windows Firewall settings" -ForegroundColor White
Write-Host "  6. See TROUBLESHOOTING_CORS_WINDOWS.md for detailed steps" -ForegroundColor White
Write-Host ""
