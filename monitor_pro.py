import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import main_app


CYAN = "#00F0FF"
BLUE = "#5A6FD8"
PURPLE = "#7C3AED"
GREEN = "#22C55E"
RED = "#FF2D75"
BG = "#050A18"
CARD = "#0B1120"


class LogDetailDialog(QDialog):
    def __init__(self, session_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("监控日志详情")
        self.resize(780, 560)
        self.session_path = session_path
        self.init_ui()
        self.load_and_parse_logs()

    def init_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG};
                color: #E5F7FF;
                font-family: "Microsoft YaHei", "Segoe UI";
            }}
            QLabel {{
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel(f"SESSION DETAIL / {os.path.basename(self.session_path)}")
        title.setStyleSheet(f"""
            color: {CYAN};
            font-size: 20px;
            font-weight: 900;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        self.content_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(11,17,32,0.95);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.25);
                border-radius: 16px;
                padding: 14px;
                font-size: 15px;
                font-family: "Consolas", "Microsoft YaHei";
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(0,240,255,0.35);
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.content_area)

        btn_close = QPushButton("确认")
        btn_close.setFixedSize(120, 40)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {CYAN}, stop:1 {PURPLE});
                color: black;
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
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
                    preview = evt.get("content_preview", "").replace("\n", " ")[:60]
                    lines.append(f"[{ts}]  CLIPBOARD   {preview}  <{app}>")
                elif evt_type in ("created", "modified", "deleted", "renamed"):
                    file_name = evt.get("file_name", "未知文件")
                    op_map = {"created": "CREATE", "modified": "MODIFY", "deleted": "DELETE", "renamed": "RENAME"}
                    lines.append(f"[{ts}]  {op_map.get(evt_type, evt_type)}   {file_name}  <{app}>")
                elif evt_type == "app_switch":
                    win_title = evt.get("window_info", {}).get("window_title", "")[:50]
                    lines.append(f"[{ts}]  APP_SWITCH   {win_title}  <{app}>")
                elif evt_type == "upload_detected":
                    lines.append(f"[{ts}]  UPLOAD   {evt.get('file_name', '')}  <{app}>")
                else:
                    lines.append(f"[{ts}]  {evt_type.upper()}   <{app}>")

            self.content_area.setPlainText("\n".join(lines) if lines else "无操作记录")
        except Exception as e:
            self.content_area.setText(f"解析失败：{e}")


class MonitorPro(QWidget):
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.record_seconds = 0

        self.init_ui()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_session_list)
        self.refresh_timer.start(3000)

        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.update_record_time)
        self.record_timer.setInterval(1000)

        self.refresh_session_list()

    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG};
                color: #E5F7FF;
                font-family: "Microsoft YaHei", "Segoe UI";
            }}
            QLabel {{
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 26)
        layout.setSpacing(18)

        # 顶部控制区
        top = QHBoxLayout()

        self.btn_toggle = QPushButton("▶ START MONITOR")
        self.btn_toggle.setFixedSize(220, 56)
        self.btn_toggle.setStyleSheet(self.start_btn_style())
        self.btn_toggle.clicked.connect(self.handle_toggle)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet(f"""
            color: {CYAN};
            font-size: 32px;
            font-weight: 900;
            font-family: "Consolas";
            letter-spacing: 2px;
        """)

        status = QLabel("● READY")
        status.setStyleSheet(f"""
            color: {GREEN};
            font-size: 13px;
            letter-spacing: 2px;
            padding: 8px 14px;
            border: 1px solid rgba(34,197,94,0.35);
            border-radius: 12px;
            background-color: rgba(34,197,94,0.08);
        """)
        self.status_label = status

        top.addWidget(self.btn_toggle)
        top.addSpacing(18)
        top.addWidget(self.timer_label)
        top.addStretch()
        top.addWidget(status)
        layout.addLayout(top)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索监控记录 / Search session...")
        self.search_input.textChanged.connect(self.refresh_session_list)
        self.search_input.setFixedWidth(620)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(11,17,32,0.92);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.24);
                border-radius: 14px;
                padding: 13px 16px;
                font-size: 18px;
            }}
            QLineEdit:focus {{
                border: 1px solid {CYAN};
            }}
        """)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_input)
        search_row.addStretch()
        layout.addLayout(search_row)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "监控时间", "当前状态", "日志详情", "录像重放"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: rgba(11,17,32,0.92);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.22);
                border-radius: 18px;
                gridline-color: transparent;
                outline: none;
            }}

            QHeaderView::section {{
                background-color: rgba(0,240,255,0.08);
                color: {CYAN};
                padding: 12px;
                border: none;
                border-bottom: 1px solid rgba(0,240,255,0.25);
                font-size: 17px;
                font-weight: bold;
                letter-spacing: 1px;
            }}

            QTableWidget::item {{
                border: none;
                padding: 10px;
                font-size: 16px;
            }}

            QTableWidget::item:selected {{
                background-color: rgba(0,240,255,0.13);
                color: {CYAN};
            }}
        """)
        layout.addWidget(self.table)

        # 底部日志
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(120)
        self.log.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(11,17,32,0.92);
                color: rgba(229,247,255,0.78);
                border: 1px solid rgba(0,240,255,0.18);
                border-radius: 14px;
                padding: 12px;
                font-size: 14px;
                font-family: "Consolas", "Microsoft YaHei";
            }}
        """)
        self.log.setPlaceholderText("监控日志输出...")
        layout.addWidget(self.log)

    def start_btn_style(self):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {CYAN}, stop:1 {PURPLE});
                color: black;
                border-radius: 14px;
                font-size: 17px;
                font-weight: 900;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                border: 1px solid {CYAN};
            }}
        """

    def stop_btn_style(self):
        return f"""
            QPushButton {{
                background-color: rgba(255,45,117,0.92);
                color: white;
                border-radius: 14px;
                font-size: 17px;
                font-weight: 900;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                border: 1px solid {RED};
            }}
        """

    def handle_toggle(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.record_seconds = 0
            self.record_timer.start()

            self.btn_toggle.setText("■ STOP MONITOR")
            self.btn_toggle.setStyleSheet(self.stop_btn_style())
            self.status_label.setText("● RECORDING")
            self.status_label.setStyleSheet(f"""
                color: {RED};
                font-size: 13px;
                letter-spacing: 2px;
                padding: 8px 14px;
                border: 1px solid rgba(255,45,117,0.45);
                border-radius: 12px;
                background-color: rgba(255,45,117,0.10);
            """)

            self.append_log("监控已启动")
            self.start_signal.emit()
        else:
            self.is_monitoring = False
            self.record_timer.stop()

            self.btn_toggle.setText("▶ START MONITOR")
            self.btn_toggle.setStyleSheet(self.start_btn_style())
            self.status_label.setText("● READY")
            self.status_label.setStyleSheet(f"""
                color: {GREEN};
                font-size: 13px;
                letter-spacing: 2px;
                padding: 8px 14px;
                border: 1px solid rgba(34,197,94,0.35);
                border-radius: 12px;
                background-color: rgba(34,197,94,0.08);
            """)

            self.append_log("监控已停止")
            self.stop_signal.emit()

    def update_record_time(self):
        self.record_seconds += 1
        h = self.record_seconds // 3600
        m = (self.record_seconds % 3600) // 60
        s = self.record_seconds % 60
        self.timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def refresh_session_list(self):
        base_path = main_app.SCREEN_RECORD
        if not os.path.exists(base_path):
            return

        search_txt = self.search_input.text().lower()

        try:
            sessions = [d for d in os.listdir(base_path) if d.startswith("session_")]
            sessions.sort(key=lambda d: os.path.getmtime(os.path.join(base_path, d)), reverse=True)
        except Exception:
            return

        display_list = []
        for s in sessions:
            time_str = s.replace("session_", "").replace("_", " ")
            if search_txt and search_txt not in s.lower() and search_txt not in time_str.lower():
                continue
            display_list.append(s)

        display_list = display_list[:8]
        self.table.setRowCount(0)

        for i, session_name in enumerate(display_list):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 72)

            time_str = session_name.replace("session_", "").replace("_", " ")
            row_bg = "rgba(0,240,255,0.06)" if i % 2 == 0 else "rgba(11,17,32,0.92)"

            self.table.setCellWidget(i, 0, self.make_label(str(i + 1), CYAN, row_bg, bold=True))
            self.table.setCellWidget(i, 1, self.make_label(time_str, "#E5F7FF", row_bg))

            self.table.setCellWidget(i, 2, self.make_status(row_bg))

            btn_log = QPushButton("DETAIL")
            btn_log.setFixedSize(105, 38)
            btn_log.setStyleSheet(self.small_btn_style(GREEN))
            btn_log.clicked.connect(lambda _, p=os.path.join(base_path, session_name): self.show_log_dialog(p))
            self.table.setCellWidget(i, 3, self.wrap(btn_log, row_bg))

            btn_video = QPushButton("PLAY")
            btn_video.setFixedSize(105, 38)
            btn_video.setStyleSheet(self.small_btn_style(CYAN))
            video_path = os.path.join(base_path, session_name, "video", f"recording_{session_name[8:]}.mp4")
            btn_video.clicked.connect(lambda _, p=video_path: self.open_v(p))
            self.table.setCellWidget(i, 4, self.wrap(btn_video, row_bg))

    def make_label(self, text, color, bg, bold=False):
        w = QWidget()
        w.setStyleSheet(f"background-color: {bg};")
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"""
            color: {color};
            font-size: 17px;
            font-weight: {'bold' if bold else 'normal'};
            background: transparent;
        """)
        layout.addWidget(lbl)
        return w

    def make_status(self, bg):
        w = QWidget()
        w.setStyleSheet(f"background-color: {bg};")
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

        icon = QLabel("●")
        icon.setStyleSheet(f"color: {GREEN}; font-size: 18px; background: transparent;")
        txt = QLabel("COMPLETED")
        txt.setStyleSheet(f"color: {GREEN}; font-size: 15px; font-weight: bold; background: transparent;")

        layout.addWidget(icon)
        layout.addWidget(txt)
        layout.addStretch()
        return w

    def small_btn_style(self, color):
        return f"""
            QPushButton {{
                background-color: rgba(0,0,0,0.25);
                color: {color};
                border: 1px solid {color};
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,240,255,0.12);
            }}
        """

    def wrap(self, widget, bg):
        c = QWidget()
        c.setStyleSheet(f"background-color: {bg};")
        l = QHBoxLayout(c)
        l.addWidget(widget)
        l.setAlignment(Qt.AlignCenter)
        l.setContentsMargins(0, 0, 0, 0)
        return c

    def show_log_dialog(self, session_path):
        LogDetailDialog(session_path, self).exec_()

    def open_v(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.information(self, "路径", f"文件路径：\n{path}")

    def append_log(self, msg):
        self.log.append(f"> {msg}")
        self.log.ensureCursorVisible()

    def refresh(self):
        self.refresh_session_list()
