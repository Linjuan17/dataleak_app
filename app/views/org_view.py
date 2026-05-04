#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面3：组别树状图（组织架构）
使用QGraphicsView实现层级式连线
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QLabel, QPushButton, QFrame, QGraphicsView,
                             QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsItemGroup)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import QFont, QPen, QColor, QBrush, QLinearGradient, QPainter, QTransform

from models.data import MockData


class TreeNode(QGraphicsItemGroup):
    """树状图节点"""

    def __init__(self, employee, group, on_toggle, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.group = group
        self.on_toggle = on_toggle

        # 节点尺寸 - 适当加大
        self.node_width = 200
        self.node_height = 110

        # 创建背景
        self.create_background()

        # 创建头像和信息（合并为一行）
        self.create_content()

        # 创建监控开关
        self.create_switch()

        # 创建状态指示器
        self.create_status()

    def create_background(self):
        """创建背景"""
        from PyQt6.QtWidgets import QGraphicsProxyWidget

        bg = QFrame()
        if self.employee['monitored'] and self.employee['risk']:
            bg.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 71, 87, 0.08), stop:1 rgba(17, 25, 40, 0.85));
                    border: 2px solid #FF4757;
                    border-radius: 12px;
                }
            """)
        elif self.employee['monitored']:
            bg.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(0, 214, 143, 0.08), stop:1 rgba(17, 25, 40, 0.85));
                    border: 2px solid #00D68F;
                    border-radius: 12px;
                }
            """)
        else:
            bg.setStyleSheet("""
                QFrame {
                    background: rgba(17, 25, 40, 0.85);
                    border: 1px solid rgba(0, 212, 255, 0.12);
                    border-radius: 12px;
                }
            """)

        bg.setFixedSize(self.node_width, self.node_height)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(bg)
        self.proxy.setPos(-self.node_width // 2, -self.node_height // 2)

    def create_content(self):
        """创建头像和信息（紧凑布局）"""
        from PyQt6.QtWidgets import QGraphicsProxyWidget, QLabel, QVBoxLayout, QWidget, QHBoxLayout

        content_widget = QWidget()
        content_widget.setFixedSize(self.node_width - 16, 50)
        content_widget.setStyleSheet("background: transparent;")

        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # 头像 - 稍大一点
        avatar = QLabel(self.employee['avatar'])
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00D4FF, stop:1 #00FFA3);
            border-radius: 20px;
            color: #0A0E17;
            font-weight: 600;
            font-size: 14px;
        """)

        # 右侧信息
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        # 姓名
        name = QLabel(self.employee['name'])
        name.setStyleSheet("color: #E8ECF1; font-size: 14px; font-weight: 600; background: transparent;")

        # 职位和监控状态同一行
        position_status = QHBoxLayout()
        position_status.setContentsMargins(0, 0, 0, 0)
        position_status.setSpacing(6)

        position = QLabel(self.employee['position'])
        position.setStyleSheet("color: #8B95A5; font-size: 12px; background: transparent;")

        # 监控状态小标签
        if self.employee['monitored']:
            status_tag = QLabel("●")
            status_tag.setStyleSheet("color: #00D4FF; font-size: 10px; background: transparent;")
        else:
            status_tag = QLabel("○")
            status_tag.setStyleSheet("color: #4a5568; font-size: 10px; background: transparent;")

        position_status.addWidget(position)
        position_status.addWidget(status_tag)
        position_status.addStretch()

        info_layout.addWidget(name)
        info_layout.addLayout(position_status)

        content_layout.addWidget(avatar)
        content_layout.addLayout(info_layout, 1)

        self.content_proxy = QGraphicsProxyWidget(self)
        self.content_proxy.setWidget(content_widget)
        self.content_proxy.setPos(-self.node_width // 2 + 8, -self.node_height // 2 + 8)

    def create_switch(self):
        """创建监控开关"""
        from PyQt6.QtWidgets import QGraphicsProxyWidget, QCheckBox, QHBoxLayout, QWidget, QLabel

        switch_widget = QWidget()
        switch_widget.setFixedHeight(20)
        switch_widget.setStyleSheet("background: transparent;")
        switch_layout = QHBoxLayout(switch_widget)
        switch_layout.setContentsMargins(0, 0, 0, 0)
        switch_layout.setSpacing(4)
        switch_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        label = QLabel("监控")
        label.setStyleSheet("color: #8B95A5; font-size: 12px; background: transparent;")

        switch = QCheckBox()
        switch.setChecked(self.employee['monitored'])
        switch.setStyleSheet("""
            QCheckBox {
                background: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                background: rgba(0, 212, 255, 0.15);
                border: 1px solid rgba(0, 212, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #00FFA3);
                border: none;
            }
        """)
        switch.stateChanged.connect(
            lambda state: self.on_toggle(self.employee['id'], state == Qt.CheckState.Checked.value))

        switch_layout.addWidget(label)
        switch_layout.addWidget(switch)

        self.switch_proxy = QGraphicsProxyWidget(self)
        self.switch_proxy.setWidget(switch_widget)
        self.switch_proxy.setPos(-self.node_width // 2 + 36, -self.node_height // 2 + self.node_height - 25)

    def create_status(self):
        """创建状态指示器"""
        # 状态已通过背景颜色和监控圆点体现
        pass

    def boundingRect(self):
        """边界矩形"""
        return QRectF(-self.node_width // 2 - 10, -self.node_height // 2 - 10,
                      self.node_width + 20, self.node_height + 20)


class OrgView(QWidget):
    """组织架构视图"""

    # 导航信号
    navigate_back = pyqtSignal()
    navigate_to_employee = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_group = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("background-color: #0A0E17;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 返回按钮
        self.back_btn = QPushButton("◀  返回")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(17, 25, 40, 0.85);
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                color: #8B95A5;
            }
            QPushButton:hover {
                background: rgba(0, 212, 255, 0.08);
                color: #00D4FF;
                border-color: #00D4FF;
            }
        """)
        self.back_btn.clicked.connect(self.navigate_back.emit)
        main_layout.addWidget(self.back_btn)

        # 树状图区域
        tree_container = QFrame()
        tree_container.setStyleSheet("""
            QFrame {
                background: rgba(17, 25, 40, 0.85);
                border-radius: 16px;
                border: 1px solid rgba(0, 212, 255, 0.12);
            }
        """)

        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(20, 20, 20, 20)

        # 头部
        header = QHBoxLayout()

        info_layout = QVBoxLayout()

        self.title_label = QLabel("研发部")
        self.title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: #E8ECF1;")

        self.subtitle_label = QLabel("12名成员 · 8人正在监控")
        self.subtitle_label.setStyleSheet("color: #8B95A5; font-size: 14px;")

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.subtitle_label)

        header.addLayout(info_layout)
        header.addStretch()

        # 开始监控按钮
        self.monitor_all_btn = QPushButton("开始监控")
        self.monitor_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.monitor_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #00FFA3);
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                color: #0A0E17;
            }
            QPushButton:hover {
            }
        """)
        self.monitor_all_btn.clicked.connect(self.toggle_monitoring_all)

        header.addWidget(self.monitor_all_btn)

        tree_layout.addLayout(header)

        # 图形视图
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 400)

        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.setStyleSheet("""
            QGraphicsView {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(17, 25, 40, 0.8);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar:handle:vertical {
                background-color: rgba(0, 212, 255, 0.3);
                border-radius: 4px;
            }
            QScrollBar:horizontal {
                background-color: rgba(17, 25, 40, 0.8);
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background-color: rgba(0, 212, 255, 0.3);
                border-radius: 4px;
            }
        """)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        tree_layout.addWidget(self.graphics_view, 1)

        main_layout.addWidget(tree_container, 1)

    def load_group(self, group_id):
        """加载组别数据"""
        self.current_group = MockData.get_group_by_id(group_id)
        if not self.current_group:
            return

        # 更新标题
        self.title_label.setText(self.current_group['name'])

        employees = self.current_group['employees']
        monitored_count = sum(1 for e in employees if e['monitored'])
        self.subtitle_label.setText(f"{len(employees)}名成员 · {monitored_count}人正在监控")

        # 清空场景
        self.scene.clear()

        # 绘制树状图
        self.draw_tree()
        self.update_monitor_all_btn()

    def draw_tree(self):
        """绘制树状图 - 三层层级布局：总监 > 高级/架构师 > 其他"""
        if not self.current_group:
            return

        employees = self.current_group['employees']

        # 布局参数
        node_width = 200
        node_height = 110
        h_spacing = 60
        v_spacing = 95
        start_y = 60

        # 三层层级分类
        # 第一层：总监、经理
        top_level = []
        # 第二层：高级工程师、架构师
        mid_level = []
        # 第三层：其他
        low_level = []

        for emp in employees:
            position = emp['position']
            if '总监' in position or '经理' in position:
                top_level.append(emp)
            elif '高级' in position or '架构师' in position:
                mid_level.append(emp)
            else:
                low_level.append(emp)

        # 如果没有顶层，把第二层提升
        if not top_level and mid_level:
            top_level = mid_level
            mid_level = low_level
            low_level = []
        elif not top_level and not mid_level:
            top_level = low_level
            low_level = []

        # 计算每层最大宽度
        max_in_row = max(len(top_level), len(mid_level), len(low_level), 1)
        total_width = max_in_row * node_width + (max_in_row - 1) * h_spacing
        center_x = max(self.scene.width() // 2, total_width // 2 + 50)

        # 绘制连接线
        line_pen = QPen(QColor(0, 212, 255, 100))
        line_pen.setWidth(2)

        # 绘制各层节点
        all_levels = []

        # 第一层
        level1_nodes = []
        if top_level:
            total_w = len(top_level) * node_width + (len(top_level) - 1) * h_spacing
            for i, emp in enumerate(top_level):
                x = center_x - total_w // 2 + i * (node_width + h_spacing)
                y = start_y
                node = TreeNode(emp, self.current_group, self.on_monitor_toggle)
                node.setPos(x, y)
                self.scene.addItem(node)
                level1_nodes.append((node, x, y))
        all_levels.append(level1_nodes)

        # 第二层
        level2_nodes = []
        if mid_level:
            total_w = len(mid_level) * node_width + (len(mid_level) - 1) * h_spacing
            for i, emp in enumerate(mid_level):
                x = center_x - total_w // 2 + i * (node_width + h_spacing)
                y = start_y + node_height + v_spacing
                node = TreeNode(emp, self.current_group, self.on_monitor_toggle)
                node.setPos(x, y)
                self.scene.addItem(node)
                level2_nodes.append((node, x, y))
        all_levels.append(level2_nodes)

        # 第三层
        level3_nodes = []
        if low_level:
            total_w = len(low_level) * node_width + (len(low_level) - 1) * h_spacing
            for i, emp in enumerate(low_level):
                x = center_x - total_w // 2 + i * (node_width + h_spacing)
                y = start_y + (node_height + v_spacing) * 2
                node = TreeNode(emp, self.current_group, self.on_monitor_toggle)
                node.setPos(x, y)
                self.scene.addItem(node)
                level3_nodes.append((node, x, y))
        all_levels.append(level3_nodes)

        # 绘制连线
        for i in range(len(all_levels) - 1):
            upper = all_levels[i]
            lower = all_levels[i + 1]
            if not upper or not lower:
                continue

            upper_bottom_y = upper[0][2] + node_height/2
            lower_top_y = lower[0][2] - node_height/2
            mid_y = (upper_bottom_y + lower_top_y) // 2

            # 从上层每个节点底部画垂线到中间
            upper_xs = []
            for node, x, y in upper:
                self.scene.addLine(x, upper_bottom_y, x, mid_y, line_pen)
                upper_xs.append(x)

            # 水平干线（连接所有上层节点）
            if len(upper_xs) > 1:
                self.scene.addLine(min(upper_xs), mid_y, max(upper_xs), mid_y, line_pen)

            # 从中间画垂线到下层每个节点顶部
            lower_xs = []
            for node, x, y in lower:
                self.scene.addLine(x, mid_y, x, lower_top_y, line_pen)
                lower_xs.append(x)

            # 水平干线（连接所有下层节点）
            if len(lower_xs) > 1:
                self.scene.addLine(min(lower_xs), mid_y, max(lower_xs), mid_y, line_pen)

        # 调整场景大小
        all_nodes = level1_nodes + level2_nodes + level3_nodes
        if all_nodes:
            max_y = max(y for _, _, y in all_nodes) + node_height + 100
            max_x = max(x for _, x, _ in all_nodes) + node_width + 100
            self.scene.setSceneRect(0, 0, max(800, max_x), max(400, max_y))

    def on_monitor_toggle(self, employee_id, monitored):
        """监控开关变化 - 单人切换监控状态"""
        for group in MockData.groups:
            for emp in group['employees']:
                if emp['id'] == employee_id:
                    emp['monitored'] = monitored
                    # 停止监控时清除风险标记
                    if not monitored:
                        emp['risk'] = False
                    break

        # 刷新整个树视图（更新节点外观和按钮状态）
        if self.current_group:
            self.load_group(self.current_group['id'])

    def toggle_monitoring_all(self):
        """切换全组监控状态：全部开启或全部停止"""
        if not self.current_group:
            return

        employees = self.current_group['employees']
        all_monitored = all(e['monitored'] for e in employees)

        # 如果当前全在监控 → 全部停止；否则 → 全部开始
        new_state = not all_monitored
        for emp in employees:
            emp['monitored'] = new_state
            if not new_state:
                emp['risk'] = False

        # 刷新树视图
        self.load_group(self.current_group['id'])

    def update_monitor_all_btn(self):
        """更新顶部监控按钮的文案和样式"""
        if not self.current_group:
            return
        employees = self.current_group['employees']
        all_monitored = all(e['monitored'] for e in employees)

        if all_monitored:
            self.monitor_all_btn.setText("停止监控")
            self.monitor_all_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 71, 87, 0.15);
                    border: 1px solid #FF4757;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #FF4757;
                }
                QPushButton:hover {
                    background: rgba(255, 71, 87, 0.25);
                }
            """)
        else:
            self.monitor_all_btn.setText("开始监控")
            self.monitor_all_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00D4FF, stop:1 #00FFA3);
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #0A0E17;
                }
                QPushButton:hover {
                }
            """)
