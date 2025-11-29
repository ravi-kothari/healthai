# Instructions for Windows Developer

## Problem Solved! 🎉

We've fixed the CORS issue and created a **much simpler setup** for you. Instead of running everything in Docker, you'll run the **frontend locally** on your Windows machine while keeping the backend in Docker.

### Why This Is Better

✅ **No more CORS issues** - Avoids Docker networking complications
✅ **Faster development** - Hot reload works instantly
✅ **Easier debugging** - Native Node.js environment
✅ **Less memory usage** - Only backend in Docker
✅ **Better Windows compatibility** - Fewer Docker Desktop issues

---

## What You Need to Do (5 Minutes)

### Step 1: Pull Latest Code

```powershell
cd path\to\Healthcare\azure-healthcare-app
git pull origin master
```

### Step 2: Make Sure You Have Node.js

Check if you have Node.js installed:

```powershell
node --version
npm --version
```

**If you see version numbers (18.x or higher):**
✅ You're good! Skip to Step 3.

**If you see "command not found" or error:**
1. Download Node.js from https://nodejs.org/
2. Install the **LTS version** (Long Term Support)
3. **Restart PowerShell** after installation
4. Verify: `node --version`

### Step 3: Run the Setup Script

This script does everything automatically:

```powershell
.\setup-local-frontend.ps1
```

**What the script does:**
1. ✅ Checks Node.js is installed
2. ✅ Starts backend Docker services (API, database, etc.)
3. ✅ Configures frontend environment
4. ✅ Installs frontend dependencies
5. ✅ Starts the frontend development server

**Wait for it to show:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000

✓ Ready in X.Xs
```

### Step 4: Open Your Browser

Navigate to:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs

**Try logging in!** The CORS error should be gone. 🎉

---

## Daily Workflow (Going Forward)

Every time you start working:

### Option A: Use the Setup Script (Easiest)

```powershell
.\setup-local-frontend.ps1
```

### Option B: Manual Start

**Terminal 1 (Backend):**
```powershell
cd backend\docker
docker-compose up -d
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

### When You're Done

- **Stop frontend:** Press `Ctrl+C` in the terminal
- **Stop backend:**
  ```powershell
  cd backend\docker
  docker-compose down
  ```

---

## Making Code Changes

### Frontend Changes
- Edit any file in `frontend\src\`
- Save the file
- Browser **automatically reloads** - no restart needed!

### Backend Changes
- Edit files in `backend\src\`
- Backend auto-reloads
- If you add new Python packages, restart: `docker-compose restart api`

---

## Troubleshooting

### "Port 3000 already in use"

Something else is using port 3000. Kill it:

```powershell
netstat -ano | findstr :3000
# Note the PID (last number)
taskkill /PID <that-number> /F
```

Then try again: `npm run dev`

### "Cannot connect to backend API"

Check backend is running:

```powershell
curl http://localhost:8000/health
```

**If it fails:**
```powershell
cd backend\docker
docker-compose up -d
docker-compose logs api
```

### "npm install fails"

Clear cache and retry:

```powershell
cd frontend
npm cache clean --force
Remove-Item -Recurse -Force node_modules
npm install
```

### Still Getting CORS Errors?

This setup should eliminate CORS issues, but if you still see them:

1. **Clear browser cache completely:**
   - Press `Ctrl + Shift + Delete`
   - Select "All time"
   - Check all boxes
   - Clear data
   - **Restart the browser**

2. **Try incognito/private mode**

3. **Run the diagnostic script:**
   ```powershell
   .\test-cors.ps1
   ```

4. **Check your `.env.local` file:**
   ```powershell
   Get-Content frontend\.env.local
   ```
   Should contain:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

---

## Documentation Available

If you need more details, these guides are in the repository:

- **WINDOWS_QUICK_START.md** - Quick reference for this setup
- **RUN_FRONTEND_LOCALLY.md** - Detailed guide with all options
- **TROUBLESHOOTING_CORS_WINDOWS.md** - CORS troubleshooting
- **DEVELOPER_ONBOARDING_WINDOWS.md** - Full Windows setup guide
- **test-cors.ps1** - Diagnostic script

---

## Expected Behavior When Working

### ✅ Success Indicators

- [ ] `docker-compose ps` shows all backend services "Up"
- [ ] `curl http://localhost:8000/health` returns JSON
- [ ] Frontend terminal shows "Ready in X.Xs"
- [ ] Browser shows login page at http://localhost:3000
- [ ] **No red CORS errors** in browser console (F12)
- [ ] Can interact with the app (even if login fails due to no account)

### ❌ Common Mistakes

1. **Using wrong URL in browser:**
   - ✅ Use: `http://localhost:3000`
   - ❌ Not: `http://127.0.0.1:3000`
   - ❌ Not: `https://localhost:3000`

2. **Backend not running:**
   - Check with: `docker-compose ps`
   - All services should show "Up"

3. **Old browser cache:**
   - Clear completely (Ctrl+Shift+Delete)
   - Or use incognito mode

---

## Quick Commands Reference

```powershell
# Pull latest code
git pull origin master

# Start everything (automated)
.\setup-local-frontend.ps1

# OR start manually
cd backend\docker && docker-compose up -d
cd ..\..\frontend && npm run dev

# Check backend status
docker-compose ps
curl http://localhost:8000/health

# View backend logs
docker-compose logs -f api

# Stop everything
# Ctrl+C (frontend terminal)
docker-compose down (backend)

# Run diagnostics
.\test-cors.ps1

# Reinstall frontend dependencies
cd frontend
Remove-Item -Recurse node_modules
npm install
```

---

## What Changed?

1. **Fixed CORS configuration** - Backend now allows requests from localhost:3000
2. **Created automated setup** - One command to start everything
3. **Local frontend** - No more Docker networking issues
4. **Better documentation** - Multiple guides for different scenarios

---

## Need Help?

If something doesn't work:

1. **Run the diagnostic:**
   ```powershell
   .\test-cors.ps1
   ```

2. **Check the logs:**
   ```powershell
   docker-compose logs api
   ```
   (in frontend terminal, errors show directly)

3. **Send screenshot of:**
   - Browser console (F12 → Console tab)
   - Network tab showing the failed request
   - Terminal output
   - Output of `test-cors.ps1`

---

## Summary

**Old way (problematic):**
- Frontend in Docker
- Backend in Docker
- CORS issues on Windows ❌

**New way (works!):**
- Frontend runs locally (native Node.js)
- Backend in Docker
- No CORS issues ✅
- Faster development ✅
- Better debugging ✅

---

## Action Items

- [ ] Pull latest code: `git pull origin master`
- [ ] Verify Node.js installed: `node --version`
- [ ] Run setup script: `.\setup-local-frontend.ps1`
- [ ] Open browser: http://localhost:3000
- [ ] Verify no CORS errors in console (F12)
- [ ] Try logging in (should not get CORS error)

---

**You should be up and running in less than 5 minutes!** 🚀

If you encounter any issues, run `.\test-cors.ps1` and send the output.

Good luck! 💪
