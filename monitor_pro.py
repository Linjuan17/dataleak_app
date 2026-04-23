import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import main_app


# ================= 弹窗：日志详情卡片 (保留原始解析逻辑) =================
class LogDetailDialog(QDialog):
    def __init__(self, session_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("监控日志详情")
        self.resize(700, 500)
        self.session_path = session_path
        self.init_ui()
        self.load_and_parse_logs()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel(f"会话详情: {os.path.basename(self.session_path)}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; font-family: 'Microsoft YaHei';")
        layout.addWidget(title)

        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        self.content_area.setStyleSheet("""
            QTextEdit {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-family: 'Consolas', 'Microsoft YaHei';
            }
        """)
        layout.addWidget(self.content_area)

        btn_close = QPushButton("确认")
        btn_close.setFixedSize(100, 35)
        btn_close.setStyleSheet("background-color: #22c55e; color: white; border-radius: 6px; font-weight: bold;")
        btn_close.clicked.connect(self.close)

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def load_and_parse_logs(self):
        key_file = os.path.join(self.session_path, "logs", "keyevents.json")
        if not os.path.exists(key_file):
            self.content_area.setText("未找到日志文件")
            return
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            lines = []
            for evt in events[::-1]:
                evt_type = evt.get("event_type", "unknown")
                app = evt.get("app_name", "未知")
                ts = evt.get("timestamp", "").split("T")[-1].split(".")[0]
                if evt_type == "clipboard_text":
                    preview = evt.get("content_preview", "").replace("\n", " ")[:40]
                    lines.append(f"[{ts}] ✂️ 剪贴板: {preview}... ({app})")
                elif evt_type in ("created", "modified", "deleted", "renamed"):
                    file_name = evt.get("file_name", "未知文件")
                    op_map = {"created": "新建", "modified": "修改", "deleted": "删除", "renamed": "重命名"}
                    op_cn = op_map.get(evt_type, evt_type)
                    lines.append(f"[{ts}] 📄 {op_cn}: {file_name} ({app})")
                elif evt_type == "app_switch":
                    win_title = evt.get("window_info", {}).get("window_title", "")[:30]
                    lines.append(f"[{ts}] 🔄 切换到: {win_title} ({app})")
                elif evt_type == "upload_detected":
                    lines.append(f"[{ts}] ⬆️ 上传行为: {evt.get('file_name', '')} ({app})")
                else:
                    lines.append(f"[{ts}] ℹ️ {evt_type} ({app})")
            self.content_area.setPlainText("\n".join(lines) if lines else "无操作记录")
        except:
            self.content_area.setText("解析失败")


# ================= 监控主界面 =================
class MonitorPro(QWidget):
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.record_seconds = 0  # 录制计时秒数
        self.init_ui()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_session_list)
        self.refresh_timer.start(3000)
        self.refresh_session_list()

        # 录制计时定时器
        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.update_record_time)
        self.record_timer.setInterval(1000)  # 每秒更新一次

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        top_bar = QHBoxLayout()
        self.btn_toggle = QPushButton("▶ 开始监控")
        self.btn_toggle.setFixedSize(200, 55)
        self.btn_toggle.setStyleSheet(
            "background-color: #6a7bdc; color: white; border-radius: 10px; font-size: 20px; font-weight: bold;")
        self.btn_toggle.clicked.connect(self.handle_toggle)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet(
            "font-size: 26px; color: #333; font-weight: bold; font-family: 'Consolas'; margin-left: 20px;")

        top_bar.addWidget(self.btn_toggle)
        top_bar.addWidget(self.timer_label)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 搜索框优化：设置固定宽度 + 居中布局（不再占满整行）
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("关键词搜索监控记录...")

        self.search_input.textChanged.connect(self.refresh_session_list)
        self.search_input.setStyleSheet(
            "background-color: white; border: 2px solid #e2e8f0; border-radius: 10px; padding: 12px; font-size: 20px;")
        # 关键：设置搜索框固定宽度（控制宽度的核心代码）
        self.search_input.setFixedWidth(600)
        search_layout = QHBoxLayout()
        search_layout.setAlignment(Qt.AlignLeft)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)  # 替换原直接addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "监控时间", "当前状态", "查看详情", "录像重放"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }
            QHeaderView::section {
                background-color: #f1f5f9; padding: 10px; border: none;
                border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: bold; font-size: 20px;
            }
        """)
        layout.addWidget(self.table)

    def handle_toggle(self):
        if not self.is_monitoring:
            # 开始监控：重置计时 + 启动定时器
            self.is_monitoring = True
            self.record_seconds = 0
            self.record_timer.start()
            self.btn_toggle.setText("■ 停止监控")
            self.btn_toggle.setStyleSheet(
                "background-color: #ef4444; color: white; border-radius: 10px; font-size: 18px; font-weight: bold;")
            self.start_signal.emit()
        else:
            # 停止监控：停止定时器
            self.is_monitoring = False
            self.record_timer.stop()
            self.btn_toggle.setText("▶ 开始监控")
            self.btn_toggle.setStyleSheet(
                "background-color: #6a7bdc; color: white; border-radius: 10px; font-size: 18px; font-weight: bold;")
            self.stop_signal.emit()

    def update_record_time(self):
        """更新录制时间标签（格式：HH:MM:SS）"""
        self.record_seconds += 1
        hours = self.record_seconds // 3600
        minutes = (self.record_seconds % 3600) // 60
        seconds = self.record_seconds % 60
        # 格式化输出，补零
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_label.setText(time_str)

    def refresh_session_list(self):
        base_path = main_app.SCREEN_RECORD
        if not os.path.exists(base_path): return
        search_txt = self.search_input.text().lower()
        try:
            sessions = [d for d in os.listdir(base_path) if d.startswith("session_")]
            sessions.sort(key=lambda d: os.path.getmtime(os.path.join(base_path, d)), reverse=True)
            display_list = sessions[:5]
        except:
            return

        self.table.setRowCount(0)
        for i, session_name in enumerate(display_list):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 70)

            # 搜索匹配判断
            time_str = session_name.replace("session_", "").replace("_", " ")
            is_matched = search_txt and (search_txt in str(i + 1) or search_txt in time_str.lower())

            # 设置这一行的背景色逻辑：匹配变灰，不匹配白色
            bg_color = "#f1f5f9" if is_matched else "white"

            # 1. ID + 绿色细线
            id_widget = QWidget()
            id_widget.setStyleSheet(f"background-color: {bg_color};")
            id_layout = QHBoxLayout(id_widget)
            id_lbl = QLabel(str(i + 1))
            id_lbl.setAlignment(Qt.AlignCenter)
            id_lbl.setStyleSheet("font-size: 20px; color: #64748b; font-weight: bold; background: transparent;")
            line = QFrame()
            line.setFrameShape(QFrame.VLine);
            line.setFixedWidth(2)
            line.setStyleSheet("background-color: #22c55e; margin: 15px 0; border: none;")
            id_layout.addWidget(id_lbl, 1);
            id_layout.addWidget(line)
            id_layout.setContentsMargins(0, 0, 0, 0);
            id_layout.setSpacing(0)
            self.table.setCellWidget(i, 0, id_widget)

            # 2. 时间
            item_time = QTableWidgetItem(time_str)
            item_time.setBackground(QColor(bg_color))
            self.table.setItem(i, 1, item_time)

            # 3. 状态
            status_widget = QWidget()
            status_widget.setStyleSheet(f"background-color: {bg_color};")
            status_layout = QHBoxLayout(status_widget)
            icon = QLabel("☑")
            icon.setStyleSheet("color: #22c55e; font-size: 22px; font-weight: bold; background: transparent;")
            txt = QLabel("已完成")
            txt.setStyleSheet("color: #22c55e; font-size: 20px; font-weight: bold; background: transparent;")
            status_layout.addStretch();
            status_layout.addWidget(icon);
            status_layout.addWidget(txt);
            status_layout.addStretch()
            status_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(i, 2, status_widget)

            # 4. 详情 (绿色按钮)
            btn_log = QPushButton("详情")
            btn_log.setFixedSize(100, 40)
            btn_log.setStyleSheet("background: #22c55e; color: white; border-radius: 6px; font-weight: bold;")
            btn_log.clicked.connect(lambda _, p=os.path.join(base_path, session_name): self.show_log_dialog(p))
            self.table.setCellWidget(i, 3, self.wrap(btn_log, bg_color))

            # 5. 播放 (绿色按钮)
            btn_video = QPushButton("播放")
            btn_video.setFixedSize(100, 40)
            btn_video.setStyleSheet("background: #22c55e; color: white; border-radius: 6px; font-weight: bold;")
            v_path = os.path.join(base_path, session_name, "video", f"recording_{session_name[8:]}.mp4")
            btn_video.clicked.connect(lambda _, p=v_path: self.open_v(p))
            self.table.setCellWidget(i, 4, self.wrap(btn_video, bg_color))

    def show_log_dialog(self, session_path):
        LogDetailDialog(session_path, self).exec_()

    def open_v(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.information(self, "路径", f"文件路径：\n{path}")

    def wrap(self, widget, bg):
        c = QWidget();
        c.setStyleSheet(f"background-color: {bg};")
        l = QHBoxLayout(c);
        l.addWidget(widget);
        l.setAlignment(Qt.AlignCenter);
        l.setContentsMargins(0, 0, 0, 0)
        return c

    def append_log(self, msg):
        if "计时" in msg: self.timer_label.setText(msg.split(":")[-1].strip())

    def refresh(self):
        self.refresh_session_list()