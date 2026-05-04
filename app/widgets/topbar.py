#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顶部导航栏组件
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFrame, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QBrush, QColor, QPen
from datetime import datetime

# ============================================================================
# 颜色定义 (整合自 main.py 和 DATA1/widgets/topbar.py)
# ============================================================================
BG_NAV = "#08101A"
ACCENT_CYAN = "#00F2FF"
ACCENT_BLUE = "#3B82F6"
TEXT_PRIMARY = "#F1F5F9"
TEXT_DIM = "#64748B"

# ============================================================================
# 圆形渐变头像（林） - 从 main.py 复制
# ============================================================================
class AvatarLabel(QLabel):
    def __init__(self, text="林", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(36, 36)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        start = QPointF(rect.topLeft())
        end = QPointF(rect.bottomRight())
        grad = QLinearGradient(start, end)
        grad.setColorAt(0, QColor(ACCENT_CYAN))
        grad.setColorAt(1, QColor(ACCENT_BLUE))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        painter.setPen(QPen(QColor("white")))
        painter.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class TopBar(QWidget):
    """顶部导航栏"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setup_ui()
        # 时间刷新定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()
        # 连接通知按钮点击事件
        self.notify_btn.clicked.connect(self.show_notifications)

    def setup_ui(self):
        """设置UI"""
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            #topbar {{
                background: {BG_NAV};
                border-bottom: 1px solid rgba(0, 212, 255, 0.15);
            }}
            QPushButton#notify_btn, QPushButton#settings_btn {{
                background: transparent;
                border: none;
                border-radius: 50%;
                font-size: 16px;
                color: {TEXT_DIM};
            }}
            QPushButton#notify_btn:hover, QPushButton#settings_btn:hover {{
                background: rgba(0, 212, 255, 0.08);
                color: {ACCENT_CYAN};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # 标题
        self.title_label = QLabel("DataLeakDetector")
        self.title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: 0.5px;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # 时间标签
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"color: {TEXT_DIM}; font-family: 'Consolas'; font-size: 11px;")
        layout.addWidget(self.time_label)

        # 通知按钮 + 角标
        notify_container = QWidget()
        notify_layout = QHBoxLayout(notify_container)
        notify_layout.setContentsMargins(0, 0, 0, 0)
        notify_layout.setSpacing(0)
        self.notify_btn = QPushButton("🔔")
        self.notify_btn.setObjectName("notify_btn")
        self.notify_btn.setFixedSize(36, 36)

        self.notify_badge = QLabel("3")
        self.notify_badge.setStyleSheet(f"""
            background-color: #EF4444; color: white; font-size: 9px; font-weight: bold;
            border-radius: 10px; padding: 2px 5px; min-width: 16px; max-height: 16px;
        """)
        self.notify_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notify_layout.addWidget(self.notify_btn)
        notify_layout.addWidget(self.notify_badge, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        notify_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(notify_container)

        # 设置按钮
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.settings_btn)

        # 用户头像
        self.user_avatar = AvatarLabel("林")
        self.user_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.user_avatar)

    def _update_time(self):
        """更新时间标签"""
        self.time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def show_notifications(self):
        """点击铃铛弹出消息菜单"""
        menu = QMenu(self)

        # 模拟的三条消息（基于员工敏感操作）
        messages = [
            {"time": "14:23:05", "employee": "周丽华", "action": "外发敏感文件 contract.docx"},
            {"time": "14:15:32", "employee": "周丽华", "action": "违规软件录屏行为"},
            {"time": "13:58:11", "employee": "周丽华", "action": "异常登录 IP 192.168.1.105"}
        ]

        for msg in messages:
            text = f"{msg['time']}  {msg['employee']}  {msg['action']}"
            action = menu.addAction(text)
            action.setEnabled(False)  # 仅展示，不可点击

        # 可以添加一个“标记全部已读”的选项（可选）
        menu.addSeparator()
        clear_action = menu.addAction("标记全部已读")
        clear_action.triggered.connect(self.clear_notifications)

        # 在按钮下方弹出菜单
        menu.exec(self.notify_btn.mapToGlobal(self.notify_btn.rect().bottomLeft()))

    def clear_notifications(self):
        """清除通知角标（模拟已读）"""
        self.notify_badge.setText("0")
        self.notify_badge.hide()
        # 实际项目中可隐藏角标或修改数字