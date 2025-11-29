# Running Frontend Locally (Outside Docker)

This guide shows how to run the frontend locally on your machine while keeping the backend services in Docker. This is a common development setup that can avoid Docker networking issues on Windows.

## Benefits of This Approach

✅ **Faster hot-reload** - Changes reflect instantly without Docker overhead
✅ **Easier debugging** - Direct access to Node.js debugger
✅ **Avoids CORS issues** - No Docker networking complications
✅ **Better performance** - Native Node.js runs faster than containerized
✅ **Simpler on Windows** - Fewer WSL2/Docker Desktop issues

---

## Prerequisites

Ensure you have installed:
- **Node.js 18+** (check: `node --version`)
- **npm 8+** (check: `npm --version`)

### Install Node.js (if needed)

**Windows:**
Download from https://nodejs.org/ (LTS version)

**WSL2/Linux:**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 18
nvm use 18
```

---

## Setup Instructions

### Step 1: Start Backend Services in Docker

```bash
# Navigate to docker directory
cd backend/docker

# Start only backend services (not frontend)
docker-compose up -d postgres redis fhir-server azurite api

# Verify services are running
docker-compose ps

# Check API is accessible
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"healthy","service":"AI Healthcare API",...}
```

### Step 2: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd ../../frontend

# Install dependencies
npm install
```

This will install all packages from `package.json`.

### Step 3: Verify Frontend Environment

Check that `frontend/.env.local` exists and has correct settings:

```bash
# View the file
cat .env.local
```

**Should contain:**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Application
NEXT_PUBLIC_APP_NAME=AI Healthcare Platform
NEXT_PUBLIC_APP_VERSION=1.0.0
```

**Important:** The `NEXT_PUBLIC_API_URL` should be `http://localhost:8000` (NOT `http://api:8000` which is for Docker internal networking).

### Step 4: Start Frontend Development Server

```bash
# From the frontend directory
npm run dev
```

**Expected output:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

### Step 5: Access the Application

Open your browser and navigate to:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

---

## Development Workflow

### Daily Startup

```bash
# Terminal 1: Start backend services
cd backend/docker
docker-compose up -d
docker-compose logs -f api  # Optional: watch logs

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Making Changes

**Frontend changes:**
- Edit files in `frontend/src/`
- Hot reload will automatically update the browser
- No restart needed!

**Backend changes:**
- Edit files in `backend/src/`
- Backend auto-reloads (FastAPI has hot reload enabled)
- If changing dependencies, rebuild: `docker-compose restart api`

### Stopping Services

```bash
# Stop frontend (Ctrl+C in the terminal running npm)

# Stop backend services
cd backend/docker
docker-compose down
```

---

## Troubleshooting

### Issue: `npm install` fails with permission errors

**Windows:**
- Run PowerShell as Administrator
- Or fix npm permissions: https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally

**WSL2/Linux:**
```bash
sudo chown -R $(whoami) ~/.npm
```

### Issue: Port 3000 already in use

```bash
# Find what's using port 3000
# Windows:
netstat -ano | findstr :3000

# WSL2/Linux:
lsof -i :3000

# Kill the process or use a different port
PORT=3001 npm run dev
```

### Issue: Cannot connect to backend API

**Check backend is running:**
```bash
curl http://localhost:8000/health
```

**If fails:**
```bash
cd backend/docker
docker-compose ps
docker-compose logs api
```

**Restart backend:**
```bash
docker-compose restart api
```

### Issue: CORS errors in browser

This should NOT happen with this setup, but if it does:

1. **Verify CORS configuration in backend:**
   ```bash
   docker-compose exec api python -c "from src.api.config import settings; print(settings.CORS_ORIGINS)"
   ```
   Should include `http://localhost:3000`

2. **Clear browser cache completely**
3. **Try incognito mode**

### Issue: Environment variables not loading

**Frontend env vars must start with `NEXT_PUBLIC_`**

To use an env var:
```typescript
// ✅ Correct
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// ❌ Wrong (won't work in browser)
const secret = process.env.SECRET_KEY;
```

After changing `.env.local`:
```bash
# Restart the dev server
# Ctrl+C then npm run dev
```

### Issue: Module not found errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Testing

### Run Frontend Tests

```bash
# Unit tests
npm test

# E2E tests (requires backend running)
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Building for Production

```bash
# Create production build
npm run build

# Test production build locally
npm run start
```

This creates an optimized build in `.next/` directory.

---

## Switching Back to Docker

If you want to run frontend in Docker again:

```bash
# Stop local frontend (Ctrl+C)

# Start frontend container
cd backend/docker
docker-compose up -d frontend
```

Note: Frontend container uses different env var: `NEXT_PUBLIC_API_URL=http://api:8000` (internal Docker network)

---

## Performance Tips

### Speed up npm install

```bash
# Use npm cache
npm cache clean --force

# Or use faster package manager
npm install -g pnpm
pnpm install  # Much faster than npm
```

### Reduce Memory Usage

If Next.js consumes too much memory:

```bash
# Limit memory
NODE_OPTIONS=--max-old-space-size=4096 npm run dev
```

### Enable Turbopack (Experimental)

Next.js 14 has experimental Turbopack for faster builds:

```bash
npm run dev -- --turbo
```

---

## IDE Setup

### VS Code Extensions (Recommended)

- **ESLint** - Linting
- **Prettier** - Code formatting
- **Tailwind CSS IntelliSense** - Autocomplete for CSS
- **TypeScript and JavaScript Language Features** - Built-in

### VS Code Settings

Create `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

---

## Environment Variables Reference

### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Application Info
NEXT_PUBLIC_APP_NAME=AI Healthcare Platform
NEXT_PUBLIC_APP_VERSION=1.0.0

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=true
```

### Backend (docker-compose.yml handles this)

The backend environment is configured in `backend/docker/docker-compose.yml`. No changes needed when running frontend locally.

---

## Quick Reference Commands

```bash
# Start everything
cd backend/docker && docker-compose up -d
cd ../../frontend && npm run dev

# View logs
docker-compose logs -f api        # Backend logs
# Frontend logs show in terminal

# Restart backend
docker-compose restart api

# Restart frontend
# Ctrl+C then npm run dev

# Stop everything
docker-compose down
# Ctrl+C in frontend terminal

# Clean restart
docker-compose down -v
docker-compose up -d
rm -rf frontend/node_modules frontend/.next
cd frontend && npm install && npm run dev
```

---

## Windows-Specific Notes

### PowerShell Commands

All bash commands work in PowerShell, but use backslashes for paths:

```powershell
# Navigate
cd backend\docker

# View file
Get-Content .env.local
# or
cat .env.local
```

### Git Bash

Git Bash provides a Linux-like environment on Windows and works perfectly for these commands.

### WSL2 Best Practices

If using WSL2:
- Clone the repo inside WSL2 filesystem (`~/projects/` not `/mnt/c/...`)
- Run both Docker and npm from WSL2 terminal
- Access via `http://localhost:3000` from Windows browser (port forwarding is automatic)

---

## Common Workflows

### Adding a New Package

```bash
cd frontend
npm install <package-name>

# Or save as dev dependency
npm install -D <package-name>
```

### Creating a New Page

```bash
# Create file: frontend/src/app/new-page/page.tsx
# Accessible at: http://localhost:3000/new-page
```

### Debugging

**Browser DevTools:**
- Press F12
- Use React DevTools extension
- Check Console and Network tabs

**VS Code Debugger:**
Add to `.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Next.js: debug",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "dev"],
  "port": 9229,
  "console": "integratedTerminal"
}
```

---

## Success Checklist

- [ ] Backend services running (`docker-compose ps`)
- [ ] API accessible (`curl http://localhost:8000/health`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Dependencies installed (`npm install` completed)
- [ ] Frontend running (`npm run dev` shows "Ready")
- [ ] Browser shows app at `http://localhost:3000`
- [ ] No CORS errors in browser console
- [ ] Login page loads correctly

---

**Happy Coding!** 🚀

For issues, see:
- `TROUBLESHOOTING_CORS_WINDOWS.md` for CORS problems
- `DEVELOPER_ONBOARDING_WINDOWS.md` for general Windows setup
- Backend logs: `docker-compose logs api`
- Frontend terminal output for errors
