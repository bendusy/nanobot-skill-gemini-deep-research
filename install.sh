#!/bin/bash
set -e

SKILL_DIR="$HOME/.nanobot/workspace/skills/gemini-cli"
echo "Installing Gemini CLI skill for nanobot..."

mkdir -p "$SKILL_DIR"
curl -sSL https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/nanobot-skill-gemini-cli/main/SKILL.md -o "$SKILL_DIR/SKILL.md"

echo "✅ Installation complete! The skill is now available at $SKILL_DIR"
