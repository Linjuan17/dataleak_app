#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模块
包含员工、组别、监控记录等数据
支持加载真实JSON日志和监控视频
"""

from datetime import datetime, timedelta
import random
import json
import os

# ====================== 真实数据路径配置 ======================
# 项目根目录（data.py在models/下，所以往上走一级）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 真实监控视频路径
REAL_VIDEO_PATH = os.path.join(_PROJECT_ROOT, "models", "videos", "recording_20260325_200140.mp4")


# ====================== 加载真实JSON日志 ======================
def load_real_data():
    """加载真实告警、操作、事件数据"""
    data = {}
    json_dir = os.path.join(_PROJECT_ROOT, "models")
    try:
        json_files = {
            "alerts": "alert_events.json",
            "sensitive": "sensitive_operations.json",
            "info": "info_events.json",
            "key": "keyevents.json",
            "mapping": "file_mappings.json",
        }
        for key, filename in json_files.items():
            filepath = os.path.join(json_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data[key] = json.load(f)
    except Exception as e:
        print(f"加载真实数据失败：{e}")
    return data


REAL_DATA = load_real_data()


# ====================== 生成真实监控记录（周丽华专用）======================
def generate_real_records(employee_id, employee_name):
    """为周丽华生成【真实日志+监控视频】的监控记录"""
    records = []
    base_time = datetime.strptime("2026-04-29 20:01:40", "%Y-%m-%d %H:%M:%S")

    # 高危：钉钉外发敏感文件
    records.append({
        'id': 'REAL-ALERT-001',
        'employee_id': employee_id,
        'employee_name': employee_name,
        'time': base_time + timedelta(minutes=1),
        'level': 'high',
        'title': '黑名单应用外发敏感文件',
        'desc': '通过钉钉发送产品设计方案.zip（内含敏感docx）',
        'duration': '3分40秒',
        'video_path': REAL_VIDEO_PATH,
        'events': [
            {'time': '20:02:59', 'title': '压缩文件', 'desc': '将docx压缩为zip试图隐藏'},
            {'time': '20:03:15', 'title': '重命名', 'desc': '反复重命名dll/zip规避检测'},
            {'time': '20:03:25', 'title': '风险行为', 'desc': '钉钉聊天窗口发送敏感文件'},
            {'time': '20:03:30', 'title': '同步录屏', 'desc': '启动录屏软件同步记录'}
        ],
        'risk_score': 92,
        'analysis': [
            '用户使用黑名单应用「钉钉」直接外发敏感文件',
            '通过压缩、重命名试图规避泄密检测',
            '外发时同步开启录屏，行为高度可疑',
            '文件为核心产品设计方案，属于高敏感数据'
        ],
        'real_events': REAL_DATA.get("alerts", {}) if REAL_DATA else {},
        'sensitive_ops': REAL_DATA.get("sensitive", {}) if REAL_DATA else {},
    })

    # 中危：文件异常操作
    records.append({
        'id': 'REAL-OP-001',
        'employee_id': employee_id,
        'employee_name': employee_name,
        'time': base_time,
        'level': 'medium',
        'title': '敏感文件多次异常操作',
        'desc': '多次压缩、重命名、复制敏感文档',
        'duration': '2分钟',
        'video_path': REAL_VIDEO_PATH,
        'events': [
            {'time': '20:01:48', 'title': '打开文档', 'desc': '打开产品设计方案.docx'},
            {'time': '20:02:10', 'title': '压缩文件', 'desc': '尝试压缩为zip'},
            {'time': '20:02:37', 'title': '重命名', 'desc': '改为dll后缀隐藏'},
        ],
        'risk_score': 58,
        'analysis': [
            '短时间内对敏感文件进行多次异常操作',
            '存在明显规避检测的行为特征',
            '无正常业务理由解释该行为'
        ]
    })

    # 低危：录屏启动
    records.append({
        'id': 'REAL-REC-001',
        'employee_id': employee_id,
        'employee_name': employee_name,
        'time': base_time + timedelta(minutes=2),
        'level': 'low',
        'title': '屏幕录制行为',
        'desc': '敏感时段手动启动录屏软件',
        'duration': '1分钟',
        'video_path': REAL_VIDEO_PATH,
        'events': [
            {'time': '20:03:30', 'title': '启动录屏', 'desc': '打开录屏工具开始录制'},
            {'time': '20:03:44', 'title': '结束录制', 'desc': '完成屏幕录制'}
        ],
        'risk_score': 28,
        'analysis': [
            '录屏行为发生在文件外发窗口期',
            '设备与地点均为常用环境，无异常登录'
        ]
    })

    return records


def generate_monitoring_records(employee_id, employee_name):
    """为员工生成监控记录 — 周丽华用真实数据，其他用模拟数据"""
    # 周丽华(E008)使用真实日志和视频
    if employee_id == 'E008':
        return generate_real_records(employee_id, employee_name)

    records = []
    base_date = datetime(2024, 1, 15)

    # 高风险记录
    if random.random() > 0.5:
        records.append({
            'id': f'MR{employee_id}01',
            'employee_id': employee_id,
            'employee_name': employee_name,
            'time': base_date - timedelta(days=random.randint(0, 2)),
            'level': 'high',
            'title': '异常文件外传行为',
            'desc': '检测到通过云存储服务传输敏感文件',
            'duration': '2分38秒',
            'events': [
                {'time': '14:32:15', 'title': '文件访问', 'desc': '用户访问了敏感文档库'},
                {'time': '14:33:20', 'title': '异常操作', 'desc': '检测到批量文件下载行为'},
                {'time': '14:34:45', 'title': '外传尝试', 'desc': '尝试上传至外部云盘'},
                {'time': '14:35:53', 'title': '风险确认', 'desc': '系统判定为高风险行为'}
            ],
            'risk_score': random.randint(70, 95),
            'analysis': [
                '用户在非工作时间访问了敏感数据',
                '短时间内大量下载与工作无关的文件',
                '尝试绕过企业防火墙传输数据',
                '行为模式与历史基线存在显著偏差'
            ]
        })

    # 中风险记录
    if random.random() > 0.3:
        records.append({
            'id': f'MR{employee_id}02',
            'employee_id': employee_id,
            'employee_name': employee_name,
            'time': base_date - timedelta(days=random.randint(3, 5)),
            'level': 'medium',
            'title': '未授权系统访问',
            'desc': '尝试访问未授权的数据库系统',
            'duration': '1分12秒',
            'events': [
                {'time': '09:15:42', 'title': '权限验证', 'desc': '发起数据库访问请求'},
                {'time': '09:16:08', 'title': '访问拒绝', 'desc': '权限验证失败'},
                {'time': '09:16:35', 'title': '重试行为', 'desc': '多次尝试绕过权限限制'}
            ],
            'risk_score': random.randint(40, 60),
            'analysis': [
                '尝试访问超出权限范围的数据库',
                '存在密码暴力破解行为',
                '访问时段符合正常工作时间'
            ]
        })

    # 低风险记录
    if random.random() > 0.4:
        records.append({
            'id': f'MR{employee_id}03',
            'employee_id': employee_id,
            'employee_name': employee_name,
            'time': base_date - timedelta(days=random.randint(6, 10)),
            'level': 'low',
            'title': '异常登录地点',
            'desc': '检测到异地登录行为',
            'duration': '5分钟',
            'events': [
                {'time': '16:48:30', 'title': '登录检测', 'desc': '检测到新地点登录'},
                {'time': '16:49:15', 'title': '位置分析', 'desc': '登录地点与常用地点不符'},
                {'time': '16:53:30', 'title': '确认登录', 'desc': '完成身份验证'}
            ],
            'risk_score': random.randint(15, 35),
            'analysis': [
                '登录IP地址发生变化',
                '设备信息与常用设备一致',
                '已完成双因素认证验证'
            ]
        })

    return records


# 模拟数据定义
class MockData:
    """模拟数据类"""

    # 日期数据
    dates = ['2026-04-28', '2026-04-29', '2026-04-30']

    # 所有月份数据
    all_dates = {
        '2026-04': ['2026-04-28', '2026-04-29', '2026-04-30'],
        '2026-03': ['2026-03-10', '2026-03-11', '2026-03-12'],
        '2026-02': ['2026-02-05', '2026-02-06']
    }

    # 组别和员工数据
    groups = [
        {
            'id': 'rd',
            'name': '研发部',
            'color': '#00D4FF',
            'employees': [
                {'id': 'E001', 'name': '张明远', 'position': '技术总监', 'avatar': '张', 'monitored': True,
                 'risk': True},
                {'id': 'E002', 'name': '李思雨', 'position': '高级工程师', 'avatar': '李', 'monitored': True,
                 'risk': False},
                {'id': 'E003', 'name': '王建国', 'position': '架构师', 'avatar': '王', 'monitored': True, 'risk': True},
                {'id': 'E004', 'name': '刘晓峰', 'position': '前端开发', 'avatar': '刘', 'monitored': False,
                 'risk': False},
                {'id': 'E005', 'name': '陈雅婷', 'position': '后端开发', 'avatar': '陈', 'monitored': True,
                 'risk': False},
                {'id': 'E006', 'name': '赵文博', 'position': '测试工程师', 'avatar': '赵', 'monitored': False,
                 'risk': False}
            ]
        },
        {
            'id': 'ops',
            'name': '运维部',
            'color': '#00FFA3',
            'employees': [
                {'id': 'E007', 'name': '孙伟东', 'position': '运维经理', 'avatar': '孙', 'monitored': True,
                 'risk': True},
                {'id': 'E008', 'name': '周丽华', 'position': '运维工程师', 'avatar': '周', 'monitored': True,
                 'risk': False},
                {'id': 'E009', 'name': '吴志强', 'position': 'DBA', 'avatar': '吴', 'monitored': False, 'risk': False},
                {'id': 'E010', 'name': '郑海燕', 'position': '运维工程师', 'avatar': '郑', 'monitored': True,
                 'risk': False}
            ]
        },
        {
            'id': 'data',
            'name': '数据部',
            'color': '#9B59B6',
            'employees': [
                {'id': 'E011', 'name': '黄建军', 'position': '数据总监', 'avatar': '黄', 'monitored': True,
                 'risk': False},
                {'id': 'E012', 'name': '林小敏', 'position': '数据分析师', 'avatar': '林', 'monitored': True,
                 'risk': True},
                {'id': 'E013', 'name': '杨志刚', 'position': '数据工程师', 'avatar': '杨', 'monitored': False,
                 'risk': False},
                {'id': 'E014', 'name': '周明杰', 'position': 'BI工程师', 'avatar': '周', 'monitored': True,
                 'risk': False},
                {'id': 'E015', 'name': '吴雪晴', 'position': '数据建模师', 'avatar': '吴', 'monitored': False,
                 'risk': False}
            ]
        },
        {
            'id': 'sec',
            'name': '安全部',
            'color': '#FF4757',
            'employees': [
                {'id': 'E016', 'name': '徐安全', 'position': '安全总监', 'avatar': '徐', 'monitored': True,
                 'risk': False},
                {'id': 'E017', 'name': '马防护', 'position': '安全工程师', 'avatar': '马', 'monitored': True,
                 'risk': True},
                {'id': 'E018', 'name': '朱预警', 'position': '渗透测试员', 'avatar': '朱', 'monitored': False,
                 'risk': False}
            ]
        }
    ]

    # 预生成的监控记录
    _all_records = {}

    @classmethod
    def get_monitoring_records(cls, employee_id, employee_name):
        """获取员工监控记录"""
        if employee_id not in cls._all_records:
            cls._all_records[employee_id] = generate_monitoring_records(employee_id, employee_name)
        return cls._all_records[employee_id]

    @classmethod
    def get_group_by_id(cls, group_id):
        """根据ID获取组别"""
        for group in cls.groups:
            if group['id'] == group_id:
                return group
        return None

    @classmethod
    def get_employee_by_id(cls, employee_id):
        """根据ID获取员工"""
        for group in cls.groups:
            for emp in group['employees']:
                if emp['id'] == employee_id:
                    return emp, group
        return None, None

    @classmethod
    def get_group_status(cls, group):
        """获取组别状态（risk/safe/warning）"""
        employees = group['employees']
        if not employees:
            return 'warning'

        monitored_count = sum(1 for e in employees if e['monitored'])
        risk_count = sum(1 for e in employees if e['risk'])

        if risk_count > 0:
            return 'risk'
        elif monitored_count == len(employees):
            return 'safe'
        else:
            return 'warning'

    @classmethod
    def get_all_employees(cls):
        """获取所有员工列表"""
        employees = []
        for group in cls.groups:
            for emp in group['employees']:
                emp_copy = emp.copy()
                emp_copy['group'] = group['name']
                emp_copy['group_id'] = group['id']
                employees.append(emp_copy)
        return employees
