import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import subprocess
import os
import sys
import time

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

    # 启动后端
    server_process = subprocess.Popen(
        [get_python(), "web_server.py"],
        cwd=os.path.join(BASE_DIR, "ScreenMonitor", "winows_monitor")
    )

    time.sleep(3)  # 等Flask启动

    try:
        r = requests.post("http://127.0.0.1:5000/api/start")
        print(r.text)
        messagebox.showinfo("提示", "监控已真正启动")
    except:
        messagebox.showerror("错误", "启动失败（可能没管理员权限）")


# ================= 停止监控 =================
def stop_monitor():
    global current_session

    try:
        r = requests.post("http://127.0.0.1:5000/api/stop")
        print(r.text)
    except:
        messagebox.showerror("错误", "停止失败")
        return

    # 等待录制写盘
    time.sleep(5)

    # 获取session
    session = get_latest_session()

    if not session:
        messagebox.showerror("错误", "没有生成录制数据（权限问题）")
        return

    current_session = session

    print(f"当前session: {session}")

    messagebox.showinfo("提示", f"录制完成\n{session}")

# ================= 数据分析 =================
def analyze():
    if not current_session:
        messagebox.showerror("错误", "请先录制")
        return

    try:
        progress.start()

        # ⭐生成record_id
        session_name = os.path.basename(current_session)
        record_id = session_name.replace("session_", "record_")

        print(f"分析: {record_id}")

        # ⭐复制到RiskHunter
        dst_base = os.path.join(RISK_DIR, "recordings", record_id)

        if os.path.exists(dst_base):
            import shutil
            shutil.rmtree(dst_base)

        import shutil
        shutil.copytree(
            current_session,
            os.path.join(dst_base, session_name)
        )

        # ⭐执行分析
        result = subprocess.run(
            [get_python(), "run_upload_detection.py", record_id],
            cwd=RISK_DIR
        )

        progress.stop()

        if result.returncode != 0:
            messagebox.showerror("错误", "分析失败")
            return

        messagebox.showinfo("完成", "分析完成")

    except Exception as e:
        progress.stop()
        messagebox.showerror("错误", str(e))

# ================= 查看报告 =================
def show_report():
    if not current_session:
        messagebox.showwarning("提示", "请先分析")
        return

    session_name = os.path.basename(current_session)
    record_id = session_name.replace("session_", "record_")

    base = os.path.join(RISK_DIR, "recordings", record_id, "results")

    if not os.path.exists(base):
        messagebox.showerror("错误", "没有结果")
        return

    subdirs = sorted(os.listdir(base))
    latest = os.path.join(base, subdirs[-1])
    report = os.path.join(latest, "report.txt")

    with open(report, "r", encoding="utf-8") as f:
        content = f.read()

    win = tk.Toplevel()
    win.title("分析报告")

    text = scrolledtext.ScrolledText(win, width=100, height=30)
    text.pack()
    text.insert(tk.END, content)

# ================= UI =================
app = tk.Tk()
app.title("DataLeakDetector Pro")
app.geometry("420x320")

tk.Label(app, text="数据泄露检测系统", font=("Arial", 16)).pack(pady=15)

tk.Button(app, text="▶ 启动监控", width=35, command=start_monitor).pack(pady=5)
tk.Button(app, text="■ 结束监控", width=35, command=stop_monitor).pack(pady=5)

tk.Button(app, text="📊 数据分析", width=35, command=analyze).pack(pady=5)
tk.Button(app, text="📄 分析报告", width=35, command=show_report).pack(pady=5)

progress = ttk.Progressbar(app, mode='indeterminate')
progress.pack(pady=10, fill='x', padx=20)

tk.Button(app, text="退出", width=35, command=app.quit).pack(pady=10)

app.mainloop()
