#!/bin/bash
# ============================================================
# PetReel Studio — Repo Reorganizer
# Run this inside your cloned Reel_creator folder:
#   git clone https://github.com/Satyajitdutta/Reel_creator.git
#   cd Reel_creator
#   bash fix_repo.sh
# ============================================================

set -e

echo "📁 Creating folder structure..."
mkdir -p backend/pipeline
mkdir -p frontend/src

echo "📦 Moving Python backend files → backend/"
# Core backend files
for f in main.py config.py media_manager.py Procfile .env.example \
          nixpacks.toml railway.toml requirements.txt \
          client_secrets.json.template; do
    [ -f "$f" ] && mv "$f" backend/ && echo "  ✓ $f"
done

# Pipeline subfolder files
for f in vision.py planner.py designer.py tts_engine.py \
          video_engine.py uploader.py audioop_shim.py; do
    [ -f "$f" ] && mv "$f" backend/pipeline/ && echo "  ✓ pipeline/$f"
done
[ -f "pipeline/__init__.py" ] && mv "pipeline/__init__.py" backend/pipeline/

echo "🎨 Moving frontend files → frontend/"
for f in index.html package.json package-lock.json vite.config.ts \
          tsconfig.json tailwind.config.js postcss.config.js \
          .env.example; do
    [ -f "$f" ] && mv "$f" frontend/ && echo "  ✓ $f"
done

# src/ folder
for f in App.tsx api.ts main.tsx index.css; do
    [ -f "$f" ] && mv "$f" frontend/src/ && echo "  ✓ src/$f"
    [ -f "src/$f" ] && mv "src/$f" frontend/src/ && echo "  ✓ src/$f"
done

# Move any remaining .tsx/.ts/.css to frontend/src/
for f in *.tsx *.ts; do
    [ -f "$f" ] && mv "$f" frontend/src/ && echo "  ✓ src/$f"
done

echo "✅ Done reorganizing. Pushing to GitHub..."
git add -A
git status
