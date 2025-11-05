#!/bin/bash
################################################################################
# Setup Backup Directory on PythonAnywhere
# TASK-0004
#
# This script provides step-by-step instructions for setting up the backup
# directory on PythonAnywhere production server.
#
# Usage:
#   ./scripts/setup_backup_dir.sh
################################################################################

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BLUE}${BOLD}╔═══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}${BOLD}║  TASK-0004: Setup Backup Directory on PythonAnywhere     ║${RESET}"
echo -e "${BLUE}${BOLD}╚═══════════════════════════════════════════════════════════╝${RESET}\n"

echo -e "${BOLD}This script will guide you through setting up the backup directory${RESET}"
echo -e "${BOLD}on your PythonAnywhere production server.${RESET}\n"

echo -e "${YELLOW}Step 1: SSH into PythonAnywhere${RESET}"
echo -e "Run this command in a separate terminal:"
echo -e "${GREEN}ssh pythonpydev@ssh.pythonanywhere.com${RESET}\n"

echo -e "${YELLOW}Step 2: Create backup directory${RESET}"
echo -e "Once logged in, run:"
echo -e "${GREEN}mkdir -p ~/backups${RESET}\n"

echo -e "${YELLOW}Step 3: Verify directory was created${RESET}"
echo -e "Run:"
echo -e "${GREEN}ls -ld ~/backups${RESET}"
echo -e "You should see output like: ${BLUE}drwxr-xr-x 2 pythonpydev pythonpydev 4096 ...${RESET}\n"

echo -e "${YELLOW}Step 4: Test backup creation${RESET}"
echo -e "Create a test backup to verify everything works:"
echo -e "${GREEN}mysqldump -u pythonpydev -p pythonpydev\\\$bankroll > ~/backups/test_backup.sql${RESET}"
echo -e "${BLUE}Note: You'll be prompted for your MySQL password${RESET}\n"

echo -e "${YELLOW}Step 5: Verify backup file was created${RESET}"
echo -e "Check the backup file size:"
echo -e "${GREEN}ls -lh ~/backups/test_backup.sql${RESET}"
echo -e "It should be a reasonable size (> 0 bytes)\n"

echo -e "${YELLOW}Step 6: Delete test backup${RESET}"
echo -e "Clean up the test file:"
echo -e "${GREEN}rm ~/backups/test_backup.sql${RESET}\n"

echo -e "${YELLOW}Step 7: Verify deletion${RESET}"
echo -e "Confirm the test backup is gone:"
echo -e "${GREEN}ls ~/backups/${RESET}"
echo -e "The directory should be empty\n"

echo -e "${BLUE}${BOLD}Alternative: Run all commands at once${RESET}"
echo -e "If you prefer, you can run this single command after SSH'ing in:\n"
echo -e "${GREEN}mkdir -p ~/backups && ls -ld ~/backups && mysqldump -u pythonpydev -p pythonpydev\\\$bankroll > ~/backups/test_backup.sql && ls -lh ~/backups/test_backup.sql && rm ~/backups/test_backup.sql && echo 'Backup directory setup complete!'${RESET}\n"

echo -e "${BLUE}${BOLD}Task Completion Checklist:${RESET}"
echo -e "  [ ] SSH'd into PythonAnywhere"
echo -e "  [ ] Created ~/backups directory"
echo -e "  [ ] Verified write permissions"
echo -e "  [ ] Created test backup successfully"
echo -e "  [ ] Verified backup file size > 0 bytes"
echo -e "  [ ] Deleted test backup"
echo -e "  [ ] Confirmed directory is ready\n"

echo -e "${YELLOW}Once completed, mark this task as done in your tracking system.${RESET}\n"
