# TASK-3002 Production Fix Guide

**Issue:** Production site failing after TASK-3002 deployment due to corrupted `.env` file  
**Root Cause:** Using `cat >> .env` to append cache configuration broke the `CHROME_BINARY_PATH` line across multiple lines  
**Status:** ⚠️ REQUIRES IMMEDIATE FIX

---

## Problem Summary

The production `.env` file has a line break in the middle of the `CHROME_BINARY_PATH` value:

```bash
CHROME_BINARY_PATH=/var/lib/flatpak/app/com.google.Chrome/x86_64/stable/f574e6db34f15b196fb792633ce63eb3229d98d170d49abbbb51609d1a4e661f/files/extra/google-c
hrome  # ← BROKEN ACROSS TWO LINES
```

This causes the Python dotenv parser to fail silently, and the app cannot load properly.

---

## Immediate Fix Steps

### On PythonAnywhere Bash Console:

```bash
# 1. Navigate to project
cd ~/total_bankroll

# 2. Backup the broken .env
cp .env .env.broken_$(date +%Y%m%d_%H%M%S)

# 3. Download the clean .env file from your local machine
# (You'll need to copy the content from .env.production.clean)

# 4. Create new .env with clean content
cat > .env << 'END_OF_ENV'
# .env file for total_bankroll project
FLASK_APP=total_bankroll
FLASK_ENV=production

# Flask Secret Key (for session management)
SECRET_KEY='daaf7210a6215a899b40ed45c644fa2be222ba7b85a5ed59'

# Exchange Rate API Key (from exchangerate-api.com)
EXCHANGE_RATE_API_KEY="447d94e4f5ddcbc0c179a1fd"

# Development Database Credentials
DEV_DB_HOST="localhost"
DEV_DB_NAME="bankroll"
DEV_DB_USER="root"
DEV_DB_PASS="f3gWoQe7X7BFCm"

# Production Database Credentials
DB_HOST_PROD="pythonpydev.mysql.pythonanywhere-services.com"
DB_NAME_PROD="pythonpydev$bankroll"
DB_USER_PROD="pythonpydev"
DB_PASS_PROD="f3gWoQe7X7BFCm"

# Flask-Security Password Salt
SECURITY_PASSWORD_SALT=cd850d8ac439bd663b75471bf9f1d865

# Do not need HTTPS on local test server
OAUTHLIB_INSECURE_TRANSPORT=1
OAUTHLIB_RELAX_TOKEN_SCOPE=1

# Google OAuth Credentials
GOOGLE_CLIENT_ID="930176693065-3ed24l13tfp29qa17a2au8hn06lqsaep.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"

# X (Twitter) OAuth Credentials
TWITTER_CLIENT_ID="WXZDNVJnbHNIeHBCVDVyWFZRVVY6MTpjaQ"
TWITTER_CLIENT_SECRET="22Odo5pKJo_DWX99dtQ2uZyg6_JmaXH99nAdo-bB0CIGmAu88S"

# Facebook OAuth Credentials
FACEBOOK_CLIENT_ID="760019966781286"
FACEBOOK_CLIENT_SECRET="5eff3e58dcd4fa011aa4cf1dae066d7f"

# Mail Server Settings (Zoho Mail)
MAIL_SERVER="smtppro.zoho.eu"
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME="admin@stakeeasy.net"
MAIL_PASSWORD="D5gibChFbVAg"

# Cache Configuration
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300
END_OF_ENV

# 5. Verify the file looks correct
tail -10 .env

# 6. Test that app can load
workon bankroll_venv
python3 -c "from src.total_bankroll import create_app; app = create_app('production'); print('✅ App loads successfully')"

# 7. Reload web app
# Go to PythonAnywhere Web tab and click "Reload"
```

---

## Verification Steps

1. **Check app loads in Python console:**
   ```python
   >>> from src.total_bankroll import create_app
   >>> from src.total_bankroll.extensions import cache
   >>> app = create_app('production')
   >>> with app.app_context():
   ...     cache.set('test', 'works')
   ...     print(f"Cache test: {cache.get('test')}")
   ```
   
   Expected output: `Cache test: works`

2. **Check website loads:**
   - Visit https://www.stakeeasy.net/
   - Should load without "Something went wrong" page

3. **Check error logs:**
   ```bash
   tail -50 /var/log/pythonpydev.pythonanywhere.com.error.log
   ```
   Should show no new errors after reload

---

## Lessons Learned

### ❌ **DON'T DO THIS:**
```bash
# BAD: Appending to .env with cat >> can corrupt existing lines
cat >> .env << 'EOF'
# New config
CACHE_TYPE=SimpleCache
EOF
```

### ✅ **DO THIS INSTEAD:**
```bash
# GOOD: Use proper editing or sed to add lines safely
echo "" >> .env
echo "# Cache Configuration" >> .env
echo "CACHE_TYPE=SimpleCache" >> .env
echo "CACHE_DEFAULT_TIMEOUT=300" >> .env
```

### ✅ **OR THIS:**
```bash
# BETTER: Use a text editor
nano .env
# Then manually add the lines
```

---

## Root Cause Analysis

The `cat >> .env` command in the TASK-3002 deployment guide created a problem because:

1. The `.env` file had a very long `CHROME_BINARY_PATH` line (162 characters)
2. The terminal or shell wrapped this line, inserting a newline character
3. This broke the line into two physical lines in the file
4. Python's `dotenv` parser couldn't handle the broken line
5. The app failed to load, showing "Something went wrong"

**Important Note:** The `CHROME_BINARY_PATH` variable is not needed on PythonAnywhere production (it's for local development), so it was removed from the clean `.env` file.

---

## Task Status Update

**TASK-3002:** ✅ Code Complete | ⚠️ Production Deployment Failed | 🔧 Fix In Progress  
**Next Action:** Apply fix above, then mark TASK-3002 as fully deployed
