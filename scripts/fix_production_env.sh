#!/bin/bash
# Production .env Fix Script for TASK-3002
# Run this on PythonAnywhere bash console

set -e  # Exit on error

echo "=================================="
echo "TASK-3002 Production .env Fix"
echo "=================================="
echo ""

# Navigate to project
cd ~/total_bankroll

# Backup broken .env
echo "1. Backing up current .env..."
cp .env .env.broken_$(date +%Y%m%d_%H%M%S)
echo "   ✓ Backup created"
echo ""

# Create clean .env
echo "2. Creating clean .env file..."
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

echo "   ✓ Clean .env created"
echo ""

# Verify
echo "3. Verifying .env file (last 5 lines)..."
tail -5 .env
echo ""

# Test app loading
echo "4. Testing app loading..."
workon bankroll_venv
python3 << 'END_PYTHON'
from src.total_bankroll import create_app
from src.total_bankroll.extensions import cache

app = create_app('production')
with app.app_context():
    cache.set('fix_test', 'working')
    result = cache.get('fix_test')
    if result == 'working':
        print("   ✅ App loads successfully!")
        print("   ✅ Cache is working!")
    else:
        print("   ❌ Cache test failed")
        exit(1)
END_PYTHON

echo ""
echo "=================================="
echo "Fix complete!"
echo "=================================="
echo ""
echo "NEXT STEP: Go to PythonAnywhere Web tab and click 'Reload'"
echo ""
