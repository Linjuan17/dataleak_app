import sys
import threading
import os

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


class LoginPage(QWidget):
    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()

        # ================= 主布局 =================
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # ================= 左侧蓝色区域 =================
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a7bdc,
                    stop:1 #5a6fd8
                );
                border-top-right-radius: 200px;
                border-bottom-right-radius: 200px;
            }
        """)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)
        left_widget.setLayout(left_layout)

        # Hello Welcome（超大字体）
        welcome_label = QLabel("Hello, Welcome!")
        welcome_label.setStyleSheet("""
            color: white;
            font-size: 60px;
            font-weight: bold;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)

        # 第一行
        line1 = QLabel("数据安全，从这里开始")
        line1.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        """)
        line1.setAlignment(Qt.AlignCenter)

        # 第二行
        line2 = QLabel("实时监测 · 智能分析 · 全面防护")
        line2.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        """)
        line2.setAlignment(Qt.AlignCenter)

        left_layout.addStretch()
        left_layout.addWidget(welcome_label)
        left_layout.addSpacing(25)
        left_layout.addWidget(line1)
        left_layout.addSpacing(15)
        left_layout.addWidget(line2)
        left_layout.addStretch()

        # ================= 右侧登录区域 =================
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
            }
        """)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(120, 80, 120, 80)
        right_layout.setSpacing(25)
        right_widget.setLayout(right_layout)

        # 标题 DataLeak
        title = QLabel("DataLeak Detector")
        title.setStyleSheet("""
            font-size: 55px;
            font-weight: bold;
            color: #333;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        """)
        title.setAlignment(Qt.AlignCenter)

        # 用户名输入框
        self.username = QLineEdit()
        self.username.setPlaceholderText("用户名")
        self.username.setFixedHeight(70)
        self.username.setStyleSheet("""
            QLineEdit {
                border-radius: 12px;
                padding: 12px;
                font-size: 30px;
                background: #eaecef;
                color: black;
            }
        """)

        # 密码输入框
        self.password = QLineEdit()
        self.password.setPlaceholderText("密码")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(70)
        self.password.setStyleSheet("""
            QLineEdit {
                border-radius: 12px;
                padding: 12px;
                font-size: 30px;
                background: #eaecef;
                color: black;
            }
        """)

        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.setFixedHeight(70)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a7bdc;
                color: white;
                font-size: 35px;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd8;
            }
        """)
        login_btn.clicked.connect(self.handle_login)

        # ================= 右侧布局组装 =================
        right_layout.addStretch()
        right_layout.addWidget(title)
        right_layout.addSpacing(35)
        right_layout.addWidget(self.username)
        right_layout.addWidget(self.password)
        right_layout.addWidget(login_btn)
        right_layout.addSpacing(10)
        right_layout.addStretch()

        # ================= 主布局比例 =================
        main_layout.addWidget(left_widget, 45)  # 左 40%
        main_layout.addWidget(right_widget, 55)  # 右 60%

        # ================= 登录逻辑 =================

    def handle_login(self):
        if self.username.text() and self.password.text():
            self.login_success.emit()
        else:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")


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
        self.report_views = {}

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # =========================================================
        # 🔹 顶部按钮（200x55 对齐监控）
        # =========================================================
        top_bar = QHBoxLayout()
        self.btn_analyze = QPushButton("▶ 开始分析")
        self.btn_analyze.setFixedSize(200, 55)
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 20px;
                font-weight: bold;
                font-family: "Microsoft YaHei";
                border-radius: 10px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6a7bdc,stop:1 #5a6fd8);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5a6fd8,stop:1 #4c5ec9);
            }
        """)
        self.btn_analyze.clicked.connect(self.start_analysis)
        top_bar.addWidget(self.btn_analyze)
        top_bar.addStretch()

        # =========================================================
        # 🔹 搜索 + 筛选栏
        # =========================================================
        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索 ID...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px;
                font-size: 20px;
                font-family: Microsoft YaHei;
            }
        """)

        # 筛选下拉框
        self.filter_box = QComboBox()
        self.filter_box.addItems(["全部", "安全", "风险"])
        self.filter_box.setFixedWidth(180)
        self.filter_box.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px;
                font-family: "Microsoft YaHei";
                font-size: 20px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { width:14px; height:14px; }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px;
                font-size: 18px;
                selection-background-color: #e0e7ff;
                selection-color: black;
            }
        """)

        search_row.addWidget(self.search_input)
        search_row.addWidget(self.filter_box)
        search_row.addStretch()

        # =========================================================
        # 🔹 表格（修复列宽+样式）
        # =========================================================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setShowGrid(False)
        self.table.setHorizontalHeaderLabels(
            ["ID", "时间", "敏感路径", "状态", "风险检测", "报告内容", "导出"]
        )
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                outline: none;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                color: #475569;
                font-weight: bold;
                font-size: 20px;
                font-family: "Microsoft YaHei";
            }
            QTableWidget::item {
                padding: 12px;
                font-size: 16px;
                border: none;
                font-family: "Microsoft YaHei";
            }
            QTableWidget::item:hover { background: #f9fafb; }
            QTableWidget::item:selected { background: #e0e7ff; color: black; }
        """)

        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        # ✅ 修复列宽：状态/风险/导出设固定最小宽度，不再过窄
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 时间
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # 路径（拉伸）
        header.setSectionResizeMode(3, QHeaderView.Fixed)             # 状态（固定）
        header.setSectionResizeMode(4, QHeaderView.Fixed)             # 风险（固定）
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # 报告（拉伸）
        header.setSectionResizeMode(6, QHeaderView.Fixed)             # 导出（固定）
        # 设置固定最小宽度
        self.table.setColumnWidth(3, 150)  # 状态列宽
        self.table.setColumnWidth(4, 160)  # 风险列宽
        self.table.setColumnWidth(6, 120)  # 导出列宽

        main_layout.addLayout(top_bar)
        main_layout.addLayout(search_row)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        # 信号绑定
        self.search_input.textChanged.connect(self.apply_filter)
        self.filter_box.currentTextChanged.connect(self.apply_filter)
        self.table.itemChanged.connect(self.fix_id_edit)  # ID编辑后保存

        # 加载所有历史记录
        self.load_all_history()
        self.is_loading_history = False  # 加在这里

        # self.clear_all_history()

    # =========================================================
    # 🔹 保存单条记录到文件（核心：ID修改后同步更新）
    # =========================================================
    def save_record_to_history(self, record_id, time_str, path, status, risk, content, old_id=None):
        # 重命名时删除旧文件，创建新文件
        if old_id and old_id != record_id:
            old_file = os.path.join(HISTORY_DIR, f"record_{old_id}.json")
            if os.path.exists(old_file):
                os.remove(old_file)
        # 写入新文件
        filename = f"record_{record_id}.json"
        filepath = os.path.join(HISTORY_DIR, filename)
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

    # =========================================================
    # 🔹 加载全部历史
    # =========================================================
    def load_all_history(self):
        self.is_loading_history = True
        self.table.setRowCount(0)
        if not os.path.exists(HISTORY_DIR):
            return
        files = sorted(os.listdir(HISTORY_DIR), reverse=True)
        for fn in files:
            if not fn.startswith("record_") or not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(HISTORY_DIR, fn), "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.add_history_row(data)
            except Exception as e:
                print(f"加载历史失败: {e}")
                continue
        self.is_loading_history = False

    def add_history_row(self, data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 110)

        # ID（纯数字，对齐监控字体）
        id_item = QTableWidgetItem(data["id"])
        id_item.setFlags(id_item.flags() | Qt.ItemIsEditable)
        id_item.setForeground(QColor("#64748b"))
        id_item.setFont(QFont("Microsoft YaHei", 8, QFont.Bold))
        self.table.setItem(row, 0, id_item)

        # 时间（字体放大）
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        bar = QWidget()
        bar.setFixedWidth(6)
        bar.setStyleSheet("background-color: #10b981; border-radius:3px;")
        label = QLabel(data["time"])
        label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(bar)
        layout.addSpacing(8)
        layout.addWidget(label)
        container.setLayout(layout)
        self.table.setCellWidget(row, 1, container)

        # 路径
        self.table.setItem(row, 2, QTableWidgetItem(data["path"]))

        # 状态：已完成（字体放大）
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        icon = QLabel("☑")
        icon.setStyleSheet("color: #22c55e; font-size:22px; font-weight:bold;")
        txt = QLabel("已完成")
        txt.setStyleSheet("color: #22c55e; font-size:20px; font-weight:bold;")
        status_layout.addStretch()
        status_layout.addWidget(icon)
        status_layout.addWidget(txt)
        status_layout.addStretch()
        status_layout.setContentsMargins(0,0,0,0)
        self.table.setCellWidget(row, 3, status_widget)

        # ✅ 风险：修复字体颜色（安全绿/风险红，非黑色）
        risk_widget = QWidget()
        risk_layout = QHBoxLayout(risk_widget)
        if data["risk"] == "✅ 安全":
            r_icon = QLabel("✅")
            r_txt = QLabel("安全")
            r_color = "#22c55e"
        else:
            r_icon = QLabel("⚠️")
            r_txt = QLabel("有风险")
            r_color = "#000000"

        r_icon.setStyleSheet(f"font-size:22px; font-weight:bold; color:{r_color};")
        r_txt.setStyleSheet(f"font-size:20px; font-weight:bold; color:{r_color};")
        risk_layout.addStretch()
        risk_layout.addWidget(r_icon)
        risk_layout.addWidget(r_txt)
        risk_layout.addStretch()
        risk_layout.setContentsMargins(0,0,0,0)
        self.table.setCellWidget(row, 4, risk_widget)

        # 报告
        report_view = QTextEdit()
        report_view.setReadOnly(True)
        report_view.setText(data["content"])
        report_view.setStyleSheet("""
            QTextEdit {
                background: white; border-radius:10px; padding:12px;
                font-size:25px; font-family:"Microsoft YaHei"; line-height:1.6;
            }
            QScrollBar:vertical { width:6px; background:transparent; }
            QScrollBar::handle:vertical { background:rgba(0,0,0,0.2); border-radius:3px; }
        """)
        self.report_views[row] = report_view
        self.table.setCellWidget(row, 5, report_view)

        # 导出按钮
        btn = QPushButton("导出")
        btn.setStyleSheet("""
            QPushButton {
                background-color:#10b981; color:white; border-radius:6px; padding:6px;
            }
            QPushButton:hover { background-color:#059669; }
        """)
        btn.clicked.connect(lambda: self.export_history(data["content"]))
        self.table.setCellWidget(row, 6, btn)

    # =========================================================
    # 🔹 开始分析
    # =========================================================
    def start_analysis(self):
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = 0
        self.table.insertRow(row)
        self.table.setRowHeight(row, 110)

        # ID（纯数字）
        id_num = self.get_next_id()
        id_item = QTableWidgetItem(id_num)
        id_item.setFlags(id_item.flags() | Qt.ItemIsEditable)
        id_item.setForeground(QColor("#64748b"))
        id_item.setFont(QFont("Microsoft YaHei", 8, QFont.Bold))
        self.table.setItem(row, 0, id_item)

        # 时间
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        bar = QWidget()
        bar.setFixedWidth(6)
        bar.setStyleSheet("background-color: orange; border-radius:3px;")
        label = QLabel(time_str)
        label.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(bar)
        layout.addSpacing(8)
        layout.addWidget(label)
        container.setLayout(layout)
        self.table.setCellWidget(row, 1, container)

        self.current_bar = bar
        self.current_row = row
        self.current_time = time_str
        self.current_id = id_num

        self.table.setItem(row, 2, QTableWidgetItem("分析中..."))
        self.table.setItem(row, 3, QTableWidgetItem("正在分析"))
        self.table.setItem(row, 4, QTableWidgetItem("检测中"))

        # 报告框
        report_view = QTextEdit()
        report_view.setReadOnly(True)
        report_view.setStyleSheet("""
            QTextEdit {
                background: white; border-radius:10px; padding:12px;
                font-size:25px; font-family:"Microsoft YaHei"; line-height:1.6;
            }
            QScrollBar:vertical { width:6px; background:transparent; }
        """)
        self.report_views[row] = report_view
        self.table.setCellWidget(row, 5, report_view)

        # 导出禁用
        btn = QPushButton("导出")
        btn.setEnabled(False)
        btn.setStyleSheet("background-color:#9ca3af; color:white; border-radius:6px; padding:8px;")
        self.table.setCellWidget(row, 6, btn)

        self.analyze_signal.emit()

    # =========================================================
    # 🔹 分析完成
    # =========================================================
    def finish_analysis(self, report_path, content):
        if self.current_row is None:
            return
        row = self.current_row

        self.table.setItem(row, 2, QTableWidgetItem(report_path))
        is_risk = "blacklist" in content.lower()
        risk_text = "⚠️ 有风险" if is_risk else "☑ 安全"

        # 状态：已完成
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        icon = QLabel("☑")
        icon.setStyleSheet("color: #22c55e; font-size:22px; font-weight:bold;")
        txt = QLabel("已完成")
        txt.setStyleSheet("color: #22c55e; font-size:20px; font-weight:bold;")
        status_layout.addStretch()
        status_layout.addWidget(icon)
        status_layout.addWidget(txt)
        status_layout.addStretch()
        status_layout.setContentsMargins(0,0,0,0)
        self.table.setCellWidget(row, 3, status_widget)

        # 风险：修复颜色
        risk_widget = QWidget()
        risk_layout = QHBoxLayout(risk_widget)
        if "安全" in risk_text:
            r_icon = QLabel("☑")
            r_txt = QLabel("安全")
            r_color = "#22c55e"
        else:
            r_icon = QLabel("⚠️")
            r_txt = QLabel("有风险")
            r_color = "#ef4444"

        r_icon.setStyleSheet(f"font-size:22px; font-weight:bold; color:{r_color};")
        r_txt.setStyleSheet(f"font-size:20px; font-weight:bold; color:{r_color};")
        risk_layout.addStretch()
        risk_layout.addWidget(r_icon)
        risk_layout.addWidget(r_txt)
        risk_layout.addStretch()
        risk_layout.setContentsMargins(0,0,0,0)
        self.table.setCellWidget(row, 4, risk_widget)

        # 报告内容
        report_view = self.report_views.get(row)
        if report_view:
            report_view.setText(content)

        # 导出按钮
        btn = QPushButton("导出")
        btn.setStyleSheet("""
            QPushButton {
                background-color:#10b981; color:white; border-radius:6px; padding:6px;
            }
            QPushButton:hover { background-color:#059669; }
        """)
        btn.clicked.connect(lambda: self.export_report(content))
        self.table.setCellWidget(row, 6, btn)

        # 进度条颜色
        if "blacklist" in content.lower():
            self.current_bar.setStyleSheet("background-color:red; border-radius:3px;")
        else:
            self.current_bar.setStyleSheet("background-color:#10b981; border-radius:3px;")

        # 保存到历史
        self.save_record_to_history(
            record_id=self.current_id,
            time_str=self.current_time,
            path=report_path,
            status="已完成",
            risk=risk_text,
            content=content
        )

    # =========================================================
    # 🔹 导出
    # =========================================================
    def export_report(self, content):
        path, _ = QFileDialog.getSaveFileName(self, "保存报告", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def export_history(self, content):
        path, _ = QFileDialog.getSaveFileName(self, "导出历史报告", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    # =========================================================
    # 🔹 筛选（修复风险筛选逻辑）
    # =========================================================
    def apply_filter(self):
        keyword = self.search_input.text().lower()
        mode = self.filter_box.currentText()
        for row in range(self.table.rowCount()):
            # ID匹配
            item_id = self.table.item(row, 0)
            id_text = item_id.text().lower() if item_id else ""
            match_id = keyword in id_text

            # 风险匹配
            match_risk = True
            if mode in ("安全", "风险"):
                risk_widget = self.table.cellWidget(row, 4)
                if risk_widget:
                    risk_label = risk_widget.layout().itemAt(2).widget()
                    risk_text = risk_label.text()
                    match_risk = (mode == "安全" and "安全" in risk_text) or (mode == "风险" and "风险" in risk_text)
                else:
                    match_risk = False

            self.table.setRowHidden(row, not (match_id and match_risk))

    # =========================================================
    # 🔹 ID编辑限制 + 永久保存（核心修复）
    # =========================================================
    def fix_id_edit(self, item):
        if item.column() != 0:
            return
        if self.is_loading_history:
            return
        row = item.row()
        self.table.blockSignals(True)

        # 1. 校验并修正ID
        old_id = item.data(Qt.UserRole) if item.data(Qt.UserRole) else item.text()
        new_id = item.text().strip()
        if not new_id:
            new_id = "0"
        elif len(new_id) > 5:
            new_id = new_id[:5]
        item.setText(new_id)
        item.setData(Qt.UserRole, old_id)  # 保存旧ID用于更新文件

        # 2. 实时同步更新历史JSON文件（永久保存）
        try:
            # 读取该行完整数据
            time_widget = self.table.cellWidget(row, 1)
            time_str = time_widget.layout().itemAt(2).widget().text() if time_widget else ""
            path_item = self.table.item(row, 2)
            path = path_item.text() if path_item else ""
            risk_widget = self.table.cellWidget(row, 4)
            risk_text = risk_widget.layout().itemAt(2).widget().text() if risk_widget else ""
            report_view = self.report_views.get(row)
            content = report_view.toPlainText() if report_view else ""

            # 更新历史文件
            self.save_record_to_history(
                record_id=new_id,
                time_str=time_str,
                path=path,
                status="已完成",
                risk=f"☑ 安全" if "安全" in risk_text else "⚠️ 有风险",
                content=content,
                old_id=old_id
            )
        except Exception as e:
            print(f"更新ID失败: {e}")

        self.table.blockSignals(False)

    def clear_all_history(self):
        # 清空表格
        self.table.setRowCount(0)
        # 清空文件
        if os.path.exists(HISTORY_DIR):
            for f in os.listdir(HISTORY_DIR):
                try:
                    os.remove(os.path.join(HISTORY_DIR, f))
                except:
                    pass

    def get_next_id(self):
        # 遍历所有历史记录，找最大ID，自动+1
        max_id = 0
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                try:
                    num = int(item.text())
                    if num > max_id:
                        max_id = num
                except:
                    pass
        return str(max_id + 1)

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
        layout = QHBoxLayout()

        layout.setSpacing(0)

        # ================= 左侧菜单容器 =================
        menu_widget = QWidget()
        menu_widget.setFixedWidth(240)
        menu_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a7bdc,
                    stop:1 #5a6fd8
                );
                border-top-right-radius: 30px;
                border-bottom-right-radius: 30px;
            }
        """)

        # ===== 顶部小圆点 =====
        dot_layout = QHBoxLayout()
        dot_layout.setSpacing(8)

        def create_dot(color):
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"""
                background-color: {color};
                border-radius: 6px;
            """)
            return dot

        dot_layout.addWidget(create_dot("#ff5f57"))  # 红
        dot_layout.addWidget(create_dot("#febc2e"))  # 黄
        dot_layout.addWidget(create_dot("#28c840"))  # 绿
        dot_layout.addStretch()

        menu_layout = QVBoxLayout()
        menu_layout.addLayout(dot_layout)
        menu_layout.addSpacing(10)
        menu_layout.setContentsMargins(10, 40, 10, 20)
        menu_layout.setSpacing(10)
        menu_widget.setLayout(menu_layout)

        # ================= 标题 =================
        title = QLabel("DataLeak\nDetector")
        title.setStyleSheet("""
            color: white;
            font-size: 30px;
            font-weight: bold;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        """)
        title.setAlignment(Qt.AlignCenter)

        menu_layout.addWidget(title)
        menu_layout.addSpacing(30)

        # ================= 菜单 =================
        self.menu = QListWidget()
        self.menu.addItem(QListWidgetItem(QIcon("icons/home.svg"), " 总览"))
        self.menu.addItem(QListWidgetItem(QIcon("icons/monitor.svg"), " 监控"))
        self.menu.addItem(QListWidgetItem(QIcon("icons/analysis.svg"), " 分析"))
        self.menu.setCurrentRow(0)

        self.menu.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                color: white;
                font-size: 30px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                outline: none;
            }

            QListWidget::item {
                padding: 22px;
                border-radius: 10px;
            }

            QListWidget::item:selected {
                background-color: rgba(255,255,255,0.2);
                font-weight: bold;
            }

            QListWidget::item:hover {
                background-color: rgba(255,255,255,0.1);
            }
        """)

        menu_layout.addWidget(self.menu)
        menu_layout.addStretch()

        # ================= 右侧页面 =================
        self.pages = QStackedWidget()

        self.dashboard = DashboardPro()
        self.monitor = MonitorPro()
        self.report = ReportPage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.monitor)
        self.pages.addWidget(self.report)
        container = QWidget()
        container.setAttribute(Qt.WA_StyledBackground, True)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)

        container_layout.addWidget(self.pages)

        container.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 20px;
        """)

        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)

        # ================= 阴影 =================
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)  # 模糊程度（越大越柔）
        shadow.setXOffset(0)
        shadow.setYOffset(5)  # 向下偏移（更真实）
        shadow.setColor(QColor(0, 0, 0, 80))  # 半透明黑

        # self.pages.setGraphicsEffect(shadow)

        # ================= 主布局 =================
        layout.addWidget(menu_widget)
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 20, 20)
        layout.setSpacing(20)

        self.main_page.setLayout(layout)

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

        base = os.path.join(main_app.RISK_DIR, "recordings", record_id, "results")
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
            background-color: #f5f7fb;   /* #f5f6fa; */
            color: black;
            font-family: "Microsoft YaHei";
        }

        QPushButton {
            background-color: #2563eb;
            padding: 6px;
            border-radius: 6px;
            color: white;
        }
    """)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())