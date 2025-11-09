# Production Fix Guide - Cache Configuration Issue

## Problem
After deploying TASK-3001/3002 (caching), the production site shows "Something went wrong" page with Quirks Mode rendering.

## Root Cause
The `.env` file on production was appended using `cat >> .env` without proper formatting, potentially causing:
1. Missing newline before cache configuration
2. Malformed .env file
3. Application failing to load configuration properly

## Solution Steps

### On PythonAnywhere Bash Console:

```bash
# 1. Navigate to project directory
cd ~/total_bankroll

# 2. Backup current .env
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

# 3. Check the end of .env file (should see cache config)
tail -15 .env

# 4. Fix: Remove the cache config that was incorrectly appended
# Open .env in editor
nano .env

# 5. Navigate to end of file (CTRL+End or CTRL+V several times)
# 6. Ensure CHROME_BINARY_PATH line ends properly
# 7. Add blank line after CHROME_BINARY_PATH
# 8. Ensure cache config section looks like this:

# Cache Configuration
# Options: SimpleCache (default, in-memory), RedisCache (requires Redis)
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300

# Redis Configuration (optional, for future use)
# REDIS_URL=redis://localhost:6379/0
# Or for Upstash Redis:
# REDIS_URL=rediss://:password@your-redis-url:6379

# 9. Save and exit (CTRL+X, then Y, then Enter)

# 10. Verify .env file is valid
python3 << 'EOF'
from dotenv import load_dotenv
import os

# Try to load .env
result = load_dotenv('.env')
print(f"✓ .env loaded successfully: {result}")

# Check cache config
cache_type = os.getenv('CACHE_TYPE')
cache_timeout = os.getenv('CACHE_DEFAULT_TIMEOUT')

print(f"✓ CACHE_TYPE: {cache_type}")
print(f"✓ CACHE_DEFAULT_TIMEOUT: {cache_timeout}")

if not cache_type or not cache_timeout:
    print("❌ Cache configuration missing!")
    exit(1)
else:
    print("✅ Cache configuration loaded correctly!")
EOF

# 11. Test the application loads
workon bankroll_venv
export FLASK_APP="src/total_bankroll"

python3 << 'EOF'
from src.total_bankroll import create_app
from src.total_bankroll.extensions import cache

app = create_app('production')
with app.app_context():
    print(f"✓ App created successfully")
    print(f"✓ Cache type: {app.config.get('CACHE_TYPE')}")
    
    # Test cache
    cache.set('test', 'working')
    result = cache.get('test')
    
    if result == 'working':
        print("✅ Application and cache working!")
    else:
        print("❌ Cache not working!")
        exit(1)
EOF

# 12. If all tests pass, reload the web app
# Go to: https://www.pythonanywhere.com/user/pythonpydev/webapps/
# Click the green "Reload" button

# 13. Test the website
# Visit: https://stakeeasy.net/
# Should load normally now
```

## Alternative: Clean .env Restoration

If the above doesn't work, restore a clean .env file:

```bash
cd ~/total_bankroll

# Backup current
mv .env .env.broken

# Pull fresh from git (may not have cache config)
git checkout .env

# Add cache config properly
cat >> .env << 'EOF'

# Cache Configuration
# Options: SimpleCache (default, in-memory), RedisCache (requires Redis)
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300

# Redis Configuration (optional, for future use)
# REDIS_URL=redis://localhost:6379/0
# Or for Upstash Redis:
# REDIS_URL=rediss://:password@your-redis-url:6379
EOF

# Verify
tail -10 .env

# Test and reload as above
```

## Verification Checklist

- [ ] .env file loads without errors
- [ ] CACHE_TYPE and CACHE_DEFAULT_TIMEOUT are set
- [ ] Application creates successfully
- [ ] Cache operations work (set/get)
- [ ] Website loads at https://stakeeasy.net/
- [ ] No errors in server log
- [ ] Dashboard displays correctly

## If Still Not Working

1. Check error log:
```bash
tail -100 /var/log/pythonpydev.pythonanywhere.com.error.log
```

2. Check server log:
```bash
tail -100 /var/log/pythonpydev.pythonanywhere.com.server.log
```

3. Check the application is using correct environment:
```bash
grep "FLASK_ENV" .env
# Should show: FLASK_ENV=production
```

4. Verify imports in code:
```bash
grep -n "from src.total_bankroll.extensions import cache" src/total_bankroll/services/*.py
# Should show cache imports in bankroll_service.py
```
