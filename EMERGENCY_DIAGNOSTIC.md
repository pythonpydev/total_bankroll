# Production Emergency Diagnostic - Site Not Loading

**Date:** 2025-11-08 21:55 UTC  
**Issue:** Site returns error page with Quirks Mode rendering

## Quick Diagnosis Steps

Execute these on **PythonAnywhere Bash Console**:

```bash
# 1. Check if Flask app even starts
cd ~/total_bankroll
workon bankroll_venv
export FLASK_APP="src/total_bankroll"

# Try to create the app - this will show any Python errors
python3 << 'EOF'
import sys
import traceback

try:
    from src.total_bankroll import create_app
    print("Attempting to create app...")
    app = create_app('production')
    print("✅ App created successfully!")
    print(f"✅ Flask environment: {app.config.get('ENV')}")
    print(f"✅ Cache type: {app.config.get('CACHE_TYPE')}")
    
    # Test a simple route
    with app.test_client() as client:
        print("Testing / route...")
        response = client.get('/')
        print(f"✅ Status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Homepage responds!")
        else:
            print(f"❌ Homepage returned {response.status_code}")
            print(f"Response: {response.data[:500]}")
            
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
EOF
```

## Common Issues and Fixes

### Issue 1: ImportError or ModuleNotFoundError

**Symptom:**  
```
ImportError: cannot import name 'cache' from 'src.total_bankroll.extensions'
```

**Fix:**
```bash
# Verify cache is in extensions.py
grep -n "cache = Cache()" src/total_bankroll/extensions.py

# If not found, add it:
nano src/total_bankroll/extensions.py
# Add: cache = Cache()
```

### Issue 2: Configuration Error

**Symptom:**
```
KeyError: 'CACHE_TYPE'
```

**Fix:**
```bash
# Check .env has cache config
grep "CACHE_TYPE" .env

# If missing, add it:
echo "" >> .env
echo "# Cache Configuration" >> .env
echo "CACHE_TYPE=SimpleCache" >> .env
echo "CACHE_DEFAULT_TIMEOUT=300" >> .env

# Verify
tail -5 .env
```

### Issue 3: Templates Not Found

**Symptom:**
```
jinja2.exceptions.TemplateNotFound: core/index.html
```

**Fix:**
```bash
# Verify templates exist
ls -la src/total_bankroll/templates/core/index.html

# If missing, restore from git
git checkout src/total_bankroll/templates/
```

### Issue 4: Static Assets Missing

**Symptom:**
```
KeyError: "Asset 'main.js' not found in Vite manifest.json."
```

**Fix:**
```bash
# Rebuild Vite assets
node --version  # Verify Node.js is available
npm install
vite build

# Verify manifest exists
ls -la src/total_bankroll/static/assets/manifest.json

# Check manifest contents
cat src/total_bankroll/static/assets/manifest.json
```

### Issue 5: Database Connection Error

**Symptom:**
```
OperationalError: (2003, "Can't connect to MySQL server")
```

**Fix:**
```bash
# Test database connection
mysql -h pythonpydev.mysql.pythonanywhere-services.com \
      -u pythonpydev -p pythonpydev\$bankroll -e "SELECT 1;"

# If fails, check .env has correct credentials
grep "DB.*PROD" .env
```

## Emergency Rollback

If you cannot fix the issue quickly:

```bash
cd ~/total_bankroll

# Find last working commit
git log --oneline -10

# Rollback to before caching (c02e878 or earlier)
git reset --hard <LAST_WORKING_COMMIT>

# Force reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Rebuild assets
npm run build

# Reload web app
# Go to: https://www.pythonanywhere.com/user/pythonpydev/webapps/
# Click "Reload"
```

## Check Error Logs

```bash
# Last 100 lines of error log
tail -100 /var/log/pythonpydev.pythonanywhere.com.error.log

# Search for specific errors
grep -i "error\|exception\|traceback" /var/log/pythonpydev.pythonanywhere.com.error.log | tail -50

# Check server log too
tail -50 /var/log/pythonpydev.pythonanywhere.com.server.log
```

## Nuclear Option: Fresh .env

If .env is truly corrupted:

```bash
cd ~/total_bankroll

# Backup broken one
mv .env .env.corrupted_$(date +%Y%m%d_%H%M%S)

# Create fresh from template (you'll need to fill in secrets)
cat > .env << 'EOF'
FLASK_APP=total_bankroll
FLASK_ENV=production

SECRET_KEY='daaf7210a6215a899b40ed45c644fa2be222ba7b85a5ed59'
EXCHANGE_RATE_API_KEY="447d94e4f5ddcbc0c179a1fd"

# Production Database Credentials
DB_HOST_PROD="pythonpydev.mysql.pythonanywhere-services.com"
DB_NAME_PROD="pythonpydev$bankroll"
DB_USER_PROD="pythonpydev"
DB_PASS_PROD="YOUR_PASSWORD_HERE"

SECURITY_PASSWORD_SALT=cd850d8ac439bd663b75471bf9f1d865

OAUTHLIB_INSECURE_TRANSPORT=1
OAUTHLIB_RELAX_TOKEN_SCOPE=1

GOOGLE_CLIENT_ID="930176693065-3ed24l13tfp29qa17a2au8hn06lqsaep.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"

TWITTER_CLIENT_ID="WXZDNVJnbHNIeHBCVDVyWFZRVVY6MTpjaQ"
TWITTER_CLIENT_SECRET="22Odo5pKJo_DWX99dtQ2uZyg6_JmaXH99nAdo-bB0CIGmAu88S"

FACEBOOK_CLIENT_ID="760019966781286"
FACEBOOK_CLIENT_SECRET="5eff3e58dcd4fa011aa4cf1dae066d7f"

MAIL_SERVER="smtppro.zoho.eu"
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME="admin@stakeeasy.net"
MAIL_PASSWORD="YOUR_MAIL_PASSWORD_HERE"

# Cache Configuration
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300
EOF

# Edit to add your passwords
nano .env

# Test it loads
python3 -c "from dotenv import load_dotenv; load_dotenv('.env'); print('OK')"
```

## Contact for Help

If none of these work, gather this information:

```bash
# Create diagnostic report
cd ~/total_bankroll

cat > /tmp/diagnostic_report.txt << 'EOF'
=== GIT STATUS ===
$(git log --oneline -1)
$(git status)

=== PYTHON VERSION ===
$(python3 --version)

=== VIRTUAL ENV PACKAGES ===
$(pip list | grep -i flask)
$(pip list | grep -i cache)

=== ERROR LOG TAIL ===
$(tail -50 /var/log/pythonpydev.pythonanywhere.com.error.log)

=== ENV CHECK ===
$(python3 -c "from dotenv import load_dotenv; import os; load_dotenv('.env'); print('FLASK_ENV:', os.getenv('FLASK_ENV')); print('CACHE_TYPE:', os.getenv('CACHE_TYPE'))")

=== APP TEST ===
$(python3 -c "from src.total_bankroll import create_app; app = create_app('production'); print('App created OK')" 2>&1)
EOF

cat /tmp/diagnostic_report.txt
```

Then share this report for further diagnosis.
