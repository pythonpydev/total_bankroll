#!/bin/bash
# Convenient wrapper script for completing tasks
# Usage: ./scripts/task_complete.sh TASK-0001 "Optional completion message"

set -e

TASK_ID=$1
MESSAGE=$2

if [ -z "$TASK_ID" ]; then
    echo "Usage: ./scripts/task_complete.sh TASK-0001 [message]"
    exit 1
fi

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable not set"
    echo "Export it first: export GITHUB_TOKEN='your_token_here'"
    exit 1
fi

echo "Completing task: $TASK_ID"

# Build comment if message provided
if [ -n "$MESSAGE" ]; then
    python scripts/close_github_issue.py \
        --task "$TASK_ID" \
        --comment "## ✅ Task Completed

**Completed:** $(date -u '+%Y-%m-%d %H:%M UTC')

$MESSAGE

This task has been completed and verified. Closing issue."
else
    python scripts/close_github_issue.py --task "$TASK_ID"
fi

echo ""
echo "✓ Task $TASK_ID marked as complete on GitHub"
