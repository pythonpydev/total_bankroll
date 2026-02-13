# TASK-3002 Production Fix - Quick Instructions

## Problem
The production site is not loading because the `.env` file is corrupted (broken `CHROME_BINARY_PATH` line).

## Fix (Takes ~2 minutes)

### On PythonAnywhere Bash Console:

```bash
# 1. Pull the fix script from GitHub
cd ~/total_bankroll
git pull

# 2. Run the fix script
bash scripts/fix_production_env.sh

# 3. You should see:
#    ✓ Backup created
#    ✓ Clean .env created
#    ✅ App loads successfully!
#    ✅ Cache is working!
```

### 4. Reload Web App
- Go to: https://www.pythonanywhere.com/user/pythonpydev/webapps/
- Click the big green **"Reload www.stakeeasy.net"** button

### 5. Test
- Visit: https://www.stakeeasy.net/
- Should load successfully!

---

## What the script does:
1. Backs up your broken `.env` file
2. Creates a clean `.env` with proper cache configuration
3. Tests that the app can load
4. Tests that cache is working

## If something goes wrong:
The script creates a backup at `.env.broken_YYYYMMDD_HHMMSS` so you can restore it if needed.

---

**Estimated time:** 2 minutes  
**Risk level:** Very low (script creates backup first)
