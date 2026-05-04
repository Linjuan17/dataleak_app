#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面2：按组别分类视图（看板）
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QLabel, QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from models.data import MockData


class GroupView(QWidget):
    """按组别分类视图（看板）"""

    # 导航信号
    navigate_to_group = pyqtSignal(str)
    navigate_to_employee = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_mode = "all"
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("background-color: #0A0E17;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 筛选栏
        filter_container = QWidget()
        filter_container.setStyleSheet("""
            background: rgba(17, 25, 40, 0.85);
            border-radius: 12px;
            padding: 12px 16px;
        """)
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(12)

        filter_label = QLabel("筛选：")
        filter_label.setStyleSheet("color: #8B95A5; font-size: 14px;")

        self.filter_buttons = []
        filters = [
            ("显示全部", "all"),
            ("仅显示有风险的", "risk"),
            ("仅显示安全的", "safe"),
            ("仅显示未监控的", "unmonitored")
        ]

        for text, value in filters:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setChecked(value == "all")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=value: self.set_filter(v))

            style = """
                QPushButton {
                    background: %s;
                    border: 1px solid %s;
                    border-radius: 20px;
                    padding: 8px 14px;
                    font-size: 13px;
                    color: %s;
                }
                QPushButton:hover {
                    border-color: #00D4FF;
                    color: #00D4FF;
                }
            """

            if value == "all":
                btn.setStyleSheet(style % (
                    "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00D4FF, stop:1 #0099CC)",
                    "transparent",
                    "#0A0E17"
                ))
            else:
                btn.setStyleSheet(style % ("transparent", "rgba(0, 212, 255, 0.15)", "#8B95A5"))

            self.filter_buttons.append((btn, value))
            filter_layout.addWidget(btn)

        filter_layout.addWidget(filter_label)
        filter_layout.addStretch()

        main_layout.addWidget(filter_container)

        # 滚动区域 - 修改滚动条样式为白底深蓝色
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal, QScrollBar:vertical {
                background: white;
                width: 10px;
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
                background: #0044BB;
                min-height: 20px;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background: none;
            }
        """)

        # 看板网格
        self.kanban_grid = QGridLayout()
        self.kanban_grid.setSpacing(20)
        self.kanban_grid.setAlignment(Qt.AlignmentFlag.AlignLeft)

        container = QWidget()
        container.setLayout(self.kanban_grid)
        scroll.setWidget(container)

        main_layout.addWidget(scroll, 1)

    def load_data(self):
        """加载数据"""
        self.populate_kanban()

    def populate_kanban(self):
        """填充看板"""
        # 清除现有内容
        while self.kanban_grid.count():
            item = self.kanban_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        col = 0
        max_cols = 4

        for group in MockData.groups:
            if not self.should_show_group(group):
                continue

            column = self.create_column(group)
            self.kanban_grid.addWidget(column, 0, col)
            col += 1

    def create_column(self, group):
        """创建看板列"""
        column = QFrame()
        column.setMinimumWidth(280)
        column.setMaximumWidth(320)
        column.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.5);
                border-radius: 16px;
                border: 1px solid rgba(0, 212, 255, 0.12);
            }
        """)

        layout = QVBoxLayout(column)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 列标题
        header = QFrame()
        header.setStyleSheet("border-bottom: 2px solid #00D4FF; padding-bottom: 12px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(group['name'])
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #E8ECF1; background: transparent;")
        title.setCursor(Qt.CursorShape.PointingHandCursor)
        title.mousePressEvent = lambda e, g=group: self.navigate_to_group.emit(g['id'])

        count = QLabel(str(len(group['employees'])))
        count.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00D4FF, stop:1 #0099CC);
            color: #0A0E17;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 600;
        """)

        header_layout.addWidget(title)
        header_layout.addWidget(count)
        header_layout.addStretch()

        layout.addWidget(header)

        # 员工卡片列表
        cards_container = QVBoxLayout()
        cards_container.setSpacing(12)

        for emp in group['employees']:
            card = self.create_employee_card(emp)
            cards_container.addWidget(card)

        cards_container.addStretch()
        layout.addLayout(cards_container)

        return column

    def create_employee_card(self, employee):
        """创建员工卡片"""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        # 根据状态设置样式
        if employee['monitored'] and employee['risk']:
            card.setStyleSheet("""
                QFrame {
                    background: rgba(17, 25, 40, 0.85);
                    border-radius: 12px;
                    border: 1px solid rgba(0, 212, 255, 0.12);
                    border-left: 4px solid #FF4757;
                    padding: 16px;
                }
                QFrame:hover {
                    border-color: rgba(0, 212, 255, 0.35);
                }
            """)
        elif employee['monitored']:
            card.setStyleSheet("""
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
            card.setStyleSheet("""
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

        card.mousePressEvent = lambda e, emp=employee: self.navigate_to_employee.emit(emp['id'])

        layout = QHBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 头像
        avatar = QLabel(employee['avatar'])
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

        name = QLabel(employee['name'])
        name.setStyleSheet("color: #E8ECF1; font-size: 14px; font-weight: 600;")

        position = QLabel(employee['position'])
        position.setStyleSheet("color: #8B95A5; font-size: 12px;")

        info_layout.addWidget(name)
        info_layout.addWidget(position)

        # 徽章
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(4)

        if employee['monitored']:
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

        if employee['risk']:
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

        return card

    def should_show_group(self, group):
        """判断是否应该显示组别"""
        status = MockData.get_group_status(group)

        if self.filter_mode == "all":
            return True
        elif self.filter_mode == "risk":
            return status == "risk"
        elif self.filter_mode == "safe":
            return status == "safe"
        elif self.filter_mode == "unmonitored":
            return status == "warning"
        return True

    def set_filter(self, mode):
        """设置筛选模式"""
        self.filter_mode = mode

        # 更新按钮样式
        for btn, value in self.filter_buttons:
            if value == mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #00D4FF, stop:1 #0099CC);
                        border: none;
                        border-radius: 20px;
                        padding: 8px 14px;
                        font-size: 13px;
                        color: #0A0E17;
                    }
                    QPushButton:hover {
                        border-color: #00D4FF;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: 1px solid rgba(0, 212, 255, 0.15);
                        border-radius: 20px;
                        padding: 8px 14px;
                        font-size: 13px;
                        color: #8B95A5;
                    }
                    QPushButton:hover {
                        border-color: #00D4FF;
                        color: #00D4FF;
                    }
                """)

        self.populate_kanban()