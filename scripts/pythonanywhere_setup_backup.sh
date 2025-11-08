#!/bin/bash
################################################################################
# PythonAnywhere Backup Directory Setup - Automated Script
# TASK-0004
#
# Usage on PythonAnywhere:
#   bash pythonanywhere_setup_backup.sh
################################################################################

set -e  # Exit on error

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BLUE}${BOLD}Setting up backup directory on PythonAnywhere...${RESET}\n"

# Step 1: Create backup directory
echo -e "${YELLOW}[1/5] Creating ~/backups directory...${RESET}"
mkdir -p ~/backups
echo -e "${GREEN}✓ Directory created${RESET}\n"

# Step 2: Verify directory
echo -e "${YELLOW}[2/5] Verifying directory permissions...${RESET}"
ls -ld ~/backups
echo -e "${GREEN}✓ Directory verified${RESET}\n"

# Step 3: Test backup creation
echo -e "${YELLOW}[3/5] Testing backup creation...${RESET}"
echo -e "${BLUE}Please enter your MySQL password when prompted:${RESET}"
if mysqldump --no-tablespaces -h pythonpydev.mysql.pythonanywhere-services.com -u pythonpydev -p pythonpydev\$bankroll > ~/backups/test_backup.sql 2>/dev/null; then
    echo -e "${GREEN}✓ Test backup created successfully${RESET}\n"
else
    echo -e "${RED}✗ Failed to create test backup${RESET}"
    echo -e "${YELLOW}Please check your MySQL password and try again${RESET}"
    exit 1
fi

# Step 4: Verify backup file
echo -e "${YELLOW}[4/5] Verifying backup file...${RESET}"
FILESIZE=$(stat -f%z ~/backups/test_backup.sql 2>/dev/null || stat -c%s ~/backups/test_backup.sql 2>/dev/null)
echo -e "Backup file size: ${BLUE}${FILESIZE} bytes${RESET}"
if [ "$FILESIZE" -gt 0 ]; then
    echo -e "${GREEN}✓ Backup file is valid${RESET}\n"
else
    echo -e "${RED}✗ Backup file is empty${RESET}"
    exit 1
fi

# Step 5: Cleanup test backup
echo -e "${YELLOW}[5/5] Cleaning up test backup...${RESET}"
rm ~/backups/test_backup.sql
echo -e "${GREEN}✓ Test backup removed${RESET}\n"

# Final verification
echo -e "${YELLOW}Final verification:${RESET}"
ls -la ~/backups/
echo ""

echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║  ✓ Backup directory setup completed!      ║${RESET}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════╝${RESET}\n"

echo -e "${BLUE}The ~/backups directory is now ready for use.${RESET}"
echo -e "${BLUE}You can now run your backup scripts without issues.${RESET}\n"
