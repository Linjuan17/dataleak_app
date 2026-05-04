#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面4：员工个人卡片
包含员工基本信息、统计数据和监控记录列表
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QLabel, QPushButton, QFrame, QListWidget,
                             QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from models.data import MockData


class EmployeeView(QWidget):
    """员工个人卡片视图"""

    # 导航信号
    navigate_back = pyqtSignal()
    navigate_to_monitor = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_employee = None
        self.current_group = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("background-color: #0A0E17;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 返回按钮
        self.back_btn = QPushButton("◀  返回组别")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(17, 25, 40, 0.85);
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                color: #8B95A5;
            }
            QPushButton:hover {
                background: rgba(0, 212, 255, 0.08);
                color: #00D4FF;
                border-color: #00D4FF;
            }
        """)
        self.back_btn.clicked.connect(self.navigate_back.emit)
        main_layout.addWidget(self.back_btn)

        # 内容区域 - 修改滚动条样式为白底深蓝色（仅此处改动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: white;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #0044BB;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background: none;
            }
        """)

        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # 员工资料卡片
        self.profile_card = self.create_profile_card()
        content_layout.addWidget(self.profile_card)

        # 统计信息
        self.stats_container = self.create_stats_container()
        content_layout.addWidget(self.stats_container)

        # 分析报告（仅特定员工显示）
        self.report_card = self.create_report_card()
        self.report_card.hide()
        content_layout.addWidget(self.report_card)

        # 监控记录列表
        self.records_card = self.create_records_card()
        content_layout.addWidget(self.records_card)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, 1)

    def create_profile_card(self):
        """创建资料卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 20px;
                border: 1px solid rgba(0, 212, 255, 0.12);
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(10)

        # 头部信息
        header = QHBoxLayout()
        header.setSpacing(16)

        # 头像
        self.profile_avatar = QLabel()
        self.profile_avatar.setFixedSize(56, 56)
        self.profile_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00D4FF, stop:1 #00FFA3);
            border-radius: 28px;
            color: #0A0E17;
            font-weight: 700;
            font-size: 20px;
        """)

        # 信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.profile_name = QLabel()
        self.profile_name.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.profile_name.setStyleSheet("color: #E8ECF1; border: none;")

        self.profile_id = QLabel()
        self.profile_id.setStyleSheet("color: #8B95A5; font-size: 12px; border: none;")

        # 徽章
        self.badges_layout = QHBoxLayout()
        self.badges_layout.setSpacing(6)

        info_layout.addWidget(self.profile_name)
        info_layout.addWidget(self.profile_id)
        info_layout.addLayout(self.badges_layout)

        header.addWidget(self.profile_avatar)
        header.addLayout(info_layout, 1)

        layout.addLayout(header)

        # 详细信息（去掉分隔线，水平排列更紧凑）
        details_layout = QHBoxLayout()
        details_layout.setSpacing(24)

        self.detail_items = []
        details = [
            ("部门", ""),
            ("职位", ""),
            ("工号", ""),
            ("监控状态", "")
        ]

        for label_text, value in details:
            item_layout = QVBoxLayout()
            item_layout.setSpacing(2)

            label = QLabel(label_text)
            label.setStyleSheet("color: #8B95A5; font-size: 11px; border: none;")

            value_label = QLabel(value)
            value_label.setStyleSheet("color: #E8ECF1; font-size: 13px; font-weight: 500; border: none;")

            item_layout.addWidget(label)
            item_layout.addWidget(value_label)

            details_layout.addLayout(item_layout)
            self.detail_items.append((label, value_label))

        details_layout.addStretch()
        layout.addLayout(details_layout)

        return card

    def create_stats_container(self):
        """创建统计信息容器"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.stat_cards = []
        stats = [
            ("0", "监控记录"),
            ("0", "高风险事件"),
            ("0", "安全评分"),
            ("0", "本月登录")
        ]

        for value, label in stats:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: rgba(15, 23, 42, 0.5);
                    border-radius: 10px;
                    border: none;
                    padding: 8px 10px;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.setSpacing(2)

            value_label = QLabel(value)
            value_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
            value_label.setStyleSheet("color: #00D4FF;")

            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #8B95A5; font-size: 14px; border: none;")

            card_layout.addWidget(value_label)
            card_layout.addWidget(label_widget)

            layout.addWidget(card)
            self.stat_cards.append(value_label)

        return container

    def create_report_card(self):
        """创建分析报告卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 20px;
                border: none;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # 标题行
        title_layout = QHBoxLayout()
        title = QLabel("分析报告")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #E8ECF1; border: none;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # 统计时间标签
        time_tag = QLabel("2026-04-30 统计周期")
        time_tag.setStyleSheet("color: #8B95A5; font-size: 14px; border: none;")
        title_layout.addWidget(time_tag)

        layout.addLayout(title_layout)

        # 统计数据网格 (3列)
        report_items = [
            ("22", "已处理事件", "#00D4FF"),
            ("28", "检测到的上传事件", "#FFA502"),
            ("34", "敏感操作记录数(去重)", "#FF4757"),
            ("2", "黑名单应用报警", "#FF4757"),
            ("0", "白名单应用上传", "#00D68F"),
            ("26", "其他应用上传", "#8B95A5"),
        ]

        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(12)

        for value, label, color in report_items:
            item_card = QFrame()
            item_card.setStyleSheet("""
                QFrame {
                    background: rgba(15, 23, 42, 0.5);
                    border-radius: 10px;
                }
            """)

            item_layout = QVBoxLayout(item_card)
            item_layout.setContentsMargins(12, 12, 12, 12)
            item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item_layout.setSpacing(6)

            val_label = QLabel(value)
            val_label.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
            val_label.setStyleSheet(f"color: {color};")
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel(label)
            desc_label.setStyleSheet("color: #8B95A5; font-size: 11px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)

            item_layout.addWidget(val_label)
            item_layout.addWidget(desc_label)

            grid_layout.addWidget(item_card)

        layout.addLayout(grid_layout)

        return card

    def create_records_card(self):
        """创建监控记录卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 20px;
                border: none;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # 标题
        title_layout = QHBoxLayout()

        title = QLabel("监控记录")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #E8ECF1; border: none;")

        title_layout.addWidget(title)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 记录列表
        self.records_list = QListWidget()
        self.records_list.setMinimumWidth(600)
        self.records_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                background: rgba(15, 23, 42, 0.5);
                border-radius: 12px;
                border: none;
                padding: 20px;
                margin-bottom: 16px;
            }
            QListWidget::item:hover {
                background: rgba(0, 212, 255, 0.05);
                border-color: rgba(0, 212, 255, 0.15);
            }
        """)
        self.records_list.itemClicked.connect(self.on_record_clicked)

        layout.addWidget(self.records_list)

        return card

    def load_employee(self, employee_id):
        """加载员工数据"""
        employee, group = MockData.get_employee_by_id(employee_id)
        if not employee:
            return

        self.current_employee = employee
        self.current_group = group

        # 分析报告：仅周丽华(E008)显示
        if employee_id == 'E008':
            self.report_card.show()
        else:
            self.report_card.hide()

        # 更新头像
        self.profile_avatar.setText(employee['avatar'])

        # 更新姓名
        self.profile_name.setText(employee['name'])

        # 更新ID
        self.profile_id.setText(f"工号：{employee['id']}")

        # 更新徽章
        while self.badges_layout.count():
            item = self.badges_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if employee['monitored']:
            badge = QLabel("🔴 监控中")
            badge.setStyleSheet("""
                background: rgba(0, 212, 255, 0.15);
                color: #00D4FF;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 12px;
                border: 1px solid rgba(0, 212, 255, 0.2);
            """)
            self.badges_layout.addWidget(badge)

        if employee['risk']:
            badge = QLabel("⚠️ 风险")
            badge.setStyleSheet("""
                background: rgba(255, 71, 87, 0.15);
                color: #FF4757;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 12px;
                border: 1px solid rgba(255, 71, 87, 0.2);
            """)
            self.badges_layout.addWidget(badge)

        self.badges_layout.addStretch()

        # 更新详细信息
        self.detail_items[0][1].setText(group['name'] if group else "")
        self.detail_items[1][1].setText(employee['position'])
        self.detail_items[2][1].setText(employee['id'])
        self.detail_items[3][1].setText("监控中" if employee['monitored'] else "未监控")

        # 更新统计数据
        records = MockData.get_monitoring_records(employee_id, employee['name'])
        high_risk_count = sum(1 for r in records if r['level'] == 'high')
        safe_score = max(0, 100 - high_risk_count * 20)

        self.stat_cards[0].setText(str(len(records)))
        self.stat_cards[1].setText(str(high_risk_count))
        self.stat_cards[2].setText(str(safe_score))
        self.stat_cards[3].setText("15")  # 模拟数据

        # 更新记录列表
        self.records_list.clear()
        for record in records:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, record['id'])
            item.setSizeHint(QSize(700, 150))

            widget = self.create_record_item(record)
            self.records_list.addItem(item)
            self.records_list.setItemWidget(item, widget)

    def create_record_item(self, record):
        """创建记录项"""
        widget = QFrame()
        widget.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 风险等级指示条
        level_bar = QFrame()
        level_bar.setFixedWidth(8)
        level_bar.setMinimumHeight(48)

        if record['level'] == 'high':
            level_bar.setStyleSheet("""
                background: #FF4757;
                border-radius: 4px;
            """)
        elif record['level'] == 'medium':
            level_bar.setStyleSheet("""
                background: #FFA502;
                border-radius: 4px;
            """)
        else:
            level_bar.setStyleSheet("""
                background: #00D68F;
                border-radius: 4px;
            """)

        # 信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        time_label = QLabel(
            record['time'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(record['time'], 'strftime') else str(
                record['time']))
        time_label.setStyleSheet("color: #8B95A5; font-size: 12px; border: none;")

        # 标题行：标题 + 视频标记
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title_label = QLabel(record['title'])
        title_label.setStyleSheet("color: #E8ECF1; font-size: 14px; font-weight: 600; border: none;")
        title_row.addWidget(title_label)

        # 如果有真实视频，显示标记
        if record.get('video_path'):
            video_tag = QLabel("REC")
            video_tag.setStyleSheet("""
                background: rgba(255, 71, 87, 0.2);
                color: #FF4757;
                font-size: 10px;
                font-weight: 600;
                padding: 2px 6px;
                border-radius: 4px;
            """)
            title_row.addWidget(video_tag)

        title_row.addStretch()

        desc_label = QLabel(record['desc'])
        desc_label.setStyleSheet("color: #8B95A5; font-size: 12px;")

        info_layout.addWidget(time_label)
        info_layout.addLayout(title_row)
        info_layout.addWidget(desc_label)

        # 箭头
        arrow = QLabel("▶")
        arrow.setStyleSheet("color: #8B95A5; font-size: 14px;")

        layout.addWidget(level_bar)
        layout.addLayout(info_layout, 1)
        layout.addWidget(arrow)

        return widget

    def on_record_clicked(self, item):
        """记录项点击"""
        record_id = item.data(Qt.ItemDataRole.UserRole)
        if record_id and self.current_employee:
            self.navigate_to_monitor.emit(record_id, self.current_employee['id'])