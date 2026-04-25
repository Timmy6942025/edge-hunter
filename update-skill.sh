#!/bin/bash
# Update edge-hunter skill to latest version
# Run: ~/.agents/skills/edge-hunter/update-skill.sh

set -e

SKILL_DIR=~/.agents/skills/edge-hunter

echo "🔄 Updating edge-hunter skill..."

cd "$SKILL_DIR" 2>/dev/null || {
    echo "❌ Error: Skill not found at $SKILL_DIR"
    echo "Run this first: git clone https://github.com/Timmy6942025/edge-hunter.git ~/.agents/skills/edge-hunter"
    exit 1
}

git pull origin main

echo "✅ Update complete!"
echo "📋 Latest changes:"
git log --oneline -3
