# FileForge – File Converter

Convert between PDF, JPG, PNG, JPEG, and SVG with a clean GUI.

## For end users (no install needed)
Just double-click the app you were given:
- **macOS**: `FileForge.app`
- **Windows**: `FileForge.exe`

---

## For developers – building the app yourself

### Requirements
- Python 3.10+
- pip

### macOS / Linux
```bash
chmod +x build.sh
./build.sh
```
The app will be at `dist/FileForge.app`.

### Windows
```powershell
pip install -r requirements.txt
pyinstaller --onefile --windowed --name FileForge --hidden-import PIL --hidden-import img2pdf --hidden-import cairosvg app.py
```
The exe will be at `dist\FileForge.exe`.

> **Note for macOS**: If you see "unverified developer" on first launch,
> right-click the app → Open → Open anyway.

---

## Supported conversions
| From \ To | PDF | JPG | PNG | JPEG | SVG |
|-----------|-----|-----|-----|------|-----|
| PDF       | –   | ✓   | ✓   | ✓    | –   |
| JPG/JPEG  | ✓   | –   | ✓   | –    | –   |
| PNG       | ✓   | ✓   | –   | ✓    | –   |
| SVG       | ✓   | ✓   | ✓   | ✓    | –   |

**Merge to PDF**: When converting to PDF, tick "Merge all files into one PDF"
to combine everything into a single document.

Output is always saved to a new folder named `{original_folder}_converted`.
