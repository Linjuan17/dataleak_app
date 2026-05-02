import os
import sys

def get_base_dir():
    """
    兼容 PyInstaller
    """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir():
    """
    写数据用（必须在 exe 外）
    """
    base = os.path.join(os.getcwd(), "DataLeakDetector_Data")
    os.makedirs(base, exist_ok=True)
    return base
