# TASK-0007 Rollback Test - Execution Guide

**Execution Date:** 2025-11-06  
**Start Time:** 13:50 UTC  
**Test Commit:** `be72357`  
**Rollback Target:** `1be6e19`

---

## ⚠️ IMPORTANT: Execute these steps on PythonAnywhere

You need to SSH into PythonAnywhere to complete this test. I cannot SSH directly from this environment.

---

## Phase 1: Deploy Test Commit to Production

### Step 1: SSH into PythonAnywhere

```bash
ssh pythonpydev@ssh.pythonanywhere.com
```

### Step 2: Navigate to Project Directory

```bash
cd ~/total_bankroll
```

### Step 3: Check Current State

```bash
# Check current branch and commit
git status
git log --oneline -3

# Expected output should show you're behind origin/main
```

### Step 4: Run Pre-Deployment Checks

```bash
# Activate virtual environment
workon bankroll_venv

# Run environment parity check
python scripts/check_env_parity.py
```

**Expected Result:** All checks should pass ✅

### Step 5: Pull Latest Code

```bash
git pull origin main
```

**Expected:** Should pull commit `be72357` with the test changes

### Step 6: Verify the Change Locally

```bash
# Check that the test change is present
grep "ROLLBACK TEST" src/total_bankroll/templates/core/index.html
```

**Expected Output:** Should show the line with "Dashboard - ROLLBACK TEST"

### Step 7: Create Database Backup (IMPORTANT!)

```bash
# Create timestamped backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mysqldump -u pythonpydev -p pythonpydev\$bankroll > ~/backups/bankroll_${TIMESTAMP}.sql

# Verify backup created
ls -lh ~/backups/bankroll_${TIMESTAMP}.sql

# Record the timestamp for later
echo "Backup created: bankroll_${TIMESTAMP}.sql"
```

**Expected:** Backup file should be several MB in size (not 0 bytes)

**⏰ Record Deployment Start Time:** `__________`

### Step 8: Reload Web Application

```bash
# Option 1: Via PythonAnywhere Web Interface (RECOMMENDED)
# 1. Open browser to: https://www.pythonanywhere.com/user/pythonpydev/webapps/
# 2. Find stakeeasy.net
# 3. Click the green "Reload" button

# Option 2: Via API (if you have token configured)
# curl -X POST https://www.pythonanywhere.com/api/v0/user/pythonpydev/webapps/stakeeasy.net/reload/ \
#      -H "Authorization: Token YOUR_API_TOKEN"
```

**⏰ Record Reload Time:** `__________`

### Step 9: Verify Test Deployment

1. **Open browser to:** https://stakeeasy.net
2. **Check homepage title:** Should show "Dashboard - ROLLBACK TEST"
3. **Check subtitle:** Should show "[TEST DEPLOYMENT]"
4. **Take screenshot** for documentation

**⏰ Record Verification Time:** `__________`

**✅ Phase 1 Complete if:**
- Test text is visible on live site
- Site loads without errors
- No broken functionality

---

## Phase 2: Execute Rollback Procedure

**⏰ Record Rollback Start Time:** `__________`

### Step 1: Still in PythonAnywhere SSH

```bash
# Make sure you're in the project directory
cd ~/total_bankroll

# Verify current commit
git log --oneline -3
```

**Expected:** HEAD should be at `be72357` (the test commit)

### Step 2: Identify Rollback Target

```bash
# The rollback target is the commit BEFORE the test commit
git log --oneline -5
```

**Rollback Target:** `1be6e19` - "docs: Add UptimeRobot monitoring documentation (TASK-0006)"

### Step 3: Execute Rollback

```bash
# Perform code rollback
git reset --hard 1be6e19

# Verify rollback successful
git log --oneline -3
```

**Expected:** HEAD should now be at `1be6e19`

### Step 4: Verify Local Change Reverted

```bash
# Check that test change is gone
grep "ROLLBACK TEST" src/total_bankroll/templates/core/index.html
```

**Expected:** Should return nothing (exit code 1) - the text is not found

### Step 5: Reload Web Application Again

```bash
# Return to PythonAnywhere Web Interface
# Click "Reload" button again for stakeeasy.net
```

**⏰ Record Reload Time:** `__________`

### Step 6: Verify Rollback on Live Site

1. **Refresh browser:** https://stakeeasy.net
2. **Check homepage title:** Should show "Dashboard" (no "ROLLBACK TEST")
3. **Check subtitle:** Should be normal (no "[TEST DEPLOYMENT]")
4. **Take screenshot** for documentation

**⏰ Record Verification Time:** `__________`

**✅ Phase 2 Complete if:**
- Test text is gone from live site
- Site shows original content
- Site loads without errors
- No functionality broken

---

## Phase 3: Documentation and Analysis

### Calculate Timings

Fill in the timing table:

| Phase | Duration | Notes |
|-------|----------|-------|
| Deploy test commit | _____ min | From pull to verification |
| Execute rollback | _____ min | From reset to verification |
| **Total Test Duration** | _____ min | Should be < 5 minutes |

### Issues Encountered

Document any issues (or write "None"):

```
_______________________________________________
_______________________________________________
_______________________________________________
```

### Lessons Learned

```
_______________________________________________
_______________________________________________
_______________________________________________
```

### Process Improvements Needed

If deployment checklist needs updates:

```
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## ✅ Success Criteria Checklist

- [ ] Test commit successfully deployed to production
- [ ] Test changes visible on live site
- [ ] Rollback procedure executed without errors
- [ ] Site returned to pre-test state after rollback
- [ ] No data loss occurred
- [ ] No unexpected downtime
- [ ] Total time for rollback: < 5 minutes
- [ ] Process documented

---

## Post-Test Cleanup (Back in Local Dev Environment)

After completing the test on PythonAnywhere, return to your local machine:

```bash
# Your local repo still has the test commit
cd /home/ed/MEGA/total_bankroll

# Check status
git status

# Note: Your local main is now ahead of origin/main
# because origin/main was reset on the server

# You have two options:

# Option A: Keep test commit in history (for documentation)
# Do nothing - the commit exists but isn't on any branch

# Option B: Remove test commit from local history
git reset --hard 1be6e19
git push origin main --force  # Force push to match production

# Option B is cleaner but removes the test from history
```

---

## Final Documentation

After completing the test, update:

1. ✅ `.github/TASK-0007_rollback_test.md` - Fill in all timing and results
2. ✅ `.github/deployment_checklist.md` - Add any improvements discovered
3. ✅ Commit documentation updates
4. ✅ Mark TASK-0007 as complete in task list

---

## Emergency Rollback (If Something Goes Wrong)

If the test causes unexpected issues:

```bash
# Restore from backup
cd ~/total_bankroll
workon bankroll_venv
mysql -u pythonpydev -p pythonpydev\$bankroll < ~/backups/bankroll_TIMESTAMP.sql

# Ensure code is at stable state
git reset --hard 1be6e19

# Reload app
# Use PythonAnywhere web interface to reload
```

---

**Test prepared by:** GitHub Copilot CLI  
**Test ready for execution:** ✅ YES  
**Risk level:** 🟢 LOW (cosmetic change only)
