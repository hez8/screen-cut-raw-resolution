# Screen Cut

跨平台选区截图工具 (macOS / Windows)，截图自动复制到剪切板，`Ctrl+V` / `Cmd+V` 粘贴到任意文档。

## 安装与使用

### macOS

```bash
# 构建 .app（首次）
bash build_app.sh
```

双击 `ScreenCut.app` 启动，自动进入截图模式 → 拖动选区 → 进剪切板。

固定到程序坞：App 启动后右键程序坞图标 → **选项 → 在程序坞中保留**。

首次使用需授权：**系统偏好设置 → 安全性与隐私 → 隐私 → 屏幕录制**，勾选 Screen Cut。

### Windows

```bash
# 安装依赖
pip install Pillow

# 启动（无控制台窗口）
pythonw screen_cut.py
```

或直接双击 `run.bat`。

固定到任务栏：App 启动后右键任务栏图标 → **固定到任务栏**。

## 依赖

| 平台 | 依赖 |
|------|------|
| macOS | Python 3.6+（标准库，无需 pip） |
| Windows | Python 3.6+、`pip install Pillow` |

## 项目结构

```
screen_cut.py       # 主程序（跨平台）
screen_cut.pyw      # Windows 双击启动器（无控制台）
run.bat             # Windows 备选启动脚本
build_app.sh        # macOS .app 构建脚本
diagnose.py         # 分辨率诊断工具
```

## 技术要点

| 要点 | macOS | Windows |
|------|-------|---------|
| 截图 | `screencapture -i` 原生十字光标 | `PIL.ImageGrab` + Tkinter 选区叠加层 |
| 剪切板 | AppleScript `«class PNGf»` | PowerShell + BMP |
| 高 DPI | `NSHighResolutionCapable` | `SetProcessDpiAwareness` |
| 状态窗口 | Tkinter | Tkinter |
| 零依赖 | 仅标准库 | 仅增加 Pillow |
