# TASK-0007: Rollback Procedure Test

**Task Priority:** 🔴 P0 (Critical)  
**Date Started:** 2025-11-06  
**Date Completed:** 2025-11-06  
**Status:** ✅ COMPLETED

## Objective

Verify that the rollback procedure works correctly before it's needed in an emergency. This ensures confidence in the deployment and recovery process.

## Prerequisites Completed

- ✅ TASK-0001: Deployment checklist created
- ✅ TASK-0002: Environment parity check script
- ✅ TASK-0003: Deployment automation script
- ✅ TASK-0004: Backup directory setup on PythonAnywhere
- ✅ TASK-0005: Python version documented
- ✅ TASK-0006: UptimeRobot monitoring setup

## Test Commit Information

**Test Commit Hash:** `be72357`  
**Test Commit Message:** "test: Add rollback test markers to homepage (TASK-0007 TEST COMMIT)"  
**Previous Commit (Rollback Target):** `1be6e19` - "docs: Add UptimeRobot monitoring documentation (TASK-0006)"

**Change Made:** Modified `src/total_bankroll/templates/core/index.html`
- Changed Dashboard title from "Dashboard" to "Dashboard - ROLLBACK TEST"
- Added "[TEST DEPLOYMENT]" to subtitle
- This change is highly visible and easily verifiable

## Test Procedure

### Phase 1: Deploy Test Commit to Production

1. **Pre-deployment checks:**
   ```bash
   cd ~/total_bankroll
   python scripts/check_env_parity.py
   ```

2. **Deploy using automation script:**
   ```bash
   ./scripts/deploy.sh
   ```
   
   The script will:
   - Create a database backup
   - Show changes being deployed
   - Prompt for confirmation
   - Pull latest code
   - Update dependencies (if needed)
   - Apply migrations (if any)
   - Provide reload instructions

3. **Reload web app:**
   - Go to PythonAnywhere Web tab
   - Click "Reload" button for stakeeasy.net

4. **Verify test deployment:**
   - Visit https://stakeeasy.net
   - Confirm homepage shows "Dashboard - ROLLBACK TEST"
   - Confirm subtitle shows "[TEST DEPLOYMENT]"
   - Take screenshot for documentation

### Phase 2: Execute Rollback Procedure

1. **SSH into PythonAnywhere:**
   ```bash
   ssh pythonpydev@ssh.pythonanywhere.com
   cd ~/total_bankroll
   ```

2. **Identify rollback target:**
   ```bash
   git log -5 --oneline
   # Target commit: 1be6e19
   ```

3. **Execute rollback (Code Only):**
   ```bash
   git reset --hard 1be6e19
   ```

4. **Reload web application:**
   - Go to PythonAnywhere Web tab
   - Click "Reload" button

5. **Verify rollback successful:**
   - Visit https://stakeeasy.net
   - Confirm homepage shows "Dashboard" (without "ROLLBACK TEST")
   - Confirm subtitle is normal (no "[TEST DEPLOYMENT]")
   - Take screenshot for documentation

### Phase 3: Documentation and Cleanup

1. **Document results:**
   - Record time taken for each phase
   - Note any issues encountered
   - Document user experience during rollback

2. **Update procedures if needed:**
   - If any steps were unclear or failed, update deployment checklist
   - Document lessons learned

3. **Return to normal state:**
   ```bash
   # The rollback itself moves us back to the previous state
   # The test commit (be72357) is now "orphaned" in git history
   # This is expected and acceptable for this test
   ```

## Success Criteria

- [x] Test commit successfully deployed to production
- [x] Test changes visible on live site
- [x] Rollback procedure executed without errors
- [x] Site returned to pre-test state after rollback
- [x] No data loss occurred
- [x] No unexpected downtime
- [x] Total time for rollback: < 5 minutes (actual rollback < 1 min)
- [x] Process documented

## Timing Log

| Phase | Start Time | End Time | Duration | Notes |
|-------|-----------|----------|----------|-------|
| Deploy test commit | 17:32 UTC | 17:55 UTC | ~23 min | Included troubleshooting Vite/npm issues |
| Verify test deployment | 17:55 UTC | 17:55 UTC | < 1 min | Test text visible on live site |
| Execute rollback | 18:00 UTC | 18:00 UTC | < 1 min | git reset --hard executed |
| Verify rollback | 18:14 UTC | 18:14 UTC | < 1 min | Test text removed, site normal |
| **Total** | 17:32 UTC | 18:14 UTC | ~42 min | Actual rollback procedure < 2 minutes |

## Issues Encountered

### Issue 1: MySQL Backup Command
**Problem:** Standard mysqldump command failed with socket error, then with tablespaces permission error.

**Solution:** Use remote MySQL host with --no-tablespaces flag:
```bash
mysqldump -h pythonpydev.mysql.pythonanywhere-services.com -u pythonpydev -p --no-tablespaces pythonpydev\$bankroll > backup.sql
```

### Issue 2: Vite Build Not Working on Production
**Problem:** 
- npm modules corrupted (rollup missing)
- Vite config had incorrect entry path
- Build process not documented in deployment procedure

**Workaround Used:** Created minimal manifest.json manually to proceed with test.

**Impact:** Significant time spent troubleshooting (20+ minutes)

### Issue 3: Static Assets Not in Git
**Problem:** Vite build outputs are in .gitignore, so they don't deploy with git pull.

**Implication:** Deployment process needs to include asset building step.

## Lessons Learned

### 1. Core Rollback Procedure Works Perfectly ✅
- `git reset --hard <commit>` executed flawlessly
- Web app reload process is simple and fast
- Actual rollback time: < 1 minute
- No data loss, no corruption

### 2. Pre-Rollback Testing is Essential
- Discovered multiple deployment issues that would have caused problems in a real emergency
- Issues found: MySQL backup syntax, Vite builds, asset deployment
- These would have added stress and time in a real incident

### 3. Deployment Process Needs Improvement
- Asset building not documented
- MySQL backup command incorrect in checklist
- npm/Node.js dependency management needs attention

### 4. Documentation is Invaluable
- Having step-by-step procedures made the test manageable
- Clear rollback commands reduced cognitive load
- Test environment allowed safe experimentation

## Rollback Procedure Updates Needed

### Update 1: MySQL Backup Command
**Current:** Uses localhost without flags
**Updated:** Must use PythonAnywhere MySQL host with --no-tablespaces

```bash
# OLD (incorrect)
mysqldump -u pythonpydev -p pythonpydev\$bankroll > backup.sql

# NEW (correct)
mysqldump -h pythonpydev.mysql.pythonanywhere-services.com -u pythonpydev -p --no-tablespaces pythonpydev\$bankroll > backup.sql
```

### Update 2: Add Asset Build Step
**New step needed in deployment checklist:**
```bash
# After git pull, before reload
cd ~/total_bankroll
npm run build
```

### Update 3: Document Vite/npm Prerequisites
- Node.js version requirements
- npm package integrity checks
- Vite configuration validation

### Update 4: Add Pre-Deployment Asset Verification
```bash
# Check that manifest exists before deploying
test -f src/total_bankroll/static/dist/.vite/manifest.json || npm run build
```

## Next Steps After Completion

1. Update `.github/deployment_checklist.md` if needed
2. Commit this completed test documentation
3. Mark TASK-0007 as complete
4. Proceed to Phase 1 tasks (TASK-1001+)

---

## Quick Reference: Rollback Commands

### Code-Only Rollback
```bash
cd ~/total_bankroll
git log -5 --oneline  # Find target commit
git reset --hard <COMMIT_HASH>
# Then reload web app via PythonAnywhere interface
```

### Full Rollback (Code + Database)
```bash
# 1. Rollback code
cd ~/total_bankroll
git reset --hard <COMMIT_HASH>

# 2. Restore database
workon bankroll_venv
mysql -u pythonpydev -p pythonpydev\$bankroll < ~/backups/bankroll_<TIMESTAMP>.sql

# 3. Downgrade migrations if needed
export FLASK_APP="src/total_bankroll"
flask db downgrade <PREVIOUS_REVISION>

# 4. Reload web app
```

---

**Test Status:** Ready for execution on production  
**Risk Level:** Low (cosmetic change only, no database modifications)  
**Expected Impact:** None (visible only on homepage for duration of test)
