#!/bin/bash
export PATH=$PATH:/usr/local/bin:/usr/bin
cd /Users/tuankth/.gemini/antigravity/scratch/video_project
echo "Start Push..."
# Token removed for security - use git credential manager
git add .
git commit -m "Manual Push Verify Dashboard $(date)"
git push origin main
echo "End Push."
