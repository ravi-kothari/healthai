# Provider Signup Testing Checklist

**Journey:** P1 - Provider Signup & Onboarding
**Date:** November 27, 2024
**Status:** 🔄 In Progress
**Known Blocker:** Dropdown bug (documented in TEST_FINDINGS_JOURNEY_1.md)

---

## 🧪 Test Steps

### ✅ Step 1: Page Load
- [x] Navigate to `http://localhost:3000/signup`
- [x] Page loads successfully
- [x] No console errors (F12)
- [x] Form displays all fields

**Result:** ✅ PASS

---

### ✅ Step 2: Form Structure Verification
Check that all expected fields are present:

- [x] First Name field
- [x] Last Name field
- [x] Email field
- [x] Password field
- [x] Password strength indicators visible
- [x] Phone field
- [x] Practice Type field (⚠️ broken dropdown)
- [x] Agreement checkbox
- [x] Submit button: "Start My Free Trial Now"

**Result:** ✅ PASS (except dropdown bug)

---

### ⏳ Step 3: Password Strength Indicators

**Test A: Weak Password**
- [ ] Clear password field
- [ ] Type: `test`
- [ ] Observe indicators

**Expected:**
- ✅ One lowercase letter (blue)
- ⚪ One uppercase letter (gray)
- ⚪ One number (gray)
- ⚪ 8 characters min (gray)

**Actual Result:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

**Test B: Strong Password**
- [ ] Type: `Test1234`
- [ ] Observe indicators

**Expected:**
- ✅ All four indicators blue

**Actual Result:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

---

### ⏳ Step 4: Form Validation (Empty Submission)

- [ ] Leave ALL fields empty
- [ ] Click "Start My Free Trial Now"

**Expected:**
- Form does NOT submit
- Validation errors appear for:
  - [ ] First Name required
  - [ ] Last Name required
  - [ ] Email required
  - [ ] Password required
  - [ ] Phone required
  - [ ] Practice Type required (will fail due to dropdown bug)
  - [ ] Agreement required
- No API call in Network tab

**Actual Result:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

---

### ⏳ Step 5: Email Validation

Test each email format:

**Test 5a: Invalid email - no @**
- [ ] Enter email: `notanemail`
- [ ] Tab to next field or submit

**Expected:** Error message about invalid email format

**Actual:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

**Test 5b: Invalid email - incomplete**
- [ ] Enter email: `test@`

**Expected:** Error message

**Actual:**
```
[ ] ✅ PASS
[ ] ❌ FAIL
```

**Test 5c: Valid email**
- [ ] Enter email: `test@example.com`

**Expected:** No error

**Actual:**
```
[ ] ✅ PASS
[ ] ❌ FAIL
```

---

### ⏳ Step 6: Phone Number Validation

- [ ] Enter phone: `123`
- [ ] Tab to next field

**Expected:** Format validation or mask applied

**Actual:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

---

### ⏳ Step 7: Agreement Checkbox

- [ ] Fill all fields EXCEPT agreement checkbox
- [ ] Try to submit

**Expected:**
- Form does not submit
- Error message about required agreement

**Actual:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

---

### ⏳ Step 8: Form Submission (Mock - Dropdown Workaround)

Since the dropdown is broken, let's test what happens if we bypass it using browser console:

**Option A: Use Browser Console Workaround**
1. [ ] Fill all other fields with valid data:
   ```
   First Name: Test
   Last Name: Provider
   Email: test.provider@healthai.com
   Password: TestPass123!
   Phone: (555) 123-4567
   Agreement: [Checked]
   ```

2. [ ] Open browser console (F12)

3. [ ] Paste this JavaScript to set practice type value:
   ```javascript
   document.querySelector('#practiceType').value = 'Solo Practitioner';
   document.querySelector('#practiceType').dispatchEvent(new Event('change', { bubbles: true }));
   ```

4. [ ] Click submit

**Expected (Current Mock Behavior):**
- Alert: "Signup successful!"
- Console log: Form data object

**Actual Result:**
```
[ ] ✅ PASS
[ ] ❌ FAIL - Describe:
_____________________________________________
```

**Console Output:**
```
(Paste what you see in console)


```

**Network Tab:**
```
(Any API calls? POST requests?)


```

---

### ⏳ Step 9: Check API Integration

- [ ] Open Network tab in DevTools
- [ ] Submit form (using workaround above)
- [ ] Look for API requests

**Expected (Current State):**
- NO API call to backend
- Only setTimeout mock
- Alert shows after 1 second delay

**Future Expected:**
- POST to `/api/auth/register`
- Status 201 Created
- Response with user data and token

**Actual Result:**
```
API Call Made: [ ] Yes [ ] No

If Yes:
  URL: ___________
  Method: ___________
  Status: ___________
  Response: ___________
```

---

### ⏳ Step 10: Post-Submission Behavior

After successful submission (using mock):

- [ ] What happens after alert dismissal?
- [ ] Are you redirected anywhere?
- [ ] Does form clear?
- [ ] Any other behavior?

**Expected (Future):**
- Redirect to `/onboarding` or `/provider/dashboard`
- Email verification sent
- Token stored in localStorage

**Actual:**
```
Behavior observed:
_____________________________________________
```

---

## 🐛 Bugs Found (Add to TEST_FINDINGS)

### New Bug #1
**Title:** ___________________________________
**Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
**Description:**
```


```

---

### New Bug #2
**Title:** ___________________________________
**Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
**Description:**
```


```

---

## 📊 Summary

**Tests Completed:** ___ / 10
**Tests Passed:** ___
**Tests Failed:** ___
**Tests Blocked:** ___ (by dropdown bug)

**Can we proceed with signup flow?**
- [ ] ✅ Yes - Most functionality works
- [ ] ⚠️ Partial - Some issues but can continue
- [ ] ❌ No - Too many blockers

---

## 🎯 Recommendations

### Should We Fix Dropdown Now?
- [ ] **Yes** - Blocks too much testing
- [ ] **No** - Continue documenting other issues

### Other Observations
```
(Any UX issues, performance problems, design feedback?)




```

---

## 📝 Next Actions

After completing this checklist:

1. [ ] Update TEST_FINDINGS_JOURNEY_1.md with new bugs
2. [ ] Decide: Fix dropdown now or continue testing?
3. [ ] If continuing: Test CarePrep token flow (Journey PT1)
4. [ ] If fixing: Implement dropdown fix and retest
5. [ ] Update todo list

---

**Tester:** _____________________
**Completed:** _____________________
**Ready for Fix:** [ ] Yes [ ] No
