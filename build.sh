#!/bin/bash
set -e
echo "🐍  Creating virtual environment..."
python3 -m venv .venv
echo "📦  Installing dependencies..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q
echo "🔨  Building..."
.venv/bin/pyinstaller \
  --onefile \
  --windowed \
  --name "FileConverter" \
  --hidden-import PyQt6 \
  --hidden-import PyQt6.QtWidgets \
  --hidden-import PyQt6.QtCore \
  --hidden-import PyQt6.QtGui \
  --hidden-import pdf2image \
  --hidden-import PIL \
  --hidden-import img2pdf \
  --collect-all PyQt6 \
  app.py
echo "✅  Done → dist/FileConverter.app"
