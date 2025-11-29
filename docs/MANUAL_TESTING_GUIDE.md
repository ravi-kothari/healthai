# Manual Testing Guide - Post-Signup Redirect Flow

## Prerequisites
- All services running (verified ✅)
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Test 1: Provider Signup with Redirect

### Steps:
1. **Open signup page**
   - Navigate to: http://localhost:3000/signup
   - Page should load with signup form

2. **Fill out the form**
   - Email: `newprovider@test.com`
   - Username: `newprovider`
   - Password: `Test1234!`
   - Confirm Password: `Test1234!`
   - Full Name: `New Provider Test`
   - Role: Select **Doctor** from dropdown

3. **Submit the form**
   - Click "Sign Up" button
   - Watch for the redirect behavior

### Expected Results:
- ✅ Form submission succeeds (no errors)
- ✅ **Automatic redirect to `/provider/dashboard`** (no alert, no manual navigation)
- ✅ Dashboard page loads
- ✅ User sees provider dashboard interface

### What to Check:
1. **Browser DevTools Console** (F12 → Console tab):
   - Should see successful registration logs
   - No JavaScript errors

2. **LocalStorage** (F12 → Application → Local Storage → http://localhost:3000):
   - `access_token`: Should contain JWT token
   - `refresh_token`: Should contain JWT token
   - `user`: Should contain JSON user object with role "doctor"

3. **Network Tab** (F12 → Network):
   - POST request to `/api/auth/register` → Status 201
   - Response contains `access_token`, `refresh_token`, and `user` object

---

## Test 2: Landing Page Auto-Redirect for Authenticated Users

### Steps:
1. **While still logged in from Test 1**, navigate to homepage:
   - Go to: http://localhost:3000/

### Expected Results:
- ✅ **Automatic redirect to `/provider/dashboard`** (should not see landing page)
- ✅ You remain on the dashboard

### Explanation:
The landing page now has a `useEffect` that:
- Loads user from localStorage on mount
- Checks if user is authenticated
- Auto-redirects providers to `/provider/dashboard`
- Auto-redirects patients to `/patient/dashboard`

---

## Test 3: Patient Signup and Redirect

### Steps:
1. **Logout** (or open incognito window)

2. **Navigate to signup page**
   - Go to: http://localhost:3000/signup

3. **Fill out form as patient**
   - Email: `newpatient@test.com`
   - Username: `newpatient`
   - Password: `Test1234!`
   - Confirm Password: `Test1234!`
   - Full Name: `New Patient Test`
   - Role: Select **Patient** from dropdown

4. **Submit form**

### Expected Results:
- ✅ Form submission succeeds
- ✅ **Automatic redirect to `/patient/dashboard`** (when patient dashboard is implemented)
- ✅ User sees patient dashboard interface

**Note**: If patient dashboard is not yet implemented, you might see a 404 page - this is expected. The redirect logic is still working correctly.

---

## Test 4: Hash Anchor Navigation on Landing Page

### Steps:
1. **Logout** and navigate to: http://localhost:3000/

2. **Click on mega menu links**:
   - Features → PreVisit → CarePrep
   - Features → Appoint-Ready → ContextAI

### Expected Results:
- ✅ Page scrolls smoothly to the respective section
- ✅ URL changes to include hash (e.g., `http://localhost:3000/#careprep`)
- ✅ No page reload occurs (client-side navigation)

---

## Test 5: Client-Side Navigation Performance

### Steps:
1. **On landing page**, click various navigation links:
   - Features → Transcribe & Dictate
   - Features → Clinical Notes
   - Platform → Security
   - Platform → Integrations

### Expected Results:
- ✅ Navigation is **fast** (no full page reload)
- ✅ Links use Next.js `<Link>` component (check in DevTools)
- ✅ Pages prefetch on hover (check Network tab)

---

## Common Issues and Troubleshooting

### Issue 1: Redirect Not Working
**Symptoms**: After signup, user sees alert and stays on signup page

**Check**:
1. Browser console for errors
2. Verify `useRouter` import in `SignupForm.tsx`
3. Check that `router.push('/provider/dashboard')` is being called
4. Verify authStore state is being set

**Fix**: Clear browser cache and localStorage, then try again

---

### Issue 2: Dashboard Shows 404
**Symptoms**: Redirect happens but dashboard page not found

**Check**:
1. Verify `/provider/dashboard` route exists in frontend
2. Check if page file exists at `frontend/src/app/(provider)/dashboard/page.tsx`

**Note**: Patient dashboard might not be implemented yet - this is expected

---

### Issue 3: Landing Page Doesn't Auto-Redirect
**Symptoms**: Authenticated user can still see landing page

**Check**:
1. Verify `loadUser()` is called on landing page mount
2. Check localStorage has valid tokens
3. Verify `useEffect` with auto-redirect is present in `page.tsx`

---

### Issue 4: Hash Navigation Doesn't Scroll
**Symptoms**: Clicking #careprep or #contextai doesn't scroll

**Check**:
1. Verify section has `id` attribute: `<section id="careprep">`
2. Check browser console for errors
3. Try manually navigating to `http://localhost:3000/#careprep`

---

## Success Criteria

### All Tests Pass When:
- [x] Provider signup redirects to `/provider/dashboard` automatically
- [x] Patient signup redirects to `/patient/dashboard` automatically
- [x] Authenticated users are auto-redirected when visiting homepage
- [x] Tokens are stored in localStorage
- [x] Auth state is updated in authStore
- [x] No JavaScript errors in console
- [x] Hash anchor navigation scrolls correctly
- [x] Client-side navigation is fast and smooth

---

## Next Steps After Testing

If all tests pass:
1. Mark Priority 4 as fully complete ✅
2. Document any issues found
3. Move to next priority (email verification, branding, etc.)

If tests fail:
1. Document the specific failure
2. Check error messages in console
3. Review the implementation in `SignupForm.tsx` and `page.tsx`
4. Fix issues and re-test
