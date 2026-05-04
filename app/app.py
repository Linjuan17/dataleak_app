#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
包含左侧导航栏、顶部栏、页面切换
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QLabel, QLineEdit, QPushButton, QToolButton,
                             QButtonGroup, QGraphicsView, QGraphicsScene, QScrollArea)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient, QIcon, QAction

from widgets.sidebar import Sidebar
from widgets.topbar import TopBar
from views.date_view import DateView
from views.group_view import GroupView
from views.org_view import OrgView
from views.employee_view import EmployeeView
from views.monitor_view import MonitorView

# Import your pages
from risk_overview import RiskOverviewPage
from backlist import BlacklistPage
from widgets.system_monitor_bar import SystemMonitorBar


class SettingsPage(QWidget):
    """设置页面占位符"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder = QLabel("⚙️ 设置页面\n（待开发）")
        placeholder.setStyleSheet("color: #64748B; font-size: 18pt; font-weight: bold;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)


class MainWindow(QWidget):
    # Define page indices
    PAGE_RISK_OVERVIEW = 0
    PAGE_PERSONNEL_MANAGEMENT = 1
    PAGE_BLACKLIST = 2
    PAGE_ORG_VIEW = 3
    PAGE_EMPLOYEE_VIEW = 4
    PAGE_MONITOR_VIEW = 5

    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")

        # 创建页面（直接使用原始页面，不额外包裹 QScrollArea）
        self.risk_overview_page = RiskOverviewPage()
        self.blacklist_page = BlacklistPage()

        # DATA1's existing pages
        self.date_view = DateView()
        self.date_view.navigate_to_group.connect(self.show_org_view)
        self.date_view.navigate_to_employee.connect(self.show_employee_view)

        self.group_view = GroupView()
        self.group_view.navigate_to_group.connect(self.show_org_view)
        self.group_view.navigate_to_employee.connect(self.show_employee_view)

        self.org_view = OrgView()
        self.org_view.navigate_back.connect(self.back_to_personnel_list)
        self.org_view.navigate_to_employee.connect(self.show_employee_view)

        self.employee_view = EmployeeView()
        self.employee_view.navigate_back.connect(self.back_to_org_view)
        self.employee_view.navigate_to_monitor.connect(self.show_monitor_view)

        self.monitor_view = MonitorView()
        self.monitor_view.navigate_back.connect(self.back_to_employee_view)

        # 添加页面到堆栈
        self.stacked_widget.addWidget(self.risk_overview_page)   # 0
        self.stacked_widget.addWidget(self.date_view)            # 1
        self.stacked_widget.addWidget(self.blacklist_page)       # 2
        self.stacked_widget.addWidget(self.org_view)             # 3
        self.stacked_widget.addWidget(self.employee_view)        # 4
        self.stacked_widget.addWidget(self.monitor_view)         # 5

        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.on_sidebar_page_changed)

        self.topbar = TopBar()

        self.main_layout.addWidget(self.sidebar)

        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.topbar)
        content_layout.addWidget(self.stacked_widget)

        self.main_layout.addWidget(content_container)

        self.system_monitor_bar = SystemMonitorBar()
        content_layout.addWidget(self.system_monitor_bar)

        self.main_layout.setStretch(0, 0)
        self.main_layout.setStretch(1, 1)

        self.current_view_mode = "date"
        self.view_history = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("数据泄露检测系统 - 企业管理端")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0A0E17;
                color: #E8ECF1;
            }
        """)

    def on_sidebar_page_changed(self, page_index):
        if page_index == self.PAGE_RISK_OVERVIEW:
            self.stacked_widget.setCurrentIndex(self.PAGE_RISK_OVERVIEW)
        elif page_index == self.PAGE_PERSONNEL_MANAGEMENT:
            self.stacked_widget.setCurrentIndex(self.PAGE_PERSONNEL_MANAGEMENT)
        elif page_index == self.PAGE_BLACKLIST:
            self.stacked_widget.setCurrentIndex(self.PAGE_BLACKLIST)
        self.view_history = []

    def show_view(self, view_index):
        self.stacked_widget.setCurrentIndex(view_index)

    def show_org_view(self, group_id):
        self.org_view.load_group(group_id)
        self.stacked_widget.setCurrentIndex(self.PAGE_ORG_VIEW)
        self.view_history.append((self.PAGE_PERSONNEL_MANAGEMENT, None))

    def show_employee_view(self, employee_id):
        self.employee_view.load_employee(employee_id)
        self.stacked_widget.setCurrentIndex(self.PAGE_EMPLOYEE_VIEW)
        self.view_history.append((self.PAGE_ORG_VIEW, None))

    def show_monitor_view(self, record_id, employee_id):
        self.monitor_view.load_record(record_id, employee_id)
        self.stacked_widget.setCurrentIndex(self.PAGE_MONITOR_VIEW)
        self.view_history.append((self.PAGE_EMPLOYEE_VIEW, employee_id))

    def back_to_personnel_list(self):
        if self.view_history:
            prev_page_index, _ = self.view_history.pop()
            self.stacked_widget.setCurrentIndex(prev_page_index)
        else:
            self.stacked_widget.setCurrentIndex(self.PAGE_PERSONNEL_MANAGEMENT)

    def back_to_org_view(self):
        if self.view_history:
            prev_page_index, _ = self.view_history.pop()
            self.stacked_widget.setCurrentIndex(prev_page_index)
        else:
            self.stacked_widget.setCurrentIndex(self.PAGE_ORG_VIEW)

    def back_to_employee_view(self):
        if self.view_history:
            prev_page_index, employee_id = self.view_history.pop()
            if prev_page_index == self.PAGE_EMPLOYEE_VIEW and employee_id:
                self.employee_view.load_employee(employee_id)
            self.stacked_widget.setCurrentIndex(prev_page_index)
        else:
            self.stacked_widget.setCurrentIndex(self.PAGE_EMPLOYEE_VIEW)

    def switch_view_mode(self, mode):
        self.current_view_mode = mode
        if mode == "date":
            self.stacked_widget.setCurrentIndex(self.PAGE_PERSONNEL_MANAGEMENT)
        else:
            self.stacked_widget.setCurrentIndex(self.PAGE_PERSONNEL_MANAGEMENT)