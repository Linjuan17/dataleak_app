import sys
import os

# 修复路径（打包后）
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    sys.path.append(base_dir)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# 启动主程序
from main_app import app

if __name__ == "__main__":
    main()
