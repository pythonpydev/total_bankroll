# Creating GitHub Issues from tasks.md

This guide provides multiple methods to create GitHub issues from the task list.

---

## Method 1: Automated Script (Recommended)

### Prerequisites

1. **Install PyGithub:**
   ```bash
   pip install PyGithub
   ```

2. **Create GitHub Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Give it a descriptive name: "Task Issue Creator"
   - Select scopes:
     - `repo` (Full control of private repositories)
     - `write:discussion` (if using discussions)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again)

### Usage

**Dry run first (recommended):**
```bash
python scripts/create_github_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --dry-run
```

**Test with limited issues:**
```bash
python scripts/create_github_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --limit 3
```

**Create all issues:**
```bash
python scripts/create_github_issues.py \
  --token YOUR_GITHUB_TOKEN
```

**Advanced options:**
```bash
python scripts/create_github_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --repo pythonpydev/total_bankroll \
  --tasks-file .specify/memory/tasks.md \
  --skip-labels  # If labels already exist
```

---

## Method 2: GitHub CLI (gh)

### Prerequisites

1. **Install GitHub CLI:**
   ```bash
   # macOS
   brew install gh
   
   # Linux
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   sudo apt install gh
   ```

2. **Authenticate:**
   ```bash
   gh auth login
   ```

### Create Issues Manually

```bash
# Example for TASK-0001
gh issue create \
  --title "TASK-0001: Create Deployment Checklist" \
  --body "$(cat <<'EOF'
**Priority:** 🔴 P0
**Effort:** 30 minutes
**Phase:** Week 0 - Deployment Safety

## Description
Create deployment checklist document

## Acceptance Criteria
- [ ] File created: `.github/deployment_checklist.md`
- [ ] Contains pre-deployment, deployment, and post-deployment sections
- [ ] Committed to repository

## Related Files
- `.github/deployment_checklist.md` (new)

## Reference
Section 7.4 of plan.md
EOF
)" \
  --label priority-p0-critical \
  --label phase-0-deployment
```

---

## Method 3: GitHub Web Interface (Manual)

### Step-by-Step

1. **Go to your repository:**
   https://github.com/pythonpydev/total_bankroll

2. **Click "Issues" tab**

3. **Click "New issue"**

4. **For each task:**
   - **Title:** Copy from tasks.md (e.g., "TASK-0001: Create Deployment Checklist")
   - **Description:** Copy the full task section
   - **Labels:** Add appropriate priority and phase labels
   - **Assignees:** Assign to yourself or team member
   - **Projects:** Add to project board if using
   - **Milestone:** Add to appropriate phase milestone

5. **Click "Submit new issue"**

---

## Method 4: Bulk Import via CSV

### Step 1: Convert tasks.md to CSV

Create `tasks.csv`:
```csv
title,body,labels,assignee
"TASK-0001: Create Deployment Checklist","Priority: P0
Effort: 30 minutes
...","priority-p0-critical,phase-0-deployment",""
```

### Step 2: Import with GitHub Importer

Unfortunately, GitHub doesn't have a native CSV importer for issues, so this method requires the PyGithub script or manual creation.

---

## Method 5: Use GitHub Projects Import

### Step 1: Create Project

1. Go to: https://github.com/pythonpydev/total_bankroll/projects
2. Click "New project"
3. Choose "Board" template
4. Name it: "StakeEasy Implementation Roadmap"

### Step 2: Add Issue Templates

Create issue templates in `.github/ISSUE_TEMPLATE/`:

```yaml
# .github/ISSUE_TEMPLATE/task.yml
name: Implementation Task
description: Task from implementation plan
title: "[TASK-XXXX]: "
labels: []
body:
  - type: input
    id: task-id
    attributes:
      label: Task ID
      description: Task identifier (e.g., TASK-0001)
      placeholder: TASK-0001
    validations:
      required: true
  
  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - P0 - Critical
        - P1 - High
        - P2 - Medium
        - P3 - Low
    validations:
      required: true
  
  - type: dropdown
    id: phase
    attributes:
      label: Phase
      options:
        - Week 0 - Deployment Safety
        - Phase 1 - Foundation
        - Phase 2 - Service Layer
        - Phase 3 - Performance
        - Phase 4 - Frontend
        - Phase 5 - Database
        - Phase 6 - API
        - Phase 7 - Observability
    validations:
      required: true
  
  - type: input
    id: effort
    attributes:
      label: Effort Estimate
      description: Time estimate (e.g., 2 hours, 1 day)
      placeholder: 2 hours
  
  - type: textarea
    id: description
    attributes:
      label: Description
      description: What needs to be done?
    validations:
      required: true
  
  - type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance Criteria
      description: List of requirements for completion
      value: |
        - [ ] 
    validations:
      required: true
  
  - type: textarea
    id: related-files
    attributes:
      label: Related Files
      description: Files that will be created or modified
  
  - type: textarea
    id: dependencies
    attributes:
      label: Dependencies
      description: Tasks that must be completed first
  
  - type: input
    id: reference
    attributes:
      label: Reference
      description: Link to documentation (plan.md section)
```

---

## Recommended Workflow

### Option A: Full Automation (Fastest)

```bash
# 1. Install dependencies
pip install PyGithub

# 2. Get GitHub token
# (See instructions above)

# 3. Dry run to verify
python scripts/create_github_issues.py --token YOUR_TOKEN --dry-run

# 4. Create labels
python scripts/create_github_issues.py --token YOUR_TOKEN --limit 0

# 5. Create first 5 issues as test
python scripts/create_github_issues.py --token YOUR_TOKEN --limit 5

# 6. Review created issues on GitHub
# Check they look correct

# 7. Create all remaining issues
python scripts/create_github_issues.py --token YOUR_TOKEN
```

### Option B: Phase-by-Phase (More Control)

1. **Week 0 Only:**
   - Create 7 issues manually for Week 0
   - Test the workflow
   - Complete Week 0 tasks

2. **After Week 0:**
   - Use script to create Phase 1 issues
   - Continue phase by phase

### Option C: Manual with Milestones

1. **Create Milestones:**
   - Week 0: Deployment Safety
   - Phase 1: Foundation
   - Phase 2: Service Layer
   - Phase 3: Performance
   - Phase 4: Frontend
   - Phase 5: Database
   - Phase 6: API
   - Phase 7: Observability

2. **Create Issues Manually:**
   - Copy from tasks.md
   - Assign to milestone
   - Add labels
   - Assign to team member

---

## Post-Creation Setup

### 1. Create Project Board

```bash
gh project create --title "StakeEasy Roadmap" --body "Implementation roadmap"
```

Or via web interface:
- Go to: https://github.com/pythonpydev/total_bankroll/projects
- Click "New project"
- Choose "Board" or "Table" view

### 2. Add Issues to Project

```bash
# Add all issues with label to project
gh project item-add PROJECT_NUMBER --owner pythonpydev --content-id ISSUE_ID
```

### 3. Create Milestones

```bash
gh milestone create "Week 0: Deployment Safety" --due-date 2025-11-12
gh milestone create "Phase 1: Foundation" --due-date 2025-11-26
gh milestone create "Phase 2: Service Layer" --due-date 2025-12-24
# ... continue for all phases
```

### 4. Setup Issue Templates

Commit the issue template to your repository:
```bash
mkdir -p .github/ISSUE_TEMPLATE
# Create task.yml as shown above
git add .github/ISSUE_TEMPLATE/task.yml
git commit -m "Add task issue template"
git push
```

---

## Troubleshooting

### "Permission denied" error
- Verify your GitHub token has `repo` scope
- Check token hasn't expired
- Ensure you have write access to the repository

### "Label not found" error
- Run script with `--skip-labels` removed to create labels first
- Or create labels manually in GitHub settings

### Rate limiting
- GitHub API has rate limits (5,000 requests/hour for authenticated)
- Creating 50 issues should be fine
- If rate limited, wait an hour or use `--limit` to batch

### Issues created but not visible
- Check repository Issues tab
- Verify issues weren't created in wrong repository
- Check if issues are assigned to wrong milestone/project

---

## Tips

1. **Start small:** Use `--limit 5` to test before creating all issues
2. **Use dry-run:** Always run with `--dry-run` first
3. **Create labels first:** Run once with `--limit 0` to just create labels
4. **Version control:** Commit the script and this README to your repo
5. **Document token:** Store token securely (1Password, etc.)
6. **Automate closing:** Link commits to issues with "Closes #123" in commit messages

---

## Security Notes

⚠️ **Never commit your GitHub token to the repository!**

Store it securely:
```bash
# Option 1: Environment variable
export GITHUB_TOKEN="your_token_here"
python scripts/create_github_issues.py --token $GITHUB_TOKEN

# Option 2: .env file (add to .gitignore!)
echo "GITHUB_TOKEN=your_token_here" >> .env
echo ".env" >> .gitignore

# Then in script, use python-dotenv:
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
```

---

## Next Steps

After creating issues:

1. **Review all created issues** on GitHub
2. **Assign issues** to team members
3. **Add to project board** for visual tracking
4. **Set milestones** for each phase
5. **Start with TASK-0001** (Deployment Checklist)

---

**Need Help?**

- GitHub Issues docs: https://docs.github.com/en/issues
- PyGithub docs: https://pygithub.readthedocs.io/
- GitHub CLI docs: https://cli.github.com/manual/
