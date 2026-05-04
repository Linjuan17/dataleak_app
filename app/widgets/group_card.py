#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组别卡片组件
用于日历视图中的组别展示
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

from models.data import MockData


class GroupCard(QFrame):
    """组别卡片组件"""

    clicked = pyqtSignal()

    def __init__(self, group, parent=None):
        super().__init__(parent)
        self.group = group
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 根据状态设置样式
        status = MockData.get_group_status(self.group)

        # 获取风险人数
        risk_count = sum(1 for emp in self.group['employees'] if emp.get('risk', False))
        total_count = len(self.group['employees'])

        if status == 'risk':
            status_dot_color = "#FF4757"
            status_text_color = "#FF4757"
            status_text = f"{risk_count}人存在风险"
        elif status == 'safe':
            status_dot_color = "#00D68F"
            status_text_color = "#00D68F"
            status_text = "无风险"
        else:
            status_dot_color = "#FFA502"
            status_text_color = "#FFA502"
            status_text = "未完全监控"

        # 有风险的卡片用淡红色渐变背景
        if status == 'risk':
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255, 71, 87, 0.08), stop:1 rgba(15, 23, 42, 0.6));
                    border-radius: 8px;
                    border: 1px solid rgba(255, 71, 87, 0.15);
                    border-left: 4px solid #FF4757;
                    padding: 10px 12px;
                }}
                QFrame:hover {{
                    border-color: rgba(255, 71, 87, 0.3);
                }}
            """)
        elif status == 'safe':
            self.setStyleSheet(f"""
                QFrame {{
                    background: rgba(17, 25, 40, 0.6);
                    border-radius: 8px;
                    border: 1px solid rgba(0, 212, 255, 0.08);
                    border-left: 4px solid #00D68F;
                    padding: 10px 12px;
                }}
                QFrame:hover {{
                    border-color: rgba(0, 212, 255, 0.15);
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: rgba(17, 25, 40, 0.6);
                    border-radius: 8px;
                    border: 1px solid rgba(0, 212, 255, 0.08);
                    border-left: 4px solid #FFA502;
                    padding: 10px 12px;
                }}
                QFrame:hover {{
                    border-color: rgba(0, 212, 255, 0.15);
                }}
            """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 两行布局：第一行组名，第二行其他信息
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 第一行：状态圆点 + 组名
        line1 = QHBoxLayout()
        line1.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {status_dot_color}; font-size: 10px; background: transparent; padding: 0; border: none;")

        name = QLabel(self.group['name'])
        name.setStyleSheet("color: #E8ECF1; font-size: 15px; font-weight: 600; background: transparent; border: none;")

        line1.addWidget(dot)
        line1.addWidget(name)
        line1.addStretch()

        # 第二行：人数 + 风险描述（去掉线框）
        line2 = QHBoxLayout()
        line2.setSpacing(10)

        # 人数
        count = QLabel(f"{total_count}人")
        count.setStyleSheet("""
            background: rgba(0, 212, 255, 0.08);
            color: #8B95A5;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            border: 1px solid rgba(0, 212, 255, 0.1);
        """)

        # 风险描述（无线框）
        risk_label = QLabel(status_text)
        risk_label.setStyleSheet(f"color: {status_text_color}; font-size: 11px; background: transparent; border: none;")

        line2.addWidget(count)
        line2.addWidget(risk_label)
        line2.addStretch()

        layout.addLayout(line1)
        layout.addLayout(line2)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
