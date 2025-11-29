# CORS Troubleshooting Guide for Windows Developer

## Current Status

✅ **Server-side CORS is configured correctly** - confirmed via curl test
❌ **Browser is still showing CORS error** - need to troubleshoot client-side

## Step 1: Verify You Have Latest Code

```powershell
# Pull latest changes
git pull origin master

# Check docker-compose.yml has CORS_ORIGINS
grep -A 2 "CORS Configuration" backend/docker/docker-compose.yml
```

**Expected output:**
```yaml
# CORS Configuration
CORS_ORIGINS: '["http://localhost:3000", "http://localhost:3001"]'
```

## Step 2: Rebuild and Restart Containers

```powershell
# Navigate to docker directory
cd backend/docker

# Stop everything
docker-compose down

# Rebuild the API container
docker-compose build api

# Start all services
docker-compose up -d

# Wait for services to start
Start-Sleep -Seconds 10

# Verify all services are running
docker-compose ps
```

**All services should show "Up" status.**

## Step 3: Verify CORS Configuration Inside Container

```powershell
# Check CORS settings are loaded
docker-compose exec api python -c "from src.api.config import settings; print('CORS:', settings.CORS_ORIGINS)"
```

**Expected output:**
```
CORS: ['http://localhost:3000', 'http://localhost:3001']
```

If you see different values, the docker-compose.yml wasn't updated correctly.

## Step 4: Test CORS from Command Line

```powershell
# Test with curl (Git Bash or WSL2)
curl -X OPTIONS http://localhost:8000/api/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Look for these headers in the response:
# access-control-allow-origin: http://localhost:3000
# access-control-allow-credentials: true
```

**If curl shows CORS headers but browser doesn't, it's a browser issue.**

## Step 5: Browser Debugging

### A. Clear Browser Cache Completely

**Chrome/Edge:**
1. Press `Ctrl + Shift + Delete`
2. Select **"All time"**
3. Check:
   - ✅ Cookies and site data
   - ✅ Cached images and files
4. Click **"Clear data"**
5. **Restart the browser completely**

**Firefox:**
1. Press `Ctrl + Shift + Delete`
2. Time range: **"Everything"**
3. Check all boxes
4. Click **"Clear Now"**
5. **Restart Firefox**

### B. Try Incognito/Private Mode

1. Open a new Incognito/Private window
2. Navigate to `http://localhost:3000`
3. Try logging in

**If it works in Incognito, it's a browser cache/extension issue.**

### C. Disable Browser Extensions

Some browser extensions (ad blockers, privacy tools) can interfere with CORS:

1. Open browser extensions page:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
   - Firefox: `about:addons`
2. **Disable ALL extensions**
3. Try logging in again

### D. Check Browser Console for Exact Error

1. Open Developer Tools (`F12`)
2. Go to **Console** tab
3. Clear the console
4. Try logging in
5. **Take a screenshot of the error**

Send the exact error message. It should look like:

```
Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**But if our server is working, the error might be different now.**

## Step 6: Check Network Tab

1. Open Developer Tools (`F12`)
2. Go to **Network** tab
3. Try logging in
4. Look for the login request (usually `/api/auth/login`)
5. Click on it and check:

### Request Headers (should include):
```
Origin: http://localhost:3000
```

### Response Headers (should include):
```
access-control-allow-origin: http://localhost:3000
access-control-allow-credentials: true
```

**Take a screenshot of both Request and Response headers.**

## Step 7: Verify Frontend Configuration

Check `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**NOT** `https` and **NOT** `127.0.0.1` - must be exactly `http://localhost:8000`

## Step 8: Check Windows Firewall

Sometimes Windows Firewall blocks localhost connections:

1. Open **Windows Defender Firewall**
2. Click **"Allow an app through firewall"**
3. Find **Docker Desktop**
4. Ensure it's checked for both:
   - ✅ Private networks
   - ✅ Public networks
5. Click **OK**
6. **Restart Docker Desktop**

## Step 9: WSL2 Specific Issues

If using WSL2, there might be networking issues:

```powershell
# In PowerShell as Administrator
wsl --shutdown
```

Then restart Docker Desktop from the Start Menu.

## Step 10: Test with Different Browser

Try a completely different browser:
- If using Chrome, try Firefox
- If using Firefox, try Edge
- If using Edge, try Chrome

**If it works in a different browser, it's a browser-specific issue.**

## Common Mistakes

### ❌ Wrong Origin Format

**Incorrect:**
```
http://127.0.0.1:3000  # Using IP instead of localhost
https://localhost:3000  # Using HTTPS instead of HTTP
localhost:3000         # Missing http://
```

**Correct:**
```
http://localhost:3000
```

### ❌ Mixing localhost and 127.0.0.1

Frontend and backend must use the **same** format:

**Both should be:**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

**OR both should be:**
- Frontend: `http://127.0.0.1:3000`
- Backend: `http://127.0.0.1:8000`

### ❌ Not Restarting After Changes

After ANY change to docker-compose.yml:
```powershell
docker-compose down
docker-compose up -d
```

Not just `docker-compose restart`.

## Expected Working State

When everything is working:

1. ✅ `docker-compose ps` shows all services "Up"
2. ✅ `curl http://localhost:8000/health` returns `{"status":"healthy"...}`
3. ✅ curl with Origin header shows CORS headers in response
4. ✅ Browser console shows NO CORS errors
5. ✅ Network tab shows `access-control-allow-origin` header
6. ✅ Login request completes (even if credentials are wrong)

## Still Not Working?

Provide these outputs:

```powershell
# 1. Docker version
docker --version
docker-compose --version

# 2. Service status
docker-compose ps

# 3. CORS config
docker-compose exec api python -c "from src.api.config import settings; print('CORS:', settings.CORS_ORIGINS)"

# 4. Test CORS
curl -i http://localhost:8000/api/auth/login -H "Origin: http://localhost:3000"

# 5. Frontend env
cat frontend/.env.local | grep API_BASE_URL

# 6. Windows version
systeminfo | findstr /C:"OS Name" /C:"OS Version"

# 7. Browser version
# Open browser, go to Settings > About
```

Send all these outputs plus:
- Screenshot of browser console error
- Screenshot of Network tab showing the failed request
- Which browser and version you're using
- Whether you're using WSL2 or native Windows

---

**Last Updated:** 2025-11-29
**Status:** Server CORS is working - need to debug client-side
