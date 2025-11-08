# TASK-1002: Production Deployment Guide

**Task:** Complete Vite Configuration  
**Target:** PythonAnywhere Production Server  
**Date:** 2025-11-08

---

## Prerequisites

Before deploying, ensure you have:
- [x] SSH access to PythonAnywhere
- [x] Git repository updated with TASK-1002 changes
- [x] Backup of production site (follow TASK-0004 procedure)

---

## Deployment Steps

### Step 1: SSH into PythonAnywhere

```bash
ssh pythonpydev@ssh.pythonanywhere.com
```

### Step 2: Navigate to Project Directory

```bash
cd ~/total_bankroll
```

### Step 3: Pull Latest Changes

```bash
git fetch origin
git status  # Check for any uncommitted changes
git pull origin main
```

**Expected output:**
```
Updating abc1234..a9ef4bb
Fast-forward
 .gitignore                                    |    5 +
 package.json                                  |    6 +-
 src/total_bankroll/frontend/card_utils.js    |  XXX +++++++
 src/total_bankroll/frontend/chart_utils.js   |  XXX +++++++
 src/total_bankroll/vite_asset_helper.py      |   14 +-
 vite.config.mjs                               |   51 +-
 ...
```

### Step 4: Install Node.js (if not already installed)

Check if Node.js is available:
```bash
node --version
npm --version
```

If not installed, you have two options:

#### Option A: Use PythonAnywhere's Node.js (Recommended if available)
Check PythonAnywhere documentation for available Node.js versions.

#### Option B: Install Node.js locally (if allowed)
```bash
# This may not be available on all PythonAnywhere plans
# Check with PythonAnywhere support first
```

### Step 5: Install Vite

Due to the npm installation issue we encountered, install Vite globally:

```bash
npm install -g vite@5.4.11
```

**If you get permission errors**, try:
```bash
# Create a local npm prefix directory
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to PATH (add this to ~/.bashrc for persistence)
export PATH=~/.npm-global/bin:$PATH

# Now install vite
npm install -g vite@5.4.11
```

### Step 6: Verify Vite Installation

```bash
which vite
vite --version
```

**Expected output:**
```
/home/pythonpydev/.npm-global/bin/vite
vite v5.4.11
```

### Step 7: Build Frontend Assets

```bash
cd ~/total_bankroll
vite build
```

**Expected output:**
```
vite v5.4.11 building for production...
transforming (1) main.js
✓ 3 modules transformed.
rendering chunks (1)...
computing gzip size (0)...
computing gzip size (1)...
computing gzip size (2)...
../static/assets/.vite/manifest.json      0.12 kB │ gzip: 0.11 kB
../static/assets/assets/main-DGU9veUe.js  5.04 kB │ gzip: 2.07 kB
✓ built in 225ms
```

### Step 8: Verify Build Output

```bash
ls -la src/total_bankroll/static/assets/
ls -la src/total_bankroll/static/assets/.vite/
cat src/total_bankroll/static/assets/.vite/manifest.json
```

**Expected structure:**
```
src/total_bankroll/static/assets/
├── .vite/
│   └── manifest.json
└── assets/
    └── main-[hash].js
```

### Step 9: Test the Build Locally (Optional)

If you have a development database on PythonAnywhere:

```bash
cd ~/total_bankroll
workon bankroll_venv  # or whatever your virtualenv is called
export FLASK_APP="src/total_bankroll"
flask run --port 8000
```

Then visit `http://pythonpydev.pythonanywhere.com:8000` in your browser (if console ports are accessible).

### Step 10: Reload the Web App

1. Go to the **Web** tab in your PythonAnywhere dashboard
2. Click the big green **"Reload"** button
3. Wait for the reload to complete

### Step 11: Verify Deployment

1. Visit your production site: `https://stakeeasy.net`
2. Open browser DevTools (F12)
3. Go to the **Network** tab
4. Reload the page
5. Check for:
   - ✅ `main-[hash].js` loads successfully from `/static/assets/assets/`
   - ✅ No 404 errors for JavaScript files
   - ✅ Console shows no JavaScript errors
   - ✅ Site functionality works (theme toggle, modals, etc.)

### Step 12: Check Application Logs

If anything goes wrong:

```bash
# On PythonAnywhere, check error log
tail -f ~/logs/error.log

# Or from the Web tab in PythonAnywhere dashboard:
# Click "Log files" to view error.log and server.log
```

---

## Rollback Procedure (If Needed)

If the deployment fails:

### Quick Rollback

```bash
cd ~/total_bankroll
git log --oneline  # Find the commit before a9ef4bb
git reset --hard <previous-commit-hash>

# Rebuild with old config (if vite.config.mjs was different)
vite build

# Reload web app from dashboard
```

### Full Rollback with Database Restore

If you need to restore everything:

```bash
cd ~/total_bankroll
git reset --hard <previous-commit-hash>

# If you made a backup before deployment:
mysql -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p --no-tablespaces \
  pythonpydev\$bankroll < ~/backups/backup_YYYY-MM-DD.sql

# Reload web app
```

---

## Troubleshooting

### Issue: `vite: command not found`

**Solution:**
```bash
# Check if vite is in your PATH
echo $PATH

# If ~/.npm-global/bin is not in PATH, add it:
export PATH=~/.npm-global/bin:$PATH

# Make it permanent:
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Issue: `Cannot find module 'vite'`

**Solution:**
```bash
# Vite needs to be accessible when running vite build
# Make sure it's installed globally (see Step 5)
npm list -g vite
```

### Issue: `manifest.json not found` error in Flask app

**Solution:**
```bash
# Verify manifest exists
cat src/total_bankroll/static/assets/.vite/manifest.json

# If it doesn't exist, run:
cd ~/total_bankroll
vite build
```

### Issue: JavaScript not loading on the site

**Checklist:**
1. Check manifest.json exists: `cat src/total_bankroll/static/assets/.vite/manifest.json`
2. Check built JS exists: `ls -la src/total_bankroll/static/assets/assets/`
3. Check base.html template uses: `{{ vite_asset('main.js') }}`
4. Check browser console for errors
5. Check Flask app has `init_vite_asset_helper(app)` called

### Issue: Permission errors during npm install

**Solution:**
```bash
# Use a local npm directory
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
npm install -g vite@5.4.11
```

### Issue: Old JavaScript still loading (cache issue)

**Solution:**
- The manifest uses content hashing, so this shouldn't happen
- If it does, check that the hash in the filename changed
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that the manifest.json was updated

---

## Post-Deployment Verification Checklist

- [ ] Site loads without errors
- [ ] JavaScript functionality works:
  - [ ] Theme toggler (dark/light mode)
  - [ ] Modal popups
  - [ ] Back to top button
  - [ ] Cookie consent banner (if in EU)
  - [ ] Toast notifications
- [ ] Browser console shows no errors
- [ ] Network tab shows `main-[hash].js` loads successfully
- [ ] Page load time is acceptable
- [ ] Mobile view works correctly

---

## Notes for Future Deployments

### Automated Build in Deployment Script

You can add this to your `scripts/deploy.sh`:

```bash
# After git pull, before reloading app:
echo "Building frontend assets..."
cd ~/total_bankroll
vite build
if [ $? -ne 0 ]; then
    echo "❌ Vite build failed!"
    exit 1
fi
echo "✓ Vite build completed"
```

### Alternative: Local Build, Commit Assets

If you have issues with npm/node on PythonAnywhere, you can:

1. Build locally: `npm run build`
2. Commit the built assets: `git add src/total_bankroll/static/assets/`
3. Push to repository
4. Pull on production (no build step needed)

**Pros:** No npm/node needed on production  
**Cons:** Larger git repository, assets in version control

---

## Estimated Deployment Time

- With SSH access ready: **10-15 minutes**
- If Node.js needs installation: **20-30 minutes**
- Including testing: **30-45 minutes**

---

## Support Resources

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Vite Documentation:** https://vitejs.dev/
- **Project Repository:** https://github.com/pythonpydev/total_bankroll

---

**Last Updated:** 2025-11-08  
**Deployment Status:** Ready for Production  
**Risk Level:** Low (JavaScript bundling change, backwards compatible)

---

## UPDATE (2025-11-08 14:31 UTC)

### Issue Fixed: "Could not resolve entry module index.html"

**Problem:** During production deployment, `vite build` failed with:
```
error during build:
Could not resolve entry module "index.html".
```

**Cause:** The `vite.config.mjs` had `root: path.resolve(__dirname, 'src/total_bankroll/frontend')` set. When `root` is defined, Vite expects an `index.html` file in that directory by default. Since we're using a JavaScript entry point (not HTML), this caused the error.

**Fix:** Removed the `root` configuration line. The JavaScript entry point is already properly defined in `rollupOptions.input`, so the `root` setting was unnecessary.

**Fixed commit:** `01658bf` - "fix(build): Remove root config to fix 'Could not resolve index.html' error"

**Action Required:** Pull the latest changes before building:
```bash
cd ~/total_bankroll
git pull origin main
vite build
```

The build should now complete successfully!
