#!/bin/bash
#
# TASK-3002 Production .env Emergency Fix
# Fixes corrupted CHROME_BINARY_PATH line
# Run on PythonAnywhere: bash scripts/fix_production_env_simple.sh

set -e

echo "=========================================="
echo "TASK-3002 Production .env Emergency Fix"
echo "=========================================="

# Step 1: Backup current .env
echo "1. Backing up current .env..."
cp ~/.env ~/.env.corrupted_backup_$(date +%Y%m%d_%H%M%S)
echo "   ✓ Backup created"

# Step 2: Remove the corrupted CHROME_BINARY_PATH line(s)
echo "2. Removing corrupted CHROME_BINARY_PATH..."
cd ~/total_bankroll
sed -i '/^CHROME_BINARY_PATH/d' .env
sed -i '/^hrome$/d' .env  # Remove the orphaned "hrome" line
echo "   ✓ Corrupted lines removed"

# Step 3: Remove duplicate CACHE_TYPE if exists
echo "3. Removing duplicate entries..."
awk '!seen[$0]++ || /^[A-Z_]+=/' .env > .env.tmp && mv .env.tmp .env
echo "   ✓ Duplicates removed"

# Step 4: Verify last 10 lines
echo "4. Verifying .env file (last 10 lines):"
tail -10 .env

echo ""
echo "=========================================="
echo "Fix complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reload your web app on PythonAnywhere dashboard"
echo "2. Visit stakeeasy.net to test"
echo "3. If still broken, check error log:"
echo "   tail -50 /var/log/pythonpydev.pythonanywhere.com.error.log"
echo ""
