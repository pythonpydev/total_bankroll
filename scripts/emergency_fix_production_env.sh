#!/bin/bash
###############################################################################
# EMERGENCY Production .env Fix Script
# Task: TASK-3002 - Fix corrupted .env file on PythonAnywhere
# Issue: Multi-line CHROME_BINARY_PATH and duplicate CACHE_TYPE entries
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "EMERGENCY: Production .env Fix"
echo "=========================================="

# Navigate to project directory
cd ~/total_bankroll || { echo "❌ Cannot find ~/total_bankroll"; exit 1; }

echo "1. Backing up current (broken) .env..."
cp .env .env.broken_backup_$(date +%Y%m%d_%H%M%S)
echo "   ✓ Backup created"

echo "2. Creating clean .env file..."

cat > .env << 'ENVEOF'
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
ENVEOF

echo "   ✓ Clean .env created"

echo "3. Verifying .env file (last 5 lines)..."
tail -5 .env

echo ""
echo "=========================================="
echo "Fix complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click the big green 'Reload' button"
echo "3. Visit stakeeasy.net to test"
echo "4. Check error log if still broken:"
echo "   tail -50 /var/log/pythonpydev.pythonanywhere.com.error.log"
echo ""
