# Database Migration Fix

## The Problem

The login endpoint is returning `ERR_EMPTY_RESPONSE` because the database tables don't exist yet. The database migrations need to be run to create the required tables (users, patients, appointments, etc.).

## Root Cause

1. `alembic.ini` and `alembic/` directory were not being copied into the Docker container
2. Database needs to be initialized with migrations before the login endpoint will work

## The Fix

### Step 1: Pull Latest Code

```powershell
git pull origin master
```

This includes the fix to `Dockerfile.api` that copies the alembic files into the container.

### Step 2: Rebuild the API Container

```powershell
cd backend\docker
docker-compose build api
```

### Step 3: Stop and Remove Everything

```powershell
docker-compose down -v
```

**WARNING**: The `-v` flag removes volumes (databases will be wiped). This is necessary for a clean start.

### Step 4: Start Services in Order

```powershell
# Start database first
docker-compose up -d postgres redis

# Wait for database to be ready (15 seconds)
Start-Sleep -Seconds 15

# Start API
docker-compose up -d api

# Wait for API to be ready
Start-Sleep -Seconds 5
```

### Step 5: Run Database Migrations

```powershell
docker-compose exec api alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 4e807a69e5a7, initial migration
INFO  [alembic.runtime.migration] Running upgrade 4e807a69e5a7 -> a1b2c3d4e5f6, add visits and transcripts
...
```

If you see errors, check the troubleshooting section below.

### Step 6: Verify Migrations Worked

```powershell
# Check current migration version
docker-compose exec api alembic current

# Should show the latest migration revision
```

### Step 7: Test the Login Endpoint

```powershell
# Test with curl
curl -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"test","password":"test"}'
```

**Expected**: Should return a JSON error (401 Unauthorized or 422 Validation Error), NOT `ERR_EMPTY_RESPONSE`

### Step 8: Try Login in Browser

Now try logging in from the frontend:
- Frontend (local): `http://localhost:3000`
- Should no longer get `ERR_EMPTY_RESPONSE`
- May get "invalid credentials" which is expected (need to create a user first)

---

## Troubleshooting

### Issue: "No config file 'alembic.ini' found"

**Cause**: Docker image wasn't rebuilt after the Dockerfile fix.

**Solution:**
```powershell
docker-compose build api
docker-compose up -d api
```

### Issue: "connection to server at 'postgres' failed: Connection refused"

**Cause**: Database isn't ready yet or networking issue.

**Solutions:**

1. **Wait longer for database:**
   ```powershell
   # Check if postgres is healthy
   docker-compose ps

   # Should show "healthy" not "starting"
   # If starting, wait 10 more seconds
   Start-Sleep -Seconds 10
   ```

2. **Restart everything:**
   ```powershell
   docker-compose down
   docker-compose up -d postgres redis
   Start-Sleep -Seconds 20
   docker-compose up -d api
   Start-Sleep -Seconds 10
   docker-compose exec api alembic upgrade head
   ```

3. **Check database connectivity:**
   ```powershell
   # Test direct connection to database
   docker-compose exec postgres psql -U healthcare_user -d healthcare_db -c "SELECT 1;"

   # Should return:
   # ?column?
   # ----------
   #         1
   ```

### Issue: "type 'visittype' already exists" (Duplicate Object Error)

**Cause**: Database has partial/old schema from previous runs.

**Solution**: Reset the database completely
```powershell
docker-compose down -v
docker-compose up -d postgres redis
Start-Sleep -Seconds 15
docker-compose up -d api
Start-Sleep -Seconds 5
docker-compose exec api alembic upgrade head
```

### Issue: DNS Resolution Error ("could not translate host name 'postgres'")

**Cause**: Docker networking DNS cache issue.

**Solutions:**

1. **Full Docker Desktop restart:**
   - Stop all containers: `docker-compose down`
   - Quit Docker Desktop
   - Start Docker Desktop
   - Wait for it to be fully running
   - Start containers: `docker-compose up -d`

2. **Recreate the network:**
   ```powershell
   docker-compose down
   docker network rm docker_healthcare-network
   docker-compose up -d
   ```

3. **Check network connectivity:**
   ```powershell
   docker network inspect docker_healthcare-network
   ```

   Should show both `healthcare-api` and `healthcare-postgres` containers.

---

## Creating Your First User

After migrations are successful, you need to create a user account to log in:

### Option 1: Using API Docs

1. Open http://localhost:8000/docs
2. Find `POST /api/auth/register` endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "patient@example.com",
     "password": "password123",
     "full_name": "Test Patient",
     "role": "patient"
   }
   ```
5. Click "Execute"

### Option 2: Using curl

```powershell
curl -X POST http://localhost:8000/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "patient@example.com",
    "password": "password123",
    "full_name": "Test Patient",
    "role": "patient"
  }'
```

### Now Try Logging In

**Browser**: Go to http://localhost:3000 and log in with:
- Email: `patient@example.com`
- Password: `password123`

**Should work!** ✅

---

## Verification Checklist

- [ ] `git pull origin master` completed
- [ ] `docker-compose build api` completed
- [ ] `docker-compose down -v` completed
- [ ] `docker-compose up -d postgres redis` completed
- [ ] Waited 15+ seconds for database
- [ ] `docker-compose up -d api` completed
- [ ] Waited 5+ seconds for API
- [ ] `docker-compose exec api alembic upgrade head` succeeded
- [ ] `docker-compose exec api alembic current` shows a revision
- [ ] Created a test user account
- [ ] Can log in from browser at http://localhost:3000
- [ ] No `ERR_EMPTY_RESPONSE` error

---

## Complete Reset Script (If All Else Fails)

```powershell
# Stop everything
docker-compose down -v

# Remove network (forces recreation)
docker network rm docker_healthcare-network 2>$null

# Rebuild API
docker-compose build api

# Start database and wait
docker-compose up -d postgres redis
Write-Host "Waiting for database..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Start API and wait
docker-compose up -d api
Write-Host "Waiting for API..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run migrations
Write-Host "Running migrations..." -ForegroundColor Green
docker-compose exec api alembic upgrade head

# Check migration status
Write-Host "`nMigration status:" -ForegroundColor Cyan
docker-compose exec api alembic current

# Check services
Write-Host "`nService status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nDone! Try logging in at http://localhost:3000" -ForegroundColor Green
```

Save this as `reset-and-migrate.ps1` and run it:
```powershell
.\reset-and-migrate.ps1
```

---

## Summary

**The core issue**: Database tables didn't exist because migrations weren't run.

**The solution**:
1. Pull latest code (includes Dockerfile fix)
2. Rebuild API container
3. Reset database
4. Run migrations
5. Create a user
6. Log in

**Expected result**: Login should work without `ERR_EMPTY_RESPONSE`!

---

**Last Updated**: 2025-11-29
**Status**: Tested and working on macOS. Windows developers may need to adjust Sleep timing if database takes longer to start.
