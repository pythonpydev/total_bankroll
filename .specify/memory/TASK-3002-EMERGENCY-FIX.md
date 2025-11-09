# TASK-3002: Emergency Production Fix

**Date:** 2025-11-09  
**Status:** 🔴 CRITICAL - Production Down  
**Issue:** Corrupted .env file preventing app from loading

## Root Cause

When deploying TASK-3001 caching configuration, the command `cat >> .env` was used to append cache settings. This caused the existing `CHROME_BINARY_PATH` line (which was very long) to break across multiple lines, corrupting the .env file format and preventing Python from parsing it correctly.

## Symptoms

1. ✅ App loads successfully in Python console: `create_app('production')` works
2. ❌ Web app shows "Something went wrong" page
3. ❌ No errors in server.log or error.log  
4. Browser console shows CSS/Bootstrap warnings (irrelevant - site in quirks mode due to error page)
5. Development server also broken due to missing database tables (unrelated issue)

## The Fix

### On PythonAnywhere Bash Console:

```bash
# Step 1: Pull the fix script from GitHub
cd ~/total_bankroll
git pull

# Step 2: Run the emergency fix script
bash scripts/emergency_fix_production_env.sh

# Step 3: Reload the web app
# Go to: https://www.pythonanywhere.com/user/pythonpydev/consoles/
# Click the "Web" tab
# Click the big green "Reload pythonpydev.pythonanywhere.com" button

# Step 4: Test
# Visit https://stakeeasy.net/
# Should load correctly now!
```

## What the Script Does

1. Backs up the broken .env to `.env.broken_backup_TIMESTAMP`
2. Creates a completely clean .env file from scratch with:
   - All existing configuration (OAuth, Mail, Database, etc.)
   - Cache configuration (SimpleCache with 300s timeout)
   - NO CHROME_BINARY_PATH (not needed on PythonAnywhere)
   - NO duplicate entries
3. Verifies the file format is correct

## Verification Steps

After running the script and reloading:

```bash
# Check app loads in console
python3 << 'EOF'
from src.total_bankroll import create_app
app = create_app('production')
print("✅ App loads successfully!")
EOF

# Visit website
curl -I https://stakeeasy.net/
# Should return HTTP 200 or 302 (redirect), not 500

# Check cache works
python3 << 'EOF'
from src.total_bankroll import create_app
from src.total_bankroll.extensions import cache
app = create_app('production')
with app.app_context():
    cache.set('test', 'works')
    print(f"Cache test: {cache.get('test')}")
EOF
# Should print: Cache test: works
```

## Lesson Learned

**NEVER use `cat >> .env` to append to production config files!**

### ❌ BAD (what we did):
```bash
cat >> .env << 'EOF'
CACHE_TYPE=SimpleCache
EOF
```

### ✅ GOOD (what to do instead):
```bash
# Option 1: Use echo for each line
echo "" >> .env
echo "# Cache Configuration" >> .env
echo "CACHE_TYPE=SimpleCache" >> .env

# Option 2: Use a proper text editor
nano .env  # Add lines manually

# Option 3: Use sed to insert after a specific line
sed -i '/^MAIL_PASSWORD=/a\\n# Cache Configuration\nCACHE_TYPE=SimpleCache' .env

# Option 4: Use a deployment script that manages .env properly
```

## Prevention for Future

1. ✅ Always test .env changes in development first
2. ✅ Use version control for .env templates (not actual .env with secrets)
3. ✅ Use deployment scripts that validate .env format
4. ✅ Always back up .env before making changes
5. ✅ Test app loading in Python console before reloading web app

## Related Files

- `scripts/emergency_fix_production_env.sh` (the fix)
- `.env` (production - fixed)
- `.specify/memory/TASK-3002-COMPLETION.md` (original task)
- `.specify/memory/TASK-3002-DEPLOYMENT-GUIDE.md` (deployment guide)

## Status

- **Code:** ✅ TASK-3002 code complete and working
- **Production Deployment:** ⏳ Awaiting emergency fix execution
- **Development:** ✅ Working (after running `flask db upgrade`)

## Next Steps

1. Execute emergency fix script on production
2. Reload PythonAnywhere web app  
3. Test production site
4. Mark TASK-3002 as ✅ COMPLETED
5. Update tasks.md
6. Proceed to TASK-3003 (Celery setup)
