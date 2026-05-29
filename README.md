# Screen Cut

macOS 选区截图工具，自动复制到剪切板，`Cmd+V` 粘贴到任意文档。

## 使用方式

双击 `ScreenCut.app` 启动后自动进入截图模式 → 拖动选区 → 截图进剪切板。

App 会保持运行并显示状态窗口，可点击 **新建截图** 继续截取。

### 固定到程序坞

App 启动后图标会显示在程序坞中，**右键图标 → 选项 → 在程序坞中保留** 即可固定。

### 权限设置

首次运行需授权：**系统偏好设置 → 安全性与隐私 → 隐私 → 屏幕录制**，勾选 Screen Cut。

## 依赖

- macOS 系统（调用原生 `screencapture`）
- Python 3.6+（标准库 `tkinter`、`subprocess`、`tempfile`，无需 pip 安装）

## 重新构建

```bash
bash build_app.sh
```

## 技术要点

| 要点 | 实现 |
|------|------|
| Retina 分辨率 | `Info.plist` 声明 `NSHighResolutionCapable=true`，确保 2x 像素输出 |
| 截图 | `screencapture -i` 保存为临时 PNG（原始分辨率），AppleScript 写入剪切板 |
| 程序坞固定 | 截图后保持运行，Tkinter 状态窗口维持程序坞图标，右键即可固定 |
| Python 查找 | Shell 启动脚本按 conda → Homebrew → 系统优先级查找 python3 |
| UI | Tkinter 内置窗口，含"新建截图"和"退出"按钮 |
