#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工卡片组件
用于看板视图中的员工展示
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class EmployeeCard(QFrame):
    """员工卡片组件"""

    clicked = pyqtSignal()

    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 根据状态设置样式
        if self.employee['monitored'] and self.employee['risk']:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(17, 25, 40, 0.85);
                    border-radius: 12px;
                    border: none;
                    border-left: 4px solid #FF4757;
                    padding: 16px;
                }
                QFrame:hover {
                    border-color: rgba(0, 212, 255, 0.35);
                }
            """)
        elif self.employee['monitored']:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(17, 25, 40, 0.85);
                    border-radius: 12px;
                    border: 1px solid rgba(0, 212, 255, 0.12);
                    border-left: 4px solid #00D68F;
                    padding: 16px;
                }
                QFrame:hover {
                    border-color: rgba(0, 212, 255, 0.35);
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(17, 25, 40, 0.85);
                    border-radius: 12px;
                    border: 1px solid rgba(0, 212, 255, 0.12);
                    padding: 16px;
                }
                QFrame:hover {
                    border-color: rgba(0, 212, 255, 0.35);
                }
            """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 头像
        avatar = QLabel(self.employee['avatar'])
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00D4FF, stop:1 #00FFA3);
            border-radius: 22px;
            color: #0A0E17;
            font-weight: 600;
            font-size: 14px;
        """)

        # 信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name = QLabel(self.employee['name'])
        name.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.DemiBold))
        name.setStyleSheet("color: #E8ECF1;")

        position = QLabel(self.employee['position'])
        position.setStyleSheet("color: #8B95A5; font-size: 12px;")

        info_layout.addWidget(name)
        info_layout.addWidget(position)

        # 徽章
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(4)

        if self.employee['monitored']:
            monitor_badge = QLabel("监控中")
            monitor_badge.setStyleSheet("""
                background: rgba(0, 212, 255, 0.15);
                color: #00D4FF;
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 10px;
                border: 1px solid rgba(0, 212, 255, 0.2);
            """)
            badges_layout.addWidget(monitor_badge)

        if self.employee['risk']:
            risk_badge = QLabel("风险")
            risk_badge.setStyleSheet("""
                background: rgba(255, 71, 87, 0.15);
                color: #FF4757;
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 10px;
                border: 1px solid rgba(255, 71, 87, 0.2);
            """)
            badges_layout.addWidget(risk_badge)

        info_layout.addLayout(badges_layout)

        layout.addWidget(avatar)
        layout.addLayout(info_layout, 1)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
