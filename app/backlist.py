#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QLineEdit, QRadioButton,
    QStackedWidget, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QMessageBox, QInputDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QBrush

from widgets.laser_frame import LaserFrame
from widgets.mini_bar_chart import MiniBarChart

# 视觉规范
ACCENT_CYAN = "#00F2FF"
ACCENT_BLUE = "#3B82F6"
TEXT_PRIMARY = "#F1F5F9"
TEXT_DIM = "#94A3B8"
RED_ALERT = "#EF4444"
GREEN_OK = "#10B981"


# ============================================================================
# 弹窗组件：新增审计项（修复单选按钮样式）
# ============================================================================
class AddItemDialog(QDialog):
    item_added = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 320)
        self.drag_pos = QPoint()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.frame = LaserFrame()
        layout.addWidget(self.frame)

        content_layout = QVBoxLayout(self.frame)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(15)

        title = QLabel("添加审计项")
        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 14pt; font-weight: bold;")
        content_layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入文件后缀或程序名 (如 *.exe)")
        self.name_input.setStyleSheet(f"""
            QLineEdit {{ 
                background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
                color: white; padding: 12px; border-radius: 6px; font-size: 10pt;
            }}
        """)
        content_layout.addWidget(self.name_input)

        type_h = QHBoxLayout()
        self.rb_black = QRadioButton("受限 (黑名单)")
        self.rb_white = QRadioButton("信任 (白名单)")
        self.rb_black.setChecked(True)

        # 修复：白色圆圈，选中后整个圆填充白色
        radio_style = """
            QRadioButton { color: #F1F5F9; font-size: 10pt; }
            QRadioButton::indicator {
                width: 16px; height: 16px;
                border-radius: 8px;
                border: 1px solid white;
                background: transparent;
            }
            QRadioButton::indicator:checked {
                background: white;
            }
        """
        for rb in [self.rb_black, self.rb_white]:
            rb.setStyleSheet(radio_style)
            type_h.addWidget(rb)

        content_layout.addLayout(type_h)

        btn_h = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        submit_btn = QPushButton("确定")

        btn_style = "QPushButton { padding: 8px 20px; border-radius: 4px; font-weight: bold; min-width: 80px; }"
        cancel_btn.setStyleSheet(btn_style + f"QPushButton {{ background: rgba(255,255,255,0.1); color: {TEXT_DIM}; }}")
        submit_btn.setStyleSheet(btn_style + f"QPushButton {{ background: {ACCENT_BLUE}; color: white; }}")

        cancel_btn.clicked.connect(self.reject)
        submit_btn.clicked.connect(self._submit)

        btn_h.addStretch()
        btn_h.addWidget(cancel_btn)
        btn_h.addWidget(submit_btn)
        content_layout.addLayout(btn_h)

    def _submit(self):
        text = self.name_input.text().strip()
        if text:
            l_type = "blacklist" if self.rb_black.isChecked() else "whitelist"
            self.item_added.emit(text, l_type)
            self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)


# ============================================================================
# 列表面板组件（受限/信任）
# ============================================================================
class ListPanel(LaserFrame):
    def __init__(self, list_type="blacklist", parent=None):
        super().__init__(parent)
        self.list_type = list_type
        self._items = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        color = RED_ALERT if self.list_type == "blacklist" else GREEN_OK

        header = QHBoxLayout()
        title = QLabel("🚫 受限资产" if self.list_type == "blacklist" else "✅ 信任资产")
        title.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12pt;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background: transparent; border: none; outline: none; }
            QListWidget::item { border-bottom: 1px solid rgba(255,255,255,0.05); }
        """)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.list_widget)

    def add_item(self, name):
        if name not in self._items:
            self._items.append(name)
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(QSize(0, 50))

            row = QWidget()
            row_l = QHBoxLayout(row)
            row_l.setContentsMargins(12, 0, 12, 0)

            lbl = QLabel(name)
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11pt;")

            del_btn = QPushButton("×")
            del_btn.setFixedSize(26, 26)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{ color: {TEXT_DIM}; border: none; font-size: 16pt; background: transparent; }}
                QPushButton:hover {{ color: {RED_ALERT}; }}
            """)
            del_btn.clicked.connect(lambda: self._remove(name))

            row_l.addWidget(lbl)
            row_l.addStretch()
            row_l.addWidget(del_btn)
            self.list_widget.setItemWidget(item, row)

    def _remove(self, name):
        if name in self._items:
            self._items.remove(name)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                label = widget.findChild(QLabel)
                if label and label.text() == name:
                    self.list_widget.takeItem(i)
                    break
        if hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'update_stats'):
            self.parent().parent().update_stats()

    def get_items(self):
        return self._items.copy()

    def get_count(self):
        return len(self._items)


# ============================================================================
# 主页面
# ============================================================================
class BlacklistPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

        # 初始化拦截记录（预置固定数据）
        self.block_records = [
            ("E001", "张明远", "公司合作合同.docx", "阻断上传", "09:32:15"),
            ("E008", "周丽华", "微信", "运行拦截", "10:05:42"),
            ("E003", "王建国", "产品设计方案.zip", "禁止访问", "10:28:33"),
            ("E012", "林小敏", "钉钉", "阻断上传", "11:12:06"),
            ("E007", "孙伟东", "API密钥.txt", "隔离文件", "13:45:22"),
            ("E017", "马防护", "百度网盘", "运行拦截", "14:30:18"),
        ]
        self._refresh_record_table()

        # 初始化黑白名单（初始只显示3-4条，使列表变矮）
        self._init_default_lists()
        self.update_stats()

    def _init_default_lists(self):
        """每个列表只显示3-4条初始记录，让中间区域更矮"""
        # 文件黑名单（3条具体文件名）
        file_black_items = ["公司合作合同.docx", "产品设计方案.zip", "API密钥.txt"]
        # 文件白名单（3条）
        file_white_items = ["普通文档.txt", "日志文件.log", "临时文件.tmp"]
        # 软件黑名单（4条）
        soft_black_items = ["微信", "钉钉", "夸克网盘", "百度网盘"]
        # 软件白名单（3条）
        soft_white_items = ["企业微信", "Microsoft Teams", "WPS"]

        for item in file_black_items:
            self.file_black.add_item(item)
        for item in file_white_items:
            self.file_white.add_item(item)
        for item in soft_black_items:
            self.soft_black.add_item(item)
        for item in soft_white_items:
            self.soft_white.add_item(item)

    def _refresh_record_table(self):
        self.table.setRowCount(len(self.block_records))
        for row, (emp_id, emp_name, target, action, time_str) in enumerate(self.block_records):
            self.table.setItem(row, 0, QTableWidgetItem(emp_id))
            self.table.setItem(row, 1, QTableWidgetItem(emp_name))
            self.table.setItem(row, 2, QTableWidgetItem(target))
            self.table.setItem(row, 3, QTableWidgetItem(action))
            self.table.setItem(row, 4, QTableWidgetItem(time_str))

    # --------------------------- UI 构建 ----------------------------
    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域（白底深蓝色滚动条）
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
                margin: 0px;
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

        # --- 顶部统计指标卡片（恢复原始高度110，数字26pt）---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        self.card_black = self._create_stat_card("受限资产总数", "0", RED_ALERT, height=110, font_size=26)
        self.card_white = self._create_stat_card("信任资产总数", "0", GREEN_OK, height=110, font_size=26)
        self.card_chart = self._create_chart_card("最近拦截趋势", "47", height=110)
        stats_layout.addWidget(self.card_black, 1)
        stats_layout.addWidget(self.card_white, 1)
        stats_layout.addWidget(self.card_chart, 1)
        main_layout.addLayout(stats_layout)

        # --- 导航与操作栏 ---
        nav_h = QHBoxLayout()
        self.btn_file = QPushButton("📁 文件审计")
        self.btn_soft = QPushButton("💿 软件审计")
        nav_btn_style = f"""
            QPushButton {{ 
                background: rgba(13, 20, 33, 0.4); color: {TEXT_DIM}; 
                border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; 
                font-weight: bold;
            }} 
            QPushButton:checked {{ 
                background: rgba(0, 242, 255, 0.1); color: {ACCENT_CYAN}; 
                border: 1px solid {ACCENT_CYAN}; 
            }}
        """
        for b in [self.btn_file, self.btn_soft]:
            b.setCheckable(True)
            b.setFixedSize(140, 42)
            b.setStyleSheet(nav_btn_style)
        self.btn_file.setChecked(True)

        self.import_btn = QPushButton("📥 批量导入")
        self.add_btn = QPushButton("＋ 新增审计项")
        act_style = f"""
            QPushButton {{ 
                background: {ACCENT_BLUE}; color: white; border-radius: 6px; 
                font-weight: bold; font-size: 10pt; padding: 0 15px;
            }}
            QPushButton:hover {{ background: #2563EB; }}
        """
        self.import_btn.setStyleSheet(act_style)
        self.add_btn.setStyleSheet(act_style)
        self.import_btn.setFixedHeight(40)
        self.add_btn.setFixedHeight(40)

        nav_h.addWidget(self.btn_file)
        nav_h.addWidget(self.btn_soft)
        nav_h.addStretch()
        nav_h.addWidget(self.import_btn)
        nav_h.addWidget(self.add_btn)
        main_layout.addLayout(nav_h)

        # --- 审计列表堆栈（降低最小高度，使中间区域更矮）---
        self.stack = QStackedWidget()
        self.stack.setMinimumHeight(280)   # 从350降为280，适应少量列表项

        # 文件审计页
        self.page_file = QWidget()
        fl = QHBoxLayout(self.page_file)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(15)
        self.file_black = ListPanel("blacklist")
        self.file_white = ListPanel("whitelist")
        fl.addWidget(self.file_black, 1)
        fl.addWidget(self.file_white, 1)

        # 软件审计页
        self.page_soft = QWidget()
        sl = QHBoxLayout(self.page_soft)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(15)
        self.soft_black = ListPanel("blacklist")
        self.soft_white = ListPanel("whitelist")
        sl.addWidget(self.soft_black, 1)
        sl.addWidget(self.soft_white, 1)

        self.stack.addWidget(self.page_file)
        self.stack.addWidget(self.page_soft)
        main_layout.addWidget(self.stack)

        # --- 底部拦截记录表格（高度保持160）---
        main_layout.addWidget(
            QLabel("🕒 最近拦截记录", styleSheet=f"color: {TEXT_PRIMARY}; font-weight: bold; margin-top: 5px;"))
        self.record_table_container = self._create_record_table(height=160)
        main_layout.addWidget(self.record_table_container)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

        # 信号连接
        self.btn_file.clicked.connect(self._switch_to_file)
        self.btn_soft.clicked.connect(self._switch_to_soft)
        self.add_btn.clicked.connect(self._show_add)
        self.import_btn.clicked.connect(self._do_import)

    def _create_stat_card(self, title, val, color, height=110, font_size=26):
        card = LaserFrame()
        card.setFixedHeight(height)
        l = QVBoxLayout(card)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel(title)
        t.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10pt;")
        v = QLabel(val)
        v.setStyleSheet(f"color: {color}; font-size: {font_size}pt; font-weight: bold; font-family: 'Segoe UI';")
        l.addWidget(t, 0, Qt.AlignmentFlag.AlignCenter)
        l.addWidget(v, 0, Qt.AlignmentFlag.AlignCenter)
        return card

    def _create_chart_card(self, title, val, height=110):
        card = LaserFrame()
        card.setFixedHeight(height)
        l = QVBoxLayout(card)
        header = QLabel(f"{title}: {val}")
        header.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10pt;")
        l.addWidget(header)
        chart = MiniBarChart()
        l.addWidget(chart)
        return card

    def _create_record_table(self, height=160):
        container = LaserFrame()
        container.setFixedHeight(height)
        l = QVBoxLayout(container)
        l.setContentsMargins(10, 10, 10, 10)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["员工ID", "员工姓名", "拦截目标", "审计动作", "命中时间"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{ 
                background: transparent; color: {TEXT_PRIMARY}; 
                gridline-color: transparent; border: none;
                alternate-background-color: rgba(255,255,255,0.03);
            }}
            QHeaderView::section {{
                background: rgba(255,255,255,0.05); color: {TEXT_DIM};
                padding: 4px; border: none; font-weight: bold;
            }}
        """)
        l.addWidget(self.table)
        return container

    # --------------------------- 功能方法 --------------------------
    def update_stats(self):
        black_total = self.file_black.get_count() + self.soft_black.get_count()
        white_total = self.file_white.get_count() + self.soft_white.get_count()
        for child in self.card_black.children():
            if isinstance(child, QLabel) and child.styleSheet() and 'font-size: 26pt' in child.styleSheet():
                child.setText(str(black_total))
                break
        for child in self.card_white.children():
            if isinstance(child, QLabel) and child.styleSheet() and 'font-size: 26pt' in child.styleSheet():
                child.setText(str(white_total))
                break

    def _switch_to_file(self):
        self.btn_soft.setChecked(False)
        self.btn_file.setChecked(True)
        self.stack.setCurrentIndex(0)

    def _switch_to_soft(self):
        self.btn_file.setChecked(False)
        self.btn_soft.setChecked(True)
        self.stack.setCurrentIndex(1)

    def _show_add(self):
        dlg = AddItemDialog(self)
        dlg.item_added.connect(self._do_add)
        dlg.exec()

    def _do_add(self, name, l_type):
        if self.stack.currentIndex() == 0:
            target = self.file_black if l_type == "blacklist" else self.file_white
        else:
            target = self.soft_black if l_type == "blacklist" else self.soft_white
        target.add_item(name)
        self.update_stats()

    # =================== 修复后的批量导入逻辑 ===================
    def _do_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "批量导入审计清单", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            # 确定当前页面类型
            is_file_page = (self.stack.currentIndex() == 0)

            black_added = 0
            white_added = 0

            for line in lines:
                # 支持格式： "白名单:飞书" 或 "黑名单:迅雷"
                if ':' in line:
                    parts = line.split(':', 1)
                    dtype = parts[0].strip()
                    name = parts[1].strip()
                    if dtype == "黑名单":
                        is_black = True
                    elif dtype == "白名单":
                        is_black = False
                    else:
                        # 未知类型默认黑名单
                        is_black = True
                        name = line
                else:
                    # 无类型前缀，默认黑名单
                    is_black = True
                    name = line

                if not name:
                    continue

                # 根据当前页面类型选择正确的 ListPanel
                if is_file_page:
                    target = self.file_black if is_black else self.file_white
                else:
                    target = self.soft_black if is_black else self.soft_white

                # 去重（add_item 内部会判断）
                if name not in target.get_items():
                    target.add_item(name)
                    if is_black:
                        black_added += 1
                    else:
                        white_added += 1

            self.update_stats()
            QMessageBox.information(
                self, "导入完成",
                f"成功导入 {black_added + white_added} 条规则。\n黑名单: {black_added} 条，白名单: {white_added} 条。"
            )
        except Exception as e:
            QMessageBox.warning(self, "导入失败", f"读取文件出错: {e}")


__all__ = ['BlacklistPage']