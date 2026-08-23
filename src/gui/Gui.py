  #!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============== 明亮科技蓝配色方案 ==================
# 主背景: #d6ecff (极浅蓝)
# 卡片背景: #ffffff (带蓝调的白)
# 主色调: #0066ff (鲜艳蓝)
# 强调色: #00ccff (天蓝)
# 成功色: #00ff7f (鲜艳绿)
# 警告色: #ff6600 (鲜艳橙)
# ====================================================

"""
燃烧速度仿真软件 - 完整中文科技蓝版
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Label, Frame, Button, Entry, Text, StringVar, IntVar, LabelFrame, Scrollbar, Canvas, Listbox, MULTIPLE
from tkinter import BOTH, LEFT, RIGHT, TOP, BOTTOM, X, Y, END, NORMAL, DISABLED, CENTER, W, E, N, S, HORIZONTAL, VERTICAL
import os
import sys
import json
import subprocess
import math
import random
import threading
from datetime import datetime
from tksheet import Sheet

def center_window(window, width, height):
    """居中显示窗口"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# =============== 超级炫酷启动画面 ==================
class TechBlueSplash(Toplevel):
    def __init__(self, master, seconds=3):
        super().__init__(master)
        self.overrideredirect(True)
        # 明亮渐变背景
        self.configure(bg="#e8f4fd")
        center_window(self, 1200, 700)

        # 创建主Canvas
        self.canvas = tk.Canvas(self, bg="#e8f4fd", highlightthickness=0, width=1200, height=700)
        self.canvas.pack(fill='both', expand=True)

        # 绘制多层渐变背景
        self.draw_advanced_background()

        # 创建神经网络可视化
        CoolEffects.create_neural_network(self.canvas, 1200, 700, nodes=25)

        # 初始化粒子系统（更多粒子）
        self.particles = CoolEffects.create_floating_particles(self.canvas, count=60, color="#00ccff")

        # 启动粒子动画
        CoolEffects.animate_particles(self.canvas, self.particles, 1200, 700)

        # 创建扫描线效果
        CoolEffects.create_scan_line(self.canvas, 1200, 700)

        # 绘制装饰元素
        self.draw_decorations()

        # 主容器（透明背景）
        main_frame = Frame(self.canvas, bg="#e8f4fd")
        self.canvas.create_window(600, 350, window=main_frame)

        # Logo区域 - 多层发光效果
        logo_glow_outer = Frame(main_frame, bg="#00ccff")
        logo_glow_outer.pack(pady=(60, 35))

        logo_glow_mid = Frame(logo_glow_outer, bg="#33ddff")
        logo_glow_mid.pack(padx=2, pady=2)

        logo_outer = Frame(logo_glow_mid, bg="#0066ff")
        logo_outer.pack(padx=2, pady=2)

        logo_middle = Frame(logo_outer, bg="#ffffff")
        logo_middle.pack(padx=4, pady=4)

        logo_container = Frame(logo_middle, bg="#ffffff")
        logo_container.pack(padx=3, pady=3)

        logo_inner = Frame(logo_container, bg="#ffffff")
        logo_inner.pack(padx=40, pady=30)

        # 加载Logo
        try:
            from PIL import Image, ImageTk, ImageEnhance
            # Logo1 - 增强对比度
            logo1_img = Image.open("../../assets/images/logo1.png").resize((140, 140), Image.Resampling.LANCZOS)
            enhancer = ImageEnhance.Contrast(logo1_img)
            logo1_img = enhancer.enhance(1.2)
            self.logo1_photo = ImageTk.PhotoImage(logo1_img)
            logo1_label = Label(logo_inner, image=self.logo1_photo, bg="#ffffff")
            logo1_label.pack(side=LEFT, padx=(0, 40))

            # Logo2 - 增强对比度
            logo2_img = Image.open("../../assets/images/logo2.jpg").resize((140, 140), Image.Resampling.LANCZOS)
            enhancer = ImageEnhance.Contrast(logo2_img)
            logo2_img = enhancer.enhance(1.2)
            self.logo2_photo = ImageTk.PhotoImage(logo2_img)
            logo2_label = Label(logo_inner, image=self.logo2_photo, bg="#ffffff")
            logo2_label.pack(side=LEFT)
        except:
            logo_text = Label(logo_inner, text="⚡", font=("Arial", 100), fg="#0066ff", bg="#ffffff")
            logo_text.pack()

        # 主标题 - 超大字体
        self.title_label = Label(
            main_frame,
            text="燃烧速度仿真软件",
            fg="#0066ff",
            bg="#e8f4fd",
            font=("Microsoft YaHei UI", 50, "bold")
        )
        self.title_label.pack(pady=(35, 12))

        # 添加标题脉冲效果
        CoolEffects.create_pulse_effect(self.title_label, ["#0066ff", "#0099ff", "#00ccff"], interval=400)

        # 英文副标题 - 更大更醒目
        subtitle = Label(
            main_frame,
            text="● INTELLIGENT SIMULATION PLATFORM ●",
            fg="#00ccff",
            bg="#e8f4fd",
            font=("Consolas", 18, "bold")
        )
        subtitle.pack(pady=(8, 25))
        
        # 单位信息
        authors = Label(
            main_frame,
            text="西安近代化学研究所 × 西北工业大学",
            fg="#6b7280",
            bg="#e8f4fd",
            font=("Microsoft YaHei UI", 13)
        )
        authors.pack(pady=(18, 0))

        # 加载状态 - 更大更醒目
        self.status_label = Label(
            main_frame,
            text="● SYSTEM INITIALIZING",
            fg="#0066ff",
            bg="#e8f4fd",
            font=("Consolas", 15, "bold")
        )
        self.status_label.pack(pady=(50, 25))

        # 脉冲动画
        self.pulse_status()

        # 进度条容器 - 多层发光效果
        progress_glow_outer = Frame(main_frame, bg="#00ccff")
        progress_glow_outer.pack(pady=(25, 0))

        progress_glow_mid = Frame(progress_glow_outer, bg="#33ddff")
        progress_glow_mid.pack(padx=2, pady=2)

        progress_outer = Frame(progress_glow_mid, bg="#0066ff")
        progress_outer.pack(padx=2, pady=2)

        progress_middle = Frame(progress_outer, bg="#b3d9ff")
        progress_middle.pack(padx=3, pady=3)

        # 更宽更高的进度条
        self.progress_canvas = tk.Canvas(progress_middle, width=650, height=12,
                                        bg="#ffffff", highlightthickness=0)
        self.progress_canvas.pack(padx=4, pady=4)

        # 进度条背景渐变
        for i in range(650):
            ratio = i / 650
            r = int(255 - (255-230) * ratio)
            g = int(255 - (255-240) * ratio)
            b = 255
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.progress_canvas.create_line(i, 0, i, 12, fill=color)

        # 进度条主体
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 12,
            fill="#0066ff",
            outline=""
        )

        # 进度条发光层1
        self.progress_glow1 = self.progress_canvas.create_rectangle(
            0, 0, 0, 12,
            fill="#00ccff",
            outline="",
            stipple="gray50"
        )

        # 进度条发光层2
        self.progress_glow2 = self.progress_canvas.create_rectangle(
            0, 0, 0, 12,
            fill="#00ff7f",
            outline="",
            stipple="gray25"
        )

        # 启动动画
        self.animate_progress(0, seconds * 1000)
        self.after(seconds * 1000, self.close_splash)

    def draw_advanced_background(self):
        """绘制高级渐变背景"""
        # 创建径向渐变效果
        center_x, center_y = 600, 350
        max_radius = 850

        for radius in range(max_radius, 0, -10):
            ratio = radius / max_radius
            # 从中心的亮蓝到边缘的深蓝
            r = int(214 + (180-214) * ratio)
            g = int(236 + (220-236) * ratio)
            b = int(255 - (255-240) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'

            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color,
                outline=""
            )

    def draw_decorations(self):
        """绘制装饰元素"""
        # 绘制动态网格
        for i in range(0, 1200, 60):
            # 垂直线 - 渐变透明度
            alpha = int((i / 1200) * 100)
            self.canvas.create_line(i, 0, i, 700, fill="#b3d9ff", width=1, dash=(2, 4))

        for i in range(0, 700, 60):
            # 水平线 - 渐变透明度
            self.canvas.create_line(0, i, 1200, i, fill="#b3d9ff", width=1, dash=(2, 4))

        # 绘制四个角的复杂装饰
        corners = [(50, 50), (1150, 50), (50, 650), (1150, 650)]
        for x, y in corners:
            # 最外圈 - 大圆
            self.canvas.create_oval(x-25, y-25, x+25, y+25, outline="#0066ff", width=3)
            # 中圈
            self.canvas.create_oval(x-18, y-18, x+18, y+18, outline="#00ccff", width=2)
            # 内圈 - 实心
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="#00ff7f", outline="")
            # 中心点
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#0066ff", outline="")

            # 添加十字线
            self.canvas.create_line(x-30, y, x-25, y, fill="#00ccff", width=2)
            self.canvas.create_line(x+25, y, x+30, y, fill="#00ccff", width=2)
            self.canvas.create_line(x, y-30, x, y-25, fill="#00ccff", width=2)
            self.canvas.create_line(x, y+25, x, y+30, fill="#00ccff", width=2)

        # 绘制边框装饰线
        # 顶部
        self.canvas.create_line(100, 20, 1100, 20, fill="#0066ff", width=2)
        self.canvas.create_line(100, 23, 1100, 23, fill="#00ccff", width=1)
        # 底部
        self.canvas.create_line(100, 680, 1100, 680, fill="#0066ff", width=2)
        self.canvas.create_line(100, 677, 1100, 677, fill="#00ccff", width=1)
        # 左侧
        self.canvas.create_line(20, 100, 20, 600, fill="#0066ff", width=2)
        self.canvas.create_line(23, 100, 23, 600, fill="#00ccff", width=1)
        # 右侧
        self.canvas.create_line(1180, 100, 1180, 600, fill="#0066ff", width=2)
        self.canvas.create_line(1177, 100, 1177, 600, fill="#00ccff", width=1)

    def pulse_status(self):
        """脉冲状态文字 - 三色循环"""
        colors = ["#0066ff", "#00ccff", "#00ff7f"]
        current_index = [0]

        def pulse():
            self.status_label.config(fg=colors[current_index[0] % len(colors)])
            current_index[0] += 1
            self.after(400, pulse)

        pulse()

    def animate_progress(self, current, total):
        """动画进度条 - 多层发光"""
        if current <= total:
            progress = (current / total) * 650

            # 主进度条
            self.progress_canvas.coords(self.progress_bar, 0, 0, progress, 12)

            # 发光层1 - 青色
            self.progress_canvas.coords(self.progress_glow1, 0, 0, progress+20, 12)

            # 发光层2 - 绿色
            self.progress_canvas.coords(self.progress_glow2, 0, 0, progress+35, 12)

            self.after(25, lambda: self.animate_progress(current + 25, total))

    def close_splash(self):
        """关闭启动画面"""
        self.destroy()


# =============== 超级炫酷效果系统 ==================
class CoolEffects:
    """炫酷视觉效果管理器"""
    
    @staticmethod
    def create_glow_border(parent, inner_widget, glow_color="#00ccff", layers=3):
        """创建多层发光边框"""
        current = inner_widget
        for i in range(layers):
            thickness = layers - i
            frame = Frame(parent, bg=glow_color)
            frame.pack(padx=thickness, pady=thickness)
            current = frame
        return current
    
    @staticmethod
    def create_animated_gradient(canvas, x1, y1, x2, y2, colors, tag="gradient"):
        """创建动画渐变"""
        steps = len(colors) - 1
        height = (y2 - y1) // steps
        for i in range(steps):
            canvas.create_rectangle(
                x1, y1 + i * height,
                x2, y1 + (i + 1) * height,
                fill=colors[i],
                outline="",
                tags=tag
            )
    
    @staticmethod
    def create_pulse_effect(widget, colors, interval=500):
        """创建脉冲效果"""
        current_index = [0]
        
        def pulse():
            widget.config(fg=colors[current_index[0] % len(colors)])
            current_index[0] += 1
            widget.after(interval, pulse)
        
        pulse()
    
    @staticmethod
    def create_floating_particles(canvas, count=50, color="#00ccff"):
        """创建浮动粒子系统"""
        particles = []
        width = canvas.winfo_reqwidth() or 1100
        height = canvas.winfo_reqheight() or 650
        
        for _ in range(count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 6)
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            
            particle = canvas.create_oval(
                x, y, x+size, y+size,
                fill=color,
                outline="",
                tags="particle"
            )
            
            particles.append({
                'id': particle,
                'x': x, 'y': y,
                'vx': vx, 'vy': vy,
                'size': size
            })
        
        return particles
    
    @staticmethod
    def animate_particles(canvas, particles, width, height):
        """动画粒子"""
        for p in particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            # 边界处理
            if p['x'] < 0 or p['x'] > width:
                p['vx'] *= -1
            if p['y'] < 0 or p['y'] > height:
                p['vy'] *= -1
            
            canvas.coords(p['id'], p['x'], p['y'],
                         p['x']+p['size'], p['y']+p['size'])
        
        canvas.after(50, lambda: CoolEffects.animate_particles(canvas, particles, width, height))
    
    @staticmethod
    def create_neural_network(canvas, width, height, nodes=20):
        """创建神经网络可视化"""
        import math
        
        # 创建节点
        node_positions = []
        for _ in range(nodes):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            node_positions.append((x, y))
            
            # 绘制节点
            canvas.create_oval(
                x-4, y-4, x+4, y+4,
                fill="#00ccff",
                outline="#00ff7f",
                width=2,
                tags="neural"
            )
        
        # 连接节点
        for i, (x1, y1) in enumerate(node_positions):
            for x2, y2 in node_positions[i+1:]:
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                if dist < 150:
                    # 根据距离设置透明度
                    canvas.create_line(
                        x1, y1, x2, y2,
                        fill="#0099ff",
                        width=1,
                        tags="neural"
                    )
    
    @staticmethod
    def create_scan_line(canvas, width, height):
        """创建扫描线效果"""
        line = canvas.create_line(
            0, 0, width, 0,
            fill="#00ccff",
            width=2,
            tags="scanline"
        )
        
        def animate_scan(y=0):
            canvas.coords(line, 0, y, width, y)
            y = (y + 3) % height
            canvas.after(30, lambda: animate_scan(y))
        
        animate_scan()


# =================== 化学物种数据库 ======================
CHEM_DB = [
    {"name_cn": "硝化纤维素", "code": "NC(L)", "formula": "C6H7N3O11", "mw": 299.0, "default_pct": 60.0, "remark": "主要成分"},
    {"name_cn": "硝化甘油", "code": "NG(L)", "formula": "C3H5N3O9", "mw": 227.0, "default_pct": 15.0, "remark": "增塑剂"},
    {"name_cn": "中定剂", "code": "ZDJ(L)", "formula": "C12H11N", "mw": 240.0, "default_pct": 1.0, "remark": "稳定剂"},
    {"name_cn": "吉纳", "code": "DINA(L)", "formula": "C4H6N4O8", "mw": 240.0, "default_pct": 0.0, "remark": "增塑剂"},
    {"name_cn": "邻苯二甲酸二乙酯", "code": "DEP(L)", "formula": "C12H14O4", "mw": 222.0, "default_pct": 1.0, "remark": "增塑剂"},
    {"name_cn": "镍粉", "code": "Ni", "formula": "Ni", "mw": 58.69, "default_pct": 0.0, "remark": "催化剂"},
    {"name_cn": "四氧化三钴", "code": "Co3O4", "formula": "Co3O4", "mw": 240.8, "default_pct": 0.0, "remark": "催化剂"},
    {"name_cn": "邻苯二甲酸铅", "code": "C8H4O4Pb", "formula": "C8H4O4Pb", "mw": 351.3, "default_pct": 0.0, "remark": "催化剂"},
    {"name_cn": "氧化镁", "code": "MgO", "formula": "MgO", "mw": 40.3, "default_pct": 0.0, "remark": "添加剂"},
    {"name_cn": "石墨", "code": "C", "formula": "C", "mw": 12.01, "default_pct": 0.0, "remark": "添加剂"},
]

CHEM_BY_NAME = {item["name_cn"]: item for item in CHEM_DB}
CHEM_BY_CODE = {item["code"]: item for item in CHEM_DB}

def parse_burn_rate(output_text):
    """从输出中解析燃烧速度"""
    for line in output_text.split('\n'):
        if 'Burn rate' in line or '燃速' in line:
            try:
                parts = line.split(':')
                if len(parts) >= 2:
                    val_str = parts[1].strip().split()[0]
                    return float(val_str)
            except:
                pass
    return None

# =================== 主应用类 ======================
class Step1Files(Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#e8f4fd")
        self.app = app
        self.create_interface()

    def create_interface(self):
        # 步骤标题
        title_frame = Frame(self, bg="#e8f4fd")
        title_frame.pack(fill=X, pady=(0, 25), padx=30)

        # 标题行
        title_row = Frame(title_frame, bg="#e8f4fd")
        title_row.pack(fill=X)

        # 步骤编号
        step_num = Label(title_row,
                        text="01",
                        font=("Consolas", 36, "bold"),
                        fg="#00aaff", bg="#e8f4fd")
        step_num.pack(side=LEFT, padx=(0, 20))

        # 标题信息
        title_info = Frame(title_row, bg="#e8f4fd")
        title_info.pack(side=LEFT, fill=X, expand=True)

        title = Label(title_info,
                     text="选择仿真机理文件",
                     font=("Microsoft YaHei UI", 22, "bold"),
                     fg="#0066ff", bg="#e8f4fd")
        title.pack(anchor=W)

        subtitle = Label(title_info,
                        text="● SELECT SIMULATION MECHANISM FILES ●",
                        font=("Consolas", 10, "bold"),
                        fg="#00aaff", bg="#e8f4fd")
        subtitle.pack(anchor=W, pady=(4, 0))

        desc = Label(title_info,
                    text="请选择液相机理、分子参数数据和气相机理文件，这些文件将用于燃烧速度计算",
                    font=("Microsoft YaHei UI", 11),
                    fg="#6699cc", bg="#e8f4fd")
        desc.pack(anchor=W, pady=(6, 0))

        # 文件选择区域
        files_frame = Frame(self, bg="#e8f4fd")
        files_frame.pack(fill=BOTH, expand=True, pady=18, padx=30)

        self.entries = {}
        self.status_labels = {}

        # 文件配置
        file_configs = [
            {
                "key": "mech",
                "title": "液相机理文件",
                "subtitle": "LIQUID PHASE MECHANISM",
                "description": "包含液相反应机理的文本文件",
                "icon": "📄",
                "color": "#0099ff",
                "default": "../../assets/resources/chem-liquid-phase-mechanism.txt"
            },
            {
                "key": "thermo",
                "title": "分子参数数据文件",
                "subtitle": "MOLECULAR PARAMETERS",
                "description": "包含分子热力学参数的数据文件",
                "icon": "📊",
                "color": "#00aaff",
                "default": "../../assets/resources/log-file-data-minima.txt"
            },
            {
                "key": "yaml",
                "title": "气相机理文件",
                "subtitle": "GAS PHASE MECHANISM",
                "description": "包含气相反应机理的YAML格式文件",
                "icon": "⚙️",
                "color": "#00ccff",
                "default": "../../assets/resources/chem.yaml"
            }
        ]

        for i, config in enumerate(file_configs):
            self.create_file_selector(files_frame, config, i)

    def create_file_selector(self, parent, config, index):
        """创建超炫酷文件选择器卡片"""
        # 外层发光阴影
        shadow = Frame(parent, bg="#99d6ff")
        shadow.pack(fill=X, pady=15)

        # 第二层发光
        glow1 = Frame(shadow, bg=config["color"])
        glow1.pack(fill=X, padx=4, pady=4)

        # 第三层发光
        glow2 = Frame(glow1, bg="#ffffff")
        glow2.pack(fill=X, padx=3, pady=3)

        # 主卡片
        card = Frame(glow2, bg="#ffffff")
        card.pack(fill=X, padx=2, pady=2)

        # 顶部装饰条
        top_bar = Frame(card, bg=config["color"], height=4)
        top_bar.pack(fill=X)

        # 内容区
        content = Frame(card, bg="#ffffff")
        content.pack(fill=X, padx=30, pady=25)

        # 标题行
        title_row = Frame(content, bg="#ffffff")
        title_row.pack(fill=X, pady=(0, 18))

        # 左侧：图标和标题
        left_section = Frame(title_row, bg="#ffffff")
        left_section.pack(side=LEFT, fill=X, expand=True)

        # 图标 - 大号炫酷
        icon_container = Frame(left_section, bg=config["color"], width=70, height=70)
        icon_container.pack(side=LEFT, padx=(0, 25))
        icon_container.pack_propagate(False)

        icon_inner = Frame(icon_container, bg="#ffffff")
        icon_inner.place(relx=0.5, rely=0.5, anchor="center", width=62, height=62)

        icon_label = Label(icon_inner,
                          text=config["icon"],
                          font=("Arial", 36),
                          bg="#ffffff", fg=config["color"])
        icon_label.pack(expand=True)

        # 标题信息
        title_info = Frame(left_section, bg="#ffffff")
        title_info.pack(side=LEFT, fill=X, expand=True)

        title_label = Label(title_info,
                           text=config["title"],
                           font=("Microsoft YaHei UI", 18, "bold"),
                           bg="#ffffff", fg="#0066ff",
                           anchor=W)
        title_label.pack(fill=X)

        subtitle_label = Label(title_info,
                              text="● " + config["subtitle"] + " ●",
                              font=("Consolas", 10, "bold"),
                              bg="#ffffff", fg=config["color"],
                              anchor=W)
        subtitle_label.pack(fill=X, pady=(3, 0))

        desc_label = Label(title_info,
                          text=config["description"],
                          font=("Microsoft YaHei UI", 11),
                          bg="#ffffff", fg="#6699cc",
                          anchor=W)
        desc_label.pack(fill=X, pady=(8, 0))

        # 右侧：状态指示器
        status_container = Frame(title_row, bg="#ffffff")
        status_container.pack(side=RIGHT, padx=(25, 0))

        # 状态发光卡片
        status_glow1 = Frame(status_container, bg="#00ff7f")
        status_glow1.pack()

        status_glow2 = Frame(status_glow1, bg="#00dd66")
        status_glow2.pack(padx=3, pady=3)

        status_inner = Frame(status_glow2, bg="#ffffff")
        status_inner.pack(padx=2, pady=2)

        status_label = Label(status_inner,
                           text="● READY",
                           font=("Consolas", 12, "bold"),
                           bg="#ffffff", fg="#00bb55",
                           padx=18, pady=10)
        status_label.pack()
        self.status_labels[config["key"]] = status_label

        # 输入行
        input_row = Frame(content, bg="#ffffff")
        input_row.pack(fill=X, pady=(0, 0))

        # 输入框 - 发光边框
        input_glow1 = Frame(input_row, bg=config["color"])
        input_glow1.pack(side=LEFT, fill=X, expand=True, padx=(0, 20))

        input_glow2 = Frame(input_glow1, bg="#e6f7ff")
        input_glow2.pack(fill=X, padx=3, pady=3)

        input_inner = Frame(input_glow2, bg="#e6f7ff")
        input_inner.pack(fill=X, padx=2, pady=2)

        # 路径标签
        path_label = Label(input_inner,
                          text="FILE PATH:",
                          font=("Consolas", 9, "bold"),
                          bg="#e6f7ff", fg="#6699cc",
                          anchor=W)
        path_label.pack(fill=X, padx=15, pady=(10, 3))

        entry = Entry(input_inner,
                     font=("Consolas", 12),
                     bg="#e6f7ff", fg="#0066ff",
                     insertbackground="#0099ff",
                     relief="flat", bd=0)
        entry.pack(fill=X, padx=15, pady=(0, 12))
        entry.insert(0, config["default"])
        self.entries[config["key"]] = entry

        # 浏览按钮 - 发光设计
        btn_glow1 = Frame(input_row, bg=config["color"])
        btn_glow1.pack(side=LEFT)

        btn_glow2 = Frame(btn_glow1, bg="#ffffff")
        btn_glow2.pack(padx=4, pady=4)

        browse_btn = Button(btn_glow2,
                           text="🔍 BROWSE",
                           font=("Consolas", 12, "bold"),
                           bg="#ffffff", fg=config["color"],
                           activebackground="#f0f8ff",
                           relief="flat", bd=0,
                           padx=30, pady=18,
                           cursor="hand2",
                           command=lambda: self.browse_file(config["key"]))
        browse_btn.pack(padx=3, pady=3)

        # 初始验证
        self.verify_file(config["key"])

    def browse_file(self, key):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title=f"选择文件 - {key.upper()}",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.entries[key].delete(0, END)
            self.entries[key].insert(0, filename)
            self.app.state["files"][key] = filename
            self.verify_file(key)

    def verify_file(self, key):
        """验证文件"""
        path = self.entries[key].get().strip()
        status_label = self.status_labels[key]

        if path and os.path.exists(path):
            status_label.config(text="● 已验证", fg="#00bb55")
            # 更新父容器的背景色为绿色
            status_label.master.master.config(bg="#00dd66")
            status_label.master.master.master.config(bg="#00ff7f")
        elif path:
            status_label.config(text="● 错误", fg="#ff0044")
            # 更新父容器的背景色为红色
            status_label.master.master.config(bg="#ff6666")
            status_label.master.master.master.config(bg="#ff8888")
        else:
            status_label.config(text="● 空", fg="#ff6600")
            # 更新父容器的背景色为橙色
            status_label.master.master.config(bg="#ffaa66")
            status_label.master.master.master.config(bg="#ffcc88")

    def validate(self):
        """验证当前步骤"""
        vals = {k: v.get().strip() for k, v in self.entries.items()}

        # 保存状态（无论文件是否存在）
        self.app.state["files"].update(vals)

        # 检查文件是否存在
        missing = [k for k, v in vals.items() if v and not os.path.exists(v)]

        if missing:
            missing_names = []
            if "mech" in missing:
                missing_names.append("液相机理文件")
            if "thermo" in missing:
                missing_names.append("分子参数数据文件")
            if "yaml" in missing:
                missing_names.append("气相机理文件")

            result = messagebox.askyesno(
                "文件路径无效",
                f"以下文件路径不存在：\n\n{chr(10).join(missing_names)}\n\n是否继续到下一步？\n（建议先检查文件路径）",
                icon="warning"
            )
            if not result:
                return False

        return True

    def on_show(self):
        """显示时的回调"""
        # 恢复之前的选择
        for key, entry in self.entries.items():
            if self.app.state["files"].get(key):
                entry.delete(0, END)
                entry.insert(0, self.app.state["files"][key])
                self.verify_file(key)

# =================== 步骤2: 配方设计 ===================
class Step2Formula(Frame):
    COLS = ("序号", "化学名称", "化学组成", "备注", "含量(%)", "相对分子质量", "机理名")
    DISPLAY_COLS = ("序号", "化学名称", "化学组成", "备注", "含量(%)")
    LOCKED_COLS = {"序号", "化学组成", "相对分子质量", "机理名"}
    EDITABLE_COLS = {"备注", "含量(%)"}

    def __init__(self, parent, app):
        super().__init__(parent, bg="#e8f4fd")
        self.app = app
        # 存储完整数据（包括隐藏字段）
        self.row_data = {}  # {row_id: {"mw": ..., "code": ...}}
        self.create_interface()

    def create_interface(self):
        # 步骤标题
        title_frame = Frame(self, bg="#e8f4fd")
        title_frame.pack(fill=X, pady=(0, 20))

        title = Label(title_frame,
                     text="步骤二：配方设计与密度设置",
                     font=("Microsoft YaHei UI", 20, "bold"),
                     fg="#0066ff", bg="#e8f4fd")
        title.pack(anchor=W)

        subtitle = Label(title_frame,
                        text="选择化学名称会自动填充其他列；含量(%)与备注可手动修改。双击单元格进行操作。",
                        font=("Microsoft YaHei UI", 12),
                        fg="#0099ff", bg="#e8f4fd")
        subtitle.pack(anchor=W, pady=(6, 0))

        # 表格容器
        table_container = Frame(self, bg="#ffffff", relief="flat", bd=2)
        table_container.pack(fill=BOTH, expand=True, pady=8)

        table_content = Frame(table_container, bg="#ffffff")
        table_content.pack(fill=BOTH, expand=True, padx=10, pady=8)

        # 表格 - 使用tksheet实现Excel样式网格
        table_frame = Frame(table_content, bg="#ffffff")
        table_frame.pack(fill=BOTH, expand=True)

        # 创建Sheet表格 - 填充满可用空间
        self.sheet = Sheet(
            table_frame,
            headers=self.DISPLAY_COLS,
            show_x_scrollbar=False,
            show_y_scrollbar=True,
            show_row_index=False,  # 隐藏行号列
            show_header=True,
            show_top_left=False,
            empty_horizontal=0,  # 不显示额外的空白列
            empty_vertical=0,    # 不显示额外的空白行
            total_columns=5,     # ✅ 限制总列数为5
            align="center",
            header_align="center",
            default_row_height=35,
            default_header_height=40,
            font=("Microsoft YaHei UI", 11, "normal"),
            header_font=("Microsoft YaHei UI", 12, "bold"),
            theme="light blue"
        )

        # 配置颜色
        self.sheet.change_theme("light blue")
        self.sheet.set_options(
            table_bg="#ffffff",
            table_fg="#0066ff",
            header_bg="#b3d9ff",
            header_fg="#0066ff",
            index_bg="#e6f2ff",
            index_fg="#0066ff",
            top_left_bg="#b3d9ff",
            frame_bg="#b3d9ff",
            table_grid_fg="#b3d9ff",  # 网格线颜色
            header_grid_fg="#99ccff",
            index_grid_fg="#99ccff"
        )

        # 初始化15行空数据，确保只有5列
        self.sheet.set_sheet_data([["", "", "", "", ""] for _ in range(15)])

        # 隐藏所有额外的列（只保留定义的5列）
        self.sheet.headers(newheaders=self.DISPLAY_COLS, reset_col_positions=True, show_headers_if_not_sheet=True)

        # 启用编辑功能 - 包括双击编辑
        self.sheet.enable_bindings(
            "single_select",
            "row_select",
            "column_width_resize",
            "double_click_column_resize",
            "arrowkeys",
            "right_click_popup_menu",
            "rc_select",
            "rc_insert_row",
            "rc_delete_row",
            "copy",
            "cut",
            "paste",
            "delete",
            "undo",
            "edit_cell"
        )

        # 绑定双击事件 - 化学名称列弹出选择框，其他列正常编辑
        self.sheet.bind("<Double-Button-1>", self.on_double_click)

        # 绑定表格编辑事件，自动更新序号
        self.sheet.bind("<<SheetModified>>", lambda e: self.update_row_numbers())

        self.sheet.pack(fill=BOTH, expand=True, padx=0, pady=0)

        # 自动调整列宽填充所有空间
        self.sheet.bind("<Configure>", lambda e: self._auto_resize_columns())

        # 密度输入
        density_frame = Frame(self, bg="#ffffff", relief="flat", bd=2)
        density_frame.pack(fill=X, pady=12)

        density_content = Frame(density_frame, bg="#ffffff")
        density_content.pack(fill=X, padx=20, pady=15)

        Label(density_content,
              text="密度 (g/cm³)：",
              font=("Microsoft YaHei UI", 12, "bold"),
              bg="#ffffff", fg="#0066ff").pack(side=LEFT, padx=(0, 10))

        self.density_var = StringVar(value=str(self.app.state.get("density", 1.60)))
        density_entry = Entry(density_content,
                             textvariable=self.density_var,
                             font=("Microsoft YaHei UI", 12),
                             bg="#b3d9ff", fg="#0066ff",
                             width=12, justify=CENTER)
        density_entry.pack(side=LEFT, padx=8)

    def on_double_click(self, event):
        """处理双击事件 - 化学名称列弹出选择框"""
        try:
            # 获取当前选中的单元格
            selected = self.sheet.get_currently_selected()
            if not selected:
                return

            row, col = selected[0], selected[1]

            # 如果双击的是"化学名称"列（第1列，索引为1）
            if col == 1:
                self.show_chemical_selector(row)
            else:
                # 其他列正常编辑
                self.sheet.open_cell()
        except Exception as e:
            print(f"双击事件错误: {e}")
            self.sheet.open_cell()

    def show_chemical_selector(self, row):
        """显示化学名称选择对话框"""
        # 创建对话框
        dialog = Toplevel(self)
        dialog.title("选择化学组分")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 500) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 600) // 2
        dialog.geometry(f"500x600+{x}+{y}")

        # 标题
        title_frame = Frame(dialog, bg="#0066ff", height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)

        Label(title_frame,
              text="🧪 选择化学组分",
              font=("Microsoft YaHei UI", 16, "bold"),
              bg="#0066ff", fg="#ffffff").pack(expand=True)

        # 搜索框
        search_frame = Frame(dialog, bg="#ffffff")
        search_frame.pack(fill=X, padx=20, pady=10)

        Label(search_frame,
              text="🔍 搜索：",
              font=("Microsoft YaHei UI", 10),
              bg="#ffffff").pack(side=LEFT, padx=(0, 5))

        search_var = StringVar()
        search_entry = Entry(search_frame,
                            textvariable=search_var,
                            font=("Microsoft YaHei UI", 10),
                            width=30)
        search_entry.pack(side=LEFT, fill=X, expand=True)

        # 列表框
        list_frame = Frame(dialog, bg="#ffffff")
        list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        listbox = Listbox(list_frame,
                         font=("Microsoft YaHei UI", 10),
                         yscrollcommand=scrollbar.set,
                         selectmode=tk.SINGLE)
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 填充化学组分列表
        def update_list(filter_text=""):
            listbox.delete(0, END)
            for item in CHEM_DB:
                name = item["name_cn"]
                formula = item["formula"]
                if filter_text.lower() in name.lower() or filter_text.lower() in formula.lower():
                    display_text = f"{name} ({formula})"
                    listbox.insert(END, display_text)

        update_list()

        # 搜索功能
        def on_search(*args):
            update_list(search_var.get())

        search_var.trace('w', on_search)

        # 双击选择
        def on_select(event=None):
            selection = listbox.curselection()
            if not selection:
                return

            selected_text = listbox.get(selection[0])
            # 提取化学名称（括号前的部分）
            chem_name = selected_text.split(" (")[0]

            # 从数据库获取完整信息
            chem_info = CHEM_BY_NAME.get(chem_name)
            if chem_info:
                # 更新表格
                current_data = self.sheet.get_sheet_data()
                if row < len(current_data):
                    current_data[row][1] = chem_name  # 化学名称
                    current_data[row][2] = chem_info["formula"]  # 化学组成
                    current_data[row][3] = chem_info["remark"]  # 备注
                    # 含量保持不变或使用默认值
                    if not current_data[row][4]:
                        current_data[row][4] = chem_info.get("default_pct", 0.0)

                    self.sheet.set_sheet_data(current_data)
                    # 自动更新序号
                    self.update_row_numbers()

            dialog.destroy()

        listbox.bind("<Double-Button-1>", on_select)

        # 按钮
        button_frame = Frame(dialog, bg="#ffffff")
        button_frame.pack(fill=X, padx=20, pady=(0, 20))

        Button(button_frame,
               text="✓ 确定",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#0066ff", fg="#ffffff",
               activebackground="#0055dd",
               relief="flat", bd=0,
               padx=30, pady=10,
               command=on_select).pack(side=LEFT, padx=(0, 10))

        Button(button_frame,
               text="✗ 取消",
               font=("Microsoft YaHei UI", 11),
               bg="#cccccc", fg="#333333",
               activebackground="#bbbbbb",
               relief="flat", bd=0,
               padx=30, pady=10,
               command=dialog.destroy).pack(side=LEFT)

        # 焦点到搜索框
        search_entry.focus_set()

    def update_row_numbers(self):
        """自动更新序号列"""
        try:
            current_data = self.sheet.get_sheet_data()
            row_num = 1
            for i, row in enumerate(current_data):
                # 如果该行有化学名称，则分配序号
                if row[1]:  # 化学名称列不为空
                    current_data[i][0] = row_num
                    row_num += 1
                else:
                    current_data[i][0] = ""  # 空行不显示序号

            self.sheet.set_sheet_data(current_data)
        except Exception as e:
            print(f"更新序号错误: {e}")

    def _auto_resize_columns(self):
        """自动调整列宽以填充所有可用空间"""
        try:
            # 获取表格可用宽度
            total_width = self.sheet.winfo_width()
            if total_width <= 1:  # 还未渲染完成
                return

            # 减去滚动条和边距
            available_width = total_width - 20

            # 按比例分配列宽：序号(10%), 化学组分(30%), 化学组成(20%), 备注(20%), 含量(20%)
            col_ratios = [0.10, 0.30, 0.20, 0.20, 0.20]

            for i, ratio in enumerate(col_ratios):
                width = int(available_width * ratio)
                self.sheet.column_width(column=i, width=width)
        except:
            pass

    def _on_sheet_select(self, event=None):
        """Sheet选择事件 - 用于化学物质选择"""
        # Sheet已经内置编辑功能，这里可以添加自定义逻辑
        pass

    def validate(self):
        """验证并保存"""
        try:
            density = float(self.density_var.get())
            self.app.state["density"] = density
        except:
            messagebox.showerror("错误", "密度格式不正确")
            return False

        # 从Sheet收集配方数据
        formula_rows = []
        data = self.sheet.get_sheet_data()

        for row_idx, row_data in enumerate(data):
            if len(row_data) >= 5 and row_data[1]:  # 有化学名称
                try:
                    # row_data格式: [序号, 化学名称, 分子式, 备注, 含量(%)]
                    name = str(row_data[1]).strip()
                    formula = str(row_data[2]).strip() if row_data[2] else ""
                    remark = str(row_data[3]).strip() if row_data[3] else ""
                    content = float(row_data[4]) if row_data[4] else 0.0

                    # 从化学数据库查找mw和code
                    rec = CHEM_BY_NAME.get(name)
                    if rec:
                        formula_rows.append({
                            "name": name,
                            "formula": formula or rec.get('formula', ''),
                            "remark": remark or rec.get('remark', ''),
                            "content": content,
                            "mw": float(rec.get('mw', 0.0)),
                            "code": rec.get('code', '')
                        })
                except Exception as e:
                    print(f"Error processing row {row_idx}: {e}")
                    pass

        self.app.state["formula_rows"] = formula_rows
        return True

    def on_show(self):
        """显示时恢复数据"""
        pass

# =================== 步骤3: 贮存时间 ===================
class Step3Storage(Frame):
    YEARS = [0, 4, 8, 12, 16, 20, 24, 30, 40, 50]

    def __init__(self, parent, app):
        super().__init__(parent, bg="#e8f4fd")
        self.app = app
        self.create_interface()

    def create_interface(self):
        # 步骤标题
        title_frame = Frame(self, bg="#e8f4fd")
        title_frame.pack(fill=X, pady=(0, 25))

        title = Label(title_frame,
                     text="步骤三：贮存时间设置",
                     font=("Microsoft YaHei UI", 20, "bold"),
                     fg="#0066ff", bg="#e8f4fd")
        title.pack(anchor=W)

        subtitle = Label(title_frame,
                        text="选择推进剂的贮存时间（年），用于计算老化对燃烧速度的影响",
                        font=("Microsoft YaHei UI", 12),
                        fg="#0099ff", bg="#e8f4fd")
        subtitle.pack(anchor=W, pady=(6, 0))

        # 参数设置区域
        params_container = Frame(self, bg="#ffffff", relief="flat", bd=2)
        params_container.pack(fill=BOTH, expand=True, pady=20)

        params_content = Frame(params_container, bg="#ffffff")
        params_content.pack(fill=BOTH, expand=True, padx=30, pady=25)

        # 贮存时间设置
        storage_frame = Frame(params_content, bg="#ffffff")
        storage_frame.pack(pady=20)

        Label(storage_frame,
              text="⏱️ 贮存时间：",
              font=("Microsoft YaHei UI", 14, "bold"),
              bg="#ffffff", fg="#0066ff").pack(side=LEFT, padx=(0, 15))

        self.year_var = IntVar(value=self.YEARS[0])
        year_combo = ttk.Combobox(storage_frame,
                                 state="readonly",
                                 values=self.YEARS,
                                 textvariable=self.year_var,
                                 font=("Microsoft YaHei UI", 13),
                                 width=15)
        year_combo.pack(side=LEFT, padx=10)

        Label(storage_frame,
              text="年",
              font=("Microsoft YaHei UI", 14, "bold"),
              bg="#ffffff", fg="#0099ff").pack(side=LEFT, padx=(5, 0))

        # 说明文本
        info_frame = Frame(params_content, bg="#b3d9ff", relief="flat", bd=1)
        info_frame.pack(fill=X, pady=25)

        info_content = Frame(info_frame, bg="#b3d9ff")
        info_content.pack(fill=X, padx=20, pady=15)

        Label(info_content,
              text="💡 说明：",
              font=("Microsoft YaHei UI", 12, "bold"),
              bg="#b3d9ff", fg="#0066ff").pack(anchor=W)

        Label(info_content,
              text="• 贮存时间范围：0-50年",
              font=("Microsoft YaHei UI", 11),
              bg="#b3d9ff", fg="#0088ff").pack(anchor=W, pady=(5, 2))

        Label(info_content,
              text="• 贮存时间会影响推进剂的化学稳定性和燃烧性能",
              font=("Microsoft YaHei UI", 11),
              bg="#b3d9ff", fg="#0088ff").pack(anchor=W, pady=2)

        Label(info_content,
              text="• 建议根据实际贮存条件选择合适的时间参数",
              font=("Microsoft YaHei UI", 11),
              bg="#b3d9ff", fg="#0088ff").pack(anchor=W, pady=2)

    def validate(self):
        """验证并保存"""
        self.app.state["storage_year"] = int(self.year_var.get())
        return True

    def on_show(self):
        """显示时恢复数据"""
        if "storage_year" in self.app.state:
            self.year_var.set(self.app.state["storage_year"])

# =================== 步骤4: 工况配置 ===================
class Step4PT(Frame):
    TEMPS = list(range(-40, 81, 5))  # °C: -40 to 75
    PRESSURES = [0.1] + list(range(1, 31))  # MPa: 0.1, 1, 2, 3, ..., 30

    def __init__(self, parent, app):
        super().__init__(parent, bg="#e8f4fd")
        self.app = app
        self.cases = []
        self.create_interface()

    def create_interface(self):
        # 步骤标题
        title_frame = Frame(self, bg="#e8f4fd")
        title_frame.pack(fill=X, pady=(0, 20))

        title = Label(title_frame,
                     text="步骤四：工况配置",
                     font=("Microsoft YaHei UI", 20, "bold"),
                     fg="#0066ff", bg="#e8f4fd")
        title.pack(anchor=W)

        subtitle = Label(title_frame,
                        text="添加温度-压力工况组合，系统将对每个工况进行燃烧速度计算",
                        font=("Microsoft YaHei UI", 12),
                        fg="#0099ff", bg="#e8f4fd")
        subtitle.pack(anchor=W, pady=(6, 0))

        # 输入区域
        input_container = Frame(self, bg="#ffffff", relief="flat", bd=2)
        input_container.pack(fill=X, pady=15)

        input_content = Frame(input_container, bg="#ffffff")
        input_content.pack(fill=X, padx=25, pady=18)

        # 温度输入
        temp_frame = Frame(input_content, bg="#ffffff")
        temp_frame.pack(side=LEFT, padx=(0, 25))

        Label(temp_frame,
              text="🌡️ 温度：",
              font=("Microsoft YaHei UI", 12, "bold"),
              bg="#ffffff", fg="#0066ff").pack(side=LEFT, padx=(0, 10))

        self.temp_var = IntVar(value=25)
        temp_combo = ttk.Combobox(temp_frame,
                                 state="readonly",
                                 values=self.TEMPS,
                                 textvariable=self.temp_var,
                                 font=("Microsoft YaHei UI", 11),
                                 width=10)
        temp_combo.pack(side=LEFT, padx=5)

        Label(temp_frame,
              text="°C",
              font=("Microsoft YaHei UI", 12, "bold"),
              bg="#ffffff", fg="#0099ff").pack(side=LEFT, padx=(3, 0))

        # 压力输入
        pres_frame = Frame(input_content, bg="#ffffff")
        pres_frame.pack(side=LEFT, padx=25)

        Label(pres_frame,
              text="💨 压力：",
              font=("Microsoft YaHei UI", 12, "bold"),
              bg="#ffffff", fg="#0066ff").pack(side=LEFT, padx=(0, 10))

        self.pres_var = StringVar(value="0.1")
        pres_combo = ttk.Combobox(pres_frame,
                                 state="readonly",
                                 values=self.PRESSURES,
                                 textvariable=self.pres_var,
                                 font=("Microsoft YaHei UI", 11),
                                 width=10)
        pres_combo.pack(side=LEFT, padx=5)

        Label(pres_frame,
              text="MPa",
              font=("Microsoft YaHei UI", 12, "bold"),
              bg="#ffffff", fg="#0099ff").pack(side=LEFT, padx=(3, 0))

        # 按钮区域
        button_frame = Frame(input_content, bg="#ffffff")
        button_frame.pack(side=LEFT, padx=25)

        Button(button_frame,
               text="➕ 添加工况",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#00ff7f", fg="#ffffff",
               activebackground="#00e64d",
               relief="flat", bd=0,
               padx=18, pady=8,
               command=self.add_case).pack(side=LEFT, padx=5)

        Button(button_frame,
               text="🗑️ 删除选中",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#ff0044", fg="#ffffff",
               activebackground="#d32f2f",
               relief="flat", bd=0,
               padx=18, pady=8,
               command=self.delete_selected).pack(side=LEFT, padx=5)

        Button(button_frame,
               text="🔄 清空全部",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#ff6600", fg="#ffffff",
               activebackground="#ff4500",
               relief="flat", bd=0,
               padx=18, pady=8,
               command=self.clear_cases).pack(side=LEFT, padx=5)

        # 工况列表 - 使用左右布局
        list_container = Frame(self, bg="#ffffff", relief="flat", bd=2)
        list_container.pack(fill=BOTH, expand=True, pady=8)

        list_content = Frame(list_container, bg="#ffffff")
        list_content.pack(fill=BOTH, expand=True, padx=10, pady=8)

        # 左侧：工况列表表格（固定宽度）
        left_panel = Frame(list_content, bg="#ffffff")
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 10))
        left_panel.config(width=450)  # 固定宽度450px
        left_panel.pack_propagate(False)  # 禁止子组件改变父组件大小

        Label(left_panel,
              text="📋 工况列表",
              font=("Microsoft YaHei UI", 14, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, pady=(0, 8))

        # 使用tksheet实现Excel样式网格
        list_frame = Frame(left_panel, bg="#ffffff")
        list_frame.pack(fill=BOTH, expand=True)

        self.case_sheet = Sheet(
            list_frame,
            headers=["序号", "温度(°C)", "压力(MPa)"],
            show_x_scrollbar=False,
            show_y_scrollbar=True,
            show_row_index=False,  # 隐藏行号列
            show_header=True,
            show_top_left=False,
            empty_horizontal=0,  # 不显示额外的空白列
            empty_vertical=0,    # 不显示额外的空白行
            align="center",
            header_align="center",
            default_row_height=38,
            default_header_height=42,
            font=("Microsoft YaHei UI", 11, "normal"),
            header_font=("Microsoft YaHei UI", 12, "bold")
        )

        # 配置颜色
        self.case_sheet.set_options(
            table_bg="#ffffff",
            table_fg="#0066ff",
            header_bg="#b3d9ff",
            header_fg="#0066ff",
            table_grid_fg="#b3d9ff",
            header_grid_fg="#99ccff"
        )

        # 禁用编辑（只读显示）
        self.case_sheet.enable_bindings("single_select", "row_select")

        self.case_sheet.pack(fill=BOTH, expand=True, padx=0, pady=0)

        # 确保只显示3列
        self.case_sheet.headers(newheaders=["序号", "温度(°C)", "压力(MPa)"], reset_col_positions=True, show_headers_if_not_sheet=True)

        # 设置固定列宽，总和 = 440px（小于面板宽度450px）
        self.case_sheet.column_width(column=0, width=80)   # 序号
        self.case_sheet.column_width(column=1, width=180)  # 温度
        self.case_sheet.column_width(column=2, width=180)  # 压力

        # 保持兼容性
        self.case_view = self.case_sheet

        # 右侧：信息面板（填充剩余空间）
        right_panel = Frame(list_content, bg="#e8f4fd", relief="flat", bd=2)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        # 信息面板标题
        info_title = Frame(right_panel, bg="#0066ff", height=50)
        info_title.pack(fill=X)
        info_title.pack_propagate(False)

        Label(info_title,
              text="📊 工况统计",
              font=("Microsoft YaHei UI", 13, "bold"),
              bg="#0066ff", fg="#ffffff").pack(expand=True)

        # 统计信息区域
        stats_frame = Frame(right_panel, bg="#e8f4fd")
        stats_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # 工况总数
        count_frame = Frame(stats_frame, bg="#ffffff", relief="flat", bd=1)
        count_frame.pack(fill=X, pady=(0, 12))

        Label(count_frame,
              text="工况总数",
              font=("Microsoft YaHei UI", 10),
              bg="#ffffff", fg="#666666").pack(pady=(8, 2))

        self.case_count_label = Label(count_frame,
                                      text="0",
                                      font=("Microsoft YaHei UI", 28, "bold"),
                                      bg="#ffffff", fg="#0066ff")
        self.case_count_label.pack(pady=(0, 8))

        # 温度范围
        temp_range_frame = Frame(stats_frame, bg="#ffffff", relief="flat", bd=1)
        temp_range_frame.pack(fill=X, pady=12)

        Label(temp_range_frame,
              text="🌡️ 温度范围",
              font=("Microsoft YaHei UI", 10, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, padx=10, pady=(8, 4))

        self.temp_range_label = Label(temp_range_frame,
                                      text="未设置",
                                      font=("Microsoft YaHei UI", 11),
                                      bg="#ffffff", fg="#333333")
        self.temp_range_label.pack(anchor=W, padx=10, pady=(0, 8))

        # 压力范围
        pres_range_frame = Frame(stats_frame, bg="#ffffff", relief="flat", bd=1)
        pres_range_frame.pack(fill=X, pady=12)

        Label(pres_range_frame,
              text="💨 压力范围",
              font=("Microsoft YaHei UI", 10, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, padx=10, pady=(8, 4))

        self.pres_range_label = Label(pres_range_frame,
                                      text="未设置",
                                      font=("Microsoft YaHei UI", 11),
                                      bg="#ffffff", fg="#333333")
        self.pres_range_label.pack(anchor=W, padx=10, pady=(0, 8))

        # 快捷操作区域
        quick_actions_frame = Frame(stats_frame, bg="#ffffff", relief="flat", bd=1)
        quick_actions_frame.pack(fill=X, pady=(20, 0))

        Label(quick_actions_frame,
              text="⚡ 快捷操作",
              font=("Microsoft YaHei UI", 10, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, padx=10, pady=(8, 8))

        # 批量添加按钮
        Button(quick_actions_frame,
               text="📦 批量添加工况",
               font=("Microsoft YaHei UI", 10),
               bg="#00aaff", fg="#ffffff",
               activebackground="#0088cc",
               relief="flat", bd=0,
               padx=15, pady=8,
               command=self.batch_add_cases).pack(fill=X, padx=10, pady=(0, 8))

        # 删除选中按钮（右侧面板）
        Button(quick_actions_frame,
               text="🗑️ 删除选中工况",
               font=("Microsoft YaHei UI", 10),
               bg="#ff4444", fg="#ffffff",
               activebackground="#cc0000",
               relief="flat", bd=0,
               padx=15, pady=8,
               command=self.delete_selected).pack(fill=X, padx=10, pady=(0, 8))

        # 使用说明
        help_frame = Frame(stats_frame, bg="#fff9e6", relief="flat", bd=1)
        help_frame.pack(fill=X, pady=(20, 0))

        Label(help_frame,
              text="💡 使用提示",
              font=("Microsoft YaHei UI", 9, "bold"),
              bg="#fff9e6", fg="#ff9900").pack(anchor=W, padx=8, pady=(6, 4))

        help_text = "• 点击表格行选中工况\n• 可多选后批量删除\n• 建议设置3-10个工况"
        Label(help_frame,
              text=help_text,
              font=("Microsoft YaHei UI", 8),
              bg="#fff9e6", fg="#666666",
              justify=LEFT).pack(anchor=W, padx=8, pady=(0, 6))

    def add_case(self):
        """添加工况"""
        try:
            t = int(self.temp_var.get())
            p = float(self.pres_var.get())
        except Exception:
            messagebox.showerror("格式错误", "温度或压力数值不合法")
            return

        self.cases.append({"T": t, "P": p})
        self.refresh_view()
        self.update_statistics()
        # 立即保存到状态
        self.app.state["cases"] = self.cases
        messagebox.showinfo("成功", f"已添加工况：{t}°C, {p} MPa")

    def delete_selected(self):
        """删除选中的工况"""
        # 获取选中的行（支持整行选择和单元格选择）
        selected_rows = set()

        # 方法1: 获取选中的整行
        rows = self.case_sheet.get_selected_rows()
        if rows:
            selected_rows.update(rows)

        # 方法2: 获取选中的单元格，提取行号
        cells = self.case_sheet.get_selected_cells()
        if cells:
            for cell in cells:
                selected_rows.add(cell[0])  # cell = (row, col)

        # 方法3: 获取当前选中的位置
        current = self.case_sheet.get_currently_selected()
        if current:
            # current 可能是 (row, col) 或其他格式
            if isinstance(current, tuple) and len(current) >= 2:
                selected_rows.add(current[0])

        if not selected_rows:
            messagebox.showinfo("提示", "请先选中要删除的工况")
            return

        # 转换为列表并排序
        selected_rows = list(selected_rows)
        count = len(selected_rows)

        # 确认删除
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除选中的 {count} 个工况吗？",
            icon="warning"
        )

        if not result:
            return

        # 从后往前删除，避免索引变化
        for row_idx in sorted(selected_rows, reverse=True):
            if 0 <= row_idx < len(self.cases):
                self.cases.pop(row_idx)

        self.refresh_view()
        self.update_statistics()
        # 立即保存到状态
        self.app.state["cases"] = self.cases
        messagebox.showinfo("成功", f"已删除 {count} 个工况")

    def clear_cases(self):
        """清空所有工况"""
        if not self.cases:
            messagebox.showinfo("提示", "工况列表已经是空的")
            return

        result = messagebox.askyesno(
            "确认清空",
            f"确定要清空所有 {len(self.cases)} 个工况吗？",
            icon="warning"
        )

        if result:
            self.cases.clear()
            self.refresh_view()
            self.update_statistics()
            # 立即保存到状态
            self.app.state["cases"] = self.cases
            messagebox.showinfo("成功", "已清空所有工况")

    def refresh_view(self):
        """刷新工况列表"""
        # 清空并重新填充Sheet数据
        data = [[i, case["T"], case["P"]] for i, case in enumerate(self.cases, 1)]
        self.case_sheet.set_sheet_data(data if data else [[]])

        # 更新统计信息
        self.update_statistics()

    def update_statistics(self):
        """更新右侧统计信息"""
        # 更新工况总数
        count = len(self.cases)
        self.case_count_label.config(text=str(count))

        if count == 0:
            self.temp_range_label.config(text="未设置")
            self.pres_range_label.config(text="未设置")
        else:
            # 计算温度范围
            temps = [case["T"] for case in self.cases]
            min_temp = min(temps)
            max_temp = max(temps)
            if min_temp == max_temp:
                temp_text = f"{min_temp}°C"
            else:
                temp_text = f"{min_temp}°C ~ {max_temp}°C"
            self.temp_range_label.config(text=temp_text)

            # 计算压力范围
            pressures = [case["P"] for case in self.cases]
            min_pres = min(pressures)
            max_pres = max(pressures)
            if min_pres == max_pres:
                pres_text = f"{min_pres} MPa"
            else:
                pres_text = f"{min_pres} ~ {max_pres} MPa"
            self.pres_range_label.config(text=pres_text)

    def batch_add_cases(self):
        """批量添加工况"""
        # 创建批量添加对话框
        dialog = Toplevel(self)
        dialog.title("批量添加工况")
        dialog.geometry("500x400")
        dialog.configure(bg="#e8f4fd")
        dialog.transient(self)
        dialog.grab_set()

        # 标题
        title_frame = Frame(dialog, bg="#0066ff", height=60)
        title_frame.pack(fill=X)
        title_frame.pack_propagate(False)

        Label(title_frame,
              text="📦 批量添加工况",
              font=("Microsoft YaHei UI", 14, "bold"),
              bg="#0066ff", fg="#ffffff").pack(expand=True)

        # 内容区域
        content = Frame(dialog, bg="#ffffff")
        content.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 说明
        Label(content,
              text="选择温度和压力，系统将自动生成所有组合",
              font=("Microsoft YaHei UI", 10),
              bg="#ffffff", fg="#666666").pack(pady=(0, 15))

        # 温度选择
        temp_frame = Frame(content, bg="#ffffff")
        temp_frame.pack(fill=X, pady=10)

        Label(temp_frame,
              text="🌡️ 选择温度（可多选）：",
              font=("Microsoft YaHei UI", 11, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, pady=(0, 5))

        temp_list_frame = Frame(temp_frame, bg="#ffffff", relief="sunken", bd=1)
        temp_list_frame.pack(fill=BOTH, expand=True)

        temp_scrollbar = Scrollbar(temp_list_frame)
        temp_scrollbar.pack(side=RIGHT, fill=Y)

        temp_listbox = Listbox(temp_list_frame,
                              selectmode=MULTIPLE,
                              font=("Microsoft YaHei UI", 10),
                              height=5,
                              yscrollcommand=temp_scrollbar.set)
        temp_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        temp_scrollbar.config(command=temp_listbox.yview)

        for temp in self.TEMPS:
            temp_listbox.insert(END, f"{temp}°C")

        # 压力选择
        pres_frame = Frame(content, bg="#ffffff")
        pres_frame.pack(fill=X, pady=10)

        Label(pres_frame,
              text="💨 选择压力（可多选）：",
              font=("Microsoft YaHei UI", 11, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, pady=(0, 5))

        pres_list_frame = Frame(pres_frame, bg="#ffffff", relief="sunken", bd=1)
        pres_list_frame.pack(fill=BOTH, expand=True)

        pres_scrollbar = Scrollbar(pres_list_frame)
        pres_scrollbar.pack(side=RIGHT, fill=Y)

        pres_listbox = Listbox(pres_list_frame,
                              selectmode=MULTIPLE,
                              font=("Microsoft YaHei UI", 10),
                              height=5,
                              yscrollcommand=pres_scrollbar.set)
        pres_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        pres_scrollbar.config(command=pres_listbox.yview)

        for pres in self.PRESSURES:
            pres_listbox.insert(END, f"{pres} MPa")

        # 按钮
        button_frame = Frame(content, bg="#ffffff")
        button_frame.pack(fill=X, pady=(15, 0))

        def confirm_batch_add():
            # 获取选中的温度
            selected_temps = [self.TEMPS[i] for i in temp_listbox.curselection()]
            # 获取选中的压力
            selected_pres = [self.PRESSURES[i] for i in pres_listbox.curselection()]

            if not selected_temps or not selected_pres:
                messagebox.showwarning("提示", "请至少选择一个温度和一个压力")
                return

            # 生成所有组合
            new_cases = []
            for temp in selected_temps:
                for pres in selected_pres:
                    new_cases.append({"T": temp, "P": pres})

            # 确认添加
            count = len(new_cases)
            result = messagebox.askyesno(
                "确认添加",
                f"将添加 {count} 个工况组合\n（{len(selected_temps)}个温度 × {len(selected_pres)}个压力）\n\n是否继续？"
            )

            if result:
                self.cases.extend(new_cases)
                self.refresh_view()
                self.update_statistics()
                # 立即保存到状态
                self.app.state["cases"] = self.cases
                dialog.destroy()
                messagebox.showinfo("成功", f"已成功添加 {count} 个工况")

        Button(button_frame,
               text="✅ 确认添加",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#00ff7f", fg="#ffffff",
               activebackground="#00e64d",
               relief="flat", bd=0,
               padx=20, pady=10,
               command=confirm_batch_add).pack(side=LEFT, padx=5)

        Button(button_frame,
               text="❌ 取消",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#cccccc", fg="#333333",
               activebackground="#999999",
               relief="flat", bd=0,
               padx=20, pady=10,
               command=dialog.destroy).pack(side=LEFT, padx=5)

    def validate(self):
        """验证并保存"""
        if not self.cases:
            result = messagebox.askyesno(
                "未添加工况",
                "您还没有添加任何工况，是否继续？",
                icon="warning"
            )
            if not result:
                return False

        self.app.state["cases"] = self.cases
        return True

    def on_show(self):
        """显示时恢复数据"""
        self.cases = list(self.app.state.get("cases", []))
        self.refresh_view()

# =================== 步骤5: 结果输出 ===================
class Step5Output(Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#e8f4fd")
        self.app = app
        self.proc = None  # 当前运行的进程
        self.sim_thread = None  # 仿真线程
        self.is_running = False  # 是否正在运行
        self.create_interface()

    def create_interface(self):
        # 步骤标题
        title_frame = Frame(self, bg="#e8f4fd")
        title_frame.pack(fill=X, pady=(0, 20))

        title = Label(title_frame,
                     text="步骤五：运行仿真与结果查看",
                     font=("Microsoft YaHei UI", 20, "bold"),
                     fg="#0066ff", bg="#e8f4fd")
        title.pack(anchor=W)

        subtitle = Label(title_frame,
                        text='点击"开始计算"按钮运行仿真，查看燃烧速度计算结果',
                        font=("Microsoft YaHei UI", 12),
                        fg="#0099ff", bg="#e8f4fd")
        subtitle.pack(anchor=W, pady=(6, 0))

        # 开始计算按钮区域
        start_container = Frame(self, bg="#00ff7f", relief="flat", bd=2)
        start_container.pack(fill=X, pady=(0, 15))

        start_content = Frame(start_container, bg="#ffffff")
        start_content.pack(fill=X, padx=3, pady=3)

        self.start_btn = Button(start_content,
               text="🚀 开始计算",
               font=("Microsoft YaHei UI", 16, "bold"),
               bg="#00ff7f", fg="#ffffff",
               activebackground="#00e64d",
               relief="flat", bd=0,
               padx=40, pady=15,
               command=self.run_simulation)
        self.start_btn.pack(pady=10)

        # 输出区域
        output_container = Frame(self, bg="#ffffff", relief="flat", bd=2)
        output_container.pack(fill=BOTH, expand=True, pady=(0, 15))

        output_content = Frame(output_container, bg="#ffffff")
        output_content.pack(fill=BOTH, expand=True, padx=18, pady=15)

        # 工具栏
        toolbar = Frame(output_content, bg="#ffffff")
        toolbar.pack(fill=X, pady=(0, 10))

        Label(toolbar,
              text="📊 计算输出",
              font=("Microsoft YaHei UI", 14, "bold"),
              bg="#ffffff", fg="#0066ff").pack(side=LEFT)

        # 停止按钮
        self.stop_btn = Button(toolbar,
               text="⏹️ 停止计算",
               font=("Microsoft YaHei UI", 10, "bold"),
               bg="#ff0044", fg="#ffffff",
               activebackground="#d32f2f",
               relief="flat", bd=0,
               padx=15, pady=6,
               state="disabled",
               command=self.stop_simulation)
        self.stop_btn.pack(side=RIGHT, padx=5)

        Button(toolbar,
               text="💾 保存日志",
               font=("Microsoft YaHei UI", 10, "bold"),
               bg="#0099ff", fg="#ffffff",
               activebackground="#0088ff",
               relief="flat", bd=0,
               padx=15, pady=6,
               command=self.save_log).pack(side=RIGHT, padx=5)

        Button(toolbar,
               text="🗑️ 清空输出",
               font=("Microsoft YaHei UI", 10, "bold"),
               bg="#ff6600", fg="#ffffff",
               activebackground="#ff4500",
               relief="flat", bd=0,
               padx=15, pady=6,
               command=self.clear_output).pack(side=RIGHT, padx=5)

        # 文本输出区域
        text_frame = Frame(output_content, bg="#ffffff")
        text_frame.pack(fill=BOTH, expand=True)

        self.text = Text(text_frame,
                        font=("Consolas", 10),
                        bg="#263238", fg="#00ff88",
                        insertbackground="#00ff88",
                        wrap="word",
                        height=15)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, orient=VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=LEFT, fill=Y)

        # 结果表格区域
        result_container = Frame(self, bg="#ffffff", relief="flat", bd=2)
        result_container.pack(fill=BOTH, expand=True, pady=(0, 8))

        result_content = Frame(result_container, bg="#ffffff")
        result_content.pack(fill=BOTH, expand=True, padx=10, pady=8)

        Label(result_content,
              text="📋 结果汇总表",
              font=("Microsoft YaHei UI", 14, "bold"),
              bg="#ffffff", fg="#0066ff").pack(anchor=W, pady=(0, 8))

        # 使用tksheet实现Excel样式网格
        table_frame = Frame(result_content, bg="#ffffff")
        table_frame.pack(fill=BOTH, expand=True)

        self.result_sheet = Sheet(
            table_frame,
            headers=["序号", "温度(°C)", "压力(MPa)", "燃速(mm/s)"],
            show_x_scrollbar=False,
            show_y_scrollbar=True,
            show_row_index=False,  # 隐藏行号列，只显示4列
            show_header=True,
            show_top_left=False,
            empty_horizontal=0,  # 不显示额外的空白列
            empty_vertical=0,    # 不显示额外的空白行
            total_columns=4,     # ✅ 限制总列数为4
            align="center",
            header_align="center",
            default_row_height=38,
            default_header_height=42,
            font=("Microsoft YaHei UI", 11, "normal"),
            header_font=("Microsoft YaHei UI", 12, "bold")
        )

        # 配置颜色
        self.result_sheet.set_options(
            table_bg="#ffffff",
            table_fg="#0066ff",
            header_bg="#b3d9ff",
            header_fg="#0066ff",
            table_grid_fg="#b3d9ff",
            header_grid_fg="#99ccff"
        )

        # 禁用编辑（只读显示）
        self.result_sheet.enable_bindings("single_select", "row_select")

        self.result_sheet.pack(fill=BOTH, expand=True, padx=0, pady=0)

        # 确保只显示4列，隐藏所有额外的列
        self.result_sheet.headers(newheaders=["序号", "温度(°C)", "压力(MPa)", "燃速(mm/s)"], reset_col_positions=True, show_headers_if_not_sheet=True)

        # 设置固定列宽
        self.result_sheet.column_width(column=0, width=100)   # 序号
        self.result_sheet.column_width(column=1, width=150)   # 温度
        self.result_sheet.column_width(column=2, width=150)   # 压力
        self.result_sheet.column_width(column=3, width=200)   # 燃速

        # 保持兼容性
        self.result_view = self.result_sheet

        # 图表按钮
        chart_btn_frame = Frame(result_content, bg="#ffffff")
        chart_btn_frame.pack(fill=X, pady=(10, 0))

        Button(chart_btn_frame,
               text="📈 查看燃速曲线图",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#0099ff", fg="#ffffff",
               activebackground="#0088ff",
               relief="flat", bd=0,
               padx=20, pady=8,
               command=self.show_chart).pack(side=LEFT, padx=5)

        Button(chart_btn_frame,
               text="💾 导出结果到Excel",
               font=("Microsoft YaHei UI", 11, "bold"),
               bg="#00aa00", fg="#ffffff",
               activebackground="#009900",
               relief="flat", bd=0,
               padx=20, pady=8,
               command=self.export_results).pack(side=LEFT, padx=5)

    def on_show(self):
        """显示时的回调"""
        # 展示配置概览
        s = self.app.state
        self.append("="*70 + "\n")
        self.append("📋 配置概览\n")
        self.append("="*70 + "\n\n")

        self.append(f"📁 机理文件:\n")
        self.append(f"   液相机理: {s['files'].get('mech', '未设置')}\n")
        self.append(f"   分子参数: {s['files'].get('thermo', '未设置')}\n")
        self.append(f"   气相机理: {s['files'].get('yaml', '未设置')}\n\n")

        self.append(f"🧪 配方信息:\n")
        if s.get('formula_rows'):
            for row in s['formula_rows']:
                self.append(f"   {row['name']}: {row['content']}%\n")
        else:
            self.append("   未设置配方\n")
        self.append(f"\n⚖️ 密度: {s['density']} g/cm³\n")
        self.append(f"⏱️ 贮存时间: {s['storage_year']} 年\n")
        self.append(f"🌡️ 环境温度: {s.get('env_temp', 25)} °C\n\n")

        self.append(f"🌡️ 工况列表:\n")
        if s.get('cases'):
            for i, c in enumerate(s['cases'], 1):
                self.append(f"   工况{i}: 温度 {c['T']}°C, 压力 {c['P']} MPa\n")
        else:
            self.append("   未设置工况\n")

        self.append("\n" + "="*70 + "\n")
        self.append('💡 准备就绪！点击上方"🚀 开始计算"按钮运行仿真\n')
        self.append("="*70 + "\n\n")

    def clear_output(self):
        """清空输出"""
        self.text.delete("1.0", END)

    def append(self, msg: str):
        """追加输出"""
        self.text.insert(END, msg)
        self.text.see(END)
        self.update_idletasks()

    def save_log(self):
        """保存日志"""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", END))
        messagebox.showinfo("已保存", f"日志已保存到：\n{path}")

    def stop_simulation(self):
        """停止仿真"""
        if self.proc:
            try:
                self.proc.terminate()
                self.append("\n⚠️ 用户中止计算\n")
            except:
                pass
        self.is_running = False
        self.stop_btn.config(state="disabled")

    def run_simulation(self):
        """运行仿真（多线程）"""
        if self.is_running:
            messagebox.showwarning("警告", "仿真正在运行中，请等待完成或停止后再运行")
            return

        s = self.app.state
        cases = s.get("cases", [])

        if not cases:
            self.append("❌ 错误：未设置工况，无法运行仿真\n")
            messagebox.showerror("错误", "请先在步骤四中添加工况")
            return

        # 清空结果表格
        self.result_sheet.set_sheet_data([[]])

        # 启用停止按钮，禁用开始按钮
        self.is_running = True
        self.stop_btn.config(state="normal")
        self.start_btn.config(state="disabled")

        # 在新线程中运行
        import threading
        self.sim_thread = threading.Thread(target=self._run_simulation_thread, daemon=True)
        self.sim_thread.start()

    def _run_simulation_thread(self):
        """仿真线程（内部方法）"""
        try:
            self.append("\n" + "="*70 + "\n")
            self.append("🚀 开始运行燃烧速度仿真...\n")
            self.append("="*70 + "\n\n")

            s = self.app.state
            files = s.get("files", {})
            cases = s.get("cases", [])
            formula_rows = s.get("formula_rows", [])

            # 准备物种数据
            species = []
            for row in formula_rows:
                code = row.get('code', '')
                if code and code in CHEM_BY_CODE:
                    mw = CHEM_BY_CODE[code]['mw']
                    species.append({
                        "name": code,
                        "molecular_weight": mw,
                        "amount": row['content']
                    })

            if not species:
                self.append("⚠️ 警告：未设置配方，使用默认配方\n")
                species = [
                    {"name": "NC(L)", "molecular_weight": 299.0, "amount": 60.0},
                    {"name": "NG(L)", "molecular_weight": 227.0, "amount": 15.0},
                    {"name": "DEP(L)", "molecular_weight": 222.0, "amount": 1.0}
                ]

            # 逐工况运行
            self.app.state["summary"] = []
            for i, case in enumerate(cases, 1):
                if not self.is_running:
                    break

                t_c = float(case["T"])  # °C
                p = float(case["P"])   # MPa
                Tinit = t_c + 273.15  # convert to K

                config = {
                    "density": float(s["density"]),
                    "pressure": p,
                    "Tinit": float(Tinit),
                    "storage_time": float(s["storage_year"]),
                    "environment_temp": float(s.get("env_temp", 25)) + 273.15,  # 转换为K
                    "liquid_phase_mech_file": files.get("mech", ""),
                    "thermo_data_file": files.get("thermo", ""),
                    "gas_phase_yaml_file": files.get("yaml", ""),
                    "species": species
                }

                with open("config_input.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                self.append(f"\n{'─'*70}\n")
                self.append(f"🔬 工况 {i}/{len(cases)}: 温度 {t_c}°C, 压力 {p} MPa\n")
                self.append(f"{'─'*70}\n")
                self.append("📝 写入配置文件 config_input.json 完成\n")
                self.append("⚙️ 正在运行计算...\n\n")

                exe = sys.executable
                cmd = [exe, "run.py", "--config", "config_input.json", "--case", str(i)]
                try:
                    self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    stdout_lines = []
                    for line in self.proc.stdout:
                        if not self.is_running:
                            break
                        stdout_lines.append(line)
                        self.append(line)
                    self.proc.wait()
                    out = "".join(stdout_lines)
                    self.proc = None
                except FileNotFoundError:
                    out = f"[INFO] 未找到 run.py，使用示例数据\nBurn rate: {max(0.5, (t_c+40)/300) * (1 + p/30):.3f} mm/s\n"
                    self.append(out)
                except Exception as e:
                    out = f"[ERROR] 运行失败：{e}\n"
                    self.append(out)

                if not self.is_running:
                    break

                rate = parse_burn_rate(out)
                self.app.state["summary"].append({"T": t_c, "P": p, "burn_rate": rate})

                if rate is not None:
                    self.append(f"\n✅ 工况 {i} 完成: 燃速 = {rate:.3f} mm/s\n")
                    # 更新结果表格 - 添加新行到Sheet
                    current_data = self.result_sheet.get_sheet_data()
                    current_data.append([i, t_c, p, f"{rate:.3f}"])
                    self.result_sheet.set_sheet_data(current_data)
                else:
                    self.append(f"\n⚠️ 工况 {i} 完成: 未能解析燃速\n")
                    current_data = self.result_sheet.get_sheet_data()
                    current_data.append([i, t_c, p, "未解析"])
                    self.result_sheet.set_sheet_data(current_data)

            if self.is_running:
                # 汇总结果
                self.append("\n" + "="*70 + "\n")
                self.append("📊 仿真结果汇总\n")
                self.append("="*70 + "\n\n")

                for i, result in enumerate(self.app.state["summary"], 1):
                    t = result['T']
                    p = result['P']
                    rate = result.get('burn_rate')
                    if rate is not None:
                        self.append(f"工况 {i}: T={t}°C, P={p} MPa → 燃速 = {rate:.3f} mm/s\n")
                    else:
                        self.append(f"工况 {i}: T={t}°C, P={p} MPa → 燃速 = 未解析\n")

                self.append("\n" + "="*70 + "\n")
                self.append("🎉 所有工况计算完成！\n")
                self.append("="*70 + "\n")

                messagebox.showinfo("完成", "燃烧速度仿真计算已完成！")

        finally:
            self.is_running = False
            self.stop_btn.config(state="disabled")
            self.start_btn.config(state="normal")
            self.proc = None

    def show_chart(self):
        """显示燃速曲线图"""
        summary = self.app.state.get("summary", [])
        if not summary:
            messagebox.showinfo("提示", "暂无结果数据，请先运行计算")
            return

        # 创建图表窗口
        chart_win = Toplevel(self)
        chart_win.title("燃速曲线图")
        chart_win.geometry("900x700")
        chart_win.configure(bg="#ffffff")

        # 标题
        title_label = Label(chart_win,
                           text="燃烧速度随温度和压力变化曲线",
                           font=("Microsoft YaHei UI", 16, "bold"),
                           fg="#0066ff", bg="#ffffff")
        title_label.pack(pady=20)

        try:
            import matplotlib
            matplotlib.use('TkAgg')
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.pyplot as plt

            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False

            # 创建图表
            fig = Figure(figsize=(10, 6), dpi=90)

            # 按压力分组
            pressure_groups = {}
            for item in summary:
                p = item['P']
                if p not in pressure_groups:
                    pressure_groups[p] = {'T': [], 'rate': []}
                if item['burn_rate'] is not None:
                    pressure_groups[p]['T'].append(item['T'])
                    pressure_groups[p]['rate'].append(item['burn_rate'])

            # 绘制曲线
            ax = fig.add_subplot(111)
            colors = ['#0066ff', '#00aa00', '#ff6600', '#ff0044', '#9900ff', '#00ccff']
            for i, (p, data) in enumerate(sorted(pressure_groups.items())):
                if data['T'] and data['rate']:
                    color = colors[i % len(colors)]
                    ax.plot(data['T'], data['rate'],
                           marker='o', linewidth=2, markersize=8,
                           label=f'P = {p} MPa', color=color)

            ax.set_xlabel('温度 (°C)', fontsize=12, fontweight='bold')
            ax.set_ylabel('燃烧速度 (mm/s)', fontsize=12, fontweight='bold')
            ax.set_title('燃烧速度 vs 温度（不同压力）', fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            fig.tight_layout()

            # 嵌入到Tkinter窗口
            canvas = FigureCanvasTkAgg(fig, master=chart_win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=20, pady=10)

        except ImportError:
            # 如果没有matplotlib，显示简单的文本图表
            text_frame = Frame(chart_win, bg="#ffffff")
            text_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

            text = Text(text_frame, font=("Consolas", 10), bg="#f0f0f0", wrap="none")
            text.pack(side=LEFT, fill=BOTH, expand=True)

            scrollbar = Scrollbar(text_frame, orient=VERTICAL, command=text.yview)
            text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=LEFT, fill=Y)

            text.insert(END, "燃烧速度数据表\n")
            text.insert(END, "="*60 + "\n\n")
            text.insert(END, f"{'序号':<6} {'温度(°C)':<12} {'压力(MPa)':<12} {'燃速(mm/s)':<12}\n")
            text.insert(END, "-"*60 + "\n")
            for i, item in enumerate(summary, 1):
                rate_str = f"{item['burn_rate']:.3f}" if item['burn_rate'] is not None else "未解析"
                text.insert(END, f"{i:<6} {item['T']:<12} {item['P']:<12} {rate_str:<12}\n")
            text.insert(END, "\n" + "="*60 + "\n")
            text.insert(END, "\n提示：安装matplotlib可查看图形化曲线图\n")
            text.insert(END, "命令：pip install matplotlib\n")
            text.config(state="disabled")

    def export_results(self):
        """导出结果到Excel"""
        summary = self.app.state.get("summary", [])
        if not summary:
            messagebox.showinfo("提示", "暂无结果数据，请先运行计算")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8-sig") as f:
                # 写入表头
                f.write("序号,温度(°C),压力(MPa),燃烧速度(mm/s)\n")
                # 写入数据
                for i, item in enumerate(summary, 1):
                    rate_str = f"{item['burn_rate']:.3f}" if item['burn_rate'] is not None else "未解析"
                    f.write(f"{i},{item['T']},{item['P']},{rate_str}\n")
            messagebox.showinfo("导出成功", f"结果已导出到：\n{path}\n\n可用Excel打开查看")
        except Exception as e:
            messagebox.showerror("导出失败", f"导出时发生错误：\n{e}")

    def validate(self):
        """验证"""
        return True




class TechBlueWizardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("燃烧速度仿真软件")
        center_window(self, 1700, 1000)
        self.minsize(1500, 900)
        # 更亮的科技蓝配色
        self.configure(bg="#e8f4fd")

        # 设置窗口图标
        try:
            self.iconbitmap("../../assets/images/logo1.png")
        except:
            pass

        # 配置样式
        self.setup_styles()

        # 共享状态
        self.state = {
            "files": {"mech": "", "thermo": "", "yaml": ""},
            "formula_rows": [],
            "density": 1.60,
            "storage_year": 0,
            "env_temp": 25,
            "cases": [],
            "outputs": [],
            "summary": []
        }

        # 当前步骤
        self.current_step = 0
        self.step_names = ["Step1Files", "Step2Formula", "Step3Storage", "Step4PT", "Step5Output"]

        # 启动画面
        self.withdraw()
        splash = TechBlueSplash(self, seconds=4)
        self.wait_window(splash)
        self.deiconify()

        # 创建主界面
        self.create_interface()

    def setup_styles(self):
        """设置科技蓝样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 按钮样式
        style.configure("TechBlue.TButton",
                       background="#0099ff",
                       foreground="#ffffff",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(25, 12))
        style.map("TechBlue.TButton",
                 background=[('active', '#0088ff'), ('pressed', '#0066ff')])

        # Treeview样式 - Excel网格样式
        style.configure("Treeview",
                       background="#ffffff",
                       foreground="#0066ff",
                       fieldbackground="#ffffff",
                       borderwidth=0,
                       relief="flat",
                       rowheight=32)  # 增加行高

        # 表头样式 - 带边框
        style.configure("Treeview.Heading",
                       background="#b3d9ff",
                       foreground="#0066ff",
                       font=("Microsoft YaHei UI", 11, "bold"),
                       borderwidth=1,
                       relief="raised")  # 凸起效果

        style.map("Treeview.Heading",
                 background=[('active', '#99ccff')],
                 relief=[('active', 'sunken')])

        # 配置Treeview元素 - 添加列分隔线效果
        # 通过修改元素布局来添加边框
        style.element_create("Treeitem.separator", "from", "default")

        # 自定义Treeview布局 - 在每列之间添加分隔符
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        # 配置单元格边框颜色
        style.configure("Treeview",
                       bordercolor="#b3d9ff",
                       lightcolor="#b3d9ff",
                       darkcolor="#b3d9ff")

    def create_interface(self):
        """创建主界面 - 侧边栏布局"""
        # 创建背景Canvas
        self.bg_canvas = tk.Canvas(self, bg="#e8f4fd", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # 绘制背景网格
        for i in range(0, 1600, 100):
            self.bg_canvas.create_line(i, 0, i, 950, fill="#d6ecff", width=1, dash=(2, 6))
        for i in range(0, 950, 100):
            self.bg_canvas.create_line(0, i, 1600, i, fill="#d6ecff", width=1, dash=(2, 6))

        # 创建侧边栏
        self.create_sidebar()

        # 创建顶部标题栏
        self.create_header()

        # 创建主内容区
        self.create_content_area()

        # 创建所有步骤框架
        self.frames = {}
        for F in (Step1Files, Step2Formula, Step3Storage, Step4PT, Step5Output):
            frame = F(self.scrollable_frame, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # 显示第一步
        self.show_frame("Step1Files")

    def create_sidebar(self):
        """创建侧边栏导航"""
        # 侧边栏外框
        sidebar_outer = Frame(self, bg="#0066ff")
        sidebar_outer.place(x=0, y=0, width=280, height=950)

        # 侧边栏主体
        sidebar = Frame(sidebar_outer, bg="#0055dd")
        sidebar.place(x=3, y=3, width=274, height=944)

        # Logo区域
        logo_frame = Frame(sidebar, bg="#0055dd")
        logo_frame.pack(fill=X, pady=(20, 30), padx=20)

        # Logo卡片
        logo_card = Frame(logo_frame, bg="#00aaff")
        logo_card.pack()

        logo_inner = Frame(logo_card, bg="#ffffff")
        logo_inner.pack(padx=3, pady=3)

        logo_content = Frame(logo_inner, bg="#ffffff")
        logo_content.pack(padx=15, pady=15)

        try:
            from PIL import Image, ImageTk
            # Logo 1
            logo1 = Image.open("../../assets/images/logo1.png").resize((60, 60), Image.Resampling.LANCZOS)
            self.sidebar_logo1 = ImageTk.PhotoImage(logo1)
            logo1_label = Label(logo_content, image=self.sidebar_logo1, bg="#ffffff")
            logo1_label.pack(side=LEFT, padx=(0, 10))

            # Logo 2
            logo2 = Image.open("../../assets/images/logo2.jpg").resize((60, 60), Image.Resampling.LANCZOS)
            self.sidebar_logo2 = ImageTk.PhotoImage(logo2)
            logo2_label = Label(logo_content, image=self.sidebar_logo2, bg="#ffffff")
            logo2_label.pack(side=LEFT)
        except:
            logo_label = Label(logo_content, text="⚡", font=("Arial", 50), fg="#0066ff", bg="#ffffff")
            logo_label.pack()

        # 标题
        title_label = Label(sidebar,
                           text="燃烧速度仿真",
                           font=("Microsoft YaHei UI", 16, "bold"),
                           fg="#ffffff", bg="#0055dd")
        title_label.pack(pady=(0, 5))

        subtitle_label = Label(sidebar,
                              text="SIMULATION PLATFORM",
                              font=("Consolas", 9, "bold"),
                              fg="#00ccff", bg="#0055dd")
        subtitle_label.pack(pady=(0, 30))

        # 步骤导航
        self.nav_buttons = []
        steps = [
            {"icon": "📁", "title": "机理选择", "subtitle": "MECHANISM"},
            {"icon": "🧪", "title": "配方设计", "subtitle": "FORMULA"},
            {"icon": "⏱️", "title": "贮存参数", "subtitle": "STORAGE"},
            {"icon": "⚙️", "title": "工况配置", "subtitle": "CONDITIONS"},
            {"icon": "📊", "title": "结果输出", "subtitle": "RESULTS"}
        ]

        for i, step in enumerate(steps):
            self.create_nav_button(sidebar, i, step)

        # 底部信息
        info_frame = Frame(sidebar, bg="#0055dd")
        info_frame.pack(side=BOTTOM, fill=X, pady=20, padx=20)

        info_label = Label(info_frame,
                          text="西安近代化学研究所\n西北工业大学",
                          font=("Microsoft YaHei UI", 9),
                          fg="#99ccff", bg="#0055dd",
                          justify=CENTER)
        info_label.pack()

    def create_nav_button(self, parent, index, step):
        """创建导航按钮"""
        # 按钮容器
        btn_container = Frame(parent, bg="#0055dd")
        btn_container.pack(fill=X, pady=8, padx=15)

        # 按钮外框（发光效果）
        btn_outer = Frame(btn_container, bg="#00aaff" if index == 0 else "#0055dd")
        btn_outer.pack(fill=X)

        # 按钮主体
        btn_frame = Frame(btn_outer, bg="#ffffff" if index == 0 else "#004499")
        btn_frame.pack(fill=X, padx=2, pady=2)

        # 按钮内容 - 使用grid布局实现垂直居中
        btn_content = Frame(btn_frame, bg="#ffffff" if index == 0 else "#004499")
        btn_content.pack(fill=X, padx=15, pady=12)

        # 配置grid权重，使文字区域可以扩展
        btn_content.grid_columnconfigure(1, weight=1)
        btn_content.grid_rowconfigure(0, weight=1)

        # 图标 - 使用grid布局，垂直居中，固定宽度
        icon_label = Label(btn_content,
                          text=step["icon"],
                          font=("Arial", 24),
                          fg="#0066ff" if index == 0 else "#00aaff",
                          bg="#ffffff" if index == 0 else "#004499",
                          width=2,  # 固定宽度，确保所有图标占用相同空间
                          anchor=CENTER)
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="")

        # 中文标题 - 使用grid布局
        title_label = Label(btn_content,
                           text=step["title"],
                           font=("Microsoft YaHei UI", 13, "bold"),
                           fg="#0066ff" if index == 0 else "#ffffff",
                           bg="#ffffff" if index == 0 else "#004499",
                           anchor=W)
        title_label.grid(row=0, column=1, sticky="sw", pady=(0, 1))

        # 英文副标题 - 使用grid布局
        subtitle_label = Label(btn_content,
                              text=step["subtitle"],
                              font=("Consolas", 8, "bold"),
                              fg="#00aaff" if index == 0 else "#6699cc",
                              bg="#ffffff" if index == 0 else "#004499",
                              anchor=W)
        subtitle_label.grid(row=1, column=1, sticky="nw", pady=(1, 0))

        # 绑定点击事件
        step_names = ["Step1Files", "Step2Formula", "Step3Storage", "Step4PT", "Step5Output"]
        for widget in [btn_frame, btn_content, icon_label, title_label, subtitle_label]:
            widget.bind("<Button-1>", lambda e, idx=index: self.show_frame(step_names[idx]))
            widget.bind("<Enter>", lambda e, f=btn_outer: f.config(bg="#00ccff"))
            widget.bind("<Leave>", lambda e, f=btn_outer, idx=index: f.config(bg="#00aaff" if idx == self.current_step else "#0055dd"))

        self.nav_buttons.append({
            'outer': btn_outer,
            'frame': btn_frame,
            'content': btn_content,
            'icon': icon_label,
            'title': title_label,
            'subtitle': subtitle_label
        })

    def create_header(self):
        """创建顶部标题栏"""
        # 标题栏外框
        header_outer = Frame(self, bg="#00aaff")
        header_outer.place(x=280, y=0, width=1320, height=100)

        # 标题栏主体
        header = Frame(header_outer, bg="#0066ff")
        header.place(x=3, y=3, width=1314, height=94)

        # 内容容器
        header_content = Frame(header, bg="#0066ff")
        header_content.pack(fill=BOTH, expand=True, padx=30, pady=15)

        # 左侧：当前步骤信息
        left_section = Frame(header_content, bg="#0066ff")
        left_section.pack(side=LEFT, fill=Y)

        # 步骤编号
        self.step_num_label = Label(left_section,
                                    text="01",
                                    font=("Consolas", 36, "bold"),
                                    fg="#00ccff", bg="#0066ff")
        self.step_num_label.pack(side=LEFT, padx=(0, 20))

        # 步骤标题
        title_frame = Frame(left_section, bg="#0066ff")
        title_frame.pack(side=LEFT)

        self.step_title_label = Label(title_frame,
                                      text="机理选择",
                                      font=("Microsoft YaHei UI", 24, "bold"),
                                      fg="#ffffff", bg="#0066ff",
                                      anchor=W)
        self.step_title_label.pack(fill=X)

        self.step_subtitle_label = Label(title_frame,
                                         text="● MECHANISM SELECTION ●",
                                         font=("Consolas", 11, "bold"),
                                         fg="#00ccff", bg="#0066ff",
                                         anchor=W)
        self.step_subtitle_label.pack(fill=X)

        # 右侧：进度和状态
        right_section = Frame(header_content, bg="#0066ff")
        right_section.pack(side=RIGHT, padx=(30, 0))

        # 进度显示
        progress_frame = Frame(right_section, bg="#00ccff")
        progress_frame.pack()

        progress_inner = Frame(progress_frame, bg="#ffffff")
        progress_inner.pack(padx=3, pady=3)

        progress_content = Frame(progress_inner, bg="#ffffff")
        progress_content.pack(padx=20, pady=12)

        self.progress_label = Label(progress_content,
                                    text="步骤 1/5",
                                    font=("Microsoft YaHei UI", 14, "bold"),
                                    fg="#0066ff", bg="#ffffff")
        self.progress_label.pack()

        # 状态指示器
        status_frame = Frame(right_section, bg="#00ff7f")
        status_frame.pack(pady=(10, 0))

        status_inner = Frame(status_frame, bg="#ffffff")
        status_inner.pack(padx=3, pady=3)

        self.status_label = Label(status_inner,
                            text="● 系统就绪",
                            font=("Consolas", 11, "bold"),
                            fg="#00bb55", bg="#ffffff",
                            padx=15, pady=8)
        self.status_label.pack()

    def create_content_area(self):
        """创建主内容区"""
        # 内容区外框
        content_outer = Frame(self, bg="#99d6ff")
        content_outer.place(x=280, y=100, width=1320, height=850)

        # 内容区主体
        self.content_area = Frame(content_outer, bg="#e8f4fd")
        self.content_area.place(x=3, y=3, width=1314, height=844)

        # 创建滚动区域
        self.content_canvas = tk.Canvas(self.content_area, bg="#e8f4fd", highlightthickness=0)
        self.content_scrollbar = Scrollbar(self.content_area, orient=VERTICAL, command=self.content_canvas.yview)
        self.scrollable_frame = Frame(self.content_canvas, bg="#e8f4fd")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )

        self.content_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)

        self.content_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.content_scrollbar.pack(side=RIGHT, fill=Y)

        # 鼠标滚轮绑定
        def _on_mousewheel(event):
            self.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.content_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def show_frame(self, frame_name):
        """显示指定框架"""
        # 在切换前，先验证并保存当前步骤的数据
        if hasattr(self, 'current_step') and self.current_step < len(self.step_names):
            current_frame_name = self.step_names[self.current_step]
            current_frame = self.frames.get(current_frame_name)
            if current_frame and hasattr(current_frame, 'validate'):
                # 调用validate保存数据（不阻止切换）
                try:
                    current_frame.validate()
                except:
                    pass  # 即使验证失败也允许切换

        frame = self.frames[frame_name]
        frame.tkraise()

        # 调用on_show回调
        if hasattr(frame, 'on_show'):
            frame.on_show()

        # 更新当前步骤
        if frame_name in self.step_names:
            self.current_step = self.step_names.index(frame_name)

            # 更新侧边栏导航按钮状态
            for i, btn in enumerate(self.nav_buttons):
                is_active = (i == self.current_step)
                btn['outer'].config(bg="#00aaff" if is_active else "#0055dd")
                btn['frame'].config(bg="#ffffff" if is_active else "#004499")
                btn['content'].config(bg="#ffffff" if is_active else "#004499")
                btn['icon'].config(fg="#0066ff" if is_active else "#00aaff",
                                 bg="#ffffff" if is_active else "#004499")
                btn['title'].config(fg="#0066ff" if is_active else "#ffffff",
                                  bg="#ffffff" if is_active else "#004499")
                btn['subtitle'].config(fg="#00aaff" if is_active else "#6699cc",
                                     bg="#ffffff" if is_active else "#004499")

            # 更新顶部标题栏
            step_info = [
                ("01", "机理选择", "MECHANISM SELECTION"),
                ("02", "配方设计", "FORMULA DESIGN"),
                ("03", "贮存参数", "STORAGE PARAMETERS"),
                ("04", "工况配置", "CONDITION CONFIGURATION"),
                ("05", "结果输出", "RESULTS OUTPUT")
            ]

            num, title, subtitle = step_info[self.current_step]
            self.step_num_label.config(text=num)
            self.step_title_label.config(text=title)
            self.step_subtitle_label.config(text=f"● {subtitle} ●")
            self.progress_label.config(text=f"步骤 {self.current_step + 1}/5")

if __name__ == "__main__":
    app = TechBlueWizardApp()
    app.mainloop()
