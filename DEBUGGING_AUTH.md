# Authentication Debugging Guide

## Error: "Could not validate credentials: Not enough segments"

This error occurs when the JWT token is malformed, expired, or missing.

### Quick Fix (For Testing):

1. **Clear browser localStorage and re-login**:
   - Open Browser DevTools (F12)
   - Go to Application → Local Storage → http://localhost:3000
   - Delete the `token` entry
   - Refresh the page and log in again

2. **Or use this JavaScript in the browser console**:
   ```javascript
   localStorage.clear();
   window.location.href = '/login';
   ```

### Root Causes:

1. **Token expired**: JWT tokens expire after 30 minutes (1800 seconds)
   - Solution: Log in again to get a fresh token

2. **Malformed token**: Token was corrupted during storage
   - Solution: Clear localStorage and re-login

3. **Page refresh without token**: Token not persisted properly
   - Solution: The app should redirect to login automatically

### Testing Authentication Flow:

```bash
# 1. Login and get token
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "provider_demo", "password": "demo123"}'

# 2. Use the token in subsequent requests
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET http://localhost:8000/api/visits/VISIT_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Verify Token in Browser Console:

```javascript
// Check if token exists
const token = localStorage.getItem('token');
console.log('Token:', token);

// Decode token (without verification) to check expiration
function parseJwt(token) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  );
  return JSON.parse(jsonPayload);
}

if (token) {
  try {
    const decoded = parseJwt(token);
    console.log('Token payload:', decoded);
    console.log('Expires at:', new Date(decoded.exp * 1000));
    console.log('Is expired:', Date.now() > decoded.exp * 1000);
  } catch (e) {
    console.error('Invalid token format:', e);
  }
}
```

### Permanent Fix (TODO):

The app should implement automatic token refresh or redirect to login when token expires. Current implementation stores token in localStorage but doesn't handle expiration gracefully.

**Recommended improvements**:
1. Add token expiration check before API calls
2. Implement automatic redirect to /login when token is invalid
3. Add refresh token flow to get new access token without re-login
4. Show user-friendly error message instead of technical error

### Current Workaround:

For development/testing, simply:
1. Go to http://localhost:3000/login
2. Log in with: `provider_demo` / `demo123`
3. You'll be redirected to dashboard with a fresh token
4. Token is valid for 30 minutes

### Account Credentials:

**Provider Account**:
- Username: `provider_demo`
- Password: `demo123`
- Role: DOCTOR

**Other Test Accounts** (from database):
```sql
-- Check all users in database:
docker compose exec -T postgres psql -U healthcare_user -d healthcare_db -c "SELECT username, role, is_active FROM users;"
```
