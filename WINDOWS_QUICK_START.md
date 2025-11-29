# Windows Quick Start - Local Frontend Setup

**Recommended approach for Windows developers experiencing CORS issues**

This guide sets up the frontend to run **locally on your Windows machine** while keeping the backend in Docker. This avoids Docker networking complications and provides a better development experience.

---

## Prerequisites

1. ✅ **Docker Desktop** installed and running
2. ✅ **Node.js 18+** installed from https://nodejs.org/
3. ✅ **Git** installed
4. ✅ Repository cloned to your machine

---

## Quick Setup (5 Minutes)

### Option A: Automated Setup (Recommended)

1. **Pull latest changes:**
   ```powershell
   git pull origin master
   ```

2. **Run the setup script:**
   ```powershell
   .\setup-local-frontend.ps1
   ```

   This script will:
   - ✅ Check Node.js installation
   - ✅ Start backend Docker services
   - ✅ Configure frontend environment
   - ✅ Install dependencies
   - ✅ Start the frontend server

3. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

**That's it!** 🎉

---

### Option B: Manual Setup

If you prefer to do it manually or the script doesn't work:

#### Step 1: Start Backend Services

```powershell
# Navigate to docker directory
cd backend\docker

# Start backend services
docker-compose up -d postgres redis api

# Verify services are running
docker-compose ps

# Test API
curl http://localhost:8000/health
```

#### Step 2: Install Frontend Dependencies

```powershell
# Navigate to frontend directory
cd ..\..\frontend

# Install dependencies
npm install
```

#### Step 3: Configure Environment

Create or verify `frontend\.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Healthcare Platform
NEXT_PUBLIC_APP_VERSION=1.0.0
```

#### Step 4: Start Frontend

```powershell
# From frontend directory
npm run dev
```

#### Step 5: Open Browser

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

---

## Daily Workflow

### Starting Work

**Terminal 1 (Backend):**
```powershell
cd backend\docker
docker-compose up -d
docker-compose logs -f api  # Optional: watch logs
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

### Stopping Work

- **Frontend:** Press `Ctrl+C` in the terminal
- **Backend:**
  ```powershell
  cd backend\docker
  docker-compose down
  ```

---

## Troubleshooting

### Issue: "Node.js not found"

**Install Node.js:**
1. Download from https://nodejs.org/ (LTS version)
2. Run installer
3. **Restart PowerShell**
4. Verify: `node --version`

### Issue: "Port 3000 already in use"

**Kill the process:**
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F

# Or use a different port
$env:PORT=3001; npm run dev
```

### Issue: "Cannot connect to backend"

**Check backend is running:**
```powershell
curl http://localhost:8000/health
```

**If fails:**
```powershell
cd backend\docker
docker-compose ps
docker-compose logs api
docker-compose restart api
```

### Issue: "npm install fails"

**Clear cache and retry:**
```powershell
npm cache clean --force
Remove-Item -Recurse -Force node_modules
npm install
```

### Issue: Still getting CORS errors

**This should NOT happen with local frontend, but if it does:**

1. **Clear browser cache** (Ctrl+Shift+Delete → All time → Clear)
2. **Try incognito mode**
3. **Verify API URL:**
   ```powershell
   Get-Content .env.local | Select-String API_URL
   ```
   Should be: `NEXT_PUBLIC_API_URL=http://localhost:8000`

4. **Run diagnostic:**
   ```powershell
   ..\test-cors.ps1
   ```

---

## Making Changes

### Frontend Code Changes

- Edit files in `frontend\src\`
- **Hot reload** automatically updates browser
- **No restart needed!**

### Backend Code Changes

- Edit files in `backend\src\`
- Backend auto-reloads
- If adding dependencies: `docker-compose restart api`

---

## Advantages of This Setup

✅ **No CORS issues** - Direct localhost communication
✅ **Faster development** - Instant hot reload
✅ **Better debugging** - Native Node.js debugger
✅ **Less memory** - Only backend in Docker
✅ **Windows friendly** - Fewer Docker Desktop issues

---

## VS Code Tips

### Recommended Extensions

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Tailwind CSS IntelliSense** - CSS autocomplete
- **Error Lens** - Inline error display

### Integrated Terminal

Open two terminals in VS Code:
1. **Terminal 1:** `cd backend\docker && docker-compose up -d`
2. **Terminal 2:** `cd frontend && npm run dev`

---

## Testing

```powershell
# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

---

## Need Help?

1. **CORS issues:** See `TROUBLESHOOTING_CORS_WINDOWS.md`
2. **General setup:** See `RUN_FRONTEND_LOCALLY.md`
3. **Docker issues:** See `DEVELOPER_ONBOARDING_WINDOWS.md`

---

## Quick Reference

```powershell
# Start everything
cd backend\docker && docker-compose up -d
cd ..\..\frontend && npm run dev

# Stop everything
# Ctrl+C (frontend)
cd backend\docker && docker-compose down

# View logs
docker-compose logs -f api

# Restart backend
docker-compose restart api

# Reinstall dependencies
Remove-Item -Recurse node_modules
npm install

# Test CORS
..\test-cors.ps1
```

---

## Success Checklist

- [ ] Node.js 18+ installed
- [ ] Docker Desktop running
- [ ] Latest code pulled (`git pull`)
- [ ] Backend services running (`docker-compose ps`)
- [ ] API accessible (`curl http://localhost:8000/health`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend running (`npm run dev`)
- [ ] Browser shows app at http://localhost:3000
- [ ] No CORS errors in console
- [ ] Can see login page

---

**Happy coding!** 🚀

If you encounter issues, run the diagnostic script:
```powershell
.\test-cors.ps1
```

Then check the troubleshooting guides listed above.
