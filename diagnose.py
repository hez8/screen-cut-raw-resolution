#!/usr/bin/env python3
"""诊断截图分辨率问题"""
import subprocess
import sys
import struct
import os


def get_screen_info():
    """获取屏幕分辨率信息（逻辑分辨率和物理像素）"""
    result = subprocess.run(
        ["system_profiler", "SPDisplaysDataType"],
        capture_output=True, text=True
    )
    print("=== 显示器信息 ===")
    for line in result.stdout.split("\n"):
        line = line.strip()
        if any(kw in line for kw in ["Resolution", "Resolution", "UI Looks",
                                       "Framebuffer", "Retina", "Scale"]):
            print(f"  {line}")

    # 通过 Python 获取 NSScreen 信息
    try:
        import tkinter
        root = tkinter.Tk()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        print(f"\n  tkinter 报告的逻辑分辨率: {w}x{h} (points)")
    except Exception as e:
        print(f"  tkinter 获取失败: {e}")


def test_screencapture():
    """测试 screencapture 产生的实际图片分辨率"""
    test_file = "/tmp/screencut_resolution_test.png"
    subprocess.run(["screencapture", "-i", test_file])
    if not os.path.exists(test_file):
        print("\n⚠️  未生成截图文件（可能被取消了）")
        return

    # 读取 PNG 文件头获取尺寸
    with open(test_file, "rb") as f:
        f.read(16)  # skip PNG signature
        f.read(4)   # skip IHDR length
        f.read(4)   # skip IHDR tag
        w = struct.unpack(">I", f.read(4))[0]
        h = struct.unpack(">I", f.read(4))[0]

    file_size = os.path.getsize(test_file)
    print(f"\n=== 截图文件分析 ===")
    print(f"  文件: {test_file}")
    print(f"  像素尺寸: {w}x{h}")
    print(f"  文件大小: {file_size:,} bytes")
    print(f"  如果屏幕是 Retina 且逻辑分辨率为 1440x900，")
    print(f"  期望截图像素应为 2880x1800 (2x)。")
    print(f"  如果是 1x，则说明 screencapture 未以 Retina 分辨率运行。")

    os.remove(test_file)


def check_infoplist():
    """检查当前 Info.plist 是否包含 NSHighResolutionCapable"""
    plist = "/Users/apple/code/screen-cut/ScreenCut.app/Contents/Info.plist"
    if not os.path.exists(plist):
        print("\n⚠️  Info.plist 不存在")
        return

    with open(plist) as f:
        content = f.read()

    if "NSHighResolutionCapable" in content:
        print("\n✅ Info.plist 包含 NSHighResolutionCapable")
    else:
        print("\n❌ Info.plist 缺少 NSHighResolutionCapable = true")
        print("   这是导致 Retina 截图分辨率降为 1x 的可能原因！")
        print("   macOS 会将没有此标记的 App 视为低分辨率应用，")
        print("   screencapture 也会降级到 1x 像素输出。")


if __name__ == "__main__":
    get_screen_info()
    check_infoplist()
