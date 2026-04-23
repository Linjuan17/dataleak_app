import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import subprocess
import os
import sys
import time
import requests
import time
#日志接口
logger = None
report_callback = None


def set_logger(func):
    global logger
    logger = func


def set_report_callback(func):
    global report_callback
    report_callback = func

dashboard_callback = None

def set_dashboard_callback(cb):
    global dashboard_callback
    dashboard_callback = cb

# ================= 路径 =================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()

SCREEN_RECORD = os.path.join(BASE_DIR, "ScreenMonitor", "winows_monitor", "recordings")
RISK_DIR = os.path.join(BASE_DIR, "3-RiskHunter")

server_process = None
current_session = None

# ================= Python =================
def get_python():
    if getattr(sys, 'frozen', False):
        return "python"
    return sys.executable

# ================= 获取最新session =================
def get_latest_session():
    if not os.path.exists(SCREEN_RECORD):
        return None

    sessions = []

    for d in os.listdir(SCREEN_RECORD):
        if d.startswith("session_"):
            full = os.path.join(SCREEN_RECORD, d)
            if os.path.isdir(full):
                sessions.append(full)

    if not sessions:
        return None

    latest = max(sessions, key=os.path.getmtime)
    return latest

# ================= 启动监控 =================
import requests


def start_monitor():
    global server_process

    server_process = subprocess.Popen(
        [get_python(), "web_server.py"],
        cwd=os.path.join(BASE_DIR, "ScreenMonitor", "winows_monitor")
    )
    for _ in range(10):
        try:
            r = requests.post("http://127.0.0.1:5000/api/start", timeout=1)
            if logger:
                logger("✅ 监控已启动")
            return
        except:
            time.sleep(0.5)

    if logger:
        logger("❌ 启动失败")


# ================= 停止监控 =================
def stop_monitor():
    global current_session

    try:
        if logger:
            logger("🛑 正在停止监控...")

        r = requests.post("http://127.0.0.1:5000/api/stop", timeout=3)

    except Exception as e:
        if logger:
            logger(f"❌ 停止失败: {str(e)}")
        return

    # ⭐ 等待 session 生成（核心修复）
    import time

    session = None
    for i in range(10):  # 最多等10秒
        time.sleep(1)
        session = get_latest_session()

        if session:
            break

    if not session:
        if logger:
            logger("❌ 等待超时，未生成录制数据")
        return

    current_session = session

    if logger:
        logger(f"✅ session设置成功: {session}")

# ================= 数据分析 =================
def analyze():
    print("=== analyze 被调用 ===")

    session = get_latest_session()   # ⭐ 每次直接从磁盘拿

    print("自动获取session:", session)

    if not session:
        if logger:
            logger("❌ 没有录制数据，请先监控")
        return

    try:
        import shutil

        session_name = os.path.basename(session)
        record_id = session_name.replace("session_", "record_")

        dst_root = os.path.join(RISK_DIR, "recordings","stage1")
        os.makedirs(dst_root, exist_ok=True)

        dst_base = os.path.join(dst_root, record_id)

        if os.path.exists(dst_base):
            shutil.rmtree(dst_base)

        dst_final = os.path.join(dst_base, session_name)

        print("复制:", session, "→", dst_final)

        shutil.copytree(session, dst_final)

        if logger:
            logger("📁 数据复制完成")

        result = subprocess.run(
            [get_python(), "run_upload_detection.py", record_id],
            cwd=RISK_DIR
        )

        if result.returncode != 0:
            if logger:
                logger("❌ 分析失败")
            return

        if logger:
            logger("✅ 分析完成")

        show_report()

    except Exception as e:
        print("异常:", e)
        if logger:
            logger(str(e))
# ================= 查看报告 =================
def show_report():
    if not current_session:
        if logger:
            logger("❌ 请先分析")
        return

    session_name = os.path.basename(current_session)
    record_id = session_name.replace("session_", "record_")

    base = os.path.join(RISK_DIR, "recordings", record_id, "results")

    if not os.path.exists(base):
        if logger:
            logger("❌ 没有结果")
        return

    subdirs = sorted(os.listdir(base))
    latest = os.path.join(base, subdirs[-1])
    report = os.path.join(latest, "report.txt")

    with open(report, "r", encoding="utf-8") as f:
        content = f.read()

    if report_callback:
        report_callback(content)


def main():
    import UI
    UI.run()


if __name__ == "__main__":
    main()