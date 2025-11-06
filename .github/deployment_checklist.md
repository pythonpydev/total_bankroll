# StakeEasy.net Deployment Checklist

**Version:** 1.0  
**Last Updated:** 2025-11-05  
**Environment:** PythonAnywhere Production Server

---

## Pre-Deployment Checklist

### Code Preparation
- [ ] All changes committed to git with descriptive commit messages
- [ ] Code reviewed (self-review or peer review if available)
- [ ] All tests passing locally: `pytest`
- [ ] Linting passed: `flake8`
- [ ] No sensitive data (API keys, passwords) in code
- [ ] `.env` file changes documented (if any)

### Database Preparation
- [ ] Check for pending migrations: `flask db current`
- [ ] Review migration scripts in `migrations/versions/`
- [ ] Migrations tested on local development environment
- [ ] Database backup plan confirmed (see Deployment section)
- [ ] Understand rollback procedure for migrations

### Environment Verification
- [ ] Run environment parity check: `python scripts/check_env_parity.py`
- [ ] Verify Python version matches production (check `.python-version`)
- [ ] Review `requirements.txt` for new dependencies
- [ ] Check for breaking changes in dependency updates

### Static Assets
- [ ] Frontend assets built: `npm run build` (if using Vite)
- [ ] Static files tested locally
- [ ] No broken links or missing images

### Communication
- [ ] Team notified of deployment window (if team exists)
- [ ] Users notified if downtime expected (for major changes)
- [ ] Rollback contact information ready

---

## Deployment Checklist

### 1. Create Backup
**Critical: Always backup before deployment**

```bash
# SSH into PythonAnywhere
ssh pythonpydev@ssh.pythonanywhere.com

# Activate virtual environment
workon bankroll_venv

# Create timestamped backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mysqldump -h pythonpydev.mysql.pythonanywhere-services.com -u pythonpydev -p --no-tablespaces pythonpydev\$bankroll > ~/backups/bankroll_${TIMESTAMP}.sql

# Verify backup created
ls -lh ~/backups/bankroll_${TIMESTAMP}.sql
```

- [ ] Database backup created successfully
- [ ] Backup file size is reasonable (not 0 bytes)
- [ ] Backup timestamp recorded: `______________`

### 2. Pull Latest Code

```bash
# Navigate to project directory
cd ~/total_bankroll

# Check current status
git status

# Pull latest changes
git pull origin main

# Verify correct branch and commit
git log -1 --oneline
```

- [ ] Git pull completed without conflicts
- [ ] Correct commit hash confirmed: `______________`

### 3. Update Dependencies

```bash
# Activate virtual environment (if not already)
workon bankroll_venv

# Update Python dependencies
pip install -r requirements.txt

# Verify critical packages installed
pip list | grep -E "Flask|SQLAlchemy|Flask-Migrate"
```

- [ ] Dependencies installed successfully
- [ ] No error messages during installation

### 4. Apply Database Migrations

```bash
# Set Flask app environment variable
export FLASK_APP="src/total_bankroll"

# Check migration status
flask db current

# Apply migrations
flask db upgrade

# Verify migration succeeded
flask db current
```

- [ ] Current migration alembic revision: `______________`
- [ ] Migrations applied successfully
- [ ] No error messages

### 5. Build Frontend Assets

```bash
# Build Vite assets (required for production)
npm run build

# Verify manifest created
ls -la src/total_bankroll/static/dist/.vite/manifest.json
```

- [ ] Vite build completed successfully
- [ ] manifest.json exists

### 6. Reload Web Application

```bash
# Option 1: Via PythonAnywhere Web Interface
# Go to: https://www.pythonanywhere.com/user/pythonpydev/webapps/
# Click the "Reload" button for stakeeasy.net

# Option 2: Via API (if configured)
# curl -X POST https://www.pythonanywhere.com/api/v0/user/pythonpydev/webapps/stakeeasy.net/reload/
```

- [ ] Web application reloaded
- [ ] Reload timestamp: `______________`

### 7. Clear Application Cache (if applicable)

```bash
# If using Flask-Caching or similar
# Clear cache through admin interface or CLI command
```

- [ ] Cache cleared (if applicable)

---

## Post-Deployment Checklist

### Immediate Verification (within 5 minutes)
- [ ] Site loads: https://stakeeasy.net
- [ ] Homepage renders correctly
- [ ] Login functionality works
- [ ] Database connections working (check user dashboard)
- [ ] No JavaScript console errors (check browser DevTools)

### Functional Testing (within 15 minutes)
- [ ] User authentication works (login/logout)
- [ ] Can add a new deposit transaction
- [ ] Can add a new withdrawal transaction
- [ ] Charts load on dashboard
- [ ] Currency conversion working
- [ ] Article pages load (if applicable)

### Database Verification
- [ ] Check for database errors in logs
- [ ] Verify data integrity (spot check a few records)
- [ ] Confirm no unexpected data loss

### Performance Check
- [ ] Page load times reasonable (< 3 seconds)
- [ ] No obvious performance degradation
- [ ] Server response times acceptable

### Error Monitoring
- [ ] Check PythonAnywhere error logs: `/var/log/`
- [ ] Review application logs: `src/total_bankroll/app.log`
- [ ] Check for new error patterns
- [ ] No 500 errors on critical pages

### Documentation
- [ ] Deployment notes recorded below
- [ ] Any issues encountered documented
- [ ] Rollback decision made: ✅ Keep deployment / ❌ Rollback

---

## Deployment Notes

**Deployment Date:** `______________`  
**Deployed By:** `______________`  
**Git Commit:** `______________`  
**Database Backup:** `______________`

### Changes Deployed
```
List the key changes deployed in this release:
- 
- 
- 
```

### Issues Encountered
```
Document any issues encountered during deployment:
- 
- 
- 
```

### Resolution Actions
```
Document how issues were resolved:
- 
- 
- 
```

---

## Rollback Procedure

**Use if deployment fails or causes critical issues**

### Quick Rollback (Code Only)

```bash
# SSH into PythonAnywhere
cd ~/total_bankroll

# Find previous commit hash
git log -5 --oneline

# Revert to previous commit
git reset --hard <PREVIOUS_COMMIT_HASH>

# Reload web app
# Use PythonAnywhere web interface to click "Reload"
```

### Full Rollback (Code + Database)

```bash
# 1. Revert code (as above)
git reset --hard <PREVIOUS_COMMIT_HASH>

# 2. Restore database from backup
mysql -u pythonpydev -p pythonpydev\$bankroll < ~/backups/bankroll_<TIMESTAMP>.sql

# 3. Verify database restored
mysql -u pythonpydev -p pythonpydev\$bankroll -e "SHOW TABLES;"

# 4. Downgrade migrations to previous version (if needed)
export FLASK_APP="src/total_bankroll"
flask db downgrade <PREVIOUS_REVISION>

# 5. Reload web app
```

- [ ] Rollback completed
- [ ] Site functionality verified after rollback
- [ ] Root cause analysis scheduled

---

## Emergency Contacts

**PythonAnywhere Support:** help@pythonanywhere.com  
**Documentation:** https://help.pythonanywhere.com

---

## Deployment History

Keep a log of recent deployments for reference:

| Date       | Commit Hash | Deployed By | Status  | Notes |
|------------|-------------|-------------|---------|-------|
| 2025-11-05 | example123  | Developer   | Success | Initial checklist creation |
|            |             |             |         |       |
|            |             |             |         |       |

---

## Appendix: Useful Commands

### Check Disk Space
```bash
df -h
```

### Check MySQL Status
```bash
mysql -u pythonpydev -p -e "SHOW STATUS;"
```

### View Recent Logs
```bash
tail -50 src/total_bankroll/app.log
```

### Check Virtual Environment
```bash
workon bankroll_venv
pip list
```

### Test Database Connection
```bash
export FLASK_APP="src/total_bankroll"
flask shell
>>> from src.total_bankroll.extensions import db
>>> db.engine.connect()
```

---

**Document Status:** Active  
**Review Cycle:** After each deployment, update as needed  
**Maintained By:** Development Team

*End of Deployment Checklist*
