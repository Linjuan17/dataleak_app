#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控开关组件
用于控制员工的监控状态
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class MonitorSwitch(QWidget):
    """监控开关组件"""

    # 状态变化信号
    state_changed = pyqtSignal(bool)

    def __init__(self, monitored=False, parent=None):
        super().__init__(parent)
        self._monitored = monitored
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 标签
        self.label = QLabel("监控")
        self.label.setStyleSheet("color: #8B95A5; font-size: 11px;")

        # 开关
        self.switch = QCheckBox()
        self.switch.setChecked(self._monitored)
        self.switch.setStyleSheet("""
            QCheckBox {
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                background: rgba(0, 212, 255, 0.15);
                border: 1px solid rgba(0, 212, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #00FFA3);
                border: none;
            }
        """)
        self.switch.stateChanged.connect(self.on_state_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.switch)

    def on_state_changed(self, state):
        """状态变化"""
        self._monitored = state == Qt.CheckState.Checked.value
        self.state_changed.emit(self._monitored)

    def is_checked(self):
        """获取状态"""
        return self._monitored

    def set_checked(self, checked):
        """设置状态"""
        self._monitored = checked
        self.switch.setChecked(checked)
