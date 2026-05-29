#!/usr/bin/env python3
"""Screen Cut - 截图工具，选区截图后自动复制到剪切板"""
import os
import subprocess
import sys
import tempfile
import tkinter as tk
import threading


def do_capture(status_label):
    """执行截图并复制到剪切板"""
    tmp = os.path.join(tempfile.gettempdir(), "screencut_tmp.png")

    try:
        result = subprocess.run(
            ["screencapture", "-i", tmp],
            capture_output=True,
        )
        if result.returncode != 0:
            status_label.config(text="已取消")
            return

        subprocess.run([
            "osascript", "-e",
            f'set the clipboard to (read (POSIX file "{tmp}") as «class PNGf»)',
        ], capture_output=True)

        os.remove(tmp)

        subprocess.run([
            "osascript", "-e",
            'display notification "截图已复制到剪切板" with title "Screen Cut"',
        ])
        status_label.config(text="截图已复制到剪切板")
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def main():
    root = tk.Tk()
    root.title("Screen Cut")
    root.geometry("280x150")
    root.resizable(False, False)

    label = tk.Label(
        root,
        text="截图已复制到剪切板",
        font=("Helvetica", 14),
        pady=20,
    )
    label.pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    # 用线程执行截图，避免阻塞 UI
    def new_screenshot():
        label.config(text="正在截图...")
        root.iconify()  # 最小化窗口以露出桌面
        root.after(200, lambda: threading.Thread(
            target=do_capture, args=(label,), daemon=True
        ).start())

    tk.Button(
        btn_frame, text="新建截图", command=new_screenshot,
        width=12, height=1,
    ).pack(side=tk.LEFT, padx=8)

    tk.Button(
        btn_frame, text="退出", command=root.destroy,
        width=12, height=1,
    ).pack(side=tk.LEFT, padx=8)

    tk.Label(
        root,
        text="右键程序坞图标 → 选项 → 在程序坞中保留",
        font=("Helvetica", 10),
        fg="gray",
        pady=5,
    ).pack()

    # 启动后自动触发截图
    root.after(300, new_screenshot)

    root.mainloop()
    sys.exit(0)


if __name__ == "__main__":
    main()
