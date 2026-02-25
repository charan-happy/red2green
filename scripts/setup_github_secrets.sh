#!/bin/bash
# Run this to add secrets to your GitHub repo via CLI
# Requires: gh CLI (https://cli.github.com/)

REPO="charan-happy/red2green"

echo "Setting GitHub Actions secrets..."
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY" --repo "$REPO"
gh secret set GITHUB_WEBHOOK_SECRET --body "$GITHUB_WEBHOOK_SECRET" --repo "$REPO"
echo "Secrets set! ✓"
