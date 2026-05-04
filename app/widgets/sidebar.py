from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# ============================================================================
# 颜色定义 (与 DATA1 整体风格保持一致)
# ============================================================================
ACCENT_CYAN = "#00F2FF" # Used for hover/selected states
BG_DARK = "#0A0E17" # Main background, for general styling consistency
TEXT_PRIMARY = "#F1F5F9" # Main text color

class Sidebar(QWidget):
    """左侧纯文字侧边栏"""

    # 页面切换信号
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setFixedWidth(80)
        self.setStyleSheet(f"""
            #sidebar {{
                background: {BG_DARK};
                border-right: 1px solid rgba(0, 212, 255, 0.05);
            }}
            QPushButton {{
                color: {TEXT_PRIMARY};
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: rgba(0, 212, 255, 0.08);
            }}
            QPushButton:checked {{
                background: rgba(0, 212, 255, 0.12);
                color: {ACCENT_CYAN};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 30, 0, 16)
        layout.setSpacing(10)

        self.nav_buttons = []
        nav_items = [
            ("总览", 0),          # Risk Overview
            ("人员管理", 1),      # Personnel Management (Original "管理")
            ("黑白名单", 2),      # Blacklist Management
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setFixedSize(68, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Microsoft YaHei", 10))
            btn.setCheckable(True) # Make buttons checkable

            btn.clicked.connect(lambda checked, i=index: self.on_nav_clicked(i))
            self.nav_buttons.append(btn)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)

        # Set default selected button (Risk Overview)
        self.nav_buttons[0].setChecked(True)
        self.on_nav_clicked(0) # Manually call to set initial style and emit signal

        layout.addStretch()

    def on_nav_clicked(self, index):
        """导航按钮点击"""
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

        self.page_changed.emit(index)