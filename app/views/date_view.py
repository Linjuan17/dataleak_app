#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面1：按日期分类视图
包含年月选择器和日历月视图
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QLabel, QPushButton, QButtonGroup, QLineEdit,
                             QFrame, QGridLayout, QCheckBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush, QPen

from models.data import MockData
from widgets.group_card import GroupCard


class DateView(QWidget):
    """日期分类视图"""

    # 导航信号
    navigate_to_group = pyqtSignal(str)
    navigate_to_employee = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = 2026
        self.current_month = 4
        self.view_mode = "date"  # date | group
        self.kanban_filter = "all"
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("background-color: #0A0E17;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 分类标签切换
        self.category_tabs = QButtonGroup()
        tab_container = QWidget()
        tab_container.setStyleSheet("""
            background: rgba(17, 25, 40, 0.85);
            border-radius: 12px;
            padding: 6px;
        """)
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(8)

        self.tab_calendar = QPushButton("按日期分类")
        self.tab_calendar.setCheckable(True)
        self.tab_calendar.setChecked(True)
        self.tab_calendar.setFixedHeight(36)
        self.tab_calendar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #0099CC);
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 600;
                color: #0A0E17;
            }
        """)

        self.tab_kanban = QPushButton("按组别分类")
        self.tab_kanban.setCheckable(True)
        self.tab_kanban.setFixedHeight(36)
        self.tab_kanban.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
                color: #8B95A5;
            }
            QPushButton:hover {
                color: #00D4FF;
            }
        """)

        self.category_tabs.addButton(self.tab_calendar, 0)
        self.category_tabs.addButton(self.tab_kanban, 1)

        tab_layout.addWidget(self.tab_calendar)
        tab_layout.addWidget(self.tab_kanban)

        self.category_tabs.buttonClicked.connect(self.on_tab_changed)
        main_layout.addWidget(tab_container)

        # 日期选择器（仅日期视图显示）
        self.date_picker_widget = QWidget()
        date_picker_layout = QHBoxLayout(self.date_picker_widget)
        date_picker_layout.setContentsMargins(0, 0, 0, 0)
        date_picker_layout.setSpacing(16)

        date_label = QLabel("选择月份：")
        date_label.setStyleSheet("color: #8B95A5; font-size: 14px;")

        # 左箭头
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(32, 32)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 8px;
                color: #8B95A5;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 212, 255, 0.08);
                border-color: #00D4FF;
                color: #00D4FF;
            }
        """)
        self.btn_prev.clicked.connect(lambda: self.change_month(-1))

        # 月份输入
        self.month_input = QLineEdit()
        self.month_input.setObjectName("month_input")
        self.month_input.setFixedSize(120, 32)
        self.month_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_input.setText(f"{self.current_year}-{self.current_month:02d}")
        self.month_input.textChanged.connect(self.on_month_text_changed)

        # 右箭头
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(32, 32)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 8px;
                color: #8B95A5;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 212, 255, 0.08);
                border-color: #00D4FF;
                color: #00D4FF;
            }
        """)
        self.btn_next.clicked.connect(lambda: self.change_month(1))

        date_picker_layout.addWidget(date_label)
        date_picker_layout.addWidget(self.btn_prev)
        date_picker_layout.addWidget(self.month_input)
        date_picker_layout.addWidget(self.btn_next)
        date_picker_layout.addStretch()

        main_layout.addWidget(self.date_picker_widget)

        # 筛选栏（仅看板视图显示）
        self.filter_widget = QWidget()
        self.filter_widget.setVisible(False)
        filter_layout = QHBoxLayout(self.filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(12)

        filter_label = QLabel("筛选：")
        filter_label.setStyleSheet("color: #8B95A5; font-size: 14px;")
        filter_layout.addWidget(filter_label)  # 在按钮之前添加标签

        self.filter_group = QButtonGroup()
        filter_options = [
            ("显示全部", "all"),
            ("仅显示有风险的", "risk"),
            ("仅显示安全的", "safe"),
            ("仅显示未监控的", "unmonitored")
        ]

        for text, value in filter_options:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("filter_btn")
            if value == "all":
                btn.setChecked(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1px solid rgba(0, 212, 255, 0.15);
                    border-radius: 20px;
                    padding: 8px 14px;
                    font-size: 13px;
                    color: #8B95A5;
                }
                QPushButton:checked {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00D4FF, stop:1 #0099CC);
                    border-color: transparent;
                    color: #0A0E17;
                }
                QPushButton:hover {
                    border-color: #00D4FF;
                    color: #00D4FF;
                }
            """)
            # 修正按钮ID计算逻辑
            option_ids = [opt[1] for opt in filter_options]
            btn_id = option_ids.index(value)
            self.filter_group.addButton(btn, id=btn_id)
            filter_layout.addWidget(btn)

        self.filter_group.idClicked.connect(self.on_filter_changed)
        filter_layout.addStretch()  # 将筛选控件推到左侧

        main_layout.addWidget(self.filter_widget)

        # 日历视图容器
        self.calendar_container = QWidget()
        calendar_layout = QVBoxLayout(self.calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: white; /* 白底 */
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #0044BB; /* 深蓝色 */
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background: none;
            }
        """)

        # 日历网格
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(20)
        self.calendar_grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        calendar_content = QWidget()
        calendar_content.setLayout(self.calendar_grid)
        scroll.setWidget(calendar_content)
        calendar_layout.addWidget(scroll, 1)

        main_layout.addWidget(self.calendar_container, 1)

        # 看板视图容器
        self.kanban_container = QWidget()
        self.kanban_container.setVisible(False)
        kanban_layout = QVBoxLayout(self.kanban_container)
        kanban_layout.setContentsMargins(0, 0, 0, 0)

        self.kanban_scroll = QScrollArea()
        self.kanban_scroll.setWidgetResizable(True)
        self.kanban_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.kanban_scroll.setStyleSheet(scroll.styleSheet())

        self.kanban_grid = QGridLayout()
        self.kanban_grid.setSpacing(20)

        kanban_content = QWidget()
        kanban_content.setLayout(self.kanban_grid)
        self.kanban_scroll.setWidget(kanban_content)
        kanban_layout.addWidget(self.kanban_scroll)

        main_layout.addWidget(self.kanban_container, 1)

    def load_data(self):
        """加载数据"""
        self.populate_calendar_view()
        self.populate_kanban_view()

    def populate_calendar_view(self):
        """填充日历视图"""
        # 清除现有内容
        while self.calendar_grid.count():
            item = self.calendar_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 获取当前月份的数据
        month_key = f"{self.current_year}-{self.current_month:02d}"
        dates = MockData.all_dates.get(month_key, [])

        if not dates:
            # 如果没有数据，显示所有组别作为演示
            dates = [f"{self.current_year}-{self.current_month:02d}-15"]

        col = 0
        row = 0
        max_cols = 3  # 日历网格：3列，让每个日期卡有足够空间展示组别信息

        for date_str in dates:
            # 创建日期卡片
            day_widget = self.create_day_card(date_str)
            self.calendar_grid.addWidget(day_widget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_day_card(self, date_str):
        """创建日期卡片 - 带组别卡片版本"""
        card = QFrame()
        card.setObjectName("day_card")
        card.setStyleSheet("""
            QFrame#day_card {
                background: rgba(17, 25, 40, 0.85);
                border: 1px solid rgba(0, 212, 255, 0.12);
                border-radius: 12px;
            }
            QFrame#day_card:hover {
                border-color: rgba(0, 212, 255, 0.35);
            }
        """)
        card.setFixedWidth(400)  # 足够宽以展示组别卡片
        card.setMinimumHeight(280)  # 设置最小高度

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 日期头部
        header = QHBoxLayout()
        header.setSpacing(8)

        date_label = QLabel(date_str)  # 显示完整日期
        date_label.setStyleSheet("color: #E8ECF1; font-size: 15px; font-weight: 600;")

        weekday_label = QLabel(self.get_weekday(date_str))
        weekday_label.setStyleSheet("""
            color: #00D4FF; 
            font-size: 12px;
            background: rgba(0, 212, 255, 0.08);
            padding: 4px 10px;
            border-radius: 8px;
        """)

        header.addWidget(date_label)
        header.addWidget(weekday_label)
        header.addStretch()

        layout.addLayout(header)

        # 分隔线
        divider = QFrame()
        divider.setStyleSheet("border-bottom: 1px solid rgba(0, 212, 255, 0.1);")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # 遍历该日期的所有组别，每个组别用 GroupCard 组件渲染
        for group in MockData.groups:
            group_card = GroupCard(group)
            group_card.clicked.connect(lambda g=group: self.navigate_to_group.emit(g['id']))
            layout.addWidget(group_card)

        return card

    def populate_kanban_view(self):
        """填充看板视图"""
        # 清除现有内容
        while self.kanban_grid.count():
            item = self.kanban_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        col = 0
        max_cols = 4

        for group in MockData.groups:
            # 根据筛选条件过滤
            if not self.should_show_group(group):
                continue

            column = self.create_kanban_column(group)
            self.kanban_grid.addWidget(column, 0, col)
            col += 1

    def create_kanban_column(self, group):
        """创建看板列"""
        column = QFrame()
        column.setObjectName("kanban_column")
        column.setStyleSheet("""
            QFrame#kanban_column {
                background: rgba(15, 23, 42, 0.5);
                border-radius: 16px;
                border: 1px solid rgba(0, 212, 255, 0.12);
                min-width: 280px;
            }
        """)
        column.setFixedWidth(300)

        layout = QVBoxLayout(column)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 列标题
        header = QHBoxLayout()

        title = QLabel(group['name'])
        title.setStyleSheet("color: #E8ECF1; font-size: 16px; font-weight: 600;")

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

        header.addWidget(title)
        header.addWidget(count)
        header.addStretch()

        # 标题底部边框
        header_frame = QFrame()
        header_frame.setStyleSheet("border-bottom: 2px solid #00D4FF; padding-bottom: 12px;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addLayout(header)

        layout.addWidget(header_frame)

        # 员工卡片
        for emp in group['employees']:
            emp_card = self.create_employee_card(emp, group)
            layout.addWidget(emp_card)

        layout.addStretch()

        return column

    def create_employee_card(self, employee, group):
        """创建员工卡片"""
        card = QFrame()
        card.setObjectName("employee_card")

        # 根据状态设置样式
        if employee['monitored']:
            if employee['risk']:
                card.setStyleSheet("""
                    QFrame#employee_card {
                        background: rgba(17, 25, 40, 0.85);
                        border-radius: 12px;
                        border: 1px solid rgba(0, 212, 255, 0.12);
                        border-left: 4px solid #FF4757;
                        padding: 16px;
                    }
                    QFrame#employee_card:hover {
                        border-color: rgba(0, 212, 255, 0.35);
                    }
                """)
            else:
                card.setStyleSheet("""
                    QFrame#employee_card {
                        background: rgba(17, 25, 40, 0.85);
                        border-radius: 12px;
                        border: 1px solid rgba(0, 212, 255, 0.12);
                        border-left: 4px solid #00D68F;
                        padding: 16px;
                    }
                    QFrame#employee_card:hover {
                        border-color: rgba(0, 212, 255, 0.35);
                    }
                """)
        else:
            card.setStyleSheet("""
                QFrame#employee_card {
                    background: rgba(17, 25, 40, 0.85);
                    border-radius: 12px;
                    border: 1px solid rgba(0, 212, 255, 0.12);
                    border-left: 4px solid #4a5568;
                    padding: 16px;
                }
                QFrame#employee_card:hover {
                    border-color: rgba(0, 212, 255, 0.35);
                }
            """)

        card.setCursor(Qt.CursorShape.PointingHandCursor)
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
        name.setStyleSheet("color: #E8ECF1; font-size: 14px; font-weight: 600; border: none;")

        position = QLabel(employee['position'])
        position.setStyleSheet("color: #8B95A5; font-size: 12px;")

        info_layout.addWidget(name)
        info_layout.addWidget(position)

        # 徽章 + 监控开关
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
        else:
            unmonitored_badge = QLabel("未监控")
            unmonitored_badge.setStyleSheet("""
                background: rgba(74, 85, 104, 0.15);
                color: #8B95A5;
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 10px;
                border: 1px solid rgba(74, 85, 104, 0.2);
            """)
            badges_layout.addWidget(unmonitored_badge)

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

        badges_layout.addStretch()

        # 单人监控开关
        monitor_switch = QCheckBox()
        monitor_switch.setChecked(employee['monitored'])
        monitor_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        monitor_switch.setStyleSheet("""
            QCheckBox {
                background: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                background: rgba(0, 212, 255, 0.15);
                border: 1px solid rgba(0, 212, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #00FFA3);
                border: none;
            }
        """)
        monitor_switch.stateChanged.connect(
            lambda state, eid=employee['id']: self.on_kanban_monitor_toggle(eid, state == Qt.CheckState.Checked.value)
        )
        # 阻止开关点击冒泡到卡片（防止切换时跳转员工详情）
        monitor_switch.mousePressEvent = lambda e: (
            monitor_switch.setChecked(not monitor_switch.isChecked()),
            e.accept()
        )[1]

        badges_layout.addWidget(monitor_switch)

        info_layout.addLayout(badges_layout)

        layout.addWidget(avatar)
        layout.addLayout(info_layout, 1)

        return card

    def should_show_group(self, group):
        """判断是否应该显示组别"""
        status = MockData.get_group_status(group)

        if self.kanban_filter == "all":
            return True
        elif self.kanban_filter == "risk":
            return status == "risk"
        elif self.kanban_filter == "safe":
            return status == "safe"
        elif self.kanban_filter == "unmonitored":
            return status == "warning"
        return True

    def on_kanban_monitor_toggle(self, employee_id, monitored):
        """看板视图单人监控切换"""
        for group in MockData.groups:
            for emp in group['employees']:
                if emp['id'] == employee_id:
                    emp['monitored'] = monitored
                    if not monitored:
                        emp['risk'] = False
                    break
        # 刷新看板视图
        self.populate_kanban_view()
        # 同时刷新日历视图（组别卡片状态也会变）
        self.populate_calendar_view()

    def on_tab_changed(self, button):
        """标签切换"""
        id = self.category_tabs.id(button)
        if id == 0:
            self.view_mode = "date"
            self.date_picker_widget.setVisible(True)
            self.filter_widget.setVisible(False)
            self.calendar_container.setVisible(True)
            self.kanban_container.setVisible(False)
            self.tab_calendar.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00D4FF, stop:1 #0099CC);
                    border: none;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #0A0E17;
                }
            """)
            self.tab_kanban.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    color: #8B95A5;
                }
                QPushButton:hover {
                    color: #00D4FF;
                }
            """)
        else:
            self.view_mode = "group"
            self.date_picker_widget.setVisible(False)
            self.filter_widget.setVisible(True)
            self.calendar_container.setVisible(False)
            self.kanban_container.setVisible(True)
            self.tab_kanban.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00D4FF, stop:1 #0099CC);
                    border: none;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #0A0E17;
                }
            """)
            self.tab_calendar.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    color: #8B95A5;
                }
                QPushButton:hover {
                    color: #00D4FF;
                }
            """)

    def on_filter_changed(self, id):
        """筛选条件变化"""
        filters = ["all", "risk", "safe", "unmonitored"]
        if id < len(filters):
            self.kanban_filter = filters[id]
            self.populate_kanban_view()

    def change_month(self, delta):
        """切换月份"""
        self.current_month += delta
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self.month_input.setText(f"{self.current_year}-{self.current_month:02d}")
        self.populate_calendar_view()

    def on_month_text_changed(self, text):
        """月份文本变化"""
        try:
            parts = text.split('-')
            if len(parts) == 2:
                year = int(parts[0])
                month = int(parts[1])
                if 2000 <= year <= 2100 and 1 <= month <= 12:
                    self.current_year = year
                    self.current_month = month
                    self.populate_calendar_view()
        except ValueError:
            pass

    def get_weekday(self, date_str):
        """获取星期几"""
        from datetime import datetime
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            return weekdays[date.weekday()]
        except:
            return ""
