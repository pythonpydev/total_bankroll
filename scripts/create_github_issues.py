#!/usr/bin/env python3
"""
Script to create GitHub issues from tasks.md
Requires: pip install PyGithub
Usage: python scripts/create_github_issues.py --token YOUR_GITHUB_TOKEN
"""

import argparse
import re
from pathlib import Path
from github import Github

# Priority to label mapping
PRIORITY_MAP = {
    '🔴 P0': 'priority-p0-critical',
    '🟠 P1': 'priority-p1-high',
    '🟡 P2': 'priority-p2-medium',
    '🟢 P3': 'priority-p3-low',
}

# Phase to label mapping
PHASE_MAP = {
    'Week 0': 'phase-0-deployment',
    'Phase 1': 'phase-1-foundation',
    'Phase 2': 'phase-2-services',
    'Phase 3': 'phase-3-performance',
    'Phase 4': 'phase-4-frontend',
    'Phase 5': 'phase-5-database',
    'Phase 6': 'phase-6-api',
    'Phase 7': 'phase-7-monitoring',
    'Ongoing': 'maintenance',
}


def parse_tasks_file(file_path):
    """Parse tasks.md and extract task information."""
    content = Path(file_path).read_text()
    
    tasks = []
    current_phase = None
    current_task = None
    in_task = False
    task_content = []
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Detect phase headers
        if line.startswith('## Week 0:') or line.startswith('## Phase'):
            phase_match = re.search(r'## (Week 0|Phase \d+)', line)
            if phase_match:
                current_phase = phase_match.group(1)
        
        # Detect task headers
        if line.startswith('### TASK-'):
            # Save previous task if exists
            if current_task:
                current_task['body'] = '\n'.join(task_content)
                tasks.append(current_task)
            
            # Extract task ID
            task_id = line.split(':')[0].replace('### ', '').strip()
            task_title = ':'.join(line.split(':')[1:]).strip()
            
            current_task = {
                'id': task_id,
                'title': f"{task_id}: {task_title}",
                'phase': current_phase,
                'labels': [],
            }
            task_content = []
            in_task = True
            continue
        
        # Collect task content
        if in_task:
            # Stop at next task or section
            if line.startswith('###') or line.startswith('##'):
                in_task = False
                if current_task:
                    current_task['body'] = '\n'.join(task_content)
                    tasks.append(current_task)
                    current_task = None
                    task_content = []
                continue
            
            # Extract priority
            if '**Priority:**' in line:
                for emoji_priority, label in PRIORITY_MAP.items():
                    if emoji_priority in line:
                        current_task['labels'].append(label)
                        break
            
            # Add phase label
            if current_phase and current_task:
                phase_label = PHASE_MAP.get(current_phase)
                if phase_label and phase_label not in current_task['labels']:
                    current_task['labels'].append(phase_label)
            
            task_content.append(line)
    
    # Don't forget the last task
    if current_task:
        current_task['body'] = '\n'.join(task_content)
        tasks.append(current_task)
    
    return tasks


def create_github_labels(repo, dry_run=False):
    """Create standard labels in the repository."""
    labels_to_create = [
        # Priority labels
        ('priority-p0-critical', 'DC143C', 'Critical priority'),
        ('priority-p1-high', 'FF8C00', 'High priority'),
        ('priority-p2-medium', 'FFD700', 'Medium priority'),
        ('priority-p3-low', '32CD32', 'Low priority'),
        
        # Phase labels
        ('phase-0-deployment', '0E8A16', 'Deployment safety'),
        ('phase-1-foundation', '1D76DB', 'Foundation fixes'),
        ('phase-2-services', '5319E7', 'Service layer refactoring'),
        ('phase-3-performance', 'D93F0B', 'Performance improvements'),
        ('phase-4-frontend', 'FBCA04', 'Frontend modernization'),
        ('phase-5-database', '0052CC', 'Database migration'),
        ('phase-6-api', 'C5DEF5', 'API development'),
        ('phase-7-monitoring', 'BFD4F2', 'Observability'),
        ('maintenance', 'EDEDED', 'Ongoing maintenance'),
        
        # Type labels
        ('type-bug', 'D73A4A', 'Bug fix'),
        ('type-feature', '0075CA', 'New feature'),
        ('type-refactor', 'FEF2C0', 'Code refactoring'),
        ('type-test', 'C2E0C6', 'Test addition'),
        ('type-docs', '0366D6', 'Documentation'),
    ]
    
    existing_labels = {label.name for label in repo.get_labels()}
    
    for name, color, description in labels_to_create:
        if name not in existing_labels:
            if dry_run:
                print(f"[DRY RUN] Would create label: {name}")
            else:
                try:
                    repo.create_label(name=name, color=color, description=description)
                    print(f"✓ Created label: {name}")
                except Exception as e:
                    print(f"✗ Failed to create label {name}: {e}")
        else:
            print(f"  Label already exists: {name}")


def create_issues(repo, tasks, dry_run=False, limit=None):
    """Create GitHub issues from parsed tasks."""
    created_count = 0
    
    for i, task in enumerate(tasks):
        if limit and i >= limit:
            print(f"\n[Limit reached: {limit} issues]")
            break
        
        title = task['title']
        body = task['body']
        labels = task['labels']
        
        if dry_run:
            print(f"\n[DRY RUN] Would create issue:")
            print(f"  Title: {title}")
            print(f"  Labels: {', '.join(labels)}")
            print(f"  Body length: {len(body)} characters")
        else:
            try:
                issue = repo.create_issue(
                    title=title,
                    body=body,
                    labels=labels
                )
                print(f"✓ Created issue #{issue.number}: {title}")
                created_count += 1
            except Exception as e:
                print(f"✗ Failed to create issue '{title}': {e}")
    
    return created_count


def main():
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from tasks.md'
    )
    parser.add_argument(
        '--token',
        required=True,
        help='GitHub personal access token'
    )
    parser.add_argument(
        '--repo',
        default='pythonpydev/total_bankroll',
        help='Repository in format owner/repo (default: pythonpydev/total_bankroll)'
    )
    parser.add_argument(
        '--tasks-file',
        default='.specify/memory/tasks.md',
        help='Path to tasks.md file (default: .specify/memory/tasks.md)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating'
    )
    parser.add_argument(
        '--skip-labels',
        action='store_true',
        help='Skip creating labels'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of issues to create (useful for testing)'
    )
    
    args = parser.parse_args()
    
    # Initialize GitHub client
    print("Connecting to GitHub...")
    g = Github(args.token)
    
    try:
        repo = g.get_repo(args.repo)
        print(f"✓ Connected to repository: {repo.full_name}")
    except Exception as e:
        print(f"✗ Failed to connect to repository: {e}")
        return 1
    
    # Create labels if needed
    if not args.skip_labels:
        print("\nCreating/verifying labels...")
        create_github_labels(repo, dry_run=args.dry_run)
    
    # Parse tasks file
    print(f"\nParsing tasks from: {args.tasks_file}")
    tasks = parse_tasks_file(args.tasks_file)
    print(f"✓ Found {len(tasks)} tasks")
    
    # Create issues
    print("\nCreating issues...")
    created_count = create_issues(repo, tasks, dry_run=args.dry_run, limit=args.limit)
    
    if not args.dry_run:
        print(f"\n✓ Successfully created {created_count} issues")
    else:
        print(f"\n[DRY RUN] Would have created {len(tasks)} issues")
    
    return 0


if __name__ == '__main__':
    exit(main())
