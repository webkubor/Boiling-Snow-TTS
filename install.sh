#!/bin/bash
set -e

echo "⚔️ Welcome to Boiling-Snow-TTS Setup / 欢迎使用沸腾之雪武侠配音引擎安装向导 ⚔️"
echo "=========================================================================="

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Error: Python 3 could not be found. Please install Python 3.9+."
    exit 1
fi

echo "1. Creating Python Virtual Environment (.venv)..."
python3 -m venv .venv

echo "2. Activating Virtual Environment..."
source .venv/bin/activate

echo "3. Upgrading pip and setuptools..."
pip install --upgrade pip
# Install a specific version of setuptools to avoid modelscope dependency issues
pip install "setuptools<70"

echo "4. Installing project dependencies..."
pip install -e .
pip install pydub modelscope

echo "5. Downloading Base Models (This might take a while depending on your network)..."
# Download the lightweight 0.6B model for quick tests
python -m modelscope.cli.cli download --model Qwen/Qwen3-TTS-12Hz-0.6B-Base --local_dir ./models/Base-0.6B
# Download the full 1.7B model for high quality and emotion control
python -m modelscope.cli.cli download --model Qwen/Qwen3-TTS-12Hz-1.7B-Base --local_dir ./models/Base-1.7B

echo "6. Environment Setup Complete! / 环境配置完成！"
echo ""
echo "To start generating audio, run / 开始生成配音请执行:"
echo "source .venv/bin/activate"
echo "python boiling_snow_clone.py"
echo ""
echo "✨ May the Wuxia spirit guide your voice! / 雪落江湖，热血难凉！ ✨"
