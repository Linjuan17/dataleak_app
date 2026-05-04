#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面5：监控记录详情
三栏布局：时间线 | 视频区 | 风险评分
支持真实视频播放（QMediaPlayer + QVideoWidget）
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QLabel, QPushButton, QFrame, QListWidget,
                             QListWidgetItem, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

from models.data import MockData


class MonitorView(QWidget):
    """监控记录详情视图"""

    # 导航信号
    navigate_back = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_record = None
        self.current_employee = None
        self.media_player = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("background-color: #0A0E17;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 返回按钮
        self.back_btn = QPushButton("◀  返回员工详情")
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

        # ========== 滚动区域，容纳三栏布局 ==========
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # 滚动条样式：白底深蓝色条（与原始 date_view 一致）
        scroll_area.setStyleSheet("""
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

        # 内容容器
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # 三栏布局
        detail_layout = QHBoxLayout()
        detail_layout.setSpacing(24)

        # 左侧：时间线（最小宽度 320px）
        self.timeline_panel = self.create_timeline_panel()
        self.timeline_panel.setMinimumWidth(320)
        detail_layout.addWidget(self.timeline_panel, 1)

        # 中间：视频播放区（最小宽度 480px）
        self.video_panel = self.create_video_panel()
        self.video_panel.setMinimumWidth(480)
        detail_layout.addWidget(self.video_panel, 2)

        # 右侧：风险评分（最小宽度 240px）
        self.risk_panel = self.create_risk_panel()
        self.risk_panel.setMinimumWidth(240)
        detail_layout.addWidget(self.risk_panel, 1)

        scroll_layout.addLayout(detail_layout)
        scroll_area.setWidget(scroll_widget)

        main_layout.addWidget(scroll_area, 1)

    def create_timeline_panel(self):
        """创建时间线面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 16px;
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(19)

        # 标题
        title = QLabel("检测事件时间线")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #E8ECF1; border: none;")
        layout.addWidget(title)

        # 时间线列表 - 支持自动调整高度和文字换行
        self.timeline_list = QListWidget()
        self.timeline_list.setWordWrap(True)
        self.timeline_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.timeline_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 4px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(self.timeline_list, 1)

        return panel

    def create_video_panel(self):
        """创建视频播放面板（支持真实视频）"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 16px;
                border: 1px solid rgba(0, 212, 255, 0.12);
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 标题
        self.video_title = QLabel("监控录像")
        self.video_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        self.video_title.setStyleSheet("color: #E8ECF1;")
        layout.addWidget(self.video_title)

        # 视频区域 — 使用QVideoWidget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: #0D1117;
                border-radius: 12px;
                border: 1px solid rgba(0, 212, 255, 0.1);
            }
        """)
        layout.addWidget(self.video_widget, 1)

        # 播放控制条
        controls = QFrame()
        controls.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.8);
                border-radius: 8px;
                padding: 12px;
                border: 1px solid rgba(0, 212, 255, 0.1);
            }
        """)

        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(12)

        # 播放/暂停按钮
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #0099CC);
                border: none;
                border-radius: 18px;
                color: #0A0E17;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00E5FF, stop:1 #00BBEE);
            }
        """)

        # 进度条
        self.video_progress = QProgressBar()
        self.video_progress.setFixedHeight(6)
        self.video_progress.setTextVisible(False)
        self.video_progress.setValue(0)
        self.video_progress.setStyleSheet("""
            QProgressBar {
                background: rgba(0, 212, 255, 0.15);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #00FFA3);
                border-radius: 3px;
            }
        """)

        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #8B95A5; font-size: 12px; border: none;")

        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.video_progress, 1)
        controls_layout.addWidget(self.time_label)

        layout.addWidget(controls)

        # 初始化播放器
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # 播放器信号连接
        self.play_btn.clicked.connect(self.toggle_play)
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.playbackStateChanged.connect(self.on_state_changed)

        return panel

    def toggle_play(self):
        """播放/暂停切换"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def on_position_changed(self, position):
        """播放位置变化 — 更新进度条和时间"""
        duration = self.media_player.duration()
        if duration > 0:
            self.video_progress.setValue(int(position / duration * 100))
        self.time_label.setText(f"{self.format_time(position)} / {self.format_time(duration)}")

    def on_duration_changed(self, duration):
        """视频总时长变化"""
        self.video_progress.setValue(0)
        self.time_label.setText(f"00:00 / {self.format_time(duration)}")

    def on_state_changed(self, state):
        """播放状态变化 — 更新按钮图标"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    def format_time(self, ms):
        """毫秒转 mm:ss"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def create_risk_panel(self):
        """创建风险评分面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 16px;
                border: 1px solid rgba(0, 212, 255, 0.12);
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 风险评分
        risk_section = QVBoxLayout()
        risk_section.setSpacing(16)

        section_title = QLabel("风险评分")
        section_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        section_title.setStyleSheet("color: #E8ECF1;")
        risk_section.addWidget(section_title)

        # 评分圆环
        score_widget = QWidget()
        score_layout = QHBoxLayout(score_widget)
        score_layout.setSpacing(16)

        self.risk_circle = QFrame()
        self.risk_circle.setFixedSize(60, 60)
        self.risk_circle.setStyleSheet("""
            QFrame {
                border-radius: 30px;
                border: 6px solid #FF4757;
                background: transparent;
            }
        """)

        self.risk_value = QLabel("0")
        self.risk_value.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.risk_value.setStyleSheet("color: #FF4757;")
        self.risk_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 圆环内叠放数值
        circle_container = QWidget()
        circle_layout = QVBoxLayout(circle_container)
        circle_layout.setContentsMargins(0, 0, 0, 0)
        circle_layout.addWidget(self.risk_value)
        circle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 评分信息
        score_info = QVBoxLayout()
        score_info.setSpacing(4)

        self.risk_level = QLabel("高风险")
        self.risk_level.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.DemiBold))
        self.risk_level.setStyleSheet("color: #FF4757;")

        risk_desc = QLabel("风险指数偏高")
        risk_desc.setStyleSheet("color: #8B95A5; font-size: 12px;")

        score_info.addWidget(self.risk_level)
        score_info.addWidget(risk_desc)

        score_layout.addWidget(circle_container)
        score_layout.addWidget(self.risk_circle)
        score_layout.addLayout(score_info)

        risk_section.addWidget(score_widget)
        layout.addLayout(risk_section)

        # 行为分析
        analysis_title = QLabel("行为分析要点")
        analysis_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.DemiBold))
        analysis_title.setStyleSheet("color: #E8ECF1;")
        layout.addWidget(analysis_title)

        # 分析列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        self.analysis_list = QVBoxLayout()
        self.analysis_list.setSpacing(12)

        analysis_container = QWidget()
        analysis_container.setLayout(self.analysis_list)
        scroll.setWidget(analysis_container)

        layout.addWidget(scroll, 1)

        return panel

    def create_analysis_item(self, text):
        """创建分析项"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.5);
                border-radius: 8px;
                padding: 12px;
                border: none;
            }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 图标
        icon = QLabel("⚠")
        icon.setStyleSheet("color: #FFA502; font-size: 14px; background: transparent;")

        # 文本
        text_label = QLabel(text)
        text_label.setStyleSheet("color: #E8ECF1; font-size: 13px; line-height: 1.5;")
        text_label.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(text_label, 1)

        return item

    def load_record(self, record_id, employee_id):
        """加载记录数据"""
        # 获取员工信息
        employee, group = MockData.get_employee_by_id(employee_id)
        if not employee:
            return

        self.current_employee = employee
        self.current_record_id = record_id

        # 获取记录
        records = MockData.get_monitoring_records(employee_id, employee['name'])
        record = next((r for r in records if r['id'] == record_id), None)

        if not record:
            return

        self.current_record = record

        # 更新时间线（不再手动设置固定高度）
        self.timeline_list.clear()
        for event in record['events']:
            item = QListWidgetItem()
            # 不设置固定 sizeHint，让列表自动调整
            widget = self.create_timeline_item(event, record['level'])
            # 设置 item 高度由 widget 决定
            item.setSizeHint(widget.sizeHint())
            self.timeline_list.addItem(item)
            self.timeline_list.setItemWidget(item, widget)

        # 更新风险评分
        self.risk_value.setText(str(record['risk_score']))

        if record['risk_score'] >= 70:
            level = "高风险"
            color = "#FF4757"
        elif record['risk_score'] >= 40:
            level = "中风险"
            color = "#FFA502"
        else:
            level = "低风险"
            color = "#00D68F"

        self.risk_level.setText(level)
        self.risk_level.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 600;")
        self.risk_circle.setStyleSheet(f"""
            QFrame {{
                border-radius: 30px;
                border: 6px solid {color};
                background: transparent;
            }}
        """)
        self.risk_value.setStyleSheet(f"color: {color};")

        # 更新行为分析
        while self.analysis_list.count():
            item = self.analysis_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for analysis in record['analysis']:
            analysis_item = self.create_analysis_item(analysis)
            self.analysis_list.addWidget(analysis_item)

        # ===== 加载真实视频 =====
        video_path = record.get('video_path', '')
        if video_path and self.media_player:
            self.media_player.stop()
            video_url = QUrl.fromLocalFile(video_path)
            self.media_player.setSource(video_url)
            self.video_progress.setValue(0)
        elif self.media_player:
            self.media_player.stop()
            self.media_player.setSource(QUrl())

    def create_timeline_item(self, event, level):
        """创建时间线项（支持文字自动换行）"""
        widget = QFrame()
        widget.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 圆点
        dot = QFrame()
        dot.setFixedSize(16, 16)
        dot.setStyleSheet(f"""
            background: {self.get_level_color(level)};
            border-radius: 8px;
            border: 3px solid #0A0E17;
        """)

        # 信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        time_label = QLabel(event['time'])
        time_label.setStyleSheet("color: #8B95A5; font-size: 12px;")

        title_label = QLabel(event['title'])
        title_label.setStyleSheet("color: #E8ECF1; font-size: 14px; font-weight: 600;")

        desc_label = QLabel(event['desc'])
        desc_label.setStyleSheet("color: #8B95A5; font-size: 12px;")
        desc_label.setWordWrap(True)          # 关键：允许换行
        desc_label.setMaximumWidth(280)       # 限制最大宽度，避免过宽

        info_layout.addWidget(time_label)
        info_layout.addWidget(title_label)
        info_layout.addWidget(desc_label)

        layout.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(info_layout, 1)

        # 让 widget 根据内容自动调整高度
        widget.adjustSize()
        return widget

    def get_level_color(self, level):
        """获取等级颜色"""
        if level == 'high':
            return "#FF4757"
        elif level == 'medium':
            return "#FFA502"
        else:
            return "#00D68F"