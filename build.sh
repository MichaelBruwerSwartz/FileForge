#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  FileForge – Build Script
#  Run this once on your machine to produce a standalone app.
#  macOS  → dist/FileForge.app  (double-click to run)
#  Windows → dist/FileForge.exe (double-click to run)
# ─────────────────────────────────────────────────────────────

set -e

echo "📦  Installing dependencies..."
pip3 install -r requirements.txt

echo "🔨  Building standalone app..."

pyinstaller \
  --onefile \
  --windowed \
  --name "FileForge" \
  --hidden-import PIL \
  --hidden-import PIL.Image \
  --hidden-import img2pdf \
  --hidden-import cairosvg \
  --hidden-import cairocffi \
  --hidden-import cssselect2 \
  --hidden-import tinycss2 \
  app.py

echo ""
echo "✅  Build complete!"
echo ""
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "   → macOS app:  dist/FileForge.app"
  echo "   Just double-click it — no install needed."
else
  echo "   → Windows exe: dist/FileForge.exe"
  echo "   Just double-click it — no install needed."
fi
