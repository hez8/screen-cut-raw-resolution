#!/bin/bash
# Build ScreenCut.app - 将 Python 脚本打包为 macOS 应用
set -e

APP_NAME="ScreenCut"
APP_DIR="${APP_NAME}.app"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> 清理旧版本..."
rm -rf "${APP_DIR}"

echo "==> 创建 .app 目录结构..."
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources"

echo "==> 复制脚本..."
cp "${SCRIPT_DIR}/screen_cut.py" "${APP_DIR}/Contents/Resources/screen_cut.py"

echo "==> 创建启动脚本 (自动查找 Python)..."
cat > "${APP_DIR}/Contents/MacOS/${APP_NAME}" << 'SHELL'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
PY_SCRIPT="${DIR}/../Resources/screen_cut.py"

# 按优先级查找 python3
for py in \
    "${HOME}/miniconda3/envs/py39/bin/python3" \
    "${HOME}/anaconda3/envs/py39/bin/python3" \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /usr/bin/python3; do
    if [ -x "$py" ]; then
        exec "$py" "$PY_SCRIPT"
    fi
done

echo "错误: 找不到 python3" >&2
exit 1
SHELL
chmod +x "${APP_DIR}/Contents/MacOS/${APP_NAME}"

echo "==> 创建 Info.plist..."
cat > "${APP_DIR}/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>ScreenCut</string>
    <key>CFBundleDisplayName</key>
    <string>Screen Cut</string>
    <key>CFBundleIdentifier</key>
    <string>com.screencut.app</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>ScreenCut</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
PLIST

echo "==> 完成! ${APP_DIR} 已生成"
echo "    双击 ${APP_DIR} 即可运行，可拖入程序坞固定"
echo ""
echo "    首次运行需要授予「屏幕录制」权限："
echo "    系统偏好设置 → 安全性与隐私 → 隐私 → 屏幕录制"
