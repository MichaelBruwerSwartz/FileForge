import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QFileDialog, QTextEdit, QProgressBar,
    QComboBox, QDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPalette, QColor

# ── Constants ─────────────────────────────────────────────────────────────────
SUPPORTED_PDFS   = {".pdf"}
SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

# ── Palette ───────────────────────────────────────────────────────────────────
LIGHT = dict(
    BG       = "#F5F4F2",
    BG_CARD  = "#EEECEA",
    BG_INPUT = "#E8E6E3",
    BORDER   = "#C8C4BE",
    ACCENT   = "#E80D0D",
    TEXT     = "#1C1917",
    TEXT_MID = "#6B6560",
    TEXT_DIM = "#9C9590",
    LOG_BG   = "#A09C98",
    LOG_TEXT = "#3C3835",
    LOG_OK   = "#2D7A4F",
    LOG_ERR  = "#B83232",
)
DARK = dict(
    BG       = "#1E1D1B",
    BG_CARD  = "#272523",
    BG_INPUT = "#2E2C2A",
    BORDER   = "#3D3A36",
    ACCENT   = "#E80D0D",
    TEXT     = "#E8E4DF",
    TEXT_MID = "#8C8680",
    TEXT_DIM = "#5C5852",
    LOG_BG   = "#141312",
    LOG_TEXT = "#A8A49F",
    LOG_OK   = "#6EBD8A",
    LOG_ERR  = "#E87070",
)

_DARK_MODE = False

def _palette():
    return DARK if _DARK_MODE else LIGHT

# Globals resolved by _resolve_palette() — never read these before build_stylesheet()
BG = TEXT = BG_CARD = BG_INPUT = BORDER = ACCENT = ""
TEXT_MID = TEXT_DIM = LOG_BG = LOG_TEXT = LOG_OK = LOG_ERR = ""

def _resolve_palette():
    global BG, TEXT, BG_CARD, BG_INPUT, BORDER, ACCENT
    global TEXT_MID, TEXT_DIM, LOG_BG, LOG_TEXT, LOG_OK, LOG_ERR
    p = _palette()
    BG = p["BG"];         TEXT = p["TEXT"];     BG_CARD = p["BG_CARD"]
    BG_INPUT = p["BG_INPUT"]; BORDER = p["BORDER"]; ACCENT = p["ACCENT"]
    TEXT_MID = p["TEXT_MID"]; TEXT_DIM = p["TEXT_DIM"]
    LOG_BG = p["LOG_BG"]; LOG_TEXT = p["LOG_TEXT"]
    LOG_OK = p["LOG_OK"]; LOG_ERR = p["LOG_ERR"]


# ── Stylesheet ────────────────────────────────────────────────────────────────
def build_stylesheet():
    _resolve_palette()
    return f"""
QMainWindow, QWidget#root {{
    background: {BG};
}}
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLabel#muted {{
    color: {TEXT_MID};
}}
QLabel#dim {{
    color: {TEXT_DIM};
    font-size: 12px;
}}

/* Drop zone labels */
QLabel#dropicon {{
    color: {ACCENT};
}}
QLabel#dropicon[state="ok"] {{
    color: {LOG_OK};
}}
QLabel#dropmain {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#dropsub {{
    color: {TEXT_DIM};
    font-size: 12px;
}}

/* Drop zone frame */
QFrame#dropzone {{
    background: {BG_CARD};
    border: 1.5px dashed {BORDER};
    border-radius: 6px;
}}
QFrame#dropzone:hover {{
    border-color: {ACCENT};
    background: {BG_INPUT};
}}
QFrame#dropzone[dragging="true"] {{
    border-color: {ACCENT};
    background: {BG_INPUT};
}}

/* Format pills */
QPushButton#pill {{
    background: {BG_CARD};
    color: {TEXT_MID};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 5px 18px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#pill:hover {{
    border-color: {ACCENT};
    color: {TEXT};
}}
QPushButton#pill[active=true] {{
    background: {BG_INPUT};
    border: 1.5px solid {ACCENT};
    color: {ACCENT};
}}

/* Mode dropdown */
QComboBox {{
    background: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 3px;
    padding: 6px 10px;
    font-size: 13px;
    font-weight: 600;
    min-width: 200px;
}}
QComboBox:hover {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
}}
QComboBox QAbstractItemView {{
    background: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    selection-background-color: {BG_INPUT};
    selection-color: {TEXT};
    outline: none;
}}

/* Primary convert button — solid accent fill */
QPushButton#cta {{
    background: {ACCENT};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 11px 0;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}
QPushButton#cta:hover {{
    background: #D42F0A;
}}
QPushButton#cta:pressed {{
    background: #BF2A09;
}}
QPushButton#cta:disabled {{
    color: {TEXT_DIM};
    background: {BG_CARD};
    border: 1.5px solid {BORDER};
}}

/* Progress bar */
QProgressBar {{
    background: {BG_INPUT};
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: right;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 2px;
}}

/* Log panel */
QTextEdit#log {{
    background: {LOG_BG};
    color: {LOG_TEXT};
    border: none;
    border-radius: 4px;
    font-family: "Menlo", "Consolas", monospace;
    font-size: 11px;
    padding: 10px;
}}

/* Ghost / clear button */
QPushButton#ghost {{
    background: transparent;
    color: {TEXT_DIM};
    border: none;
    font-size: 11px;
    padding: 2px 6px;
}}
QPushButton#ghost:hover {{
    color: {TEXT_MID};
}}

/* Theme toggle */
QPushButton#theme_toggle {{
    background: {BG_CARD};
    color: {TEXT_MID};
    border: 1px solid {BORDER};
    border-radius: 3px;
    font-size: 15px;
    padding: 1px 7px;
    min-width: 30px;
}}
QPushButton#theme_toggle:hover {{
    border-color: {ACCENT};
    color: {TEXT};
}}

QFrame#divider {{
    background: {BORDER};
    max-height: 1px;
    border: none;
}}
"""


# ── Worker ────────────────────────────────────────────────────────────────────

class Worker(QObject):
    log      = pyqtSignal(str, str)
    progress = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, mode, files, out_fmt):
        super().__init__()
        self.mode    = mode
        self.files   = files
        self.out_fmt = out_fmt

    def run(self):
        if self.mode == "pdf2img":
            self._pdf_to_images()
        else:
            self._images_to_pdf()
        self.finished.emit()

    def _pdf_to_images(self):
        try:
            from pdf2image import convert_from_path
        except ImportError:
            self.log.emit("ERROR: pip install pdf2image", "err")
            return
        total = len(self.files)
        total_pages = 0
        for fi, pdf in enumerate(self.files):
            self.log.emit(f"  {pdf.name}", "info")
            out_dir = pdf.parent / "converted"
            out_dir.mkdir(exist_ok=True)
            pages = convert_from_path(str(pdf), dpi=200)
            for i, page in enumerate(pages, 1):
                name = f"{pdf.stem}_p{i:03d}.{self.out_fmt.lower()}"
                if self.out_fmt.lower() in ("jpg", "jpeg"):
                    page = page.convert("RGB")
                page.save(str(out_dir / name))
                self.log.emit(f"  ✓ {name}", "ok")
                self.progress.emit((fi + i / len(pages)) / total)
            total_pages += len(pages)
        self.log.emit(f"\n  {total_pages} images saved → converted/", "ok")

    def _images_to_pdf(self):
        import img2pdf
        from PIL import Image
        base = self.files[0].parent
        out_path = base / "merged.pdf"
        tmp_files = []
        paths = []
        total = len(self.files)
        for i, f in enumerate(self.files, 1):
            img = Image.open(f).convert("RGB")
            tmp = base / f"_tmp_{f.stem}.png"
            img.save(str(tmp))
            paths.append(str(tmp))
            tmp_files.append(tmp)
            self.log.emit(f"  ✓ {f.name}", "ok")
            self.progress.emit(i / total)
        with open(out_path, "wb") as fh:
            fh.write(img2pdf.convert(paths))
        for t in tmp_files:
            t.unlink(missing_ok=True)
        self.log.emit(f"\n  Merged → {out_path.name}", "ok")


# ── Drop Zone ─────────────────────────────────────────────────────────────────

class DropZone(QFrame):
    filesDropped = pyqtSignal(list)
    clicked      = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("dropzone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        self.icon_lbl = QLabel("↓")
        self.icon_lbl.setObjectName("dropicon")
        self.icon_lbl.setFont(QFont("SF Pro Display", 28, QFont.Weight.Light))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_lbl = QLabel("Drop files or folder here")
        self.title_lbl.setObjectName("dropmain")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sub_lbl = QLabel("or click to browse")
        self.sub_lbl.setObjectName("dropsub")
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.sub_lbl)

    def set_state(self, icon, title, sub, icon_ok=False):
        self.icon_lbl.setText(icon)
        self.title_lbl.setText(title)
        self.sub_lbl.setText(sub)
        self.icon_lbl.setProperty("state", "ok" if icon_ok else "")
        self.icon_lbl.style().unpolish(self.icon_lbl)
        self.icon_lbl.style().polish(self.icon_lbl)

    def _set_dragging(self, on: bool):
        self.setProperty("dragging", "true" if on else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        self.clicked.emit()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._set_dragging(True)

    def dragLeaveEvent(self, e):
        self._set_dragging(False)

    def dropEvent(self, e):
        self._set_dragging(False)
        paths = [Path(u.toLocalFile()) for u in e.mimeData().urls()]
        self.filesDropped.emit(paths)


# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Converter")
        self.setMinimumSize(480, 600)
        self.resize(520, 660)

        self._files    = []
        self._mode     = "pdf2img"
        self._worker   = None
        self._thread   = None
        self._fmt_btns = {}

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        self._layout = QVBoxLayout(root)
        self._layout.setContentsMargins(28, 28, 28, 24)
        self._layout.setSpacing(0)

        self._build()

    def _build(self):
        L = self._layout

        # Title row + theme toggle
        title_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("File Converter")
        title.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        title_col.addWidget(title)

        sub = QLabel("Convert between PDF and image formats")
        sub.setObjectName("muted")
        sub.setFont(QFont("SF Pro Text", 12))
        title_col.addWidget(sub)

        title_row.addLayout(title_col)
        title_row.addStretch()

        self.theme_btn = QPushButton("\U0001f319")  # crescent moon
        self.theme_btn.setObjectName("theme_toggle")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setToolTip("Toggle dark / light mode")
        self.theme_btn.clicked.connect(self._toggle_theme)
        title_row.addWidget(self.theme_btn, alignment=Qt.AlignmentFlag.AlignTop)

        L.addLayout(title_row)
        L.addSpacing(18)
        L.addWidget(self._divider())
        L.addSpacing(18)

        # Mode selector
        mode_row = QHBoxLayout()
        mode_lbl = QLabel("Conversion")
        mode_lbl.setObjectName("muted")
        mode_lbl.setFont(QFont("SF Pro Text", 11, QFont.Weight.Medium))
        mode_row.addWidget(mode_lbl)
        mode_row.addSpacing(12)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("PDF  →  Image", "pdf2img")
        self.mode_combo.addItem("Image  →  PDF", "img2pdf")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        L.addLayout(mode_row)
        L.addSpacing(14)

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.clicked.connect(self._browse)
        self.drop_zone.filesDropped.connect(self._handle_drop)
        L.addWidget(self.drop_zone)
        L.addSpacing(6)

        # Selection info
        self.sel_lbl = QLabel("")
        self.sel_lbl.setObjectName("dim")
        self.sel_lbl.setFont(QFont("SF Pro Text", 11))
        L.addWidget(self.sel_lbl)
        L.addSpacing(16)

        # Format selector
        self.fmt_widget = QWidget()
        fmt_layout = QVBoxLayout(self.fmt_widget)
        fmt_layout.setContentsMargins(0, 0, 0, 0)
        fmt_layout.setSpacing(8)

        fmt_lbl = QLabel("Output Format")
        fmt_lbl.setObjectName("muted")
        fmt_lbl.setFont(QFont("SF Pro Text", 11, QFont.Weight.Medium))
        fmt_layout.addWidget(fmt_lbl)

        pill_row = QHBoxLayout()
        pill_row.setSpacing(8)
        for fmt in ["JPG", "PNG", "JPEG"]:
            btn = QPushButton(fmt)
            btn.setObjectName("pill")
            btn.setProperty("active", False)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, f=fmt: self._pick_fmt(f))
            pill_row.addWidget(btn)
            self._fmt_btns[fmt] = btn
        pill_row.addStretch()
        fmt_layout.addLayout(pill_row)
        L.addWidget(self.fmt_widget)
        L.addSpacing(20)

        self._pick_fmt("JPG")

        # Convert button
        self.go_btn = QPushButton("Convert PDFs to Images")
        self.go_btn.setObjectName("cta")
        self.go_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.go_btn.clicked.connect(self._start)
        L.addWidget(self.go_btn)
        L.addSpacing(10)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        L.addWidget(self.progress)
        L.addSpacing(16)

        # Log header
        log_hdr = QHBoxLayout()
        log_lbl = QLabel("LOG")
        log_lbl.setObjectName("dim")
        log_lbl.setFont(QFont("Menlo", 9, QFont.Weight.Bold))
        log_hdr.addWidget(log_lbl)
        log_hdr.addStretch()
        clr_btn = QPushButton("Clear")
        clr_btn.setObjectName("ghost")
        clr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clr_btn.clicked.connect(lambda: self.log_box.clear())
        log_hdr.addWidget(clr_btn)
        L.addLayout(log_hdr)
        L.addSpacing(4)

        # Log box
        self.log_box = QTextEdit()
        self.log_box.setObjectName("log")
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(120)
        L.addWidget(self.log_box)
        self._apply_log_palette()

    def _divider(self):
        d = QFrame()
        d.setObjectName("divider")
        d.setFrameShape(QFrame.Shape.HLine)
        d.setFixedHeight(1)
        return d

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_log_palette(self):
        pal = self.log_box.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(LOG_BG))
        pal.setColor(QPalette.ColorRole.Text, QColor(LOG_TEXT))
        self.log_box.setPalette(pal)

    def _toggle_theme(self):
        global _DARK_MODE
        _DARK_MODE = not _DARK_MODE
        self.theme_btn.setText("☀" if _DARK_MODE else "\U0001f319")  # sun : moon
        QApplication.instance().setStyleSheet(build_stylesheet())
        self._apply_log_palette()

    # ── Mode ──────────────────────────────────────────────────────────────────

    def _on_mode_change(self, idx):
        self._mode = self.mode_combo.itemData(idx)
        self._files = []
        self.sel_lbl.setText("")
        self.drop_zone.set_state("↓", "Drop files or folder here", "or click to browse")
        if self._mode == "pdf2img":
            self.fmt_widget.show()
            self.go_btn.setText("Convert PDFs to Images")
        else:
            self.fmt_widget.hide()
            self.go_btn.setText("Convert Images to PDF")

    # ── Selection ─────────────────────────────────────────────────────────────

    def _browse(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Browse")
        dlg.setFixedSize(260, 110)
        dlg.setStyleSheet(QApplication.instance().styleSheet())

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        lbl = QLabel("What would you like to select?")
        lbl.setObjectName("muted")
        layout.addWidget(lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        file_btn   = QPushButton("Files")
        folder_btn = QPushButton("Folder")
        for b in (file_btn, folder_btn):
            b.setObjectName("pill")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(34)
        btn_row.addWidget(file_btn)
        btn_row.addWidget(folder_btn)
        layout.addLayout(btn_row)

        choice = [None]

        def pick(kind):
            choice[0] = kind
            dlg.accept()

        file_btn.clicked.connect(lambda: pick("files"))
        folder_btn.clicked.connect(lambda: pick("folder"))

        dlg.exec()

        if choice[0] == "files":
            paths, _ = QFileDialog.getOpenFileNames(
                self, "Select files", "",
                "All supported (*.pdf *.jpg *.jpeg *.png);;"
                "PDF files (*.pdf);;"
                "Images (*.jpg *.jpeg *.png)",
            )
            if paths:
                self._handle_drop([Path(p) for p in paths])
        elif choice[0] == "folder":
            folder = QFileDialog.getExistingDirectory(self, "Select folder")
            if folder:
                self._handle_drop([Path(folder)])

    def _handle_drop(self, paths: list):
        all_files = []
        for p in paths:
            if p.is_dir():
                all_files.extend(
                    f for f in sorted(p.iterdir())
                    if f.is_file() and f.suffix.lower() in (SUPPORTED_PDFS | SUPPORTED_IMAGES)
                )
            elif p.is_file():
                all_files.append(p)

        if not all_files:
            self._log("No supported files found.", "err")
            return

        has_pdf = any(f.suffix.lower() in SUPPORTED_PDFS for f in all_files)
        has_img = any(f.suffix.lower() in SUPPORTED_IMAGES for f in all_files)

        if has_pdf and not has_img:
            self.mode_combo.setCurrentIndex(0)
            self._mode = "pdf2img"
            self._files = [f for f in all_files if f.suffix.lower() in SUPPORTED_PDFS]
        elif has_img and not has_pdf:
            self.mode_combo.setCurrentIndex(1)
            self._mode = "img2pdf"
            self._files = [f for f in all_files if f.suffix.lower() in SUPPORTED_IMAGES]
        else:
            if self._mode == "pdf2img":
                self._files = [f for f in all_files if f.suffix.lower() in SUPPORTED_PDFS]
            else:
                self._files = [f for f in all_files if f.suffix.lower() in SUPPORTED_IMAGES]

        n = len(self._files)
        noun = "PDF" if self._mode == "pdf2img" else "image"
        self.drop_zone.set_state(
            "✓",
            f"{n} {noun}{'s' if n != 1 else ''} ready",
            self._files[0].parent.name + "/",
            icon_ok=True,
        )
        self.sel_lbl.setText(
            "  " + "  ·  ".join(f.name for f in self._files[:3]) +
            (f"  +{n-3} more" if n > 3 else "")
        )

    # ── Format ────────────────────────────────────────────────────────────────

    def _pick_fmt(self, fmt):
        for f, b in self._fmt_btns.items():
            b.setProperty("active", f == fmt)
            b.style().unpolish(b)
            b.style().polish(b)
        self._fmt = fmt

    # ── Log ───────────────────────────────────────────────────────────────────

    def _log(self, msg, kind="info"):
        colors = {"ok": LOG_OK, "err": LOG_ERR, "info": LOG_TEXT}
        color  = colors.get(kind, LOG_TEXT)
        self.log_box.append(
            f'<span style="color:{color}; font-family:Menlo,monospace; font-size:11px;">{msg}</span>'
        )

    # ── Convert ───────────────────────────────────────────────────────────────

    def _start(self):
        if not self._files:
            self._log("Select files or a folder first.", "err")
            return
        if self._thread and self._thread.isRunning():
            return

        self.go_btn.setEnabled(False)
        self.progress.setValue(0)
        self.log_box.clear()
        self._log(f"Starting — {len(self._files)} file(s)", "info")
        self._log("─" * 36, "info")

        self._worker = Worker(self._mode, self._files, getattr(self, "_fmt", "JPG"))
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.log.connect(lambda m, k: self._log(m, k))
        self._worker.progress.connect(lambda v: self.progress.setValue(int(v * 100)))
        self._worker.finished.connect(self._done)
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def _done(self):
        self._thread.quit()
        self.go_btn.setEnabled(True)
        self.go_btn.setText(
            "Convert PDFs to Images" if self._mode == "pdf2img" else "Convert Images to PDF"
        )
        self.progress.setValue(100)


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)

    if sys.platform != "darwin":
        app.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet(build_stylesheet())

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
