#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys          # <--- 新增，用于 resource_path
import random
import math
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize, QRectF, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont

from widgets.laser_frame import LaserFrame
from models.data import MockData

# ========== 资源路径适配函数（打包后也能找到文件）==========
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后"""
    try:
        # PyInstaller 会将资源解压到临时目录，存在 _MEIPASS 属性
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ========== 视觉规范 ==========
ACCENT_CYAN = "#00F2FF"
TEXT_DIM = "#94A3B8"
RED_ALERT = "#EF4444"
YELLOW_WARN = "#F59E0B"
BLUE_INFO = "#3B82F6"
GREEN_OK = "#10B981"
BG_CARD_GLASS = "rgba(15, 23, 42, 0.5)"


# ========== 饼图组件（稍大一圈）==========
class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setMaximumHeight(240)
        self.data = {}
        self.colors = [
            QColor(RED_ALERT), QColor(YELLOW_WARN), QColor(BLUE_INFO),
            QColor(ACCENT_CYAN), QColor(GREEN_OK), QColor("#A855F7")
        ]

    def set_data(self, data_dict):
        self.data = data_dict
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 右边距调整为 -40，饼图半径增大
        rect = self.rect().adjusted(20, 30, -40, -20)

        if not self.data or sum(self.data.values()) == 0:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        total = sum(self.data.values())
        max_radius = min(100, rect.width() / 2 - 40, rect.height() / 2 - 30)
        pie_size = max_radius * 2
        pie_rect = QRectF(rect.x() + 15, rect.y() + 15, pie_size, pie_size)
        center = QPointF(rect.center()) - QPointF(25, 0)
        pie_rect.moveCenter(center)

        start_angle = 0
        slices = []
        for i, (label, value) in enumerate(self.data.items()):
            angle_span = (value / total) * 360
            angle_16 = angle_span * 16
            color = self.colors[i % len(self.colors)]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(30, 40, 60), 1))
            painter.drawPie(pie_rect, int(start_angle), int(angle_16))

            mid_angle = start_angle / 16 + angle_span / 2
            slices.append((label, value, mid_angle, color))
            start_angle += angle_16

        pie_center = pie_rect.center()
        radius = pie_rect.width() / 2
        painter.setPen(QPen(QColor(200, 200, 200, 150), 0.6))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        for label, value, mid_angle, color in slices:
            rad = math.radians(mid_angle)
            edge_x = pie_center.x() + radius * math.cos(rad)
            edge_y = pie_center.y() - radius * math.sin(rad)
            label_radius = radius + 22
            label_x = pie_center.x() + label_radius * math.cos(rad)
            label_y = pie_center.y() - label_radius * math.sin(rad)

            painter.drawLine(int(edge_x), int(edge_y), int(label_x), int(label_y))

            painter.setPen(QPen(QColor(TEXT_DIM)))
            percent = value / total * 100
            short_label = label
            if label == "数据外发":
                short_label = "外发"
            elif label == "未授权访问":
                short_label = "越权"
            elif label == "违规软件":
                short_label = "违规"
            elif label == "异常登录":
                short_label = "异常"
            text = f"{short_label}\n{value} ({percent:.0f}%)"
            text_rect = QRectF(label_x - 32, label_y - 12, 64, 22)
            if mid_angle < 90 or mid_angle > 270:
                text_rect.moveLeft(label_x + 8)
            else:
                text_rect.moveRight(label_x - 8)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

        painter.setPen(QPen(QColor(ACCENT_CYAN)))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(rect.x(), rect.y() - 10, "风险分布")


# ========== 折线图组件（修改标题）==========
class LineChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setMaximumHeight(240)
        self.values = []
        self.setAutoFillBackground(False)

    def set_data(self, values):
        self.values = values
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(20, 30, -20, -20)

        if not self.values or len(self.values) == 0:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "暂无数据")
            return

        plot_rect = rect.adjusted(40, 10, -25, -25)
        if plot_rect.width() <= 0 or plot_rect.height() <= 0:
            return

        max_val = max(self.values)
        min_val = min(self.values)
        if max_val == min_val:
            max_val = min_val + 1

        n = len(self.values)
        painter.setPen(QPen(QColor(TEXT_DIM), 0.5, Qt.PenStyle.DotLine))
        for i in range(3):
            y = plot_rect.bottom() - (i / 2) * plot_rect.height()
            painter.drawLine(int(plot_rect.left()), int(y), int(plot_rect.right()), int(y))
            painter.setPen(QPen(QColor(TEXT_DIM)))
            val = min_val + i * (max_val - min_val) / 2
            painter.drawText(int(plot_rect.left() - 30), int(y - 2), f"{int(val)}")

        for i in range(n):
            x = plot_rect.left() + (i / (n - 1)) * plot_rect.width() if n > 1 else plot_rect.center().x()
            painter.drawText(int(x - 6), int(plot_rect.bottom() + 12), 12, 12,
                             Qt.AlignmentFlag.AlignCenter, str(i + 1))

        points = []
        for i, val in enumerate(self.values):
            if n > 1:
                x = plot_rect.left() + (i / (n - 1)) * plot_rect.width()
            else:
                x = plot_rect.center().x()
            y = plot_rect.bottom() - ((val - min_val) / (max_val - min_val)) * plot_rect.height()
            points.append(QPoint(int(x), int(y)))

        pen = QPen(QColor(ACCENT_CYAN), 2)
        painter.setPen(pen)
        for i in range(1, len(points)):
            painter.drawLine(points[i-1], points[i])

        painter.setBrush(QBrush(QColor(ACCENT_CYAN)))
        for p in points:
            painter.drawEllipse(p, 3, 3)

        painter.setPen(QPen(QColor(ACCENT_CYAN)))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        # 修改标题
        painter.drawText(rect.x(), rect.y() - 10, "近7天风险告警次数")
        painter.save()
        painter.translate(rect.x() + 8, rect.center().y())
        painter.rotate(-90)
        painter.drawText(0, 0, "次数")
        painter.restore()
        painter.drawText(int(plot_rect.center().x()), int(plot_rect.bottom() + 28), "天")


# ========== 告警列表项 ==========
class AlertItemWidget(QWidget):
    def __init__(self, level, risk_type, emp_id, emp_name, event_title, event_time, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        dot = QLabel("●")
        if level == "高危":
            dot.setStyleSheet(f"color: {RED_ALERT}; font-size: 12pt;")
        elif level == "中危":
            dot.setStyleSheet(f"color: {YELLOW_WARN}; font-size: 12pt;")
        else:
            dot.setStyleSheet(f"color: {BLUE_INFO}; font-size: 12pt;")
        layout.addWidget(dot)

        emp_info = QLabel(f"{emp_id} {emp_name}")
        emp_info.setStyleSheet("color: #FFFFFF; font-size: 10pt; font-weight: bold;")
        emp_info.setFixedWidth(110)
        layout.addWidget(emp_info)

        risk_label = QLabel(risk_type)
        risk_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 10pt;")
        risk_label.setFixedWidth(70)
        layout.addWidget(risk_label)

        short_title = event_title[:18] + "..." if len(event_title) > 18 else event_title
        evt = QLabel(short_title)
        evt.setStyleSheet("color: #E0E0E0; font-size: 10pt;")
        evt.setWordWrap(False)
        evt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(evt, 1)

        t = QLabel(event_time)
        t.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10pt;")
        t.setFixedWidth(80)
        layout.addWidget(t)


# ========== 主页面 ==========
class RiskOverviewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 修改：直接使用 app/vlm_debug_frames 文件夹（资源路径适配）
        self.image_folder = Path(resource_path("vlm_debug_frames"))
        self.image_paths = []
        self.current_image_index = 0
        self._load_images()

        self.all_alerts = []
        self.recent_alerts = []

        self._load_all_alerts()
        self._init_recent_alerts()

        self._setup_ui()
        self._draw_static_charts()
        self._refresh_alert_list()
        self._refresh_metrics()
        self._start_timers()

    def _load_images(self):
        if self.image_folder.exists():
            self.image_paths = sorted([str(p) for p in self.image_folder.glob("*.jpg")])
        if not self.image_paths:
            # 修改：提示正确的路径
            print(f"未找到轮播图片，请检查路径: {self.image_folder.absolute()}")

    def _load_all_alerts(self):
        temp = []
        for emp in MockData.get_all_employees():
            emp_id = emp['id']
            emp_name = emp['name']
            recs = MockData.get_monitoring_records(emp_id, emp_name)
            for rec in recs:
                level = {"high": "高危", "medium": "中危", "low": "低危"}.get(rec['level'], "低危")
                risk_type = self._map_risk_type(rec['title'])
                time_str = rec['time'].strftime("%H:%M:%S") if isinstance(rec['time'], datetime) else str(rec['time'])
                temp.append((level, risk_type, emp_id, emp_name, rec['title'], time_str, rec))
        temp.sort(key=lambda x: x[5], reverse=True)
        self.all_alerts = temp

    def _init_recent_alerts(self):
        self.recent_alerts = self.all_alerts[:6] if len(self.all_alerts) >= 6 else self.all_alerts.copy()

    def _map_risk_type(self, title):
        if "文件" in title or "外发" in title or "传输" in title:
            return "数据外发"
        if "访问" in title or "权限" in title:
            return "未授权访问"
        if "录屏" in title or "软件" in title:
            return "违规软件"
        if "登录" in title:
            return "异常登录"
        return "其他"

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: white;
                width: 10px;
                margin: 0px 0px 0px 0px;
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

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(20, 15, 20, 25)
        main_layout.setSpacing(20)

        self._create_top_metrics(main_layout)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        left_carousel = self._create_carousel()
        left_carousel.setMinimumHeight(320)
        left_carousel.setMaximumHeight(450)
        h_layout.addWidget(left_carousel, 6)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(12)

        alert_title = QLabel("🚨 实时风险告警")
        alert_title.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: bold; font-size: 12pt;")
        right_layout.addWidget(alert_title)

        self.alert_list = QListWidget()
        self.alert_list.setStyleSheet("""
            QListWidget {
                background: rgba(30,41,59,0.5);
                border: none;
                border-radius: 8px;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
        """)
        self.alert_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self.alert_list)

        charts_layout = QHBoxLayout()
        self.line_chart = LineChartWidget()
        self.pie_chart = PieChartWidget()
        line_frame = LaserFrame()
        line_frame_layout = QVBoxLayout(line_frame)
        line_frame_layout.addWidget(self.line_chart)
        pie_frame = LaserFrame()
        pie_frame_layout = QVBoxLayout(pie_frame)
        pie_frame_layout.addWidget(self.pie_chart)

        charts_layout.addWidget(line_frame, 1)
        charts_layout.addWidget(pie_frame, 1)
        right_layout.addLayout(charts_layout)

        h_layout.addWidget(right_container, 4)
        main_layout.addLayout(h_layout)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

    def _create_top_metrics(self, parent_layout):
        h_layout = QHBoxLayout()
        h_layout.setSpacing(15)
        self.metric_cards = []
        titles = ["今日监测", "高危阻断", "敏感预警", "节点状态"]
        for title in titles:
            card = LaserFrame()
            card.setFixedHeight(100)
            v = QVBoxLayout(card)
            v.setSpacing(5)
            title_label = QLabel(title)
            title_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10pt;")
            v.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

            val_layout = QHBoxLayout()
            value_label = QLabel("0")
            value_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 22pt; font-weight: bold;")
            change_label = QLabel("▲ 0")
            change_label.setStyleSheet(f"color: {GREEN_OK}; font-size: 9pt; font-weight: bold;")
            val_layout.addStretch()
            val_layout.addWidget(value_label)
            val_layout.addWidget(change_label)
            val_layout.addStretch()
            v.addLayout(val_layout)

            h_layout.addWidget(card)
            self.metric_cards.append({
                'title': title,
                'value': value_label,
                'change': change_label,
                'last_value': 0
            })
        parent_layout.addLayout(h_layout)

    def _refresh_metrics(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        current_month = datetime.now().month
        current_year = datetime.now().year

        raw_today = 0
        raw_high = 0
        raw_month = 0
        raw_monitored = 0

        for emp in MockData.get_all_employees():
            if emp.get('monitored', False):
                raw_monitored += 1
            recs = MockData.get_monitoring_records(emp['id'], emp['name'])
            for rec in recs:
                dt = rec.get('time')
                if not isinstance(dt, datetime):
                    continue
                if dt >= today:
                    raw_today += 1
                if rec.get('level') == 'high':
                    raw_high += 1
                if dt.month == current_month and dt.year == current_year and rec.get('level') in ('high', 'medium'):
                    raw_month += 1

        if raw_today == 0:
            raw_today = random.randint(2, 5)
        if raw_high == 0:
            raw_high = random.randint(1, 3)
        if raw_month == 0:
            raw_month = random.randint(2, 6)
        if raw_monitored == 0:
            raw_monitored = random.randint(3, 8)

        def add_wave(base):
            delta = random.randint(-2, 5)
            return max(0, base + delta)

        display_today = add_wave(raw_today)
        display_high = add_wave(raw_high)
        display_month = add_wave(raw_month)
        display_monitored = add_wave(raw_monitored)

        for card in self.metric_cards:
            title = card['title']
            if title == "今日监测":
                new_val = display_today
            elif title == "高危阻断":
                new_val = display_high
            elif title == "敏感预警":
                new_val = display_month
            elif title == "节点状态":
                new_val = display_monitored
            else:
                continue

            old = card['last_value']
            delta = new_val - old
            card['value'].setText(str(new_val))
            card['last_value'] = new_val

            if delta > 0:
                card['change'].setText(f"▲ {delta}")
                card['change'].setStyleSheet(f"color: {GREEN_OK}; font-size: 9pt; font-weight: bold;")
            elif delta < 0:
                card['change'].setText(f"▼ {abs(delta)}")
                card['change'].setStyleSheet(f"color: {RED_ALERT}; font-size: 9pt; font-weight: bold;")
            else:
                card['change'].setText("— 0")
                card['change'].setStyleSheet(f"color: {TEXT_DIM}; font-size: 9pt;")

    def _create_carousel(self):
        container = LaserFrame()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        carousel_title = QLabel("📸 实时监控画面")
        carousel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        carousel_title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 12pt; font-weight: bold; background: transparent;")
        v.addWidget(carousel_title)

        self.carousel_label = QLabel()
        self.carousel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.carousel_label.setScaledContents(True)
        if self.image_paths:
            self._update_carousel_image()
        else:
            self.carousel_label.setText("⚠️ 未找到轮播图片")
            self.carousel_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 14pt;")
        v.addWidget(self.carousel_label, 1)
        return container

    def _update_carousel_image(self):
        if not self.image_paths:
            return
        pixmap = QPixmap(self.image_paths[self.current_image_index])
        if not pixmap.isNull():
            self.carousel_label.setPixmap(pixmap.scaled(
                self.carousel_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

    def _refresh_alert_list(self):
        self.alert_list.clear()
        for alert in self.recent_alerts:
            level, risk_type, emp_id, emp_name, title, time_str, _ = alert
            item = QListWidgetItem(self.alert_list)
            item.setSizeHint(QSize(0, 36))
            widget = AlertItemWidget(level, risk_type, emp_id, emp_name, title, time_str)
            self.alert_list.setItemWidget(item, widget)

    def _draw_static_charts(self):
        type_count = {}
        for alert in self.all_alerts:
            risk_type = alert[1]
            type_count[risk_type] = type_count.get(risk_type, 0) + 1
        self.pie_chart.set_data(type_count)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily = [0] * 7
        for alert in self.all_alerts:
            rec = alert[6]
            if isinstance(rec.get('time'), datetime):
                dt = rec['time']
                days_diff = (today - dt).days
                if 0 <= days_diff <= 6:
                    daily[6 - days_diff] += 1
        # 如果全为零，生成 7 个 5~15 的随机数
        if sum(daily) == 0:
            daily = [random.randint(5, 15) for _ in range(7)]
        self.line_chart.set_data(daily)

    def _start_timers(self):
        if len(self.image_paths) > 1:
            self.carousel_timer = QTimer(self)
            self.carousel_timer.timeout.connect(self._next_carousel)
            self.carousel_timer.start(3000)

        self.alert_timer = QTimer(self)
        self.alert_timer.timeout.connect(self._update_recent_alerts)
        self.alert_timer.start(4000)

        self.metric_timer = QTimer(self)
        self.metric_timer.timeout.connect(self._refresh_metrics)
        self.metric_timer.start(10000)

    def _next_carousel(self):
        if not self.image_paths:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
        self._update_carousel_image()

    def _update_recent_alerts(self):
        all_employees = MockData.get_all_employees()
        if not all_employees:
            return
        emp = random.choice(all_employees)
        emp_id = emp['id']
        emp_name = emp['name']
        recs = MockData.get_monitoring_records(emp_id, emp_name)
        if not recs:
            return
        rec = random.choice(recs)
        level = {"high": "高危", "medium": "中危", "low": "低危"}.get(rec['level'], "低危")
        risk_type = self._map_risk_type(rec['title'])
        time_str = rec['time'].strftime("%H:%M:%S") if isinstance(rec['time'], datetime) else str(rec['time'])
        new_alert = (level, risk_type, emp_id, emp_name, rec['title'], time_str, rec)

        self.recent_alerts.insert(0, new_alert)
        if len(self.recent_alerts) > 6:
            self.recent_alerts.pop()
        self._refresh_alert_list()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'carousel_label') and self.image_paths:
            self._update_carousel_image()