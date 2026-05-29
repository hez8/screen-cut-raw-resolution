#!/usr/bin/env python3
"""Screen Cut — cross-platform screenshot tool (macOS & Windows)."""
import os
import platform
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import font as tkfont

SYSTEM = platform.system()  # "Darwin" | "Windows"


# ── Windows DPI awareness (must run before any tkinter call) ──────────
if SYSTEM == "Windows":
    import ctypes
    try:
        # Windows 10 1703+
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PER_MONITOR_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ── Platform-specific capture ─────────────────────────────────────────
def capture_macos():
    """macOS: native screencapture with crosshair, returns temp PNG path or None."""
    tmp = os.path.join(tempfile.gettempdir(), "screencut_tmp.png")
    result = subprocess.run(
        ["screencapture", "-i", tmp],
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return tmp


def capture_windows(root):
    """
    Windows: full-screen PIL capture, then Tkinter region-selection overlay.
    Returns cropped temp PNG path or None (if cancelled).
    """
    from PIL import Image, ImageGrab, ImageTk

    # 1. grab full screen into memory
    full_img = ImageGrab.grab()  # RGBA, native pixels (DPI-aware)

    # 2. show fullscreen overlay for region selection
    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-topmost", True)
    overlay.configure(cursor="crosshair")
    overlay.focus_force()

    # Convert PIL image to Tkinter-compatible PhotoImage
    tk_img = ImageTk.PhotoImage(full_img)

    canvas = tk.Canvas(overlay, highlightthickness=0, bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_image(0, 0, image=tk_img, anchor=tk.NW)

    # Selection state
    sel = {"start_x": None, "start_y": None, "rect": None, "confirmed": False}

    def on_press(event):
        sel["start_x"] = event.x
        sel["start_y"] = event.y
        if sel["rect"]:
            canvas.delete(sel["rect"])
        sel["rect"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="red", width=2, dash=(4, 2),
        )

    def on_drag(event):
        if sel["rect"]:
            canvas.coords(
                sel["rect"],
                sel["start_x"], sel["start_y"], event.x, event.y,
            )

    def on_release(event):
        sel["confirmed"] = True
        sel["end_x"] = event.x
        sel["end_y"] = event.y
        overlay.destroy()

    def on_escape(_event):
        sel["confirmed"] = False
        overlay.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    overlay.bind("<Escape>", on_escape)

    # Block until overlay closes
    root.wait_window(overlay)

    if not sel.get("confirmed") or sel["rect"] is None:
        return None

    # Normalise coordinates (x1 < x2, y1 < y2)
    x1, y1 = sel["start_x"], sel["start_y"]
    x2, y2 = sel["end_x"], sel["end_y"]
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # 3. crop and save
    if x2 - x1 < 5 or y2 - y1 < 5:  # too small, treat as cancel
        return None

    cropped = full_img.crop((x1, y1, x2, y2))
    tmp = os.path.join(tempfile.gettempdir(), "screencut_tmp.png")
    cropped.save(tmp, "PNG")
    return tmp


# ── Platform-specific clipboard ───────────────────────────────────────
def copy_to_clipboard(image_path):
    """Copy PNG image to system clipboard."""
    if SYSTEM == "Darwin":
        subprocess.run([
            "osascript", "-e",
            f'set the clipboard to (read (POSIX file "{image_path}") as «class PNGf»)',
        ], capture_output=True)

    elif SYSTEM == "Windows":
        from PIL import Image
        img = Image.open(image_path)
        bmp_path = os.path.join(tempfile.gettempdir(), "screencut_tmp.bmp")
        img.save(bmp_path, "BMP")

        ps = (
            f'Add-Type -AssemblyName System.Windows.Forms;'
            f'Add-Type -AssemblyName System.Drawing;'
            f'$img=[System.Drawing.Image]::FromFile("{bmp_path}");'
            f'[System.Windows.Forms.Clipboard]::SetImage($img);'
            f'$img.Dispose()'
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        os.remove(bmp_path)


def notify(msg):
    """Send a system notification."""
    if SYSTEM == "Darwin":
        subprocess.run([
            "osascript", "-e",
            f'display notification "{msg}" with title "Screen Cut"',
        ])
    elif SYSTEM == "Windows":
        # Use a brief Tkinter toplevel or toast — keep it light
        pass  # status label already shows the message


# ── Main UI ───────────────────────────────────────────────────────────
def do_capture(status_label, root):
    """Run capture → clipboard pipeline; called from worker thread."""
    try:
        if SYSTEM == "Darwin":
            png_path = capture_macos()
        else:
            png_path = capture_windows(root)

        if png_path is None:
            root.after(0, lambda: status_label.config(text="已取消"))
            return

        copy_to_clipboard(png_path)
        os.remove(png_path)
        notify("截图已复制到剪切板")
        root.after(0, lambda: status_label.config(text="截图已复制到剪切板"))
    except Exception as exc:
        root.after(0, lambda: status_label.config(text=f"错误: {exc}"))


def main():
    root = tk.Tk()
    root.title("Screen Cut")
    root.geometry("300x160")
    root.resizable(False, False)

    # Ensure window appears in a sensible spot
    try:
        root.eval("tk::PlaceWindow . center")
    except Exception:
        pass

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=12)

    label = tk.Label(
        root, text="", font=("Helvetica", 14), pady=20,
    )
    label.pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    def _bg_capture():
        label.config(text="正在截图...")
        root.iconify()  # minimize so desktop is visible
        root.after(200, lambda: threading.Thread(
            target=do_capture, args=(label, root), daemon=True
        ).start())

    tk.Button(
        btn_frame, text="新建截图", command=_bg_capture,
        width=12, height=1,
    ).pack(side=tk.LEFT, padx=8)

    tk.Button(
        btn_frame, text="退出", command=root.destroy,
        width=12, height=1,
    ).pack(side=tk.LEFT, padx=8)

    hint_text = (
        "右键任务栏图标 → 固定到任务栏"
        if SYSTEM == "Windows"
        else "右键程序坞图标 → 选项 → 在程序坞中保留"
    )
    tk.Label(
        root, text=hint_text, font=("Helvetica", 10), fg="gray", pady=5,
    ).pack()

    root.after(400, _bg_capture)
    root.mainloop()
    sys.exit(0)


if __name__ == "__main__":
    main()
