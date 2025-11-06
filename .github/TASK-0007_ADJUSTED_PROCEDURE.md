# TASK-0007 Adjusted Procedure

## Current Situation on PythonAnywhere

**Issue Discovered:** Production is ahead of origin/main by 38 commits, not behind.

```
HEAD: 36766a5 (Merge branch 'main')
origin/main: f049f40 (fix path to index in vite.config.mjs)
```

This means:
1. Production has local commits that haven't been pushed to GitHub
2. We need to sync production with GitHub first
3. Then we can proceed with the rollback test

## Adjusted Procedure

### Step 1: Understand Current State (ALREADY DONE)

You've discovered production is ahead. This is valuable information!

### Step 2: Stash or Discard Node Module Changes

The node_modules changes are not important for this test:

```bash
cd ~/total_bankroll

# Option A: Discard node_modules changes (RECOMMENDED for test)
git checkout -- node_modules/.package-lock.json
git clean -fd node_modules/

# Option B: Stash everything (if you want to keep changes)
git stash push -m "Stashing before rollback test"
```

### Step 3: Check Production Commits

```bash
# See what the 38 commits are
git log --oneline -40

# Compare with origin
git log origin/main..HEAD --oneline
```

**Decision Point:** Do these 38 commits contain important production changes?

### Step 4A: If Commits Are Important - Push to GitHub First

```bash
# Push production changes to GitHub
git push origin main

# Then pull back to get our test commit
git pull origin main

# Should now be in sync with test commit be72357
```

### Step 4B: If Commits Are NOT Important - Reset to Origin

```bash
# WARNING: This discards the 38 local commits
git fetch origin
git reset --hard origin/main

# Then pull test commit
git pull origin main

# Should now have test commit be72357
```

### Step 5: Verify We Have Test Commit

```bash
git log --oneline -5

# Should show:
# be72357 test: Add rollback test markers to homepage (TASK-0007 TEST COMMIT)
# 1be6e19 docs: Add UptimeRobot monitoring documentation (TASK-0006)
# ...
```

### Step 6: Check for Test Changes

```bash
grep "ROLLBACK TEST" src/total_bankroll/templates/core/index.html
```

**Expected:** Should show the test text

---

## Recommended Action for Rollback Test

Since this is a **test environment concern** and we want to proceed with TASK-0007:

### RECOMMENDED: Simplified Approach

**On PythonAnywhere, execute:**

```bash
cd ~/total_bankroll

# 1. Clean working directory
git checkout -- .
git clean -fd

# 2. Fetch latest from GitHub
git fetch origin

# 3. Record current HEAD for rollback baseline
git log --oneline -1 > ~/rollback_test_baseline.txt
BASELINE=$(git rev-parse HEAD)
echo "Baseline commit: $BASELINE"

# 4. Get test commit
git reset --hard origin/main
git pull origin main

# 5. Verify test commit present
git log --oneline -3
grep "ROLLBACK TEST" src/total_bankroll/templates/core/index.html

# If grep finds it, continue to backup step
```

### Modified Test Flow

**Phase 1: Deploy Test (Modified)**

```bash
# Already at test commit from steps above

# Create backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mysqldump -u pythonpydev -p pythonpydev\$bankroll > ~/backups/bankroll_${TIMESTAMP}.sql

# Reload app (use PythonAnywhere web interface)
# Verify at https://stakeeasy.net
```

**Phase 2: Rollback Test**

```bash
cd ~/total_bankroll

# Rollback to commit BEFORE test commit (1be6e19)
git reset --hard 1be6e19

# Verify
git log --oneline -3
grep "ROLLBACK TEST" src/total_bankroll/templates/core/index.html
# Should find nothing

# Reload app (use PythonAnywhere web interface)
# Verify at https://stakeeasy.net - test text should be gone
```

**Phase 3: Return to Production Baseline (IMPORTANT!)**

After completing the rollback test, return to original production state:

```bash
cd ~/total_bankroll

# Return to whatever commit production was at before test
# Use the baseline we recorded
git reset --hard $BASELINE

# Or if you pushed to GitHub (Step 4A):
git reset --hard 36766a5

# Reload app one more time
```

---

## Quick Decision Tree

**Q: Do you know what the 38 commits on production contain?**

- **YES, they're important** → Push to GitHub first (Step 4A)
- **NO / DON'T CARE** → Reset to origin/main (Step 4B - RECOMMENDED for test)
- **UNSURE** → Run `git log origin/main..HEAD --oneline` to review them first

---

## Immediate Next Command

**Execute this on PythonAnywhere to see what the 38 commits are:**

```bash
cd ~/total_bankroll
git log origin/main..HEAD --oneline | head -20
```

Copy the output and share it - I'll help you decide the best approach.

---

**Status:** Waiting for decision on how to handle 38 local commits
