from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen

# ============================================================================
# 颜色定义 (与 backlist.py 保持一致，也可以考虑统一到一个 color.py 文件)
# ============================================================================
ACCENT_CYAN = "#00F2FF"
ACCENT_BLUE = "#3B82F6"

class MiniBarChart(QWidget):
    """加高版拦截记录趋势图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(65)
        self.values = [40, 65, 50, 85, 100, 75, 90]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.values:
            return
        w = self.width() / len(self.values)
        for i, val in enumerate(self.values):
            bar_h = (val / 100) * (self.height() - 10)
            rect_x = int(i * w + 4)
            rect_y = int(self.height() - bar_h)
            rect_w = int(max(w - 8, 2))
            grad = QLinearGradient(0, rect_y, 0, self.height())
            grad.setColorAt(0, QColor(ACCENT_CYAN))
            grad.setColorAt(1, QColor(ACCENT_BLUE))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect_x, rect_y, rect_w, int(bar_h), 2, 2)