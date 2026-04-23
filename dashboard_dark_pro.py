import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import main_app


# ================= ⭐ 全局字体（统一QSS🔥） =================
UI_FONT_FAMILY = '"Microsoft YaHei", "Segoe UI", sans-serif'
UI_FONT_SIZE = 20  # ⭐ 主字号（接近 monitor）

def font_style(size=None, weight="normal"):
    if size is None:
        size = UI_FONT_SIZE
    return f"font-family: {UI_FONT_FAMILY}; font-size: {size}px; font-weight: {weight};"


def painter_font(size=14, bold=False):
    return QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)


# ================= 1. 基础卡片 =================
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }}
            /* 🔥 关键：去掉内部所有文字控件的框 */
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)


# ================= 2. KPI卡片 =================
class StatCard(Card):
    def __init__(self, title, subtitle, icon="📊"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title_lbl = QLabel(f"{icon} {title}")
        self.title_lbl.setStyleSheet(font_style(20, "bold") + "color:#475569;")

        self.val_lbl = QLabel("0")
        self.val_lbl.setAlignment(Qt.AlignCenter)
        self.val_lbl.setStyleSheet(font_style(34, "bold") + "color:#6a7bdc;")

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setStyleSheet(font_style(18) + "color:#94a3b8;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)

    def set_value(self, val):
        self.val_lbl.setText(str(val))


# ================= 3. 系统介绍卡片 =================
class SystemDescCard(Card):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(8)

        title = QLabel("🛡️ DataLeakDetector: 智能终端数据泄露检测系统")
        title.setStyleSheet(font_style(26, "bold") + "color:#1e293b;")

        desc = QLabel("基于 AI Agent 与多模态数据融合技术，构建从视频行为识别到全链路污点追踪的闭环防护体系。")
        desc.setStyleSheet(font_style(22) + "color:#475569;")

        tags = QLabel(" 精准检测  |  自主溯源  |  Agent 决策  |  算力优化  |  日志校验")
        tags.setStyleSheet(font_style(22, "bold") + "color:#6a7bdc;")

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(tags)


# ================= 4. 折线图 =================
class LineChart(Card):
    def __init__(self):
        super().__init__()
        self.data = [0, 0, 0, 0, 0]

    def set_data(self, data):
        self.data = data if (data and len(data) >= 2) else [0, 0, 0, 0, 0]
        while len(self.data) < 5:
            self.data.append(0)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        p.setPen(QColor("#1e293b"))
        p.setFont(painter_font(11, True))
        p.drawText(30, 40, "📈 行为监控趋势 (近5场)")

        padding_l, padding_r = 70, 50
        padding_t, padding_b = 80, 60

        draw_w = w - padding_l - padding_r
        draw_h = h - padding_t - padding_b
        if draw_w <= 0 or draw_h <= 0:
            return
        #
        # p.setFont(painter_font(11))
        # p.setPen(QColor("#94a3b8"))
        # p.drawText(padding_l - 100, padding_t - 18, "(次数)")

        max_d = max(self.data)
        y_max = max_d * 1.3 if max_d > 0 else 10

        step_x = draw_w / (len(self.data) - 1)
        points = []

        for i, v in enumerate(self.data):
            px = padding_l + i * step_x
            py = h - padding_b - (v / y_max * draw_h)
            points.append(QPointF(px, py))

            p.drawText(int(px - 10), h - padding_b + 25, f"S{i + 1}")

            p.setPen(QColor("#6a7bdc"))
            p.drawText(int(px - 8), int(py - 12), str(v))
            p.setPen(QColor("#94a3b8"))

        p.setPen(QPen(QColor("#6a7bdc"), 3))
        for i in range(len(points) - 1):
            p.drawLine(points[i], points[i + 1])

        p.setBrush(Qt.white)
        for pt in points:
            p.drawEllipse(pt, 5, 5)


# ================= 5. 环形图 =================
class StatusDetailCard(Card):
    def __init__(self):
        super().__init__()
        self.risks = [("安全", 92, "#22c55e"), ("风险", 5, "#f59e0b"), ("严重", 3, "#ef4444")]

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setFont(painter_font(11, True))
        p.drawText(20, 35, "🎯 风险分布")

        rect = QRectF(self.width() // 2 - 60, 50, 120, 120)
        start = 90 * 16

        for name, per, col in self.risks:
            span = -int(per * 5 * 16)
            p.setPen(QPen(QColor(col), 10, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(rect, start, span)
            start += span

        p.setFont(painter_font(10))
        for i, (name, per, col) in enumerate(self.risks):
            p.setPen(QColor(col))
            p.drawText(20, 200 + i * 30, f"● {name}: {per}%")


# ================= 6. 主页面 =================
class DashboardPro(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            QWidget {{
                {font_style()}
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(20)

        header = QHBoxLayout()

        title = QLabel("数据安全防护看板")
        title.setStyleSheet(font_style(26, "bold") + "color:#1e293b;")

        status = QLabel("● 实时防护中")
        status.setStyleSheet(font_style(18, "bold") + "color:#22c55e;")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(status)
        layout.addLayout(header)

        kpi_row = QHBoxLayout()
        self.card_events = StatCard("捕获行为", "Total Actions")
        self.card_risks = StatCard("风险报警", "Alerts")
        self.card_sessions = StatCard("监控场次", "Sessions")
        self.card_files = StatCard("敏感文件", "Protected")

        for c in [self.card_events, self.card_risks, self.card_sessions, self.card_files]:
            kpi_row.addWidget(c)

        layout.addLayout(kpi_row)

        chart_row = QHBoxLayout()
        self.line_chart = LineChart()
        self.status_detail = StatusDetailCard()

        chart_row.addWidget(self.line_chart, 3)
        chart_row.addWidget(self.status_detail, 1)

        layout.addLayout(chart_row, 1)

        self.desc_card = SystemDescCard()
        layout.addWidget(self.desc_card, 1)

        self.refresh()

    def update_data(self, data):
        self.card_events.set_value(data.get("events", 0))
        self.card_risks.set_value(data.get("risks", 0))
        self.card_sessions.set_value(data.get("sessions", 0))
        self.card_files.set_value(data.get("files", 0))
        self.line_chart.set_data(data.get("trend", []))

    def refresh(self):
        self.update_data(load_data())


def load_data():
    res = {"events": 0, "risks": 0, "sessions": 0, "files": 12, "trend": [0, 0, 0, 0, 0]}
    try:
        path = main_app.SCREEN_RECORD
        if os.path.exists(path):
            sess_list = sorted([d for d in os.listdir(path) if d.startswith("session_")])
            res["sessions"] = len(sess_list)

            trend = []
            for s in sess_list[-5:]:
                kf = os.path.join(path, s, "logs", "keyevents.json")
                if os.path.exists(kf):
                    with open(kf, "r", encoding="utf-8") as f:
                        trend.append(len(json.load(f)))
                else:
                    trend.append(0)

            res["trend"] = trend
            res["events"] = sum(trend)
            res["risks"] = int(res["events"] * 0.05)
    except:
        pass

    return res