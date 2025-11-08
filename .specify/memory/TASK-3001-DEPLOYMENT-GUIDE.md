# TASK-3001: Production Deployment Guide

## Pre-Deployment Checklist

- [ ] All changes tested locally
- [ ] Cache functionality verified
- [ ] No errors in application startup
- [ ] Requirements.txt updated
- [ ] .env configuration documented

## Deployment Steps for PythonAnywhere

### Step 1: Backup Current State
```bash
# SSH into PythonAnywhere
ssh pythonpydev@ssh.pythonanywhere.com

# Navigate to project
cd ~/total_bankroll

# Create backup
mysqldump -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p --no-tablespaces \
  pythonpydev\$bankroll > ~/backups/backup_before_caching_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Pull Latest Code
```bash
cd ~/total_bankroll

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Pull latest changes
git fetch origin
git pull origin main

# Verify you have the changes
git log --oneline -1
# Should show: "feat(cache): Add Flask-Caching with SimpleCache backend"
```

### Step 3: Update Dependencies
```bash
# Activate virtual environment
workon bankroll_venv

# Install new packages
pip install flask-caching redis

# Verify installation
pip list | grep -E "(caching|redis)"
# Expected output:
# cachelib          0.13.0
# Flask-Caching     2.3.1
# redis             7.0.1
```

### Step 4: Update Production .env
```bash
cd ~/total_bankroll

# Add cache configuration
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

# Verify .env updated
tail -10 .env
```

### Step 5: Test Configuration
```bash
# Activate environment
workon bankroll_venv
export FLASK_APP="src/total_bankroll"

# Test import
python << 'EOF'
from src.total_bankroll import create_app
from src.total_bankroll.extensions import cache

app = create_app('production')
with app.app_context():
    print(f"✓ Cache type: {app.config.get('CACHE_TYPE')}")
    print(f"✓ Cache timeout: {app.config.get('CACHE_DEFAULT_TIMEOUT')}")
    
    # Test cache operations
    cache.set('deployment_test', 'success', timeout=5)
    value = cache.get('deployment_test')
    
    if value == 'success':
        print("✅ Cache is working correctly!")
    else:
        print("❌ Cache test failed!")
        exit(1)
EOF

# If you see "❌ Cache test failed!", DO NOT proceed to Step 6
# Debug the issue first
```

### Step 6: Reload Web Application
```bash
# Go to PythonAnywhere Web tab in browser:
# https://www.pythonanywhere.com/user/pythonpydev/webapps/

# Click the green "Reload pythonpydev.pythonanywhere.com" button

# Or use the API (if you have API token):
# curl -X POST https://www.pythonanywhere.com/api/v0/user/pythonpydev/webapps/pythonpydev.pythonanywhere.com/reload/ \
#   -H "Authorization: Token YOUR_API_TOKEN"
```

### Step 7: Verify Deployment
```bash
# 1. Check error log for any issues
tail -50 /var/log/pythonpydev.pythonanywhere.com.error.log

# 2. Test the website
curl -I https://stakeeasy.net/
# Should return HTTP 200

# 3. Verify cache in production console
# Go to: https://www.pythonanywhere.com/user/pythonpydev/consoles/

# In Python console:
from src.total_bankroll import create_app
from src.total_bankroll.extensions import cache

app = create_app('production')
with app.app_context():
    cache.set('prod_test', 'working')
    print(f"Cache test: {cache.get('prod_test')}")
```

## Post-Deployment Verification

### Test Checklist
- [ ] Website loads without errors
- [ ] Homepage accessible
- [ ] Login page accessible  
- [ ] Dashboard accessible (for logged-in user)
- [ ] No errors in error log
- [ ] Cache working in production console

### Performance Baseline
Note: Performance improvements will be visible after TASK-3002 (when caching is actually used)

Current expected behavior:
- ✅ Application starts successfully
- ✅ No performance changes (caching not yet applied to routes)
- ✅ Cache infrastructure ready for TASK-3002

## Rollback Procedure

If something goes wrong:

```bash
cd ~/total_bankroll

# 1. Revert code
git reset --hard HEAD~1

# 2. Uninstall cache libraries (optional)
pip uninstall -y flask-caching redis cachelib

# 3. Remove cache config from .env
# Edit .env and remove the cache section manually

# 4. Reload web app
# (Use PythonAnywhere Web tab "Reload" button)
```

## Troubleshooting

### Error: "No module named 'flask_caching'"
**Solution:**
```bash
workon bankroll_venv
pip install flask-caching redis
```

### Error: "Cache type 'SimpleCache' not found"
**Check:**
1. Verify `CACHE_TYPE=SimpleCache` in .env (not RedisCache)
2. Verify flask-caching and cachelib installed
3. Check import in extensions.py: `from flask_caching import Cache`

### Warning: "Using in-memory storage for tracking rate limits"
**This is expected** - Flask-Limiter uses in-memory storage by default. This is separate from Flask-Caching and is not an error.

### Application won't start
**Debug steps:**
```bash
# Check Python errors
cd ~/total_bankroll
workon bankroll_venv
python -c "from src.total_bankroll import create_app; app = create_app('production')"

# Check error log
tail -100 /var/log/pythonpydev.pythonanywhere.com.error.log
```

## Monitoring After Deployment

### Week 1: Daily Checks
- Check error logs daily for cache-related errors
- Verify website performance remains stable
- No user-reported issues

### Week 2-4: Monitor for
- Memory usage (SimpleCache uses RAM)
- Application restart frequency
- Any cache-related errors

## Future Upgrades

### When to upgrade to Redis

**Indicators:**
1. Traffic exceeds 1,000 daily active users
2. Application restarts frequently (cache data lost)
3. Need for multi-process workers
4. Need for persistent caching
5. Performance degradation from cold cache

### How to upgrade to Redis (Upstash Free Tier)

1. **Sign up for Upstash Redis**
   - Go to https://upstash.com/
   - Create free account
   - Create new Redis database
   - Copy connection URL

2. **Update production .env**
   ```bash
   CACHE_TYPE=RedisCache
   REDIS_URL=rediss://:your-password@your-database.upstash.io:6379
   ```

3. **Reload application**
   - Click "Reload" on PythonAnywhere Web tab
   - Verify in console that cache type is RedisCache

4. **No code changes needed!**
   - The application already supports Redis
   - Automatic fallback to SimpleCache if Redis unavailable

## Expected Timeline

- **Pre-deployment:** 15 minutes (backup, verify changes)
- **Deployment:** 10 minutes (pull code, install deps, reload)
- **Verification:** 10 minutes (test, check logs)
- **Total:** ~35 minutes

## Support Resources

- Flask-Caching: https://flask-caching.readthedocs.io/
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Project Issues: Use project issue tracker
- Emergency rollback: See "Rollback Procedure" above

---

## Deployment Sign-off

**Deployed by:** _______________  
**Date:** _______________  
**Time:** _______________  
**Verification completed:** [ ] Yes [ ] No  
**Any issues?** [ ] None [ ] See notes below  

**Notes:**
```
```

---

**Document version:** 1.0  
**Last updated:** 2025-11-08  
**Task:** TASK-3001
