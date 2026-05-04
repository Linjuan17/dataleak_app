#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 确保根目录在路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 环境缩放设置
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from app import MainWindow
from load import LoginPage   # 从 load.py 导入登录界面


def main():
    # 修复 DPI 感知问题
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"DPI Awareness adjustment skipped: {e}")

    app = QApplication(sys.argv)
    app.setApplicationName("DataLeakDetector")
    app.setOrganizationName("WHU_NISPLab")

    font = QFont()
    font.setFamilies(["Microsoft YaHei", "PingFang SC", "SimHei", "sans-serif"])
    font.setPointSize(10)
    app.setFont(font)

    # 显示登录窗口
    login_window = LoginPage()
    login_window.resize(1400, 900)
    login_window.show()

    # 主窗口引用（延迟创建）
    main_window = None

    def on_login_success():
        nonlocal main_window
        login_window.close()
        main_window = MainWindow()
        main_window.show()

    login_window.login_success.connect(on_login_success)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()