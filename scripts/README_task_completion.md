# Automating Task Completion on GitHub

This guide shows multiple ways to automatically close GitHub issues when tasks are completed.

---

## 🎯 Overview

When you complete a task, you can automatically:
1. Close the corresponding GitHub issue
2. Add a completion comment with timestamp
3. Link the completion to specific commits
4. Update the issue with completion details

---

## Method 1: Git Commit Messages (Automatic)

### How It Works
GitHub automatically closes issues when you use special keywords in commit messages.

### Usage

**Option A: Use "Closes" keyword**
```bash
git commit -m "feat(deployment): Add deployment checklist

Closes TASK-0001
- Created .github/deployment_checklist.md
- Added pre/post deployment sections
- Documented rollback procedures"

git push
```

**Option B: Use issue number (if you know it)**
```bash
git commit -m "feat(deployment): Add deployment checklist

Closes #1
Resolves #2
Fixes #3"

git push
```

**Supported Keywords:**
- `Closes TASK-0001` or `Closes #123`
- `Fixes TASK-0001` or `Fixes #123`
- `Resolves TASK-0001` or `Resolves #123`

**Important:** The keyword must be followed by the issue number or TASK-ID that appears in the issue title.

---

## Method 2: Manual Script (Interactive)

### Prerequisites
```bash
pip install PyGithub
export GITHUB_TOKEN="your_token_here"
```

### Usage

**Simple completion:**
```bash
python scripts/close_github_issue.py --task TASK-0001
```

**With custom message:**
```bash
python scripts/close_github_issue.py \
  --task TASK-0001 \
  --comment "Completed deployment checklist. Tested rollback procedure successfully."
```

**Dry run (test without closing):**
```bash
python scripts/close_github_issue.py --task TASK-0001 --dry-run
```

---

## Method 3: Convenience Bash Script

### Setup
```bash
chmod +x scripts/task_complete.sh
export GITHUB_TOKEN="your_token_here"
```

### Usage

**Simple:**
```bash
./scripts/task_complete.sh TASK-0001
```

**With message:**
```bash
./scripts/task_complete.sh TASK-0001 "Completed and tested in production"
```

---

## Method 4: GitHub Actions (Automated on Push)

### How It Works
A GitHub Action automatically runs on every push to `main` branch:
1. Parses commit messages for TASK-XXXX patterns
2. Finds corresponding open issues
3. Closes them with completion comment
4. Links to the commit

### Setup

The workflow file is already created: `.github/workflows/close-task-on-commit.yml`

**To use:**
```bash
git add .github/workflows/close-task-on-commit.yml
git commit -m "Add automated task closing workflow"
git push
```

### Commit Message Format

**Single task:**
```bash
git commit -m "feat(vite): Complete Vite configuration

TASK-1002

- Added proper vite.config.js
- Configured manifest generation
- Tested dev and production builds"
```

**Multiple tasks:**
```bash
git commit -m "fix: Email library and rate limiter fixes

TASK-1001 TASK-1004

- Removed Flask-Mail duplicate
- Fixed IP detection for proxy
- Added logging for verification"
```

**The workflow will:**
- Detect `TASK-1002` and `TASK-1001` in commit
- Find matching open issues
- Close them automatically
- Add comment with commit details

---

## Method 5: Git Aliases (Convenient)

### Setup
Add to your `~/.gitconfig`:

```bash
git config --global alias.task-commit '!f() { 
    task=$1; 
    shift; 
    git commit -m "$@ 

Closes $task"; 
}; f'
```

### Usage
```bash
git add .
git task-commit TASK-0001 "feat(deployment): Add deployment checklist"
git push
```

This automatically adds "Closes TASK-0001" to your commit message.

---

## Method 6: Pre-Commit Hook (Advanced)

### Setup

Create `.git/hooks/prepare-commit-msg`:
```bash
#!/bin/bash
# Automatically add TASK-ID if branch name contains it

COMMIT_MSG_FILE=$1
BRANCH_NAME=$(git symbolic-ref --short HEAD)

# Extract TASK-ID from branch name (e.g., feature/TASK-0001-deployment)
TASK_ID=$(echo "$BRANCH_NAME" | grep -oE 'TASK-[0-9]{4}')

if [ -n "$TASK_ID" ]; then
    # Check if TASK-ID already in commit message
    if ! grep -q "$TASK_ID" "$COMMIT_MSG_FILE"; then
        # Add to commit message
        echo "" >> "$COMMIT_MSG_FILE"
        echo "Closes $TASK_ID" >> "$COMMIT_MSG_FILE"
    fi
fi
```

**Make executable:**
```bash
chmod +x .git/hooks/prepare-commit-msg
```

**Usage:**
1. Create branch: `git checkout -b feature/TASK-0001-deployment`
2. Make changes
3. Commit: `git commit -m "Add deployment checklist"`
4. Hook automatically adds "Closes TASK-0001" to message
5. Push: `git push`

---

## Recommended Workflow

### Option A: Git Commit Keywords (Simplest)

```bash
# 1. Start working on task
git checkout -b feature/TASK-0001-deployment

# 2. Make changes
# ... code ...

# 3. Commit with closing keyword
git add .
git commit -m "feat(deployment): Add deployment checklist

Closes TASK-0001

- Created checklist file
- Added all required sections
- Tested process"

# 4. Push (issue closes automatically)
git push origin feature/TASK-0001-deployment

# 5. Merge PR to main
```

### Option B: GitHub Actions (Automated)

```bash
# 1. Work on feature branch
git checkout -b feature/add-vite-config

# 2. Commit mentioning task
git commit -m "feat(build): Complete Vite configuration

TASK-1002

Added manifest generation and proper config."

# 3. Push to main (or merge PR)
git push origin main

# 4. GitHub Action automatically closes TASK-1002
```

### Option C: Manual Script (Immediate Feedback)

```bash
# 1. Complete task
# ... work done ...

# 2. Commit changes
git add .
git commit -m "feat(deployment): Add deployment checklist"
git push

# 3. Manually close task
./scripts/task_complete.sh TASK-0001 "Completed and verified"
```

---

## Best Practices

### 1. Commit Message Format

Use conventional commits with task reference:
```
<type>(<scope>): <description>

Closes TASK-XXXX

- Detailed change 1
- Detailed change 2
- Detailed change 3

Co-authored-by: Name <email>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding tests
- `docs`: Documentation
- `chore`: Maintenance

### 2. Branch Naming

Include task ID in branch name:
```bash
feature/TASK-0001-deployment-checklist
fix/TASK-1004-rate-limiter-ip
refactor/TASK-2002-bankroll-service
```

### 3. Pull Request Template

Create `.github/pull_request_template.md`:
```markdown
## Description
Brief description of changes

## Related Task
Closes TASK-XXXX

## Changes
- Change 1
- Change 2

## Testing
- [ ] Tested locally
- [ ] All tests pass
- [ ] No linting errors

## Checklist
- [ ] Code follows project standards
- [ ] Documentation updated
- [ ] Tests added/updated
```

### 4. Multiple Tasks in One PR

If a PR addresses multiple tasks:
```bash
git commit -m "feat(foundation): Complete Phase 1 fixes

Closes TASK-1001
Closes TASK-1004
Closes TASK-1005

Fixed email library duplication, rate limiter, and added security headers."
```

---

## Verification

### Check if task was closed:
```bash
# View issue status
gh issue view TASK-0001

# Or check on GitHub
# https://github.com/pythonpydev/total_bankroll/issues
```

### Reopen if needed:
```bash
# If accidentally closed
gh issue reopen TASK-0001

# Or via script
python scripts/close_github_issue.py --task TASK-0001 --reopen
```

---

## Troubleshooting

### Issue not closing automatically

**Problem:** Committed with "Closes TASK-0001" but issue still open

**Solutions:**
1. Check commit message includes exact task ID as it appears in issue title
2. Verify commit was pushed to main branch (default branch)
3. GitHub may take a few minutes to process
4. Use `git log` to verify commit message saved correctly
5. Try using issue number: `Closes #1` instead

### GitHub Action not running

**Checks:**
1. Workflow file in `.github/workflows/`
2. Pushed to main branch
3. Check Actions tab: https://github.com/pythonpydev/total_bankroll/actions
4. Verify workflow has necessary permissions

### Script can't find issue

**Problem:** `No open issue found for TASK-0001`

**Solutions:**
1. Issue might already be closed (check closed issues)
2. Task ID might not match issue title exactly
3. Issue might not exist yet
4. Check you're searching correct repository

---

## Environment Variables

### Setup for convenience

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GITHUB_TOKEN="your_token_here"
export GITHUB_REPO="pythonpydev/total_bankroll"

# Convenient aliases
alias task-close='python scripts/close_github_issue.py --task'
alias task-list='gh issue list --label phase-1-foundation'
alias task-view='gh issue view'
```

**Usage:**
```bash
task-close TASK-0001
task-list
task-view TASK-0001
```

---

## Integration with IDEs

### VS Code

Install GitHub Pull Requests extension and use:
- `Ctrl+Shift+P` → "GitHub: Close Issue"
- Reference issues in commits with `#`

### JetBrains (PyCharm, WebStorm)

1. Go to Settings → Version Control → GitHub
2. Link GitHub account
3. Use commit dialog to reference issues
4. Issues auto-complete with `#`

---

## Summary

**Simplest Method:** Use "Closes TASK-XXXX" in commit messages  
**Most Automated:** GitHub Actions workflow  
**Most Control:** Manual Python script  
**Best for Teams:** Pre-commit hooks + PR templates  

Choose the method that fits your workflow!

---

**Pro Tip:** Start with Method 1 (commit keywords) and add automation later as needed.
