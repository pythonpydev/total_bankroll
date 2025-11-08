#!/usr/bin/env python3
"""
Script to close GitHub issues when tasks are completed.
Requires: pip install PyGithub
Usage: python scripts/close_github_issue.py --task TASK-0001 --token YOUR_GITHUB_TOKEN
"""

import argparse
import sys
from datetime import datetime
from github import Github


def find_issue_by_task_id(repo, task_id):
    """Find GitHub issue matching the task ID."""
    # Search for issue with task ID in title
    issues = repo.get_issues(state='open')
    
    for issue in issues:
        if issue.title.startswith(f"{task_id}:"):
            return issue
    
    return None


def close_task_issue(repo, task_id, comment=None, dry_run=False):
    """Close a GitHub issue for a completed task."""
    print(f"Looking for issue with task ID: {task_id}")
    
    issue = find_issue_by_task_id(repo, task_id)
    
    if not issue:
        print(f"✗ No open issue found for {task_id}")
        return False
    
    print(f"✓ Found issue #{issue.number}: {issue.title}")
    
    # Prepare completion comment
    if not comment:
        comment = f"""## ✅ Task Completed

**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

This task has been completed and verified. Closing issue.
"""
    
    if dry_run:
        print(f"\n[DRY RUN] Would close issue #{issue.number}")
        print(f"[DRY RUN] Would add comment:\n{comment}")
        return True
    
    try:
        # Add completion comment
        issue.create_comment(comment)
        print(f"✓ Added completion comment to issue #{issue.number}")
        
        # Close the issue
        issue.edit(state='closed')
        print(f"✓ Closed issue #{issue.number}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to close issue: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Close GitHub issue for completed task'
    )
    parser.add_argument(
        '--task',
        required=True,
        help='Task ID (e.g., TASK-0001)'
    )
    parser.add_argument(
        '--token',
        help='GitHub personal access token (or use GITHUB_TOKEN env var)'
    )
    parser.add_argument(
        '--repo',
        default='pythonpydev/total_bankroll',
        help='Repository in format owner/repo'
    )
    parser.add_argument(
        '--comment',
        help='Custom completion comment'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    args = parser.parse_args()
    
    # Get token from args or environment
    import os
    token = args.token or os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("✗ GitHub token required. Use --token or set GITHUB_TOKEN env var")
        return 1
    
    # Initialize GitHub client
    print("Connecting to GitHub...")
    g = Github(token)
    
    try:
        repo = g.get_repo(args.repo)
        print(f"✓ Connected to repository: {repo.full_name}")
    except Exception as e:
        print(f"✗ Failed to connect to repository: {e}")
        return 1
    
    # Close the task issue
    success = close_task_issue(
        repo,
        args.task,
        comment=args.comment,
        dry_run=args.dry_run
    )
    
    if success:
        if not args.dry_run:
            print(f"\n✓ Successfully closed {args.task}")
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
