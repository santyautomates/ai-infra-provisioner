#!/bin/bash
# AI Infra Provisioner - Automated Codebase Optimizer
# This script removes cache files and temporary artifacts to keep the project lean.

PROJECT_DIR="/Users/santoshkumar/.gemini/antigravity/scratch/ai-infra-provisioner"

# Navigate to project directory
cd "$PROJECT_DIR" || exit

# 1. Remove Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 2. Remove OS-specific temp files
find . -name ".DS_Store" -delete

# 3. Clear generated deployment artifacts
if [ -d "generated_artifacts" ]; then
    rm -rf generated_artifacts/*
fi

# 4. Log the action
echo "[$(date)] Codebase optimization completed" >> "$PROJECT_DIR/optimization.log"
