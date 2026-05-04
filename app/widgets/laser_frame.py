from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen, QBrush

class LaserFrame(QFrame):
    """
    玻璃拟态容器：半透明背景、渐变边框、外发光阴影
    """
    def __init__(self, parent=None, glow_color=QColor(0, 242, 255, 60)):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")
        # 外发光阴影（加强发光效果）
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(glow_color)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = 8  # 稍小一点的圆角，配合原风格

        # 1. 半透明背景（毛玻璃）
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(15, 23, 42, 180))
        painter.drawRoundedRect(rect, radius, radius)

        # 2. 渐变边框（修复：使用 QPointF）
        start_point = QPointF(rect.topLeft())
        end_point = QPointF(rect.bottomRight())
        grad = QLinearGradient(start_point, end_point)
        grad.setColorAt(0, QColor(255, 255, 255, 80))   # 浅白高光
        grad.setColorAt(0.5, QColor(255, 255, 255, 15))
        grad.setColorAt(1, QColor(0, 242, 255, 60))     # 青色辉光

        pen = QPen(grad, 1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)
