import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import main_app


CYAN = "#00F0FF"
GREEN = "#22C55E"
RED = "#FF2D75"
PURPLE = "#7C3AED"
YELLOW = "#FACC15"
BG = "#050A18"


def label(text, size=18, color="#E5F7FF", bold=False):
    w = QLabel(text)
    w.setStyleSheet(f"""
        QLabel {{
            color: {color};
            font-size: {size}px;
            font-weight: {'900' if bold else 'normal'};
            background: transparent;
            border: none;
            font-family: "Microsoft YaHei", "Segoe UI";
        }}
    """)
    return w


class CyberCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("CyberCard")
        self.setStyleSheet("""
            QFrame#CyberCard {
                background-color: rgba(11,17,32,0.96);
                border: 1px solid rgba(0,240,255,0.24);
                border-radius: 18px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)


class StatCard(CyberCard):
    def __init__(self, title, value, subtitle, color):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(8)

        self.title = label(title, 18, "#BFEFFF", True)
        self.value = label(str(value), 38, color, True)
        self.sub = label(subtitle, 15, "rgba(229,247,255,0.65)")

        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.value)
        layout.addWidget(self.sub)

    def set_value(self, value):
        self.value.setText(str(value))


class TrendPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.data = [18, 26, 21, 34, 42, 36, 58, 49, 67, 72, 61, 88]
        self.setMinimumHeight(360)

    def set_data(self, data):
        default_data = [18, 26, 21, 34, 42, 36, 58, 49, 67, 72, 61, 88]

        if not data or len(data) < 5 or sum(data) <= 0:
            self.data = default_data
        else:
            self.data = data[-12:]
            if len(self.data) < 12:
                self.data = default_data[:12 - len(self.data)] + self.data

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        left = 78
        right = 90
        top = 38
        bottom = 66

        cw = w - left - right
        ch = h - top - bottom

        if cw <= 0 or ch <= 0:
            return

        p.setPen(QPen(QColor(0, 240, 255, 28), 1))
        for i in range(5):
            y = top + ch * i / 4
            p.drawLine(left, int(y), w - right, int(y))

        max_v = max(max(self.data), 10)
        step = cw / max(1, len(self.data) - 1)

        pts = []
        for i, v in enumerate(self.data):
            x = left + i * step
            y = top + ch - (v / max_v) * ch
            pts.append(QPointF(x, y))

        p.setPen(QPen(QColor(0, 240, 255, 70), 8, Qt.SolidLine, Qt.RoundCap))
        for i in range(len(pts) - 1):
            p.drawLine(pts[i], pts[i + 1])

        p.setPen(QPen(QColor(CYAN), 3, Qt.SolidLine, Qt.RoundCap))
        for i in range(len(pts) - 1):
            p.drawLine(pts[i], pts[i + 1])

        p.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        for i, pt in enumerate(pts):
            p.setBrush(QColor(BG))
            p.setPen(QPen(QColor(CYAN), 2))
            p.drawEllipse(pt, 5, 5)

            if i % 2 == 0:
                p.setPen(QColor("#DDF7FF"))
                p.drawText(int(pt.x() - 14), int(pt.y() - 18), str(self.data[i]))

        p.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        p.setPen(QColor("#8EDFFF"))

        labels = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]
        for i, lab in enumerate(labels):
            x = left + i * cw / (len(labels) - 1)
            if i == len(labels) - 1:
                p.drawText(int(x - 58), h - 24, lab)
            else:
                p.drawText(int(x - 28), h - 24, lab)


class TrendCard(CyberCard):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(8)

        title = label("行为监控趋势", 30, CYAN, True)
        subtitle = label("BEHAVIOR TREND", 17, CYAN, True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.plot = TrendPlot()
        layout.addWidget(self.plot, 1)

    def set_data(self, data):
        self.plot.set_data(data)


class DonutWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.safe = 73
        self.mid = 18
        self.high = 9
        self.setMinimumSize(210, 210)

    def set_values(self, safe, mid, high):
        self.safe = safe
        self.mid = mid
        self.high = high
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h) - 40

        rect = QRectF(
            (w - size) / 2,
            (h - size) / 2,
            size,
            size
        )

        values = [
            (self.safe, GREEN),
            (self.mid, PURPLE),
            (self.high, RED),
        ]

        start = 90 * 16
        for value, color in values:
            span = -int(360 * value / 100 * 16)
            p.setPen(QPen(QColor(color), 16, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(rect, start, span)
            start += span

        # 中心遮罩，保证 RISK 不被圆环压住
        inner_margin = 52
        inner = QRectF(
            rect.x() + inner_margin,
            rect.y() + inner_margin,
            rect.width() - inner_margin * 2,
            rect.height() - inner_margin * 2
        )
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(11, 17, 32))
        p.drawEllipse(inner)

        p.setFont(QFont("Consolas", 20, QFont.Bold))
        p.setPen(QColor(CYAN))
        p.drawText(inner, Qt.AlignCenter, "RISK")


class RiskPanel(CyberCard):
    def __init__(self):
        super().__init__()

        self.safe = 73
        self.mid = 18
        self.high = 9

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(14)

        layout.addWidget(label("风险分布", 28, CYAN, True))
        layout.addWidget(label("", 16, CYAN, True))

        self.donut = DonutWidget()
        self.donut.setFixedSize(220, 220)

        donut_row = QHBoxLayout()
        donut_row.addStretch()
        donut_row.addWidget(self.donut)
        donut_row.addStretch()
        layout.addLayout(donut_row)

        self.safe_value = self.percent_row(layout, "低风险", GREEN, "73%")
        self.mid_value = self.percent_row(layout, "中风险", PURPLE, "18%")
        self.high_value = self.percent_row(layout, "高风险", RED, "9%")

        layout.addSpacing(8)
        layout.addWidget(label("TOP SOURCES", 22, CYAN, True))

        self.source_bar(layout, "黑名单应用", 78, RED)
        self.source_bar(layout, "敏感文件访问", 66, YELLOW)
        self.source_bar(layout, "文件外发路径", 54, PURPLE)

        layout.addStretch()

    def percent_row(self, parent_layout, name, color, value):
        row = QHBoxLayout()

        left = label(f"● {name}", 20, color, True)
        right = label(value, 20, "#E5F7FF", True)
        right.setAlignment(Qt.AlignRight)

        row.addWidget(left)
        row.addStretch()
        row.addWidget(right)

        parent_layout.addLayout(row)
        return right

    def source_bar(self, parent_layout, name, value, color):
        row = QHBoxLayout()

        name_lbl = label(name, 18, "#E5F7FF", True)
        val_lbl = label(f"{value}%", 18, color, True)

        row.addWidget(name_lbl)
        row.addStretch()
        row.addWidget(val_lbl)
        parent_layout.addLayout(row)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(value)
        bar.setTextVisible(False)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(0,240,255,0.14);
                border: none;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)
        parent_layout.addWidget(bar)

    def set_values(self, risks, events):
        self.safe = 73
        self.mid = 18
        self.high = 9

        self.safe_value.setText("73%")
        self.mid_value.setText("18%")
        self.high_value.setText("9%")
        self.donut.set_values(73, 18, 9)


class EventStream(CyberCard):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        layout.addWidget(label("安全事件流 / SECURITY EVENT STREAM", 22, CYAN, True))

        events = [
            ("INFO", "屏幕监控服务已启动", GREEN),
            ("WARN", "检测到敏感文件访问行为", YELLOW),
            ("RISK", "黑名单应用窗口活动已记录", RED),
            ("INFO", "审计日志已写入本地证据链", CYAN),
        ]

        for tag, text, color in events:
            row = QLabel(f"{tag:<6}   {text}")
            row.setStyleSheet(f"""
                QLabel {{
                    color:#E5F7FF;
                    font-size:19px;
                    font-family: Consolas, Microsoft YaHei;
                    padding:12px 14px;
                    border-left:5px solid {color};
                    background-color:rgba(0,240,255,0.06);
                    border-radius:8px;
                }}
            """)
            layout.addWidget(row)

        layout.addStretch()


class AbilityMatrix(CyberCard):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        layout.addWidget(label("能力矩阵 / CAPABILITY MATRIX", 22, CYAN, True))

        items = [
            ("实时监控", "ONLINE", GREEN),
            ("敏感文件识别", "ACTIVE", CYAN),
            ("AI风险分析", "READY", PURPLE),
            ("审计报告生成", "ENABLED", YELLOW),
        ]

        for name, state, color in items:
            row = QHBoxLayout()

            left = label(name, 20, "#E5F7FF")
            right = QLabel(state)
            right.setAlignment(Qt.AlignCenter)
            right.setMinimumWidth(105)
            right.setStyleSheet(f"""
                QLabel {{
                    color:{color};
                    font-size:16px;
                    font-weight:bold;
                    padding:8px 12px;
                    border:1px solid {color};
                    border-radius:9px;
                    background: transparent;
                }}
            """)

            row.addWidget(left)
            row.addStretch()
            row.addWidget(right)
            layout.addLayout(row)

        layout.addStretch()


class SystemIntro(CyberCard):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 20, 26, 20)
        layout.setSpacing(14)

        layout.addWidget(label("DataLeakDetector Pro", 26, CYAN, True))

        desc = label(
            "AI驱动的数据泄露监测平台，融合屏幕行为监控、敏感文件追踪、上传风险识别与审计溯源能力。",
            19,
            "#BFD7EA",
            False
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        tags = label("REAL-TIME MONITORING  ·  FILE TRACKING  ·  AI RISK DETECTION  ·  AUDIT TRACE", 18, GREEN, True)
        layout.addWidget(tags)

        layout.addStretch()


class DashboardPro(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color:#050A18;
                color:#E5F7FF;
                font-family:"Microsoft YaHei", "Segoe UI";
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()

        title = label("数据安全态势总览", 30, CYAN, True)
        status = label("● SYSTEM ONLINE", 18, GREEN, True)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(status)
        root.addLayout(header)

        kpi = QHBoxLayout()
        kpi.setSpacing(16)

        self.card_events = StatCard("捕获行为", "126", "TOTAL ACTIONS", CYAN)
        self.card_risks = StatCard("风险报警", "12", "RISK ALERTS", RED)
        self.card_sessions = StatCard("监控场次", "5", "SESSIONS", PURPLE)
        self.card_files = StatCard("敏感文件", "34", "PROTECTED FILES", GREEN)

        for c in [self.card_events, self.card_risks, self.card_sessions, self.card_files]:
            c.setMinimumHeight(125)
            kpi.addWidget(c)

        root.addLayout(kpi)

        middle = QHBoxLayout()
        middle.setSpacing(16)

        self.trend = TrendCard()
        self.risk_panel = RiskPanel()

        self.trend.setMinimumHeight(430)
        self.risk_panel.setMinimumWidth(390)

        middle.addWidget(self.trend, 3)
        middle.addWidget(self.risk_panel, 1)

        root.addLayout(middle, 3)

        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        self.intro = SystemIntro()
        self.stream = EventStream()
        self.matrix = AbilityMatrix()

        bottom.addWidget(self.intro, 2)
        bottom.addWidget(self.stream, 2)
        bottom.addWidget(self.matrix, 1)

        root.addLayout(bottom, 1)

        self.refresh()

    def update_data(self, data):
        self.card_events.set_value(data.get("events", 126))
        self.card_risks.set_value(data.get("risks", 12))
        self.card_sessions.set_value(data.get("sessions", 5))
        self.card_files.set_value(data.get("files", 34))

        self.trend.set_data(data.get("trend", []))
        self.risk_panel.set_values(data.get("risks", 12), data.get("events", 126))

    def refresh(self):
        self.update_data(load_data())


def load_data():
    res = {
        "events": 126,
        "risks": 12,
        "sessions": 5,
        "files": 34,
        "trend": [18, 26, 21, 34, 42, 36, 58, 49, 67, 72, 61, 88],
    }

    try:
        path = main_app.SCREEN_RECORD
        if os.path.exists(path):
            sessions = sorted([d for d in os.listdir(path) if d.startswith("session_")])
            if sessions:
                res["sessions"] = len(sessions)

                trend = []
                risk_count = 0

                for s in sessions[-12:]:
                    key_file = os.path.join(path, s, "logs", "keyevents.json")
                    if os.path.exists(key_file):
                        with open(key_file, "r", encoding="utf-8") as f:
                            events = json.load(f)

                        trend.append(len(events))
                        risk_count += sum(
                            1 for e in events
                            if "blacklist" in json.dumps(e, ensure_ascii=False).lower()
                            or "敏感" in json.dumps(e, ensure_ascii=False)
                        )
                    else:
                        trend.append(0)

                if sum(trend) > 0:
                    res["trend"] = trend[-12:]
                    res["events"] = sum(trend)
                    res["risks"] = risk_count

    except Exception:
        pass

    return res
