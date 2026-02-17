#!/bin/bash

# Check if gh CLI is installed
if ! command -v gh &> /dev/null
then
    echo "gh CLI could not be found. Please install it or use the manual method."
    echo "Manual method:"
    echo "1. Create a repository on GitHub (e.g. mecobooks-ai-agent)."
    echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/mecobooks-ai-agent.git"
    echo "3. Run: git push -u origin main"
    exit 1
fi

# Create private repo
echo "Creating GitHub repository 'mecobooks-ai-agent'..."
gh repo create mecobooks-ai-agent --private --source=. --remote=origin --push

echo "Done! Code pushed to GitHub."
