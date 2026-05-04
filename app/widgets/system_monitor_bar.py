import os
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# ============================================================================
# 颜色定义 (与 main.py 保持一致)
# ============================================================================
BG_NAV = "#08101A"
TEXT_DIM = "#64748B"

class SystemMonitorBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.setStyleSheet(f"background-color: {BG_NAV}; border-top: 1px solid #1A2A3A;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        self.status_lbl = QLabel("● SYSTEM ONLINE")
        self.status_lbl.setStyleSheet("color: #10B981; font-size: 9px; font-weight: bold;")

        self.res_lbl = QLabel("CPU: 0% | MEM: 0%")
        self.res_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px;")

        layout.addWidget(self.status_lbl)
        layout.addStretch()
        layout.addWidget(self.res_lbl)

        timer = QTimer(self)
        timer.timeout.connect(self._update_res)
        timer.start(2000)

    def _update_res(self):
        if PSUTIL_AVAILABLE:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            self.res_lbl.setText(f"CPU: {cpu}% | MEM: {mem} %")
        else:
            self.res_lbl.setText("CPU: N/A | MEM: N/A (psutil not available)")