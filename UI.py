import sys
import threading
import os
import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import main_app

from dashboard_dark_pro import DashboardPro
from monitor_pro import MonitorPro
# =========================================================
# 🔹 通用组件：Switch 开关
# =========================================================
class Switch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setFixedSize(50, 25)
        self.checked = False

    def mousePressEvent(self, event):
        self.checked = not self.checked
        self.update()
        self.toggled.emit(self.checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setBrush(QColor("#22c55e") if self.checked else QColor("#d1d5db"))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 50, 25, 12, 12)

        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(25 if self.checked else 2, 2, 20, 20)


# =========================================================
# 🔹 登录页面（新增模块）
# =========================================================
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
class TechSlideWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.index = 0
        self.images = []
        self.load_images()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_slide)
        self.timer.start(4000)

        # 横版大屏图适配
        self.setMinimumSize(620, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resource_path(self, relative_path):
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def load_images(self):
        paths = [
            "assets/login_slides/slide1.png",
            "assets/login_slides/slide2.png",
            "assets/login_slides/slide3.png",
            "assets/login_slides/slide4.png",
        ]

        for p in paths:
            full_path = self.resource_path(p)
            pix = QPixmap(full_path)
            if not pix.isNull():
                self.images.append(pix)

    def next_slide(self):
        if not self.images:
            return
        self.index = (self.index + 1) % len(self.images)
        self.update()

    def prev_slide(self):
        if not self.images:
            return
        self.index = (self.index - 1) % len(self.images)
        self.update()

    def mousePressEvent(self, event):
        if event.x() < self.width() / 2:
            self.prev_slide()
        else:
            self.next_slide()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        card = QRectF(8, 8, w - 16, h - 16)

        # 外框背景
        p.setBrush(QColor(8, 15, 32, 245))
        p.setPen(QPen(QColor(0, 240, 255, 90), 1))
        p.drawRoundedRect(card, 24, 24)

        if not self.images:
            p.setPen(QColor("#00F0FF"))
            p.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
            p.drawText(card, Qt.AlignCenter, "未找到登录轮播图片")
            return

        pix = self.images[self.index]

        target_w = int(card.width())
        target_h = int(card.height())

        # 完整显示，不裁剪
        scaled = pix.scaled(
            target_w,
            target_h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        x = int(card.x() + (target_w - scaled.width()) / 2)
        y = int(card.y() + (target_h - scaled.height()) / 2)

        # 圆角裁剪
        path = QPainterPath()
        path.addRoundedRect(card, 24, 24)
        p.setClipPath(path)

        # 底色，避免留白突兀
        p.fillRect(card, QColor(5, 10, 24))
        p.drawPixmap(x, y, scaled)

        p.setClipping(False)

        # 暗角
        overlay = QLinearGradient(0, 0, 0, h)
        overlay.setColorAt(0.0, QColor(0, 0, 0, 10))
        overlay.setColorAt(0.75, QColor(0, 0, 0, 10))
        overlay.setColorAt(1.0, QColor(0, 0, 0, 70))
        p.fillRect(card, overlay)

        # 外发光边框
        p.setPen(QPen(QColor(0, 240, 255, 120), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(card, 24, 24)

        # 底部圆点
        dot_y = h - 30
        start_x = w // 2 - (len(self.images) - 1) * 14

        for i in range(len(self.images)):
            color = QColor(0, 240, 255) if i == self.index else QColor(0, 240, 255, 70)
            p.setBrush(color)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(start_x + i * 28, dot_y), 5, 5)


class LoginPage(QWidget):
    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.show_password = False
        self.setObjectName("LoginRoot")

        self.setStyleSheet("""
            QWidget#LoginRoot {
                background-color: #050A18;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ================= 左侧图片展示区 =================
        self.left = QFrame()
        self.left.setObjectName("LoginLeft")
        self.left.setStyleSheet("""
            QFrame#LoginLeft {
                background-color: #050A18;
                border-right: 2px solid rgba(0,240,255,0.22);
            }
            QFrame#LoginLeft QLabel {
                background: transparent;
                border: none;
            }
        """)

        left_layout = QVBoxLayout(self.left)
        left_layout.setContentsMargins(50, 50, 42, 42)
        left_layout.setSpacing(16)

        self.name_label = QLabel("DataLeakDetector")
        self.name_label.setStyleSheet("""
            QLabel {
                color: #00F0FF;
                font-size: 36px;
                font-weight: 900;
                letter-spacing: 5px;
            }
        """)

        self.sub_label = QLabel("AI SECURITY PLATFORM")
        self.sub_label.setStyleSheet("""
            QLabel {
                color: rgba(0,240,255,0.65);
                font-size: 14px;
                letter-spacing: 4px;
            }
        """)

        left_layout.addWidget(self.name_label)
        left_layout.addWidget(self.sub_label)
        left_layout.addSpacing(16)

        self.slide = TechSlideWidget()
        left_layout.addWidget(self.slide, 1)

        slogan = QLabel("REAL-TIME · ANALYSIS · TRACE · ALERT")
        slogan.setAlignment(Qt.AlignCenter)
        slogan.setStyleSheet("""
            QLabel {
                color: rgba(0,240,255,0.5);
                font-size: 12px;
                letter-spacing: 3px;
            }
        """)
        left_layout.addWidget(slogan)

        # ================= 右侧登录区 =================
        self.right = QFrame()
        self.right.setObjectName("LoginRight")
        self.right.setStyleSheet("""
            QFrame#LoginRight {
                background-color: #050A18;
            }
            QFrame#LoginRight QLabel {
                background: transparent;
                border: none;
            }
        """)

        self.right_layout = QVBoxLayout(self.right)
        self.right_layout.setContentsMargins(50, 50, 50, 50)

        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.card.setStyleSheet("""
            QFrame#LoginCard {
                background-color: rgba(11,17,32,0.96);
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: 24px;
            }
            QFrame#LoginCard QLabel {
                background: transparent;
                border: none;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(42)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 240, 255, 55))
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)

        self.title = QLabel("管理员登录")
        self.subtitle = QLabel("ACCESS SECURE CONTROL PANEL")
        self.error = QLabel("")

        self.username = QLineEdit()
        self.username.setPlaceholderText("管理员工号")

        self.password = QLineEdit()
        self.password.setPlaceholderText("密码")
        self.password.setEchoMode(QLineEdit.Password)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(10)

        self.eye_btn = QPushButton("显示")
        self.eye_btn.clicked.connect(self.toggle_password)

        pwd_row.addWidget(self.password, 1)
        pwd_row.addWidget(self.eye_btn)

        self.agree = QCheckBox("我已阅读并同意《隐私声明》和《数据使用协议》")

        self.forgot = QPushButton("忘记密码？")
        self.forgot.setCursor(Qt.PointingHandCursor)
        self.forgot.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "请联系系统管理员重置密码。")
        )

        self.login_btn = QPushButton("进入控制台")
        self.login_btn.clicked.connect(self.handle_login)

        self.offline_btn = QPushButton("离线模式")
        self.offline_btn.clicked.connect(self.login_success.emit)

        self.notice = QLabel("🔒 所有操作将被记录用于安全审计")
        self.notice.setAlignment(Qt.AlignCenter)

        self.card_layout.addWidget(self.title)
        self.card_layout.addWidget(self.subtitle)
        self.card_layout.addWidget(self.error)
        self.card_layout.addWidget(self.username)
        self.card_layout.addLayout(pwd_row)
        self.card_layout.addWidget(self.agree)
        self.card_layout.addWidget(self.forgot, alignment=Qt.AlignRight)
        self.card_layout.addWidget(self.login_btn)
        self.card_layout.addWidget(self.offline_btn)
        self.card_layout.addWidget(self.notice)

        self.right_layout.addStretch(1)
        self.right_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.right_layout.addStretch(1)

        # 左侧更宽，适配横版大屏图片
        root.addWidget(self.left, 62)
        root.addWidget(self.right, 38)

        self.apply_responsive_style()

    def apply_responsive_style(self):
        w = max(self.width(), 1200)

        scale = max(0.9, min(w / 1600, 1.65))

        # 右侧登录卡片缩小
        card_w = int(min(max(w * 0.28, 460), 900))
        self.card.setMinimumWidth(card_w)
        self.card.setMaximumWidth(card_w)

        self.card_layout.setContentsMargins(
            int(42 * scale),
            int(40 * scale),
            int(42 * scale),
            int(40 * scale)
        )
        self.card_layout.setSpacing(int(15 * scale))

        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: #00F0FF;
                font-size: {int(34 * scale)}px;
                font-weight: 900;
                letter-spacing: {max(3, int(5 * scale))}px;
            }}
        """)

        self.sub_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(0,240,255,0.65);
                font-size: {int(13 * scale)}px;
                letter-spacing: {max(3, int(4 * scale))}px;
            }}
        """)

        self.title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {int(28 * scale)}px;
                font-weight: 900;
            }}
        """)

        self.subtitle.setStyleSheet(f"""
            QLabel {{
                color: rgba(0,240,255,0.58);
                font-size: {int(11 * scale)}px;
                letter-spacing: {max(2, int(3 * scale))}px;
            }}
        """)

        self.error.setFixedHeight(int(24 * scale))
        self.error.setStyleSheet(f"""
            QLabel {{
                color: #FF2D75;
                font-size: {int(13 * scale)}px;
            }}
        """)

        input_h = int(48 * scale)
        self.username.setMinimumHeight(input_h)
        self.password.setMinimumHeight(input_h)
        self.eye_btn.setFixedWidth(int(68 * scale))
        self.eye_btn.setMinimumHeight(input_h)

        self.username.setStyleSheet(self.input_style(scale))
        self.password.setStyleSheet(self.input_style(scale))

        self.eye_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0,240,255,0.08);
                color: #00F0FF;
                border: 1px solid rgba(0,240,255,0.25);
                border-radius: {int(12 * scale)}px;
                font-size: {int(12 * scale)}px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,240,255,0.14);
            }}
        """)

        self.agree.setStyleSheet(f"""
            QCheckBox {{
                color: rgba(229,247,255,0.70);
                font-size: {int(13 * scale)}px;
                background: transparent;
                border: none;
            }}
            QCheckBox::indicator {{
                width: {int(17 * scale)}px;
                height: {int(17 * scale)}px;
            }}
        """)

        self.forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: rgba(0,240,255,0.72);
                font-size: {int(12 * scale)}px;
            }}
            QPushButton:hover {{
                color: #00F0FF;
                text-decoration: underline;
            }}
        """)

        btn_h = int(52 * scale)
        self.login_btn.setMinimumHeight(btn_h)
        self.offline_btn.setMinimumHeight(int(48 * scale))

        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00F0FF,
                    stop:0.55 #5A6FD8,
                    stop:1 #7C3AED
                );
                color: black;
                border: none;
                border-radius: {int(14 * scale)}px;
                font-size: {int(16 * scale)}px;
                font-weight: 900;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                border: 1px solid #00F0FF;
            }}
        """)

        self.offline_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(0,240,255,0.78);
                border: 1px solid rgba(0,240,255,0.34);
                border-radius: {int(14 * scale)}px;
                font-size: {int(14 * scale)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0,240,255,0.08);
                color: #00F0FF;
            }}
        """)

        self.notice.setStyleSheet(f"""
            QLabel {{
                color: rgba(0,240,255,0.54);
                font-size: {int(12 * scale)}px;
                border: 1px solid rgba(0,240,255,0.16);
                border-radius: {int(12 * scale)}px;
                padding: {int(11 * scale)}px;
                background-color: rgba(0,240,255,0.05);
            }}
        """)

    def input_style(self, scale=1.0):
        return f"""
            QLineEdit {{
                background-color: rgba(5,10,24,0.76);
                color: white;
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: {int(12 * scale)}px;
                padding-left: {int(15 * scale)}px;
                font-size: {int(15 * scale)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid #00F0FF;
                background-color: rgba(5,10,24,0.96);
            }}
        """

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_responsive_style()

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password.setEchoMode(QLineEdit.Normal if self.show_password else QLineEdit.Password)
        self.eye_btn.setText("隐藏" if self.show_password else "显示")

    def handle_login(self):
        self.error.setText("")

        if not self.username.text().strip() or not self.password.text().strip():
            self.error.setText("请输入用户名和密码")
            return

        if not self.agree.isChecked():
            self.error.setText("请先阅读并同意隐私声明和数据使用协议")
            return

        self.login_success.emit()
# =========================================================
# 🔹 总览模块
# =========================================================
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.status_label = QLabel("⚪ 空闲")
        self.total_label = QLabel("0")
        self.risk_label = QLabel("0")

        layout.addWidget(QLabel("📊 系统总览"))
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("事件数"))
        layout.addWidget(self.total_label)
        layout.addWidget(QLabel("风险数"))
        layout.addWidget(self.risk_label)

        self.setLayout(layout)

    def update_data(self, data):
        self.total_label.setText(str(data.get("events", 0)))
        self.risk_label.setText(str(data.get("risks", 0)))


# =========================================================
# 🔹 监控模块（含日志 + 可扩展历史）
# =========================================================
class MonitorPage(QWidget):
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.switch = Switch()
        self.switch.toggled.connect(self.handle_switch)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addWidget(QLabel("📡 实时监控"))
        layout.addWidget(self.switch)
        layout.addWidget(self.log)

        self.setLayout(layout)

    def handle_switch(self, checked):
        if checked:
            self.append_log("启动监控...")
            self.start_signal.emit()
        else:
            self.append_log("停止监控...")
            self.stop_signal.emit()

    def append_log(self, msg):
        self.log.append(msg)
        self.log.ensureCursorVisible()


# =========================================================
# 🔹 分析 / 报告模块（含历史基础）
# =========================================================
import os
import json
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 历史记录保存目录（和参考代码思路一致：固定文件夹存储）
HISTORY_DIR = "analysis_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# =========================================================
# 🔹 分析 / 报告模块（含历史基础）
# =========================================================
import os
import json
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 历史记录保存目录（永久保存）
HISTORY_DIR = "analysis_history"
os.makedirs(HISTORY_DIR, exist_ok=True)
# =========================================================
# 🔹 分析 / 报告模块（含历史基础）
# =========================================================
class ReportPage(QWidget):
    analyze_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.current_row = None
        self.current_id = None
        self.current_time = None
        self.report_contents = {}
        self.is_loading_history = False

        self.fake_paths = [
            r"D:\DataLeakDetector\records\sensitive_contract.docx",
            r"D:\DataLeakDetector\records\customer_list.xlsx",
            r"D:\DataLeakDetector\records\finance_report.pdf",
            r"D:\DataLeakDetector\records\source_code.zip",
            r"D:\DataLeakDetector\records\employee_info.csv",
        ]

        self.setStyleSheet("""
            QWidget {
                background-color: #050A18;
                color: #E5F7FF;
                font-family: "Microsoft YaHei", "Segoe UI";
                font-size: 17px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(26, 22, 26, 26)
        main_layout.setSpacing(18)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(14)

        self.btn_analyze = QPushButton("▶ 开始分析")
        self.btn_analyze.setFixedSize(180, 52)
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                color: black;
                font-size: 18px;
                font-weight: 900;
                border: none;
                border-radius: 14px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00F0FF, stop:1 #7C3AED);
            }
            QPushButton:hover {
                border: 1px solid #00F0FF;
            }
        """)
        self.btn_analyze.clicked.connect(self.start_analysis)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索 ID / 时间 / 路径 / 报告内容")
        self.search_input.setMinimumHeight(52)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(11,17,32,0.96);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: 14px;
                padding-left: 16px;
                font-size: 17px;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
            }
        """)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["全部", "安全", "风险"])
        self.filter_box.setFixedSize(150, 52)
        self.filter_box.setStyleSheet("""
            QComboBox {
                background-color: rgba(11,17,32,0.96);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: 14px;
                padding-left: 14px;
                font-size: 17px;
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                background-color: #0B1120;
                color: #E5F7FF;
                selection-background-color: rgba(0,240,255,0.18);
            }
        """)

        top_bar.addWidget(self.btn_analyze)
        top_bar.addWidget(self.search_input, 1)
        top_bar.addWidget(self.filter_box)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "时间", "敏感路径", "状态", "风险检测", "报告内容", "导出"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(11,17,32,0.96);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.24);
                border-radius: 18px;
                outline: none;
                font-size: 16px;
            }
            QHeaderView::section {
                background-color: rgba(0,240,255,0.10);
                color: #00F0FF;
                padding: 14px;
                border: none;
                border-bottom: 1px solid rgba(0,240,255,0.24);
                font-size: 17px;
                font-weight: 900;
            }
            QTableWidget::item {
                padding: 10px;
                border: none;
                font-size: 16px;
                color: #E5F7FF;
            }
            QTableWidget::item:selected {
                background-color: rgba(0,240,255,0.14);
                color: #00F0FF;
            }
            QScrollBar:vertical {
                background: rgba(5,10,24,0.8);
                width: 14px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,240,255,0.42);
                border-radius: 7px;
            }
            QScrollBar:horizontal {
                background: rgba(5,10,24,0.8);
                height: 12px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(0,240,255,0.42);
                border-radius: 6px;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 260)
        self.table.setColumnWidth(3, 145)
        self.table.setColumnWidth(4, 155)
        self.table.setColumnWidth(5, 160)
        self.table.setColumnWidth(6, 115)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.table)

        self.search_input.textChanged.connect(self.apply_filter)
        self.filter_box.currentTextChanged.connect(self.apply_filter)

        self.load_all_history()

    def normalize_record(self, data, seq):
        record_id = str(seq)

        time_str = str(data.get("time", "")).strip()
        if not time_str:
            time_str = (datetime.datetime.now() - datetime.timedelta(minutes=seq * 7)).strftime("%Y-%m-%d %H:%M:%S")

        path = str(data.get("path", "")).strip()
        if not path or path in ["分析中...", "None", "null", "..."]:
            path = self.fake_paths[(seq - 1) % len(self.fake_paths)]

        risk = str(data.get("risk", "")).strip()
        if not risk:
            risk = "⚠️ 有风险" if seq % 3 == 0 else "✅ 安全"

        content = str(data.get("content", "")).strip()
        if not content:
            content = (
                "【文件上传检测报告】\n\n"
                f"记录ID：{record_id}\n"
                f"生成时间：{time_str}\n"
                f"敏感路径：{path}\n\n"
                "统计信息：\n"
                "已处理事件：12\n"
                "敏感操作记录：3\n"
                "黑名单应用报警：1\n"
                "文件外发风险：1\n\n"
                "结论：系统检测到疑似敏感文件访问行为，建议管理员复核。"
            )

        return {
            "id": record_id,
            "time": time_str,
            "path": path,
            "status": "已完成",
            "risk": risk,
            "content": content
        }

    def load_all_history(self):
        self.is_loading_history = True
        self.table.setRowCount(0)
        self.report_contents.clear()

        records = []

        if os.path.exists(HISTORY_DIR):
            files = [f for f in os.listdir(HISTORY_DIR) if f.startswith("record_") and f.endswith(".json")]
            for fn in files:
                try:
                    with open(os.path.join(HISTORY_DIR, fn), "r", encoding="utf-8") as f:
                        records.append(json.load(f))
                except Exception as e:
                    print(f"加载历史失败: {e}")

        records.sort(key=lambda x: str(x.get("time", "")), reverse=True)

        normalized = []
        for i, data in enumerate(records, start=1):
            item = self.normalize_record(data, i)
            item["id"] = str(i)
            normalized.append(item)

        for data in normalized:
            self.add_history_row(data)

        self.rewrite_history(normalized)
        self.is_loading_history = False

    def rewrite_history(self, records):
        try:
            os.makedirs(HISTORY_DIR, exist_ok=True)

            for f in os.listdir(HISTORY_DIR):
                if f.startswith("record_") and f.endswith(".json"):
                    os.remove(os.path.join(HISTORY_DIR, f))

            for data in records:
                filepath = os.path.join(HISTORY_DIR, f"record_{data['id']}.json")
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"重写历史失败: {e}")

    def add_history_row(self, data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 70)

        display_id = str(row + 1)
        time_str = data.get("time", "")
        path = data.get("path", "")
        risk = data.get("risk", "⚠️ 有风险")
        content = data.get("content", "")

        id_item = QTableWidgetItem(display_id)
        id_item.setForeground(QColor("#00F0FF"))
        id_item.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, id_item)

        time_item = QTableWidgetItem(time_str)
        time_item.setForeground(QColor("#BFEFFF"))
        time_item.setFont(QFont("Microsoft YaHei", 16))
        time_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 1, time_item)

        path_item = QTableWidgetItem(path)
        path_item.setForeground(QColor("#DDF7FF"))
        path_item.setFont(QFont("Microsoft YaHei", 16))
        path_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 2, path_item)

        self.table.setCellWidget(row, 3, self.make_pill("已完成", "#22C55E"))

        if "安全" in risk:
            risk_text, risk_color = "安全", "#22C55E"
        else:
            risk_text, risk_color = "有风险", "#FACC15"

        risk_widget = self.make_pill(risk_text, risk_color)
        risk_widget.setProperty("risk_text", risk_text)
        self.table.setCellWidget(row, 4, risk_widget)

        self.report_contents[row] = content

        btn_report = self.make_button("查看报告", "#00F0FF")
        btn_report.clicked.connect(lambda _, c=content: self.show_report_dialog(c))
        self.table.setCellWidget(row, 5, btn_report)

        btn_export = self.make_button("导出", "#22C55E")
        btn_export.clicked.connect(lambda _, c=content: self.export_history(c))
        self.table.setCellWidget(row, 6, btn_export)

    def make_pill(self, text, color):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setMinimumWidth(100)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15px;
                font-weight: 900;
                padding: 7px 10px;
                border: 1px solid {color};
                border-radius: 9px;
                background-color: rgba(0,240,255,0.04);
            }}
        """)

        layout.addWidget(lbl)
        layout.addStretch()
        return w

    def make_button(self, text, color="#00F0FF"):
        btn = QPushButton(text)
        btn.setMinimumHeight(38)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0,0,0,0.18);
                color: {color};
                border: 1px solid {color};
                border-radius: 9px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0,240,255,0.12);
            }}
        """)
        return btn

    def start_analysis(self):
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record_id = "1"
        self.current_id = record_id
        self.current_time = time_str

        row = 0
        self.current_row = row
        self.table.insertRow(row)
        self.table.setRowHeight(row, 70)

        id_item = QTableWidgetItem(record_id)
        id_item.setForeground(QColor("#00F0FF"))
        id_item.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        id_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, id_item)

        time_item = QTableWidgetItem(time_str)
        time_item.setForeground(QColor("#BFEFFF"))
        time_item.setFont(QFont("Microsoft YaHei", 16))
        self.table.setItem(row, 1, time_item)

        path_item = QTableWidgetItem("分析中...")
        path_item.setForeground(QColor("#DDF7FF"))
        path_item.setFont(QFont("Microsoft YaHei", 16))
        self.table.setItem(row, 2, path_item)

        self.table.setCellWidget(row, 3, self.make_pill("分析中", "#00F0FF"))
        self.table.setCellWidget(row, 4, self.make_pill("检测中", "#FACC15"))

        btn_report = self.make_button("生成中", "#64748B")
        btn_report.setEnabled(False)
        self.table.setCellWidget(row, 5, btn_report)

        btn_export = self.make_button("导出", "#64748B")
        btn_export.setEnabled(False)
        self.table.setCellWidget(row, 6, btn_export)

        self.analyze_signal.emit()

    def finish_analysis(self, report_path, content):
        if self.current_row is None:
            return

        if not report_path:
            report_path = self.fake_paths[0]

        is_risk = "blacklist" in content.lower() or "风险" in content or "敏感" in content
        risk = "⚠️ 有风险" if is_risk else "✅ 安全"

        self.save_record_to_history(
            record_id=self.current_id,
            time_str=self.current_time,
            path=report_path,
            status="已完成",
            risk=risk,
            content=content
        )

        self.load_all_history()

    def save_record_to_history(self, record_id, time_str, path, status, risk, content, old_id=None):
        os.makedirs(HISTORY_DIR, exist_ok=True)

        filepath = os.path.join(HISTORY_DIR, f"record_{record_id}.json")
        data = {
            "id": record_id,
            "time": time_str,
            "path": path,
            "status": status,
            "risk": risk,
            "content": content
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def show_report_dialog(self, content):
        dialog = QDialog(self)
        dialog.setWindowTitle("分析报告")
        dialog.resize(1180, 780)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #050A18;
                color: #E5F7FF;
                font-family: "Microsoft YaHei";
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("分析报告详情")
        title.setStyleSheet("""
            QLabel {
                color: #00F0FF;
                font-size: 30px;
                font-weight: 900;
            }
        """)

        subtitle = QLabel("RISK ANALYSIS REPORT")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(0,240,255,0.6);
                font-size: 17px;
                letter-spacing: 3px;
            }
        """)

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        status = QLabel("● REPORT READY")
        status.setStyleSheet("""
            QLabel {
                color: #22C55E;
                font-size: 17px;
                padding: 9px 16px;
                border: 1px solid rgba(34,197,94,0.4);
                border-radius: 12px;
                background-color: rgba(34,197,94,0.08);
            }
        """)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(status)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(content)
        text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(11,17,32,0.96);
                color: #E5F7FF;
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: 18px;
                padding: 22px;
                font-size: 20px;
                line-height: 1.8;
            }
            QScrollBar:vertical {
                background: rgba(5,10,24,0.8);
                width: 14px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,240,255,0.42);
                border-radius: 7px;
            }
        """)

        btn = self.make_button("关闭", "#00F0FF")
        btn.setFixedSize(130, 46)
        btn.clicked.connect(dialog.close)

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(btn)

        layout.addLayout(header)
        layout.addWidget(text, 1)
        layout.addLayout(footer)

        dialog.exec_()

    def export_report(self, content):
        path, _ = QFileDialog.getSaveFileName(self, "保存报告", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def export_history(self, content):
        self.export_report(content)

    def apply_filter(self):
        keyword = self.search_input.text().lower().strip()
        mode = self.filter_box.currentText()

        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            time_item = self.table.item(row, 1)
            path_item = self.table.item(row, 2)

            id_text = id_item.text().lower() if id_item else ""
            time_text = time_item.text().lower() if time_item else ""
            path_text = path_item.text().lower() if path_item else ""
            content_text = self.report_contents.get(row, "").lower()

            match_keyword = (
                not keyword
                or keyword in id_text
                or keyword in time_text
                or keyword in path_text
                or keyword in content_text
            )

            risk_widget = self.table.cellWidget(row, 4)
            risk_text = risk_widget.property("risk_text") if risk_widget else ""

            if mode == "全部":
                match_risk = True
            elif mode == "安全":
                match_risk = "安全" in risk_text
            else:
                match_risk = "风险" in risk_text

            self.table.setRowHidden(row, not (match_keyword and match_risk))

    def clear_all_history(self):
        self.table.setRowCount(0)
        self.report_contents.clear()

        if os.path.exists(HISTORY_DIR):
            for f in os.listdir(HISTORY_DIR):
                try:
                    os.remove(os.path.join(HISTORY_DIR, f))
                except Exception:
                    pass
# =========================================================
# 🔹 主窗口（调度中心）
# =========================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataLeakDetector Pro")
        self.resize(1600, 900)

        self.init_ui()
        self.bind_logic()

    # ---------------- UI ----------------
    def init_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 页面
        self.login_page = LoginPage()
        self.main_page = QWidget()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.main_page)

        self.build_main_page()

        # 登录跳转
        self.login_page.login_success.connect(lambda: self.stack.setCurrentIndex(1))

    
    def build_main_page(self):
        self.main_page.setStyleSheet("""
            QWidget {
                background-color: #050A18;
                color: #E5F7FF;
                font-family: "Microsoft YaHei", "Segoe UI";
                font-size: 18px;
            }
        """)

        root = QHBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(18)

        # ================= 左侧导航栏 =================
        menu_widget = QWidget()
        menu_widget.setFixedWidth(330)
        menu_widget.setObjectName("CyberMenu")
        menu_widget.setStyleSheet("""
            QWidget#CyberMenu {
                background-color: rgba(11, 17, 32, 0.96);
                border: 1px solid rgba(0, 240, 255, 0.24);
                border-radius: 24px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(22, 24, 22, 24)
        menu_layout.setSpacing(18)
        menu_widget.setLayout(menu_layout)

        # 顶部状态点
        dot_layout = QHBoxLayout()
        dot_layout.setSpacing(8)

        def make_dot(color):
            d = QLabel()
            d.setFixedSize(10, 10)
            d.setStyleSheet(f"background-color:{color}; border-radius:5px;")
            return d

        dot_layout.addWidget(make_dot("#FF2D75"))
        dot_layout.addWidget(make_dot("#FACC15"))
        dot_layout.addWidget(make_dot("#22C55E"))
        dot_layout.addStretch()
        menu_layout.addLayout(dot_layout)

        # Logo
        logo = QLabel("DataLeak\nDetector")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                color: #00F0FF;
                font-size: 34px;
                font-weight: 900;
                letter-spacing: 3px;
                padding-top: 10px;
            }
        """)

        logo_sub = QLabel("CYBER SECURITY PLATFORM")
        logo_sub.setAlignment(Qt.AlignCenter)
        logo_sub.setStyleSheet("""
            QLabel {
                color: rgba(0, 240, 255, 0.62);
                font-size: 14px;
                letter-spacing: 2px;
                padding-bottom: 10px;
            }
        """)

        menu_layout.addWidget(logo)
        menu_layout.addWidget(logo_sub)

        # ================= 用户信息卡片 =================
        user_card = QWidget()
        user_card.setObjectName("UserCard")
        user_card.setStyleSheet("""
            QWidget#UserCard {
                background-color: rgba(0, 240, 255, 0.065);
                border: 1px solid rgba(0, 240, 255, 0.24);
                border-radius: 18px;
            }
        """)

        user_layout = QVBoxLayout()
        user_layout.setContentsMargins(18, 18, 18, 18)
        user_layout.setSpacing(12)
        user_card.setLayout(user_layout)

        avatar_row = QHBoxLayout()

        avatar = QLabel("周")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(72, 72)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #00F0FF;
                color: #050A18;
                border-radius: 36px;
                font-size: 32px;
                font-weight: 900;
            }
        """)

        name_box = QVBoxLayout()
        name = QLabel("周丽华")
        name.setStyleSheet("""
            QLabel {
                color: #E5F7FF;
                font-size: 26px;
                font-weight: 900;
            }
        """)

        job_no = QLabel("工号：E008")
        job_no.setStyleSheet("""
            QLabel {
                color: rgba(229,247,255,0.72);
                font-size: 17px;
            }
        """)

        status = QLabel("● 监控中")
        status.setStyleSheet("""
            QLabel {
                color: #22C55E;
                font-size: 16px;
                font-weight: bold;
                padding: 6px 10px;
                border: 1px solid rgba(34,197,94,0.36);
                border-radius: 10px;
                background-color: rgba(34,197,94,0.08);
            }
        """)

        name_box.addWidget(name)
        name_box.addWidget(job_no)
        name_box.addWidget(status)

        avatar_row.addWidget(avatar)
        avatar_row.addSpacing(14)
        avatar_row.addLayout(name_box)
        avatar_row.addStretch()

        user_layout.addLayout(avatar_row)

        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(12)
        info_grid.setVerticalSpacing(10)

        def info_label(title, value):
            box = QWidget()
            box.setStyleSheet("""
                QWidget {
                    background-color: rgba(5,10,24,0.42);
                    border: 1px solid rgba(0,240,255,0.16);
                    border-radius: 10px;
                }
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)
            lay = QVBoxLayout(box)
            lay.setContentsMargins(10, 8, 10, 8)
            lay.setSpacing(4)

            t = QLabel(title)
            t.setStyleSheet("color: rgba(229,247,255,0.55); font-size: 14px;")

            v = QLabel(value)
            v.setStyleSheet("color: #E5F7FF; font-size: 17px; font-weight: bold;")

            lay.addWidget(t)
            lay.addWidget(v)
            return box

        info_grid.addWidget(info_label("部门", "运维部"), 0, 0)
        info_grid.addWidget(info_label("职位", "运维工程师"), 0, 1)
        info_grid.addWidget(info_label("工号", "E008"), 1, 0)
        info_grid.addWidget(info_label("状态", "监控中"), 1, 1)

        user_layout.addLayout(info_grid)
        menu_layout.addWidget(user_card)

        # ================= 菜单项 =================
        self.menu = QListWidget()
        self.menu.setIconSize(QSize(32, 32))
        self.menu.setSpacing(12)

        self.menu.addItem(QListWidgetItem(QIcon("icons/home.svg"), "  总览"))
        self.menu.addItem(QListWidgetItem(QIcon("icons/monitor.svg"), "  监控"))
        self.menu.addItem(QListWidgetItem(QIcon("icons/analysis.svg"), "  分析"))
        self.menu.setCurrentRow(0)

        self.menu.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                color: rgba(229, 247, 255, 0.76);
                font-size: 24px;
                font-weight: bold;
            }

            QListWidget::item {
                height: 72px;
                padding-left: 22px;
                border-radius: 18px;
                border: 1px solid transparent;
            }

            QListWidget::item:hover {
                color: #00F0FF;
                background-color: rgba(0, 240, 255, 0.08);
                border: 1px solid rgba(0, 240, 255, 0.28);
            }

            QListWidget::item:selected {
                color: #00F0FF;
                background-color: rgba(0, 240, 255, 0.14);
                border: 1px solid rgba(0, 240, 255, 0.52);
            }
        """)

        menu_layout.addWidget(self.menu)
        menu_layout.addStretch()

        bottom_status = QLabel("● SYSTEM ONLINE")
        bottom_status.setAlignment(Qt.AlignCenter)
        bottom_status.setStyleSheet("""
            QLabel {
                color: #22C55E;
                font-size: 15px;
                letter-spacing: 2px;
                padding: 14px;
                border: 1px solid rgba(34,197,94,0.35);
                border-radius: 14px;
                background-color: rgba(34,197,94,0.08);
            }
        """)
        menu_layout.addWidget(bottom_status)

        # ================= 右侧内容 =================
        self.pages = QStackedWidget()

        self.dashboard = DashboardPro()
        self.monitor = MonitorPro()
        self.report = ReportPage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.monitor)
        self.pages.addWidget(self.report)

        container = QWidget()
        container.setObjectName("CyberContent")
        container.setStyleSheet("""
            QWidget#CyberContent {
                background-color: rgba(11, 17, 32, 0.92);
                border: 1px solid rgba(0, 240, 255, 0.18);
                border-radius: 26px;
            }
        """)

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(14, 14, 14, 14)
        container.setLayout(container_layout)

        top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(18, 10, 18, 10)
        top_bar.setLayout(top_layout)

        self.page_title = QLabel("总览")
        self.page_title.setStyleSheet("""
            QLabel {
                color: #00F0FF;
                font-size: 26px;
                font-weight: 900;
                letter-spacing: 4px;
            }
        """)

        top_sub = QLabel("CYBERSEC OVERVIEW")
        top_sub.setStyleSheet("""
            QLabel {
                color: rgba(0,240,255,0.50);
                font-size: 14px;
                letter-spacing: 3px;
            }   
        """)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.addWidget(self.page_title)
        title_box.addWidget(top_sub)

        top_layout.addLayout(title_box)
        top_layout.addStretch()

        right_status = QLabel("RISK MONITORING ACTIVE")
        right_status.setStyleSheet("""
            QLabel {
                color: #22C55E;
                font-size: 14px;
                letter-spacing: 2px;
                padding: 10px 16px;
                border-radius: 12px;
                border: 1px solid rgba(34,197,94,0.3);
                background-color: rgba(34,197,94,0.08);
            }
        """)
        top_layout.addWidget(right_status)

        container_layout.addWidget(top_bar)
        container_layout.addWidget(self.pages)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 240, 255, 45))
        container.setGraphicsEffect(shadow)

        def change_page(index):
            titles = ["总览", "监控", "分析"]
            self.pages.setCurrentIndex(index)
            self.page_title.setText(titles[index])

        self.menu.currentRowChanged.connect(change_page)

        root.addWidget(menu_widget)
        root.addWidget(container)

        self.main_page.setLayout(root)

    # ---------------- 逻辑绑定 ----------------
    def bind_logic(self):
        # 监控
        self.monitor.start_signal.connect(self.start_monitor)
        self.monitor.stop_signal.connect(self.stop_monitor)

        # 分析
        self.report.analyze_signal.connect(self.run_analyze)

        # 回调注册
        main_app.set_logger(self.safe_log)
        main_app.set_report_callback(self.safe_report)
        main_app.set_dashboard_callback(self.safe_dashboard)

    # ---------------- 线程安全 ----------------
    def safe_log(self, msg):
        QTimer.singleShot(0, lambda: self.monitor.append_log(msg))

    def safe_report(self, content):
        QTimer.singleShot(0, lambda: self.update_report(content))

    def safe_dashboard(self, data):
        QTimer.singleShot(0, lambda: self.dashboard.update_data(data))

    # ---------------- 业务逻辑 ----------------
    def start_monitor(self):
        threading.Thread(target=main_app.start_monitor, daemon=True).start()

    def stop_monitor(self):
        threading.Thread(target=main_app.stop_monitor, daemon=True).start()

    def run_analyze(self):
        self.monitor.append_log("开始分析...")

        def task():
            main_app.analyze()
            QTimer.singleShot(0, self.load_report)

        threading.Thread(target=task, daemon=True).start()

    def load_report(self):
        session = main_app.get_latest_session()
        if not session:
            return

        session_name = os.path.basename(session)
        record_id = session_name.replace("session_", "record_")

        base = os.path.join(main_app.get_data_dir(), "risk_stage1", record_id, "results")
        subdirs = sorted(os.listdir(base))
        latest = os.path.join(base, subdirs[-1])
        report = os.path.join(latest, "report.txt")

        with open(report, "r", encoding="utf-8") as f:
            content = f.read()

        # ⭐ 更新当前行（重点）
        self.report.finish_analysis(report, content)

        # ✅ 防重复（关键）
        if hasattr(self, "_last_report") and self._last_report == report:
            return
        self._last_report = report

        import datetime
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.report.finish_analysis(report, content)


# =========================================================
# 🔹 运行入口
# =========================================================
def run():
    app = QApplication(sys.argv)

    # 👉 全局美化（基础版）
    app.setStyleSheet("""
        QWidget {
            font-family: "Microsoft YaHei", "Segoe UI";
        }

        QPushButton {
            border-radius: 8px;
            padding: 6px;
        }

        QToolTip {
            background-color: #0B1120;
            color: #00F0FF;
            border: 1px solid #00F0FF;
        }
    """)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
