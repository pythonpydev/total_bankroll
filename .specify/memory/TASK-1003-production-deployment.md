# TASK-1003: Production Deployment Guide

**Task:** Add Database Indexes for Performance  
**Target:** PythonAnywhere Production Server  
**Date:** 2025-11-08  
**Risk Level:** 🟡 Low-Medium (Additive change, no data modification)

---

## Prerequisites

Before deploying, ensure you have:
- [x] Migration tested locally
- [x] SSH access to PythonAnywhere
- [x] Database backup capability verified

---

## Pre-Deployment Checklist

### 1. Estimate Index Build Time

Indexes are built **online** in MySQL, but larger tables take longer:

```sql
-- Check table sizes (run on production)
SELECT 
    table_name,
    table_rows,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'pythonpydev$bankroll'
AND table_name IN ('site_history', 'asset_history', 'deposits', 'drawings');
```

**Expected build time:**
- < 1,000 rows: < 1 second
- 1,000 - 10,000 rows: 1-5 seconds
- 10,000 - 100,000 rows: 5-30 seconds
- > 100,000 rows: 30+ seconds

**Note:** The site remains **online** during index creation.

---

## Deployment Steps

### Step 1: Backup Production Database ⚠️ CRITICAL

```bash
# SSH into PythonAnywhere
ssh pythonpydev@ssh.pythonanywhere.com

# Navigate to project
cd ~/total_bankroll

# Create timestamped backup
mysqldump -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p --no-tablespaces \
  pythonpydev\$bankroll > ~/backups/backup_before_indexes_$(date +%Y%m%d_%H%M%S).sql
```

**Verify backup:**
```bash
ls -lh ~/backups/backup_before_indexes_*.sql
# Should show file with reasonable size (>100KB)
```

### Step 2: Pull Latest Code

```bash
cd ~/total_bankroll

# Fetch and check what will be updated
git fetch origin
git log --oneline HEAD..origin/main

# Should show: f20830e feat(db): Add performance indexes
```

### Step 3: Force Pull (Recommended)

```bash
# Clear any cached Python bytecode
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Force pull to avoid conflicts
git reset --hard origin/main

# Verify you're on the right commit
git log --oneline -1
# Should show: f20830e feat(db): Add performance indexes
```

### Step 4: Activate Virtual Environment

```bash
workon bankroll_venv  # or your virtualenv name

# Verify Flask is accessible
which flask
export FLASK_APP="src/total_bankroll"
```

### Step 5: Apply Migration

```bash
# Check current migration status
flask db current

# Apply the migration (this creates the indexes)
flask db upgrade
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade e9c441c44865 -> 1e063a8cc9f8, Add performance indexes for common queries
```

**If you see errors**, STOP and check the error log. Do not proceed.

### Step 6: Verify Indexes Created

```bash
# Check that all indexes exist
mysql -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p pythonpydev\$bankroll << 'EOF'
SELECT 
    table_name,
    index_name,
    GROUP_CONCAT(column_name ORDER BY seq_in_index) as columns
FROM information_schema.statistics
WHERE table_schema = 'pythonpydev$bankroll'
AND index_name LIKE 'idx_%'
GROUP BY table_name, index_name
ORDER BY table_name, index_name;
EOF
```

**Expected output:**
```
table_name     | index_name                        | columns
---------------|-----------------------------------|------------------
asset_history  | idx_asset_history_user_recorded   | user_id,recorded_at
deposits       | idx_deposits_user_date            | user_id,date
drawings       | idx_drawings_user_date            | user_id,date
site_history   | idx_site_history_user_recorded    | user_id,recorded_at
```

Should show **4 indexes total**.

### Step 7: Test the Application

**No reload needed!** Indexes are available immediately.

Visit https://stakeeasy.net and test:
- ✅ Dashboard loads
- ✅ Charts display correctly
- ✅ Transaction history works
- ✅ No errors in browser console

### Step 8: Monitor Performance

Check query performance:

```bash
# Check slow query log (if enabled)
tail -50 ~/logs/error.log | grep -i "slow"

# Or check application logs for improved load times
tail -50 ~/logs/access.log
```

**Dashboard should load faster**, especially for users with lots of data.

---

## Verification Checklist

After deployment:

- [ ] Migration completed without errors
- [ ] All 4 indexes created (verified with SQL query)
- [ ] Dashboard loads successfully
- [ ] Charts generate correctly
- [ ] No errors in application logs
- [ ] Performance improvement observed (optional)

---

## Rollback Procedure (If Needed)

If something goes wrong:

### Quick Rollback (Remove Indexes Only)

```bash
cd ~/total_bankroll
workon bankroll_venv
export FLASK_APP="src/total_bankroll"

# Downgrade the migration
flask db downgrade

# Verify indexes removed
mysql -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p pythonpydev\$bankroll \
  -e "SELECT COUNT(*) FROM information_schema.statistics 
      WHERE table_schema='pythonpydev\$bankroll' 
      AND index_name LIKE 'idx_%';"
# Should return 0
```

### Full Rollback (Restore Database)

**Only if migration causes data issues (very unlikely):**

```bash
# This will restore the entire database to pre-migration state
mysql -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p --no-tablespaces \
  pythonpydev\$bankroll < ~/backups/backup_before_indexes_YYYYMMDD_HHMMSS.sql
```

---

## Troubleshooting

### Issue: "No such file or directory" for migration

**Cause:** Git didn't pull the migration file  
**Solution:**
```bash
git fetch origin
git reset --hard origin/main
ls migrations/versions/1e063a8cc9f8*.py  # Should exist
```

### Issue: "Target database is not up to date"

**Cause:** There are pending migrations  
**Solution:**
```bash
flask db current  # Check current revision
flask db heads    # Check target revision
flask db upgrade  # Apply all pending
```

### Issue: Index creation takes too long

**Cause:** Large table (> 100,000 rows)  
**Solution:** Wait - it's still building. Check:
```sql
SHOW PROCESSLIST;  -- Look for "ALTER TABLE" queries
```

### Issue: "Duplicate key name" error

**Cause:** Index already exists  
**Solution:** Check if indexes are already there:
```bash
mysql -h pythonpydev.mysql.pythonanywhere-services.com \
  -u pythonpydev -p pythonpydev\$bankroll \
  -e "SHOW INDEXES FROM site_history WHERE Key_name LIKE 'idx_%';"
```

If indexes exist, the migration already ran. Skip it:
```bash
flask db stamp head  # Mark as complete without running
```

---

## Performance Monitoring

### Before Deployment

Record current dashboard load time:
1. Open https://stakeeasy.net/dashboard
2. Open DevTools (F12) → Network tab
3. Reload page, note "Load" time

### After Deployment

Repeat the same test. Expected improvement:
- **Small dataset** (<1000 records): 10-20% faster
- **Medium dataset** (1000-10000): 50-70% faster  
- **Large dataset** (>10000): 80-95% faster

### MySQL Query Analysis (Optional)

```sql
-- Run EXPLAIN on a typical query
EXPLAIN SELECT * FROM site_history 
WHERE user_id = 1 
ORDER BY recorded_at DESC 
LIMIT 50;
```

**Before indexes:**
- `type: ALL` (full table scan)
- `rows: 10000+` (scans all rows)

**After indexes:**
- `type: ref` or `range` (index seek)
- `rows: 100` (only relevant rows)
- `key: idx_site_history_user_recorded` (uses our index!)

---

## Estimated Deployment Time

- Backup: **2-3 minutes**
- Pull code: **30 seconds**
- Apply migration: **5-30 seconds** (depends on table size)
- Verification: **2-3 minutes**

**Total: 10-15 minutes**

---

## Post-Deployment Notes

### Success Criteria

✅ Migration applied successfully  
✅ All 4 indexes created  
✅ Application working normally  
✅ No performance degradation  
✅ Ideally: Performance improvement observed

### Next Steps

1. Monitor application for 24 hours
2. Collect user feedback on performance
3. Check slow query logs (if any)
4. Consider additional indexes if needed

---

## Support Resources

- **Flask-Migrate Docs:** https://flask-migrate.readthedocs.io/
- **MySQL Index Docs:** https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html
- **PythonAnywhere Help:** https://help.pythonanywhere.com/

---

**Last Updated:** 2025-11-08  
**Deployment Status:** Ready for Production  
**Risk Level:** 🟡 Low-Medium (Additive, reversible, no downtime)
