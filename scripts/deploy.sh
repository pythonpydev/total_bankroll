#!/bin/bash
################################################################################
# StakeEasy.net Deployment Script for PythonAnywhere
#
# This script provides semi-automated deployment to production.
# It includes safety checks, backups, and rollback instructions.
#
# Usage:
#   ./scripts/deploy.sh [OPTIONS]
#
# Options:
#   --dry-run       Show what would be deployed without making changes
#   --skip-backup   Skip database backup (NOT RECOMMENDED)
#   -h, --help      Show this help message
#
# Exit Codes:
#   0 - Deployment successful
#   1 - Deployment failed or aborted
#   2 - Pre-deployment checks failed
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DRY_RUN=false
SKIP_BACKUP=false

# Production server configuration
PROD_SERVER="pythonpydev@ssh.pythonanywhere.com"
PROD_PROJECT_DIR="~/total_bankroll"
PROD_VENV="bankroll_venv"
PROD_DB_USER="pythonpydev"
PROD_DB_NAME="pythonpydev\$bankroll"
PROD_BACKUP_DIR="~/backups"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}${BOLD}╔═══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BLUE}${BOLD}║  $1${RESET}"
    echo -e "${BLUE}${BOLD}╚═══════════════════════════════════════════════════════════╝${RESET}\n"
}

print_step() {
    echo -e "${GREEN}▶${RESET} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${RESET} $1"
}

print_error() {
    echo -e "${RED}✗${RESET} $1"
}

print_success() {
    echo -e "${GREEN}✓${RESET} $1"
}

confirm() {
    local prompt="$1"
    local response
    echo -en "${YELLOW}${prompt} (yes/no): ${RESET}"
    read -r response
    case "$response" in
        [Yy][Ee][Ss]|[Yy])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

show_help() {
    echo "StakeEasy.net Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run       Show what would be deployed without making changes"
    echo "  --skip-backup   Skip database backup (NOT RECOMMENDED)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Normal deployment"
    echo "  $0 --dry-run          # Preview deployment"
    echo "  $0 --skip-backup      # Deploy without backup (risky!)"
    exit 0
}

################################################################################
# Parse Command Line Arguments
################################################################################

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            -h|--help)
                show_help
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
}

################################################################################
# Pre-Deployment Checks
################################################################################

check_git_status() {
    print_step "Checking git status..."
    
    cd "$PROJECT_ROOT"
    
    # Check if we're on the main branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ]; then
        print_warning "Not on main branch (current: $current_branch)"
        if ! confirm "Continue anyway?"; then
            print_error "Deployment aborted"
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes:"
        git status --short
        if ! confirm "Continue with uncommitted changes?"; then
            print_error "Deployment aborted. Commit your changes first."
            exit 1
        fi
    fi
    
    # Check if local is behind remote
    git fetch origin "$current_branch" --quiet
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        print_warning "Local branch is not in sync with remote"
        if ! confirm "Continue anyway?"; then
            print_error "Deployment aborted"
            exit 1
        fi
    fi
    
    print_success "Git status check passed"
}

check_environment_parity() {
    print_step "Running environment parity check..."
    
    cd "$PROJECT_ROOT"
    
    if [ -f "scripts/check_env_parity.py" ]; then
        # Load environment variables
        if [ -f ".env" ]; then
            export $(grep -v '^#' .env | xargs)
        fi
        
        if python3 scripts/check_env_parity.py; then
            print_success "Environment parity check passed"
        else
            print_warning "Environment parity check found issues"
            if ! confirm "Continue despite warnings?"; then
                print_error "Deployment aborted"
                exit 2
            fi
        fi
    else
        print_warning "Environment parity check script not found"
    fi
}

show_deployment_summary() {
    print_header "Deployment Summary"
    
    cd "$PROJECT_ROOT"
    
    # Get current commit info
    COMMIT_HASH=$(git rev-parse --short HEAD)
    COMMIT_MSG=$(git log -1 --pretty=%B)
    COMMIT_AUTHOR=$(git log -1 --pretty=%an)
    COMMIT_DATE=$(git log -1 --pretty=%cd --date=short)
    
    echo -e "${BOLD}Commit to Deploy:${RESET}"
    echo -e "  Hash:    ${GREEN}$COMMIT_HASH${RESET}"
    echo -e "  Message: $COMMIT_MSG"
    echo -e "  Author:  $COMMIT_AUTHOR"
    echo -e "  Date:    $COMMIT_DATE"
    echo ""
    
    # Show files changed in last commit
    echo -e "${BOLD}Files Changed:${RESET}"
    git diff --name-status HEAD~1 HEAD | sed 's/^/  /'
    echo ""
    
    # Check for migrations
    if git diff --name-only HEAD~1 HEAD | grep -q "migrations/versions/"; then
        print_warning "This deployment includes database migrations!"
        echo -e "  ${YELLOW}Migration files changed:${RESET}"
        git diff --name-only HEAD~1 HEAD | grep "migrations/versions/" | sed 's/^/    /'
        echo ""
    fi
}

################################################################################
# Deployment Steps
################################################################################

create_backup() {
    if [ "$SKIP_BACKUP" = true ]; then
        print_warning "Skipping database backup (--skip-backup flag used)"
        return 0
    fi
    
    print_step "Creating database backup..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would create backup: ${PROD_BACKUP_DIR}/bankroll_${TIMESTAMP}.sql"
        return 0
    fi
    
    # Create backup command
    BACKUP_CMD="cd ~ && mkdir -p backups && mysqldump -u ${PROD_DB_USER} -p ${PROD_DB_NAME} > ${PROD_BACKUP_DIR}/bankroll_${TIMESTAMP}.sql && ls -lh ${PROD_BACKUP_DIR}/bankroll_${TIMESTAMP}.sql"
    
    echo -e "${BLUE}Connecting to production server to create backup...${RESET}"
    echo -e "${YELLOW}You will be prompted for your PythonAnywhere password and MySQL password${RESET}"
    
    if ssh "$PROD_SERVER" "$BACKUP_CMD"; then
        print_success "Database backup created: bankroll_${TIMESTAMP}.sql"
        echo "$TIMESTAMP" > "$PROJECT_ROOT/.last_backup"
    else
        print_error "Failed to create database backup"
        if ! confirm "Continue without backup?"; then
            print_error "Deployment aborted"
            exit 1
        fi
    fi
}

deploy_code() {
    print_step "Deploying code to production..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would pull latest code on production server"
        return 0
    fi
    
    DEPLOY_CMD="cd ${PROD_PROJECT_DIR} && git status && git pull origin main && git log -1 --oneline"
    
    echo -e "${BLUE}Pulling latest code on production server...${RESET}"
    
    if ssh "$PROD_SERVER" "$DEPLOY_CMD"; then
        print_success "Code deployed successfully"
    else
        print_error "Failed to pull code"
        exit 1
    fi
}

update_dependencies() {
    print_step "Updating dependencies..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would update Python dependencies"
        return 0
    fi
    
    UPDATE_CMD="workon ${PROD_VENV} && cd ${PROD_PROJECT_DIR} && pip install -r requirements.txt && pip list | grep -E 'Flask|SQLAlchemy|Flask-Migrate'"
    
    echo -e "${BLUE}Updating dependencies on production server...${RESET}"
    
    if ssh "$PROD_SERVER" "bash -lc '$UPDATE_CMD'"; then
        print_success "Dependencies updated successfully"
    else
        print_warning "Dependency update encountered issues"
        if ! confirm "Continue anyway?"; then
            print_error "Deployment aborted"
            exit 1
        fi
    fi
}

apply_migrations() {
    print_step "Applying database migrations..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would apply database migrations"
        return 0
    fi
    
    MIGRATION_CMD="workon ${PROD_VENV} && cd ${PROD_PROJECT_DIR} && export FLASK_APP='src/total_bankroll' && flask db current && flask db upgrade && flask db current"
    
    echo -e "${BLUE}Applying migrations on production server...${RESET}"
    
    if ssh "$PROD_SERVER" "bash -lc '$MIGRATION_CMD'"; then
        print_success "Migrations applied successfully"
    else
        print_error "Failed to apply migrations"
        print_warning "You may need to rollback the deployment!"
        exit 1
    fi
}

reload_application() {
    print_step "Reloading web application..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would reload web application"
        return 0
    fi
    
    print_info "Please reload the web app manually:"
    echo -e "  1. Go to: ${BLUE}https://www.pythonanywhere.com/user/pythonpydev/webapps/${RESET}"
    echo -e "  2. Click the ${GREEN}Reload${RESET} button for stakeeasy.net"
    echo ""
    
    if confirm "Have you reloaded the web app?"; then
        print_success "Web application reloaded"
    else
        print_warning "Remember to reload the web app to apply changes!"
    fi
}

verify_deployment() {
    print_step "Verifying deployment..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would verify deployment"
        return 0
    fi
    
    echo -e "${BOLD}Post-Deployment Checklist:${RESET}"
    echo "  1. Site loads: https://stakeeasy.net"
    echo "  2. Login functionality works"
    echo "  3. Database connections working"
    echo "  4. No JavaScript console errors"
    echo ""
    
    if confirm "Has the deployment been verified?"; then
        print_success "Deployment verified"
    else
        print_warning "Please complete verification manually"
    fi
}

show_rollback_instructions() {
    print_header "Rollback Instructions"
    
    LAST_COMMIT=$(git rev-parse --short HEAD~1)
    BACKUP_FILE="bankroll_${TIMESTAMP}.sql"
    
    if [ -f "$PROJECT_ROOT/.last_backup" ]; then
        BACKUP_TIMESTAMP=$(cat "$PROJECT_ROOT/.last_backup")
        BACKUP_FILE="bankroll_${BACKUP_TIMESTAMP}.sql"
    fi
    
    echo -e "${BOLD}If deployment fails, use these commands to rollback:${RESET}"
    echo ""
    echo -e "${YELLOW}1. Rollback Code:${RESET}"
    echo "   ssh $PROD_SERVER"
    echo "   cd $PROD_PROJECT_DIR"
    echo "   git reset --hard $LAST_COMMIT"
    echo ""
    echo -e "${YELLOW}2. Rollback Database (if migrations were applied):${RESET}"
    echo "   mysql -u $PROD_DB_USER -p $PROD_DB_NAME < $PROD_BACKUP_DIR/$BACKUP_FILE"
    echo ""
    echo -e "${YELLOW}3. Reload Web App:${RESET}"
    echo "   Go to PythonAnywhere web interface and click Reload"
    echo ""
}

################################################################################
# Main Deployment Flow
################################################################################

main() {
    parse_args "$@"
    
    print_header "StakeEasy.net Deployment Script"
    
    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # Pre-deployment checks
    check_git_status
    check_environment_parity
    show_deployment_summary
    
    # Confirm deployment
    if [ "$DRY_RUN" = false ]; then
        echo ""
        if ! confirm "Proceed with deployment?"; then
            print_error "Deployment aborted by user"
            exit 1
        fi
    fi
    
    # Execute deployment steps
    create_backup
    deploy_code
    update_dependencies
    apply_migrations
    reload_application
    verify_deployment
    
    # Show rollback info
    show_rollback_instructions
    
    # Success message
    print_header "Deployment Complete"
    
    if [ "$DRY_RUN" = true ]; then
        print_info "Dry run completed successfully"
    else
        print_success "Deployment completed successfully!"
        echo ""
        echo -e "Commit deployed: ${GREEN}$(git rev-parse --short HEAD)${RESET}"
        echo -e "Backup created:  ${GREEN}${BACKUP_FILE}${RESET}"
        echo ""
        print_info "Monitor the application for any issues"
        print_info "Check logs if needed: tail -50 src/total_bankroll/app.log"
    fi
    
    exit 0
}

# Run main function
main "$@"
