import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
import img2pdf

# ── Conversion logic ──────────────────────────────────────────────────────────

SUPPORTED = {".pdf", ".jpg", ".jpeg", ".png", ".svg"}

def svg_to_pil(src: Path) -> Image.Image:
    try:
        import cairosvg, io
        png_bytes = cairosvg.svg2png(url=str(src), dpi=150)
        return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    except Exception as e:
        raise RuntimeError(f"SVG conversion failed: {e}")

def open_image(src: Path) -> Image.Image:
    if src.suffix.lower() == ".svg":
        return svg_to_pil(src)
    return Image.open(src)

def convert_file(src: Path, out_dir: Path, target_ext: str, log):
    stem = src.stem
    dst = out_dir / f"{stem}.{target_ext.lstrip('.')}"

    try:
        if target_ext == "pdf":
            if src.suffix.lower() == ".svg":
                img = svg_to_pil(src).convert("RGB")
                tmp = out_dir / f"_tmp_{stem}.png"
                img.save(tmp)
                with open(dst, "wb") as f:
                    f.write(img2pdf.convert(str(tmp)))
                tmp.unlink()
            elif src.suffix.lower() == ".pdf":
                import shutil; shutil.copy2(src, dst)
            else:
                with open(dst, "wb") as f:
                    f.write(img2pdf.convert(str(src)))
        else:
            img = open_image(src)
            if target_ext in ("jpg", "jpeg"):
                img = img.convert("RGB")
            elif target_ext == "png":
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            img.save(dst)
        log(f"✓  {src.name}  →  {dst.name}")
    except Exception as e:
        log(f"✗  {src.name}  —  {e}")


def convert_all_to_pdf(src_files: list[Path], out_dir: Path, stem: str, log):
    """Merge all images into one PDF."""
    dst = out_dir / f"{stem}_merged.pdf"
    paths = []
    tmp_files = []
    for src in src_files:
        if src.suffix.lower() == ".svg":
            img = svg_to_pil(src).convert("RGB")
            tmp = out_dir / f"_tmp_{src.stem}.png"
            img.save(tmp)
            paths.append(str(tmp))
            tmp_files.append(tmp)
        elif src.suffix.lower() == ".pdf":
            pass  # skip pdfs from merge
        else:
            paths.append(str(src))
    if paths:
        with open(dst, "wb") as f:
            f.write(img2pdf.convert(paths))
        for t in tmp_files:
            t.unlink()
        log(f"✓  Merged {len(paths)} files  →  {dst.name}")
    else:
        log("✗  No compatible files to merge into PDF")


# ── GUI ───────────────────────────────────────────────────────────────────────

BG       = "#0f0f13"
SURFACE  = "#1a1a24"
SURFACE2 = "#22222f"
ACCENT   = "#7c6af7"
ACCENT2  = "#a78bfa"
TEXT     = "#e8e6f0"
MUTED    = "#6b6880"
SUCCESS  = "#4ade80"
ERROR    = "#f87171"
RADIUS   = 12

FORMATS = ["pdf", "jpg", "png", "jpeg", "svg"]

# Emoji icons for formats
FORMAT_ICONS = {
    "pdf": "📄", "jpg": "🖼", "jpeg": "🖼", "png": "🖼", "svg": "✦"
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileForge")
        self.geometry("780x640")
        self.minsize(700, 580)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.folder_var   = tk.StringVar()
        self.target_var   = tk.StringVar(value="jpg")
        self.merge_var    = tk.BooleanVar(value=False)
        self.running      = False

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28, 0))

        tk.Label(hdr, text="FileForge", font=("Georgia", 26, "bold"),
                 fg=ACCENT2, bg=BG).pack(side="left")
        tk.Label(hdr, text="  · file converter", font=("Georgia", 14, "italic"),
                 fg=MUTED, bg=BG).pack(side="left", pady=6)

        sep = tk.Frame(self, bg=SURFACE2, height=1)
        sep.pack(fill="x", padx=32, pady=16)

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=32)

        # Folder picker
        self._folder_card(body)

        # Format selector
        self._format_card(body)

        # Convert button
        self._action_row(body)

        # Log
        self._log_card(body)

    def _folder_card(self, parent):
        card = self._card(parent, "  📁  Source Folder")
        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(fill="x", pady=(0, 4))

        entry = tk.Entry(inner, textvariable=self.folder_var,
                         font=("Courier New", 11), bg=SURFACE2, fg=TEXT,
                         insertbackground=ACCENT2, relief="flat",
                         bd=0, highlightthickness=1,
                         highlightcolor=ACCENT, highlightbackground=SURFACE2)
        entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=8)

        btn = self._pill_btn(inner, "Browse", self._browse, small=True)
        btn.pack(side="right", padx=(8, 0))

    def _format_card(self, parent):
        card = self._card(parent, "  🎯  Convert To")

        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill="x")

        self._fmt_btns = {}
        for fmt in FORMATS:
            b = tk.Label(row,
                         text=f"{FORMAT_ICONS.get(fmt,'·')} {fmt.upper()}",
                         font=("Helvetica", 11, "bold"),
                         fg=MUTED, bg=SURFACE2,
                         padx=16, pady=8, cursor="hand2")
            b.pack(side="left", padx=(0, 8), pady=4)
            b.bind("<Button-1>", lambda e, f=fmt: self._select_fmt(f))
            b.bind("<Enter>",    lambda e, w=b: w.configure(fg=ACCENT2) if w.cget("fg") == MUTED else None)
            b.bind("<Leave>",    lambda e, w=b, f=fmt: w.configure(fg=MUTED) if self.target_var.get() != f else None)
            self._fmt_btns[fmt] = b

        self._select_fmt("jpg")

        # Merge toggle (shown only for PDF target)
        self._merge_frame = tk.Frame(card, bg=SURFACE)
        self._merge_frame.pack(fill="x", pady=(10, 0))
        self._merge_cb = tk.Checkbutton(
            self._merge_frame,
            text="  Merge all files into one PDF",
            variable=self.merge_var,
            font=("Helvetica", 11),
            fg=TEXT, bg=SURFACE,
            selectcolor=ACCENT,
            activebackground=SURFACE,
            activeforeground=TEXT,
            relief="flat", bd=0,
            cursor="hand2"
        )
        self._merge_cb.pack(side="left")
        self._merge_frame.pack_forget()

    def _action_row(self, parent):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=16)
        self.convert_btn = self._pill_btn(row, "⚡  Convert", self._start)
        self.convert_btn.pack(side="left")

        self.status_lbl = tk.Label(row, text="", font=("Helvetica", 11),
                                   fg=MUTED, bg=BG)
        self.status_lbl.pack(side="left", padx=16)

    def _log_card(self, parent):
        card = self._card(parent, "  📋  Log")
        card.pack(fill="both", expand=True)

        self.log_text = tk.Text(card, bg=SURFACE2, fg=TEXT,
                                font=("Courier New", 10),
                                relief="flat", bd=0,
                                wrap="word", state="disabled",
                                highlightthickness=0)
        self.log_text.pack(fill="both", expand=True, pady=(4, 0))

        self.log_text.tag_config("ok",  foreground=SUCCESS)
        self.log_text.tag_config("err", foreground=ERROR)
        self.log_text.tag_config("inf", foreground=ACCENT2)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _card(self, parent, title=""):
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="x", pady=(0, 12))
        if title:
            tk.Label(wrap, text=title, font=("Helvetica", 10, "bold"),
                     fg=MUTED, bg=BG).pack(anchor="w", pady=(0, 6))
        card = tk.Frame(wrap, bg=SURFACE, padx=16, pady=12)
        card.pack(fill="x")
        return card

    def _pill_btn(self, parent, text, cmd, small=False):
        size = 10 if small else 12
        b = tk.Label(parent, text=text,
                     font=("Helvetica", size, "bold"),
                     fg="white", bg=ACCENT,
                     padx=18 if not small else 12,
                     pady=8 if not small else 5,
                     cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=ACCENT2))
        b.bind("<Leave>", lambda e: b.configure(bg=ACCENT))
        return b

    def _select_fmt(self, fmt):
        self.target_var.set(fmt)
        for f, b in self._fmt_btns.items():
            if f == fmt:
                b.configure(fg="white", bg=ACCENT)
            else:
                b.configure(fg=MUTED, bg=SURFACE2)
        if fmt == "pdf":
            self._merge_frame.pack(fill="x", pady=(10, 0))
        else:
            self._merge_frame.pack_forget()

    def _browse(self):
        folder = filedialog.askdirectory(title="Select source folder")
        if folder:
            self.folder_var.set(folder)

    def _log(self, msg):
        self.log_text.configure(state="normal")
        tag = "ok" if msg.startswith("✓") else "err" if msg.startswith("✗") else "inf"
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, msg, color=MUTED):
        self.status_lbl.configure(text=msg, fg=color)

    # ── Conversion ────────────────────────────────────────────────────────────

    def _start(self):
        if self.running:
            return
        folder = self.folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("No folder", "Please select a valid folder first.")
            return

        target = self.target_var.get()
        merge  = self.merge_var.get() and target == "pdf"

        src_path = Path(folder)
        files = [f for f in src_path.iterdir()
                 if f.is_file() and f.suffix.lower() in SUPPORTED]

        if not files:
            messagebox.showinfo("Nothing to convert",
                                "No supported files found in that folder.")
            return

        out_dir = src_path.parent / f"{src_path.name}_converted"
        out_dir.mkdir(exist_ok=True)

        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        self.running = True
        self.convert_btn.configure(bg=MUTED)
        self._set_status("Converting…", ACCENT2)

        def run():
            self._log(f"◆ Output → {out_dir}")
            self._log(f"◆ Files found: {len(files)}")
            self._log("─" * 48)
            if merge:
                convert_all_to_pdf(files, out_dir, src_path.name, self._log)
            else:
                for f in sorted(files):
                    convert_file(f, out_dir, target, self._log)
            self._log("─" * 48)
            self._log(f"◆ Done!  →  {out_dir}")
            self.running = False
            self.after(0, lambda: self.convert_btn.configure(bg=ACCENT))
            self.after(0, lambda: self._set_status("Done ✓", SUCCESS))

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
