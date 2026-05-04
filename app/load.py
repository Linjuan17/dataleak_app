#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import threading
import os
import math
import json
import datetime
from pathlib import Path

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# =========================================================
# 🔹 通用组件：Switch 开关
# =========================================================
class Switch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setFixedSize(50, 25)
        self.checked = False

    def mousePressEvent(self, event):
        self.checked = not self.checked
        self.update()
        self.toggled.emit(self.checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#22c55e") if self.checked else QColor("#d1d5db"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, 50, 25, 12, 12)
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(25 if self.checked else 2, 2, 20, 20)


# =========================================================
# 🔹 登录轮播图组件
# =========================================================
class TechSlideWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.index = 0
        self.images = []
        self.load_images()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_slide)
        self.timer.start(4000)
        self.setMinimumSize(620, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def resource_path(self, relative_path):
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def load_images(self):
        paths = [
            "assets/login_slides/slide1.png",
            "assets/login_slides/slide2.png",
            "assets/login_slides/slide3.png",
            "assets/login_slides/slide4.png",
        ]
        for p in paths:
            full_path = self.resource_path(p)
            pix = QPixmap(full_path)
            if not pix.isNull():
                self.images.append(pix)

    def next_slide(self):
        if not self.images:
            return
        self.index = (self.index + 1) % len(self.images)
        self.update()

    def prev_slide(self):
        if not self.images:
            return
        self.index = (self.index - 1) % len(self.images)
        self.update()

    def mousePressEvent(self, event):
        if event.position().x() < self.width() / 2:
            self.prev_slide()
        else:
            self.next_slide()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        card = QRectF(8, 8, w - 16, h - 16)
        p.setBrush(QColor(8, 15, 32, 245))
        p.setPen(QPen(QColor(0, 240, 255, 90), 1))
        p.drawRoundedRect(card, 24, 24)
        if not self.images:
            p.setPen(QColor("#00F0FF"))
            p.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
            p.drawText(card, Qt.AlignmentFlag.AlignCenter, "未找到登录轮播图片")
            return
        pix = self.images[self.index]
        target_w = int(card.width())
        target_h = int(card.height())
        scaled = pix.scaled(target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x = int(card.x() + (target_w - scaled.width()) / 2)
        y = int(card.y() + (target_h - scaled.height()) / 2)
        path = QPainterPath()
        path.addRoundedRect(card, 24, 24)
        p.setClipPath(path)
        p.fillRect(card, QColor(5, 10, 24))
        p.drawPixmap(x, y, scaled)
        p.setClipping(False)
        overlay = QLinearGradient(0, 0, 0, h)
        overlay.setColorAt(0.0, QColor(0, 0, 0, 10))
        overlay.setColorAt(0.75, QColor(0, 0, 0, 10))
        overlay.setColorAt(1.0, QColor(0, 0, 0, 70))
        p.fillRect(card, overlay)
        p.setPen(QPen(QColor(0, 240, 255, 120), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(card, 24, 24)
        dot_y = h - 30
        start_x = w // 2 - (len(self.images) - 1) * 14
        for i in range(len(self.images)):
            color = QColor(0, 240, 255) if i == self.index else QColor(0, 240, 255, 70)
            p.setBrush(color)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(start_x + i * 28, dot_y), 5, 5)


# =========================================================
# 🔹 登录页面（仅保留此类，删除所有 main_app 相关代码）
# =========================================================
class LoginPage(QWidget):
    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.show_password = False
        self.setObjectName("LoginRoot")
        self.setStyleSheet("""
            QWidget#LoginRoot {
                background-color: #050A18;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.left = QFrame()
        self.left.setObjectName("LoginLeft")
        self.left.setStyleSheet("""
            QFrame#LoginLeft {
                background-color: #050A18;
                border-right: 2px solid rgba(0,240,255,0.22);
            }
            QFrame#LoginLeft QLabel {
                background: transparent;
                border: none;
            }
        """)

        left_layout = QVBoxLayout(self.left)
        left_layout.setContentsMargins(50, 50, 42, 42)
        left_layout.setSpacing(16)

        self.name_label = QLabel("DataLeakDetector")
        self.name_label.setStyleSheet("""
            QLabel {
                color: #00F0FF;
                font-size: 36px;
                font-weight: 900;
                letter-spacing: 5px;
            }
        """)

        self.sub_label = QLabel("AI SECURITY PLATFORM")
        self.sub_label.setStyleSheet("""
            QLabel {
                color: rgba(0,240,255,0.65);
                font-size: 14px;
                letter-spacing: 4px;
            }
        """)

        left_layout.addWidget(self.name_label)
        left_layout.addWidget(self.sub_label)
        left_layout.addSpacing(16)

        self.slide = TechSlideWidget()
        left_layout.addWidget(self.slide, 1)

        slogan = QLabel("REAL-TIME · ANALYSIS · TRACE · ALERT")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slogan.setStyleSheet("""
            QLabel {
                color: rgba(0,240,255,0.5);
                font-size: 12px;
                letter-spacing: 3px;
            }
        """)
        left_layout.addWidget(slogan)

        self.right = QFrame()
        self.right.setObjectName("LoginRight")
        self.right.setStyleSheet("""
            QFrame#LoginRight {
                background-color: #050A18;
            }
            QFrame#LoginRight QLabel {
                background: transparent;
                border: none;
            }
        """)

        self.right_layout = QVBoxLayout(self.right)
        self.right_layout.setContentsMargins(50, 50, 50, 50)

        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.card.setStyleSheet("""
            QFrame#LoginCard {
                background-color: rgba(11,17,32,0.96);
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: 24px;
            }
            QFrame#LoginCard QLabel {
                background: transparent;
                border: none;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(42)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 240, 255, 55))
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)

        self.title = QLabel("管理员登录")
        self.subtitle = QLabel("ACCESS SECURE CONTROL PANEL")
        self.error = QLabel("")

        self.username = QLineEdit()
        self.username.setPlaceholderText("管理员工号")

        self.password = QLineEdit()
        self.password.setPlaceholderText("密码")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(10)

        self.eye_btn = QPushButton("显示")
        self.eye_btn.clicked.connect(self.toggle_password)

        pwd_row.addWidget(self.password, 1)
        pwd_row.addWidget(self.eye_btn)

        self.agree = QCheckBox("我已阅读并同意《隐私声明》和《数据使用协议》")

        self.forgot = QPushButton("忘记密码？")
        self.forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "请联系系统管理员重置密码。")
        )

        self.login_btn = QPushButton("进入控制台")
        self.login_btn.clicked.connect(self.handle_login)

        self.offline_btn = QPushButton("离线模式")
        self.offline_btn.clicked.connect(self.login_success.emit)

        self.notice = QLabel("🔒 所有操作将被记录用于安全审计")
        self.notice.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card_layout.addWidget(self.title)
        self.card_layout.addWidget(self.subtitle)
        self.card_layout.addWidget(self.error)
        self.card_layout.addWidget(self.username)
        self.card_layout.addLayout(pwd_row)
        self.card_layout.addWidget(self.agree)
        self.card_layout.addWidget(self.forgot, alignment=Qt.AlignmentFlag.AlignRight)
        self.card_layout.addWidget(self.login_btn)
        self.card_layout.addWidget(self.offline_btn)
        self.card_layout.addWidget(self.notice)

        self.right_layout.addStretch(1)
        self.right_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addStretch(1)

        root.addWidget(self.left, 62)
        root.addWidget(self.right, 38)

        self.apply_responsive_style()

    def apply_responsive_style(self):
        w = max(self.width(), 1200)
        scale = max(0.9, min(w / 1600, 1.65))
        card_w = int(min(max(w * 0.28, 460), 900))
        self.card.setMinimumWidth(card_w)
        self.card.setMaximumWidth(card_w)
        self.card_layout.setContentsMargins(int(42 * scale), int(40 * scale), int(42 * scale), int(40 * scale))
        self.card_layout.setSpacing(int(15 * scale))

        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: #00F0FF;
                font-size: {int(34 * scale)}px;
                font-weight: 900;
                letter-spacing: {max(3, int(5 * scale))}px;
            }}
        """)
        self.sub_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(0,240,255,0.65);
                font-size: {int(13 * scale)}px;
                letter-spacing: {max(3, int(4 * scale))}px;
            }}
        """)
        self.title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {int(28 * scale)}px;
                font-weight: 900;
            }}
        """)
        self.subtitle.setStyleSheet(f"""
            QLabel {{
                color: rgba(0,240,255,0.58);
                font-size: {int(11 * scale)}px;
                letter-spacing: {max(2, int(3 * scale))}px;
            }}
        """)
        self.error.setFixedHeight(int(24 * scale))
        self.error.setStyleSheet(f"""
            QLabel {{
                color: #FF2D75;
                font-size: {int(13 * scale)}px;
            }}
        """)
        input_h = int(48 * scale)
        self.username.setMinimumHeight(input_h)
        self.password.setMinimumHeight(input_h)
        self.eye_btn.setFixedWidth(int(68 * scale))
        self.eye_btn.setMinimumHeight(input_h)
        self.username.setStyleSheet(self.input_style(scale))
        self.password.setStyleSheet(self.input_style(scale))
        self.eye_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0,240,255,0.08);
                color: #00F0FF;
                border: 1px solid rgba(0,240,255,0.25);
                border-radius: {int(12 * scale)}px;
                font-size: {int(12 * scale)}px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,240,255,0.14);
            }}
        """)
        self.agree.setStyleSheet(f"""
            QCheckBox {{
                color: rgba(229,247,255,0.70);
                font-size: {int(13 * scale)}px;
                background: transparent;
                border: none;
            }}
            QCheckBox::indicator {{
                width: {int(17 * scale)}px;
                height: {int(17 * scale)}px;
            }}
        """)
        self.forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: rgba(0,240,255,0.72);
                font-size: {int(12 * scale)}px;
            }}
            QPushButton:hover {{
                color: #00F0FF;
                text-decoration: underline;
            }}
        """)
        btn_h = int(52 * scale)
        self.login_btn.setMinimumHeight(btn_h)
        self.offline_btn.setMinimumHeight(int(48 * scale))
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00F0FF, stop:0.55 #5A6FD8, stop:1 #7C3AED);
                color: black;
                border: none;
                border-radius: {int(14 * scale)}px;
                font-size: {int(16 * scale)}px;
                font-weight: 900;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                border: 1px solid #00F0FF;
            }}
        """)
        self.offline_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(0,240,255,0.78);
                border: 1px solid rgba(0,240,255,0.34);
                border-radius: {int(14 * scale)}px;
                font-size: {int(14 * scale)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0,240,255,0.08);
                color: #00F0FF;
            }}
        """)
        self.notice.setStyleSheet(f"""
            QLabel {{
                color: rgba(0,240,255,0.54);
                font-size: {int(12 * scale)}px;
                border: 1px solid rgba(0,240,255,0.16);
                border-radius: {int(12 * scale)}px;
                padding: {int(11 * scale)}px;
                background-color: rgba(0,240,255,0.05);
            }}
        """)

    def input_style(self, scale=1.0):
        return f"""
            QLineEdit {{
                background-color: rgba(5,10,24,0.76);
                color: white;
                border: 1px solid rgba(0,240,255,0.28);
                border-radius: {int(12 * scale)}px;
                padding-left: {int(15 * scale)}px;
                font-size: {int(15 * scale)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid #00F0FF;
                background-color: rgba(5,10,24,0.96);
            }}
        """

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_responsive_style()

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password.setEchoMode(QLineEdit.EchoMode.Normal if self.show_password else QLineEdit.EchoMode.Password)
        self.eye_btn.setText("隐藏" if self.show_password else "显示")

    def handle_login(self):
        self.error.setText("")
        if not self.username.text().strip() or not self.password.text().strip():
            self.error.setText("请输入用户名和密码")
            return
        if not self.agree.isChecked():
            self.error.setText("请先阅读并同意隐私声明和数据使用协议")
            return
        self.login_success.emit()