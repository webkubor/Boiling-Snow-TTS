#!/bin/bash
set -e

# --- 核心配置 ---
PROJECT_NAME="boiling-snow-tts"
VERSION=$(grep -m 1 'version =' pyproject.toml | cut -d '"' -f 2)

echo "🏔️ Starting Release Process for $PROJECT_NAME v$VERSION..."
echo "=========================================================================="

# 1. 检查 Git 状态
if [[ -n $(git status -s) ]]; then
    echo "❌ Error: Working directory is not clean. Please commit your changes first."
    exit 1
fi

# 2. 自动打标 (Tag)
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "⚠️ Warning: Tag v$VERSION already exists. Skipping tagging."
else
    echo "🏷️ Creating Git Tag: v$VERSION..."
    git tag -a "v$VERSION" -m "Release v$VERSION"
    git push origin "v$VERSION"
fi

# 3. 清理并构建
echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info/

echo "📦 Building source and wheel packages..."
python3 -m build

# 4. 发布到 GitHub (需要 gh CLI)
if command -v gh &> /dev/null; then
    echo "🚀 Creating GitHub Release..."
    gh release create "v$VERSION" dist/* --title "Release v$VERSION" --notes "Release version $VERSION of Boiling-Snow-TTS."
else
    echo "⚠️ Warning: gh CLI not found. Please manually upload the files in dist/ to GitHub."
fi

echo "=========================================================================="
echo "✨ v$VERSION has been successfully packaged and tagged! ✨"
echo "Check your dist/ folder for the artifacts."
