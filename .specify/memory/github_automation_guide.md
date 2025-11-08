# GitHub Issues Automation Guide for StakeEasy.net

**Version:** 1.0.0  
**Last Updated:** 2025-11-05  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Part 1: Creating Issues from tasks.md](#part-1-creating-issues-from-tasksmd)
4. [Part 2: Closing Issues Automatically](#part-2-closing-issues-automatically)
5. [Complete Workflow Examples](#complete-workflow-examples)
6. [Maintenance & Best Practices](#maintenance--best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Overview

This guide documents the complete automation system for managing GitHub issues in the StakeEasy.net project. The system provides:

✅ **Automated Issue Creation** - Bulk create 50+ issues from tasks.md  
✅ **Automated Issue Closing** - Auto-close issues via commit messages  
✅ **Manual Control** - Scripts for manual issue management  
✅ **CI/CD Integration** - GitHub Actions workflow  
✅ **Progress Tracking** - Complete visibility into implementation status

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    tasks.md (Source)                         │
│                   50 Implementation Tasks                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   create_github_issues.py             │
        │   - Parses tasks.md                   │
        │   - Creates labels                    │
        │   - Creates issues with metadata      │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   GitHub Repository                   │
        │   - 50 Issues Created                 │
        │   - Labeled by Priority & Phase       │
        │   - Ready for Assignment              │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   Development Work                    │
        │   - Code changes                      │
        │   - Git commits with TASK-IDs         │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   Automated Closing (3 Methods)      │
        │   1. GitHub Native (commit keywords)  │
        │   2. GitHub Actions (workflow)        │
        │   3. Manual Scripts (on-demand)       │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   Issue Closed                        │
        │   - Completion comment added          │
        │   - Linked to commit                  │
        │   - Progress tracked                  │
        └───────────────────────────────────────┘
```

---

## Prerequisites

### Required Software

```bash
# Python 3.9+
python --version  # Should be 3.9 or higher

# pip (Python package manager)
pip --version

# git
git --version

# GitHub CLI (optional but recommended)
gh --version
```

### Required Python Packages

```bash
pip install PyGithub
```

### GitHub Personal Access Token

1. **Navigate to GitHub Settings:**
   - Go to: https://github.com/settings/tokens
   - Click: **"Generate new token (classic)"**

2. **Configure Token:**
   - **Name:** `StakeEasy Task Automation`
   - **Expiration:** 90 days (or No expiration for permanent use)
   - **Scopes:** Check the following:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)

3. **Generate and Save:**
   - Click **"Generate token"**
   - **⚠️ CRITICAL:** Copy the token immediately - you won't see it again!
   - Store securely (use password manager like 1Password, Bitwarden)

4. **Set Environment Variable:**
   ```bash
   # Temporary (current session only)
   export GITHUB_TOKEN="ghp_your_token_here"
   
   # Permanent (add to ~/.bashrc or ~/.zshrc)
   echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
   source ~/.bashrc
   
   # Verify
   echo $GITHUB_TOKEN
   ```

### Repository Access

Ensure you have:
- ✅ Write access to `pythonpydev/total_bankroll`
- ✅ Ability to create issues
- ✅ Ability to close issues
- ✅ Ability to manage labels

---

## Part 1: Creating Issues from tasks.md

### Overview

The `create_github_issues.py` script automates the creation of GitHub issues from the task list. It:
- Parses `.specify/memory/tasks.md`
- Creates 19 standardized labels
- Creates 50+ issues with proper titles, descriptions, and labels

### Step-by-Step Procedure

#### Step 1: Verify Prerequisites

```bash
# Navigate to project directory
cd /home/ed/MEGA/total_bankroll

# Verify tasks.md exists
ls -la .specify/memory/tasks.md

# Verify script exists
ls -la scripts/create_github_issues.py

# Verify Python package installed
python -c "import github; print('PyGithub installed')"

# Verify GitHub token set
echo $GITHUB_TOKEN | head -c 10  # Should show first 10 chars
```

#### Step 2: Dry Run (Test Without Creating)

**Always do a dry run first to verify what will be created:**

```bash
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN \
  --dry-run
```

**Expected Output:**
```
Connecting to GitHub...
✓ Connected to repository: pythonpydev/total_bankroll

Creating/verifying labels...
[DRY RUN] Would create label: priority-p0-critical
[DRY RUN] Would create label: priority-p1-high
...

Parsing tasks from: .specify/memory/tasks.md
✓ Found 50 tasks

Creating issues...
[DRY RUN] Would create issue:
  Title: TASK-0001: Create Deployment Checklist
  Labels: priority-p0-critical, phase-0-deployment
  Body length: 456 characters
...

[DRY RUN] Would have created 50 issues
```

#### Step 3: Create Labels Only (First Run)

**Create labels before issues to ensure clean setup:**

```bash
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN \
  --limit 0
```

**This creates labels without creating any issues.**

**Expected Output:**
```
Connecting to GitHub...
✓ Connected to repository: pythonpydev/total_bankroll

Creating/verifying labels...
✓ Created label: priority-p0-critical
✓ Created label: priority-p1-high
✓ Created label: priority-p2-medium
✓ Created label: priority-p3-low
✓ Created label: phase-0-deployment
✓ Created label: phase-1-foundation
✓ Created label: phase-2-services
✓ Created label: phase-3-performance
✓ Created label: phase-4-frontend
✓ Created label: phase-5-database
✓ Created label: phase-6-api
✓ Created label: phase-7-monitoring
✓ Created label: maintenance
✓ Created label: type-bug
✓ Created label: type-feature
✓ Created label: type-refactor
✓ Created label: type-test
✓ Created label: type-docs
```

**Verify on GitHub:**
- Go to: https://github.com/pythonpydev/total_bankroll/labels
- Confirm all 19 labels created with correct colors

#### Step 4: Test with Limited Issues

**Create just 3 issues as a test:**

```bash
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN \
  --limit 3
```

**Expected Output:**
```
Connecting to GitHub...
✓ Connected to repository: pythonpydev/total_bankroll

Creating/verifying labels...
  Label already exists: priority-p0-critical
  Label already exists: priority-p1-high
...

Parsing tasks from: .specify/memory/tasks.md
✓ Found 50 tasks

Creating issues...
✓ Created issue #1: TASK-0001: Create Deployment Checklist
✓ Created issue #2: TASK-0002: Create Environment Parity Check Script
✓ Created issue #3: TASK-0003: Create Deployment Automation Script

[Limit reached: 3 issues]

✓ Successfully created 3 issues
```

**Verify on GitHub:**
- Go to: https://github.com/pythonpydev/total_bankroll/issues
- Confirm 3 issues created with:
  - ✅ Correct titles (format: `TASK-XXXX: Description`)
  - ✅ Full task details in description
  - ✅ Proper labels (priority + phase)
  - ✅ Acceptance criteria as checkboxes

**If issues look correct, proceed to next step. If not, close test issues:**
```bash
gh issue close 1 2 3
```

#### Step 5: Create All Remaining Issues

**Create all 50+ issues:**

```bash
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN
```

**Expected Output:**
```
Connecting to GitHub...
✓ Connected to repository: pythonpydev/total_bankroll

Creating/verifying labels...
  Label already exists: priority-p0-critical
...

Parsing tasks from: .specify/memory/tasks.md
✓ Found 50 tasks

Creating issues...
✓ Created issue #4: TASK-0004: Setup Backup Directory on PythonAnywhere
✓ Created issue #5: TASK-0005: Document Python Version on PythonAnywhere
✓ Created issue #6: TASK-0006: Setup Basic Monitoring
...
✓ Created issue #53: TASK-7006: Deploy Phase 7 Changes

✓ Successfully created 50 issues
```

**This will take 30-60 seconds depending on GitHub API response time.**

#### Step 6: Verify All Issues Created

**Check issue count:**
```bash
# Using GitHub CLI
gh issue list | wc -l

# Or check on GitHub
# https://github.com/pythonpydev/total_bankroll/issues
```

**Should show 50 open issues (or 53 if you kept the test issues).**

**Verify issue distribution:**
```bash
# Count by priority
gh issue list --label priority-p0-critical | wc -l  # Should be 10
gh issue list --label priority-p1-high | wc -l      # Should be 24
gh issue list --label priority-p2-medium | wc -l    # Should be 15

# Count by phase
gh issue list --label phase-0-deployment | wc -l    # Should be 7
gh issue list --label phase-1-foundation | wc -l    # Should be 6
gh issue list --label phase-2-services | wc -l      # Should be 6
```

#### Step 7: Organize with Projects (Optional)

**Create a project board for visual tracking:**

1. **Via GitHub Web:**
   - Go to: https://github.com/pythonpydev/total_bankroll/projects
   - Click **"New project"**
   - Name: `StakeEasy Implementation Roadmap`
   - Template: **Board** or **Table**
   - Click **"Create"**

2. **Via GitHub CLI:**
   ```bash
   gh project create --title "StakeEasy Roadmap" \
     --body "Implementation roadmap tracking all 50 tasks"
   ```

3. **Add Issues to Project:**
   - Go to project board
   - Click **"Add items"**
   - Select all issues or filter by label
   - Add to appropriate column (Todo, In Progress, Done)

#### Step 8: Create Milestones (Optional)

**Organize issues by phase with milestones:**

```bash
# Week 0
gh milestone create "Week 0: Deployment Safety" \
  --due-date 2025-11-12 \
  --description "Establish safe deployment process"

# Phase 1
gh milestone create "Phase 1: Foundation" \
  --due-date 2025-11-26 \
  --description "Fix immediate issues and stabilize"

# Phase 2
gh milestone create "Phase 2: Service Layer" \
  --due-date 2025-12-24 \
  --description "Separate business logic from presentation"

# Continue for all phases...
```

**Assign issues to milestones:**
```bash
# Via GitHub CLI (example for Week 0)
gh issue edit 1 --milestone "Week 0: Deployment Safety"
gh issue edit 2 --milestone "Week 0: Deployment Safety"
# ... etc

# Or via web interface:
# 1. Go to issue
# 2. Click "Milestone" on right sidebar
# 3. Select appropriate milestone
```

### Summary - Part 1 Checklist

- [x] Prerequisites verified
- [x] Dry run completed successfully
- [x] Labels created (19 total)
- [x] Test issues created (3) and verified
- [x] All issues created (50 total)
- [x] Issues verified on GitHub
- [x] Project board created (optional)
- [x] Milestones created (optional)

**Result:** All tasks from tasks.md now exist as GitHub issues with proper organization.

---

## Part 2: Closing Issues Automatically

### Overview

Three methods available for closing issues when tasks are completed:

| Method | Trigger | Automatic | Best For |
|--------|---------|-----------|----------|
| **1. Git Keywords** | Commit message | ✅ Yes | Daily workflow |
| **2. GitHub Actions** | Push to main | ✅ Yes | Team automation |
| **3. Manual Script** | On-demand | ❌ No | Corrections, bulk ops |

### Method 1: Git Commit Keywords (Recommended)

#### How It Works

GitHub has built-in support for closing issues via commit messages. When you push a commit containing specific keywords followed by an issue reference, GitHub automatically closes the issue.

#### Supported Keywords

- `Closes #123` or `Closes TASK-0001`
- `Fixes #123` or `Fixes TASK-0001`
- `Resolves #123` or `Resolves TASK-0001`

**Note:** The keyword must be in the commit message body (not just the title), and the commit must be pushed to the default branch (`main`).

#### Step-by-Step Procedure

**Step 1: Start Working on a Task**

```bash
# Create feature branch with task ID
git checkout -b feature/TASK-0001-deployment-checklist

# Or use main branch directly
git checkout main
```

**Step 2: Complete the Task**

```bash
# Make your code changes
# ... edit files ...

# Example: Create deployment checklist
mkdir -p .github
cat > .github/deployment_checklist.md << 'EOF'
# Production Deployment Checklist
## Pre-Deployment
- [ ] All tests passing
- [ ] Linter passes
...
EOF
```

**Step 3: Commit with Closing Keyword**

**Format:**
```
<type>(<scope>): <short description>

Closes TASK-XXXX

<detailed description>
- Change 1
- Change 2
- Change 3
```

**Example:**
```bash
git add .
git commit -m "feat(deployment): Add deployment checklist

Closes TASK-0001

Created comprehensive deployment checklist with:
- Pre-deployment verification steps
- Deployment procedure
- Post-deployment monitoring
- Rollback procedures

All sections based on plan.md Section 7.4"
```

**Step 4: Push Changes**

```bash
# If on feature branch
git push origin feature/TASK-0001-deployment-checklist

# Then create and merge PR to main
# (Issue closes when PR is merged)

# Or if on main directly
git push origin main

# Issue closes automatically within seconds
```

**Step 5: Verify Issue Closed**

```bash
# Check issue status
gh issue view 1

# Or visit GitHub
# https://github.com/pythonpydev/total_bankroll/issues/1
```

**Expected Result:**
- Issue status: **Closed**
- Closing reference visible in issue timeline
- Link to commit that closed it

#### Advanced Examples

**Close Multiple Issues:**
```bash
git commit -m "fix(foundation): Fix email library and rate limiter

Closes TASK-1001
Closes TASK-1004

- Removed Flask-Mail duplicate
- Fixed IP detection for proxied requests
- Added logging for verification"
```

**Close Issue by Number (if known):**
```bash
git commit -m "feat(vite): Complete Vite configuration

Closes #5

Added proper Vite build configuration with manifest generation."
```

**Close Issue in PR Description:**
If you prefer to close via PR instead of commit:
```markdown
## Description
Complete Vite configuration

## Changes
- Added vite.config.js
- Configured manifest generation
- Tested dev and production builds

Closes TASK-1002
```

### Method 2: GitHub Actions Workflow

#### How It Works

A GitHub Actions workflow automatically runs on every push to the `main` branch:
1. Parses commit message for `TASK-XXXX` patterns
2. Finds corresponding open issues
3. Closes them with a completion comment
4. Links to the commit

#### Setup Procedure

**Step 1: Verify Workflow File Exists**

```bash
ls -la .github/workflows/close-task-on-commit.yml
```

**If not exists, create it** (it's already been created in this project).

**Step 2: Commit and Push Workflow**

```bash
git add .github/workflows/close-task-on-commit.yml
git commit -m "ci: Add automated task closing workflow"
git push origin main
```

**Step 3: Verify Workflow Active**

- Go to: https://github.com/pythonpydev/total_bankroll/actions
- Look for workflow: **"Close Task on Commit"**
- Status should show: ✅ (enabled)

#### Usage Procedure

**Step 1: Work on Task and Commit**

```bash
# Make changes
# ... edit files ...

# Commit mentioning task ID anywhere in message
git add .
git commit -m "feat(vite): Complete Vite configuration

TASK-1002

- Added proper vite.config.js
- Configured manifest generation  
- Enabled dev server
- Tested build process"
```

**Step 2: Push to Main**

```bash
git push origin main
```

**Step 3: Workflow Runs Automatically**

The workflow:
1. Detects `TASK-1002` in commit message
2. Finds issue with title starting with `TASK-1002:`
3. Adds completion comment with:
   - ✅ Timestamp
   - 🔗 Commit SHA
   - 📝 Full commit message
4. Closes the issue

**Step 4: Verify in GitHub Actions**

- Go to: https://github.com/pythonpydev/total_bankroll/actions
- Click latest workflow run
- Check logs to see:
  ```
  Found tasks: TASK-1002
  Processing TASK-1002...
  ✓ Closed issue #5
  ```

**Step 5: Verify Issue Closed**

```bash
gh issue view 5
```

**Expected Result:**
Issue closed with comment:
```markdown
## ✅ Task Completed

**Completed:** 2025-11-05 12:30 UTC
**Commit:** abc1234

**Commit Message:**
```
feat(vite): Complete Vite configuration

TASK-1002

- Added proper vite.config.js
- Configured manifest generation  
- Enabled dev server
- Tested build process
```

This task has been completed and verified. Closing issue automatically.
```

#### Advanced Usage

**Close Multiple Tasks:**
```bash
git commit -m "fix: Multiple foundation fixes

TASK-1001 TASK-1004 TASK-1005

Completed Phase 1 foundation fixes."

git push
# Workflow closes all three issues
```

**Workflow Runs Only on Main:**
- Commits to feature branches won't trigger workflow
- Merge PR to main to trigger
- Or cherry-pick commits to main

### Method 3: Manual Script

#### When to Use

- Close task without committing code
- Close task after code was already committed
- Reopen accidentally closed tasks
- Bulk close multiple tasks
- Add custom completion messages

#### Setup Procedure

**One-time setup:**

```bash
# Ensure PyGithub installed
pip install PyGithub

# Set GitHub token
export GITHUB_TOKEN="your_token_here"

# Or add to ~/.bashrc for persistence
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc

# Make bash wrapper executable
chmod +x scripts/task_complete.sh
```

#### Usage Procedure

**Option A: Using Python Script Directly**

```bash
# Simple closure
python scripts/close_github_issue.py --task TASK-0001

# With custom message
python scripts/close_github_issue.py \
  --task TASK-0001 \
  --comment "Completed deployment checklist. Tested rollback procedure successfully."

# Dry run (test without closing)
python scripts/close_github_issue.py --task TASK-0001 --dry-run
```

**Expected Output:**
```
Connecting to GitHub...
✓ Connected to repository: pythonpydev/total_bankroll
Looking for issue with task ID: TASK-0001
✓ Found issue #1: TASK-0001: Create Deployment Checklist
✓ Added completion comment to issue #1
✓ Closed issue #1

✓ Successfully closed TASK-0001
```

**Option B: Using Bash Wrapper Script**

```bash
# Simple closure
./scripts/task_complete.sh TASK-0001

# With message
./scripts/task_complete.sh TASK-0001 "Completed and tested in production"

# With detailed message
./scripts/task_complete.sh TASK-0001 "
Completed deployment checklist with:
- All pre-deployment steps
- Rollback procedure tested
- Production deployment successful
"
```

**Expected Output:**
```
Completing task: TASK-0001
Connecting to GitHub...
✓ Connected to repository: pythonpydev/total_bankroll
Looking for issue with task ID: TASK-0001
✓ Found issue #1: TASK-0001: Create Deployment Checklist
✓ Added completion comment to issue #1
✓ Closed issue #1

✓ Task TASK-0001 marked as complete on GitHub
```

#### Advanced Manual Operations

**Close Multiple Tasks in Sequence:**
```bash
#!/bin/bash
# Close multiple tasks
for task in TASK-0001 TASK-0002 TASK-0003; do
  ./scripts/task_complete.sh "$task" "Completed Week 0 tasks"
  sleep 2  # Rate limiting
done
```

**Close with Rich Markdown Comment:**
```bash
python scripts/close_github_issue.py \
  --task TASK-1002 \
  --comment "## ✅ Task Completed

**Completed:** $(date -u '+%Y-%m-%d %H:%M UTC')
**Environment:** Development & Production

### Changes Made
- Added \`vite.config.js\` with proper configuration
- Configured manifest generation
- Set up dev server on port 5173
- Tested both dev and production builds

### Testing
- ✅ \`npm run dev\` works
- ✅ \`npm run build\` generates manifest
- ✅ Assets load correctly in browser
- ✅ HMR (Hot Module Replacement) working

### Related Commits
- \`abc1234\` feat(vite): Add configuration
- \`def5678\` test(vite): Add build tests

This task has been completed and verified."
```

### Comparison of Methods

| Feature | Git Keywords | GitHub Actions | Manual Script |
|---------|-------------|----------------|---------------|
| **Automatic** | ✅ Yes | ✅ Yes | ❌ No |
| **Setup Required** | ✅ None | ⚠️ Workflow file | ⚠️ PyGithub + token |
| **Requires Code Change** | ✅ Yes | ✅ Yes | ❌ No |
| **Custom Messages** | ⚠️ Limited | ⚠️ Template | ✅ Full control |
| **Bulk Operations** | ❌ No | ⚠️ Via commit | ✅ Yes |
| **Reopen Issues** | ❌ No | ❌ No | ✅ Yes |
| **Works Offline** | ❌ No | ❌ No | ❌ No |
| **Team Friendly** | ✅ Yes | ✅ Yes | ⚠️ Individual |

### Recommended Method by Scenario

| Scenario | Recommended Method |
|----------|-------------------|
| Daily development workflow | Git Keywords |
| Team environment | Git Keywords + GitHub Actions |
| Solo developer | Git Keywords |
| Closing without code changes | Manual Script |
| Bulk operations | Manual Script |
| Custom messages needed | Manual Script |
| Maximum automation | GitHub Actions |

---

## Complete Workflow Examples

### Example 1: Solo Developer - Week 0 Deployment Safety

**Scenario:** You're working alone and completing Week 0 tasks.

```bash
# Day 1: Start with TASK-0001
git checkout -b feature/TASK-0001-deployment-checklist

# Create deployment checklist
mkdir -p .github
nano .github/deployment_checklist.md
# ... create file ...

# Commit and close issue
git add .
git commit -m "feat(deployment): Add deployment checklist

Closes TASK-0001

Created comprehensive deployment checklist covering:
- Pre-deployment verification
- Deployment steps
- Post-deployment monitoring
- Rollback procedures

Reference: plan.md Section 7.4"

git push origin feature/TASK-0001-deployment-checklist

# Create PR and merge to main
gh pr create --title "Add deployment checklist" --body "Closes TASK-0001"
gh pr merge 1 --squash

# Issue #1 closes automatically when PR merges

# Day 2: Continue with TASK-0002
git checkout main
git pull
git checkout -b feature/TASK-0002-env-parity-check

# Create script
nano scripts/check_env_parity.py
# ... create script ...

# Commit and close
git add .
git commit -m "feat(deployment): Add environment parity check

Closes TASK-0002

Created script to verify dev/prod consistency:
- Python version check
- Environment variables check  
- Migration status check
- Static assets check

Reference: plan.md Section 7.5"

git push origin feature/TASK-0002-env-parity-check
gh pr create --title "Add environment parity check" --body "Closes TASK-0002"
gh pr merge 2 --squash

# Continue for all Week 0 tasks...
```

### Example 2: Team Environment - Phase 1

**Scenario:** Multiple developers working on Phase 1 tasks.

**Developer A works on TASK-1001:**
```bash
# Assign issue to yourself
gh issue edit 1 --add-assignee "@me"

# Create branch
git checkout -b fix/TASK-1001-email-library

# Make changes
nano requirements.in
# Remove Flask-Mail, keep Flask-Mailman

pip-compile requirements.in
pip install -r requirements.txt

# Test
python test_email.py

# Commit with closing keyword
git add .
git commit -m "fix(deps): Remove duplicate Flask-Mail library

Closes TASK-1001

- Verified codebase uses Flask-Mailman
- Removed Flask-Mail from requirements.in
- Regenerated requirements.txt
- Tested email sending successfully

Reference: plan.md Section 4.1"

git push origin fix/TASK-1001-email-library

# Create PR
gh pr create \
  --title "Fix: Remove duplicate email library" \
  --body "Closes TASK-1001

Removed Flask-Mail duplicate as identified in architecture review."

# Teammate reviews and merges
# Issue closes automatically
```

**Developer B works on TASK-1004 simultaneously:**
```bash
# Different developer, different task
gh issue edit 4 --add-assignee "@devB"

git checkout -b fix/TASK-1004-rate-limiter

# Make changes
nano src/total_bankroll/extensions.py
# Fix IP detection

# Commit
git add .
git commit -m "fix(security): Correct rate limiter IP detection

Closes TASK-1004

Fixed IP extraction for proxied requests:
- Added X-Forwarded-For parsing
- Handle comma-separated IP lists
- Fallback to request.remote_addr
- Added logging for verification"

git push origin fix/TASK-1004-rate-limiter
gh pr create --title "Fix rate limiter IP detection" --body "Closes TASK-1004"
```

### Example 3: Closing Multiple Tasks in One Commit

**Scenario:** One commit addresses multiple related tasks.

```bash
# Working on Phase 1 foundation fixes
git checkout -b feat/phase-1-foundation

# Fix email library (TASK-1001)
nano requirements.in
# ... changes ...

# Fix rate limiter (TASK-1004)  
nano src/total_bankroll/extensions.py
# ... changes ...

# Add security headers (TASK-1005)
nano src/total_bankroll/__init__.py
# ... changes ...

# Commit closing all three
git add .
git commit -m "feat(foundation): Complete Phase 1 critical fixes

Closes TASK-1001
Closes TASK-1004
Closes TASK-1005

Completed three critical Phase 1 fixes:

**TASK-1001: Email Library**
- Removed Flask-Mail duplicate
- Verified Flask-Mailman usage
- Updated requirements.txt

**TASK-1004: Rate Limiter**
- Fixed IP detection for proxied requests
- Added proper X-Forwarded-For handling

**TASK-1005: Security Headers**
- Installed Flask-Talisman
- Configured CSP policy
- Added security headers middleware

All changes tested locally and ready for deployment."

git push origin feat/phase-1-foundation

# Create PR
gh pr create \
  --title "Complete Phase 1 critical fixes" \
  --body "Closes TASK-1001, TASK-1004, TASK-1005

Three critical Phase 1 fixes completed and tested."

# When merged, all three issues close automatically
```

### Example 4: Using Manual Script for Corrections

**Scenario:** You committed code but forgot to include "Closes TASK-XXXX" in commit message.

```bash
# Already committed and pushed
git log -1
# Output shows no "Closes" keyword

# Manually close the issue
./scripts/task_complete.sh TASK-1002 "Completed in commit abc1234. 
Vite configuration added and tested."

# Or with Python script for more control
python scripts/close_github_issue.py \
  --task TASK-1002 \
  --comment "## ✅ Task Completed

**Completed:** $(date -u '+%Y-%m-%d %H:%M UTC')
**Commit:** $(git rev-parse --short HEAD)

Vite configuration completed:
- Added vite.config.js
- Configured manifest generation
- Tested dev and production builds

Note: Closed manually as commit message missed keyword."
```

### Example 5: Bulk Closing with Script

**Scenario:** Testing phase completed, need to close multiple test issues.

```bash
# Create script to close multiple issues
cat > close_week0_tasks.sh << 'EOF'
#!/bin/bash
# Close all Week 0 tasks

WEEK0_TASKS=(
  "TASK-0001"
  "TASK-0002"
  "TASK-0003"
  "TASK-0004"
  "TASK-0005"
  "TASK-0006"
  "TASK-0007"
)

for task in "${WEEK0_TASKS[@]}"; do
  echo "Closing $task..."
  ./scripts/task_complete.sh "$task" "Week 0 deployment safety phase completed"
  sleep 2  # Rate limiting
done

echo "All Week 0 tasks closed"
EOF

chmod +x close_week0_tasks.sh

# Run it
./close_week0_tasks.sh
```

---

## Maintenance & Best Practices

### Daily Workflow Best Practices

#### 1. Branch Naming Convention

Always include task ID in branch name:

```bash
# Format: <type>/<TASK-ID>-<short-description>
git checkout -b feature/TASK-0001-deployment-checklist
git checkout -b fix/TASK-1004-rate-limiter
git checkout -b refactor/TASK-2002-bankroll-service
git checkout -b test/TASK-3006-test-coverage
git checkout -b docs/TASK-6004-api-docs
```

**Benefits:**
- Easy to identify what branch is for
- Pre-commit hooks can auto-add task ID
- Clear in PR list

#### 2. Commit Message Format

Use Conventional Commits with task reference:

```
<type>(<scope>): <description>

Closes TASK-XXXX

<detailed changes>
- Bullet 1
- Bullet 2

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Adding tests
- `docs`: Documentation
- `style`: Formatting
- `chore`: Maintenance

**Examples:**
```bash
feat(deployment): Add deployment checklist

Closes TASK-0001

- Created comprehensive checklist
- Added rollback procedures
```

```bash
fix(security): Correct rate limiter IP detection

Closes TASK-1004

- Fixed X-Forwarded-For parsing
- Added fallback logic
```

#### 3. Assignment and Labels

**Before starting a task:**
```bash
# Assign to yourself
gh issue edit 1 --add-assignee "@me"

# Add in-progress label (if exists)
gh issue edit 1 --add-label "in-progress"

# Link to project board
# (Do via web UI or API)
```

**Benefits:**
- Team knows who's working on what
- Prevents duplicate work
- Progress visible at a glance

#### 4. Progress Tracking

**Weekly Review:**
```bash
# Check completed this week
gh issue list \
  --state closed \
  --search "closed:>=2025-11-01"

# Check remaining in current phase
gh issue list --label phase-1-foundation

# Check your assigned tasks
gh issue list --assignee "@me"
```

**Monthly Review:**
```bash
# Generate progress report
echo "## Progress Report $(date +%Y-%m)"
echo ""
echo "### Completed Tasks"
gh issue list --state closed --search "closed:>=2025-11-01" | wc -l
echo ""
echo "### Open Tasks by Phase"
for phase in 0 1 2 3 4 5 6 7; do
  count=$(gh issue list --label "phase-$phase" --state open | wc -l)
  echo "Phase $phase: $count tasks"
done
```

### Maintenance Scripts

#### Weekly Label Cleanup

```bash
#!/bin/bash
# cleanup_labels.sh
# Remove stale labels, verify consistency

echo "Cleaning up GitHub labels..."

# Remove labels from closed issues
gh issue list --state closed --limit 100 | while read -r number rest; do
  # Remove in-progress label if exists
  gh issue edit "$number" --remove-label "in-progress" 2>/dev/null
done

echo "✓ Label cleanup complete"
```

#### Monthly Issue Audit

```bash
#!/bin/bash
# audit_issues.sh
# Check for issues without labels, assignees, etc.

echo "## Issue Audit $(date +%Y-%m-%d)"
echo ""

# Issues without priority label
echo "### Issues Without Priority"
gh issue list --json number,title,labels --jq \
  '.[] | select(.labels | map(.name) | any(startswith("priority-")) | not) | "\(.number) \(.title)"'

echo ""

# Issues without phase label  
echo "### Issues Without Phase"
gh issue list --json number,title,labels --jq \
  '.[] | select(.labels | map(.name) | any(startswith("phase-")) | not) | "\(.number) \(.title)"'

echo ""

# Open issues without assignees
echo "### Unassigned Open Issues"
gh issue list --json number,title,assignees --jq \
  '.[] | select(.assignees | length == 0) | "\(.number) \(.title)"'
```

### Security Best Practices

#### 1. Token Management

**Never commit tokens to repository:**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.token" >> .gitignore

# Store token securely
echo "GITHUB_TOKEN=your_token_here" > .env
chmod 600 .env

# Load in scripts
# from dotenv import load_dotenv
# load_dotenv()
```

**Rotate tokens regularly:**
- Personal tokens: Every 90 days
- Team tokens: Every 30 days

**Use token with minimal permissions:**
- Only `repo` scope needed
- Don't grant `admin` unless necessary

#### 2. Script Safety

**Always use dry-run first:**
```bash
# Test before running
python scripts/close_github_issue.py --task TASK-0001 --dry-run

# Then run for real
python scripts/close_github_issue.py --task TASK-0001
```

**Verify before bulk operations:**
```bash
# Count what will be affected
gh issue list --label phase-1-foundation | wc -l

# Review list
gh issue list --label phase-1-foundation

# Then proceed with bulk action
```

### Backup and Recovery

#### Backup Open Issues

```bash
#!/bin/bash
# backup_issues.sh
# Backup all open issues to JSON

BACKUP_DIR="$HOME/backups/github_issues"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/issues_$(date +%Y%m%d_%H%M%S).json"

gh issue list \
  --state all \
  --limit 1000 \
  --json number,title,body,state,labels,assignees,milestone,createdAt,closedAt \
  > "$BACKUP_FILE"

echo "✓ Backup saved to: $BACKUP_FILE"
```

**Run weekly:**
```bash
# Add to crontab
crontab -e

# Add line:
0 0 * * 0 /home/ed/MEGA/total_bankroll/scripts/backup_issues.sh
```

#### Reopen Accidentally Closed Issue

```bash
# Reopen single issue
gh issue reopen 1

# Reopen multiple issues
gh issue reopen 1 2 3 4

# Reopen with comment
gh issue reopen 1 --comment "Reopening - additional work needed"
```

---

## Troubleshooting

### Issue Creation Problems

#### Problem: "Permission denied" error

**Symptoms:**
```
✗ Failed to connect to repository: 403 Forbidden
```

**Solutions:**
1. Verify token has `repo` scope:
   - Go to: https://github.com/settings/tokens
   - Click on your token
   - Ensure `repo` is checked
   - Regenerate if needed

2. Check token hasn't expired:
   ```bash
   gh auth status
   ```

3. Verify repository access:
   ```bash
   gh repo view pythonpydev/total_bankroll
   ```

#### Problem: "Label not found" error

**Symptoms:**
```
✗ Failed to create issue: Label 'priority-p0-critical' does not exist
```

**Solutions:**
1. Create labels first:
   ```bash
   python scripts/create_github_issues.py --token $GITHUB_TOKEN --limit 0
   ```

2. Or skip labels in issue creation:
   ```bash
   python scripts/create_github_issues.py --token $GITHUB_TOKEN --skip-labels
   ```

3. Manually create labels via web UI:
   - Go to: https://github.com/pythonpydev/total_bankroll/labels
   - Create labels as defined in script

#### Problem: Duplicate issues created

**Symptoms:**
```
✓ Created issue #1: TASK-0001: Create Deployment Checklist
✓ Created issue #2: TASK-0001: Create Deployment Checklist
```

**Solutions:**
1. Always use `--dry-run` first
2. Check existing issues before running:
   ```bash
   gh issue list | grep TASK-0001
   ```

3. Delete duplicates:
   ```bash
   gh issue delete 2
   ```

4. Prevent reruns - script doesn't check for existing issues

#### Problem: Rate limiting

**Symptoms:**
```
✗ GitHub API rate limit exceeded
```

**Solutions:**
1. Wait an hour (rate limit resets hourly)
2. Check rate limit status:
   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit
   ```

3. Use `--limit` for smaller batches:
   ```bash
   python scripts/create_github_issues.py --limit 10
   # Wait a bit
   # Manually track which issues created
   ```

### Issue Closing Problems

#### Problem: Commit has "Closes TASK-0001" but issue not closing

**Possible Causes & Solutions:**

**1. Commit not on default branch:**
```bash
# Check which branch you're on
git branch

# Issue only closes when merged to main
git checkout main
git merge feature/TASK-0001-deployment
git push
```

**2. Keyword format incorrect:**
```bash
# ✅ Correct formats:
Closes TASK-0001
Closes #1
Fixes TASK-0001
Resolves TASK-0001

# ❌ Incorrect formats:
closes TASK-0001  # Lowercase might not work on some systems
Closed TASK-0001  # Wrong tense
TASK-0001 (without keyword)
Closes: TASK-0001  # Extra colon
```

**3. Task ID doesn't match issue title:**
```bash
# Check exact task ID in issue title
gh issue view 1 | head -1

# Might show: "TASK-0001: Create Deployment Checklist"
# Must use exact: TASK-0001
```

**4. GitHub processing delay:**
```bash
# Wait 30-60 seconds then check
gh issue view 1

# Force refresh
gh issue view 1 --web
```

**5. Repository settings:**
- Go to: Settings → General → Pull Requests
- Ensure "Allow auto-merge" is enabled
- Ensure "Automatically delete head branches" is enabled

**Solutions:**
```bash
# Solution A: Use issue number instead
git commit --amend
# Change "Closes TASK-0001" to "Closes #1"
git push --force

# Solution B: Close manually
./scripts/task_complete.sh TASK-0001

# Solution C: Reference in PR description
gh pr create --body "Closes TASK-0001"
```

#### Problem: GitHub Actions workflow not running

**Symptoms:**
- Commit pushed to main
- TASK-ID in commit message
- Issue still open
- No workflow run visible

**Checks:**

**1. Workflow file exists:**
```bash
ls -la .github/workflows/close-task-on-commit.yml
```

**2. Workflow enabled:**
- Go to: https://github.com/pythonpydev/total_bankroll/actions
- Check if workflow appears in list
- Check if workflow is disabled (shouldn't be)

**3. Workflow permissions:**
- Go to: Settings → Actions → General → Workflow permissions
- Ensure "Read and write permissions" is selected

**4. Check workflow run logs:**
```bash
# Via CLI
gh run list --workflow="close-task-on-commit.yml"

# View latest run
gh run view

# Or via web
# https://github.com/pythonpydev/total_bankroll/actions
```

**5. Syntax errors in workflow:**
```bash
# Validate workflow syntax
cat .github/workflows/close-task-on-commit.yml | python -c "import yaml, sys; yaml.safe_load(sys.stdin)"
```

**Solutions:**

**A. Fix workflow permissions:**
1. Go to: Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Click Save

**B. Trigger workflow manually:**
```bash
# If workflow supports manual trigger
gh workflow run close-task-on-commit.yml
```

**C. Check workflow logs for errors:**
```bash
gh run view --log
# Look for errors like:
# - "Permission denied"
# - "PyGithub not found"
# - "Script not found"
```

**D. Re-push to trigger:**
```bash
git commit --allow-empty -m "trigger: Re-run workflow"
git push
```

#### Problem: Manual script can't find issue

**Symptoms:**
```
✗ No open issue found for TASK-0001
```

**Solutions:**

**1. Check issue actually exists:**
```bash
gh issue list | grep TASK-0001
```

**2. Check if issue already closed:**
```bash
gh issue list --state all | grep TASK-0001
```

**3. Check exact task ID format:**
```bash
# View issue title
gh issue view 1

# Script looks for title starting with "TASK-0001:"
# Ensure format matches exactly
```

**4. Search all issues:**
```bash
gh issue list --state all --search "TASK-0001"
```

**5. Use issue number directly:**
```bash
# Modify script to use issue number instead of task ID
# (Would require code change)

# Or use gh CLI
gh issue close 1 --comment "Completed manually"
```

### General Issues

#### Problem: Lost GitHub token

**Solution:**
```bash
# Generate new token
# 1. Go to: https://github.com/settings/tokens
# 2. Click: Generate new token (classic)
# 3. Select scopes: repo
# 4. Generate and copy

# Update environment variable
export GITHUB_TOKEN="new_token_here"
echo 'export GITHUB_TOKEN="new_token_here"' >> ~/.bashrc
```

#### Problem: Script not executable

**Symptoms:**
```
bash: ./scripts/task_complete.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/task_complete.sh
chmod +x scripts/create_github_issues.py
chmod +x scripts/close_github_issue.py
```

#### Problem: PyGithub not found

**Symptoms:**
```
ModuleNotFoundError: No module named 'github'
```

**Solution:**
```bash
pip install PyGithub

# Or in virtual environment
workon bankroll_venv
pip install PyGithub
```

#### Problem: Wrong repository

**Symptoms:**
```
✗ Failed to connect to repository: 404 Not Found
```

**Solution:**
```bash
# Check repository name
gh repo view

# Use correct format: owner/repo
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN \
  --repo pythonpydev/total_bankroll
```

---

## Quick Reference

### Essential Commands

#### Create Issues
```bash
# Dry run
python scripts/create_github_issues.py --token $GITHUB_TOKEN --dry-run

# Create labels only
python scripts/create_github_issues.py --token $GITHUB_TOKEN --limit 0

# Create limited issues
python scripts/create_github_issues.py --token $GITHUB_TOKEN --limit 5

# Create all issues
python scripts/create_github_issues.py --token $GITHUB_TOKEN
```

#### Close Issues
```bash
# Via commit message
git commit -m "feat: Description

Closes TASK-0001"

# Via manual script
./scripts/task_complete.sh TASK-0001

# Via Python script
python scripts/close_github_issue.py --task TASK-0001

# Via GitHub CLI
gh issue close 1
```

#### View Issues
```bash
# List open issues
gh issue list

# List by label
gh issue list --label phase-1-foundation

# View specific issue
gh issue view 1

# List closed issues
gh issue list --state closed
```

#### Manage Labels
```bash
# List all labels
gh label list

# Create label
gh label create priority-p0-critical --color DC143C --description "Critical"

# Delete label
gh label delete old-label
```

### File Locations

```
total_bankroll/
├── .specify/memory/
│   ├── tasks.md                    # Source task list
│   ├── constitution.md             # Project constitution
│   ├── specification.md            # Technical specification
│   ├── plan.md                     # Architecture plan
│   └── github_automation_guide.md  # This document
├── .github/
│   ├── deployment_checklist.md     # Deployment checklist (TASK-0001)
│   └── workflows/
│       └── close-task-on-commit.yml  # Auto-close workflow
└── scripts/
    ├── create_github_issues.py     # Issue creation script
    ├── close_github_issue.py       # Issue closing script
    ├── task_complete.sh            # Bash wrapper
    ├── README_github_issues.md     # Issue creation guide
    └── README_task_completion.md   # Task completion guide
```

### Environment Variables

```bash
# Required
export GITHUB_TOKEN="ghp_your_token_here"

# Optional
export GITHUB_REPO="pythonpydev/total_bankroll"

# Verify
echo $GITHUB_TOKEN | head -c 10
```

### Commit Message Template

```bash
# Save to ~/.gitmessage
cat > ~/.gitmessage << 'EOF'
<type>(<scope>): <description>

Closes TASK-XXXX

# Detailed description
- Change 1
- Change 2
- Change 3

# Reference
Reference: plan.md Section X.X

# Co-authors (if applicable)
# Co-authored-by: Name <email>
EOF

# Configure git to use template
git config --global commit.template ~/.gitmessage
```

### Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc

# Issue management
alias task-list='gh issue list'
alias task-view='gh issue view'
alias task-close='./scripts/task_complete.sh'
alias task-create='python scripts/create_github_issues.py --token $GITHUB_TOKEN'

# Quick views
alias tasks-open='gh issue list --state open'
alias tasks-closed='gh issue list --state closed'
alias tasks-mine='gh issue list --assignee "@me"'
alias tasks-p0='gh issue list --label priority-p0-critical'

# Git with task
alias git-task='!f() { git commit -m "$2

Closes $1"; }; f'

# Usage: git-task TASK-0001 "feat: Add feature"
```

### URLs

- **Repository:** https://github.com/pythonpydev/total_bankroll
- **Issues:** https://github.com/pythonpydev/total_bankroll/issues
- **Actions:** https://github.com/pythonpydev/total_bankroll/actions
- **Labels:** https://github.com/pythonpydev/total_bankroll/labels
- **Projects:** https://github.com/pythonpydev/total_bankroll/projects
- **Token Settings:** https://github.com/settings/tokens

---

## Appendix: Full Script Documentation

### create_github_issues.py

**Purpose:** Bulk create GitHub issues from tasks.md

**Arguments:**
- `--token` (required): GitHub personal access token
- `--repo` (optional): Repository in format owner/repo (default: pythonpydev/total_bankroll)
- `--tasks-file` (optional): Path to tasks.md (default: .specify/memory/tasks.md)
- `--dry-run` (flag): Test without creating
- `--skip-labels` (flag): Skip label creation
- `--limit` (optional): Limit number of issues to create

**Examples:**
```bash
# Full dry run
python scripts/create_github_issues.py --token $GITHUB_TOKEN --dry-run

# Create labels only
python scripts/create_github_issues.py --token $GITHUB_TOKEN --limit 0

# Create 5 issues
python scripts/create_github_issues.py --token $GITHUB_TOKEN --limit 5

# Create all from different file
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN \
  --tasks-file custom_tasks.md

# Different repo
python scripts/create_github_issues.py \
  --token $GITHUB_TOKEN \
  --repo myuser/myrepo
```

### close_github_issue.py

**Purpose:** Close specific GitHub issue by task ID

**Arguments:**
- `--task` (required): Task ID (e.g., TASK-0001)
- `--token` (optional): GitHub token (or use GITHUB_TOKEN env var)
- `--repo` (optional): Repository (default: pythonpydev/total_bankroll)
- `--comment` (optional): Custom completion comment
- `--dry-run` (flag): Test without closing

**Examples:**
```bash
# Simple close
python scripts/close_github_issue.py --task TASK-0001

# With custom comment
python scripts/close_github_issue.py \
  --task TASK-0001 \
  --comment "Completed and deployed to production"

# Dry run
python scripts/close_github_issue.py --task TASK-0001 --dry-run

# Different repo
python scripts/close_github_issue.py \
  --task TASK-0001 \
  --repo myuser/myrepo
```

### task_complete.sh

**Purpose:** Bash wrapper for easy task completion

**Arguments:**
1. Task ID (required)
2. Message (optional)

**Examples:**
```bash
# Simple
./scripts/task_complete.sh TASK-0001

# With message
./scripts/task_complete.sh TASK-0001 "Completed successfully"

# Multi-line message
./scripts/task_complete.sh TASK-0001 "
Completed deployment checklist:
- All steps documented
- Tested rollback
- Ready for production
"
```

### close-task-on-commit.yml

**Purpose:** GitHub Actions workflow to auto-close issues

**Trigger:** Push to main branch

**Process:**
1. Checkout code
2. Parse commit message for TASK-XXXX patterns
3. Find matching open issues
4. Close with completion comment

**Configuration:** No configuration needed - uses repository GITHUB_TOKEN automatically

**To Disable:**
```bash
# Rename or delete workflow file
mv .github/workflows/close-task-on-commit.yml \
   .github/workflows/close-task-on-commit.yml.disabled
```

---

## Summary Checklist

### Initial Setup (One-time)
- [ ] Install PyGithub: `pip install PyGithub`
- [ ] Create GitHub personal access token
- [ ] Set GITHUB_TOKEN environment variable
- [ ] Verify repository access
- [ ] Make scripts executable: `chmod +x scripts/*.sh`

### Creating Issues (Once)
- [ ] Review tasks.md for accuracy
- [ ] Run dry-run to verify parsing
- [ ] Create labels (--limit 0)
- [ ] Test with 3-5 issues
- [ ] Create all 50+ issues
- [ ] Verify on GitHub
- [ ] Set up project board (optional)
- [ ] Create milestones (optional)

### Daily Workflow
- [ ] Assign issue to yourself
- [ ] Create feature branch with task ID
- [ ] Complete work
- [ ] Commit with "Closes TASK-XXXX"
- [ ] Push to GitHub
- [ ] Create PR (if using branches)
- [ ] Merge to main
- [ ] Verify issue closed

### Weekly Maintenance
- [ ] Review completed tasks
- [ ] Check open issues
- [ ] Update project board
- [ ] Backup issues (optional)
- [ ] Clean up stale branches

### Monthly Review
- [ ] Generate progress report
- [ ] Review and update milestones
- [ ] Audit issue labels and assignees
- [ ] Rotate GitHub token (every 90 days)

---

**Document Status:** Production Ready  
**Last Updated:** 2025-11-05  
**Next Review:** After Week 0 completion

---

*For additional help, refer to:*
- `scripts/README_github_issues.md` - Detailed issue creation guide
- `scripts/README_task_completion.md` - Detailed task completion guide
- `.specify/memory/plan.md` - Full architecture and implementation plan
- `.specify/memory/tasks.md` - Complete task list

*End of GitHub Automation Guide*
