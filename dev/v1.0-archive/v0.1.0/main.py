#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR字准确率对比工具 - 历史版本(v0.1.0)
基于jieba分词器的单一分词器版本

该版本功能：
- 基于jieba的中文分词和字准确率计算
- 图形界面文件选择和拖拽排序
- 语气词过滤功能
- 结果导出为TXT/CSV格式

作者：CER-MatchingTools项目组
版本：V0.1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
import jiwer
from functools import partial
from utils import ASRMetrics


class ASRComparisonTool:
    """
    ASR字准确率对比工具主类 - v0.1.0版本
    
    提供基于jieba分词器的字准确率计算工具
    主要功能包括：
    - 文件选择和管理
    - 字准确率计算（基于jieba）
    - 结果展示和导出
    """
    
    def __init__(self, root):
        """
        初始化ASR对比工具界面
        
        Args:
            root: tkinter主窗口对象
        """
        # 主窗口设置
        self.root = root
        self.root.title("ASR字准确率对比工具")
        self.root.geometry("800x600")
        # 设置窗口大小可调整，支持最大化
        self.root.resizable(True, True)
        # 设置最小窗口大小，确保界面完整显示
        self.root.minsize(800, 600)
        
        # 数据存储变量
        self.asr_files = []  # ASR转写结果文件列表
        self.ref_files = []  # 标注文件列表
        self.file_pairs = []  # 文件配对信息
        self.results = []  # 计算结果列表
        
        # 创建主框架分为上下两部分
        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)  # 固定上部区域高度
        
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # 下部结果区域自动扩展
        
        # 控制变量设置
        self.filter_fillers = tk.BooleanVar(value=False)  # 语气词过滤开关
        
        # UI辅助变量
        self.tooltip_window = None  # 提示框窗口对象
        
        # 初始化UI组件
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化用户界面
        创建所有GUI组件并设置布局
        """
        # 上半部分 - 文件选择区域
        # 创建包含左右两帧和底部按钮的上半部分框架
        self.file_area_frame = ttk.Frame(self.top_frame)
        self.file_area_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建一个固定比例的网格系统，确保左右框架宽度一致
        self.file_area_frame.columnconfigure(0, weight=1, uniform="group1")  # 左侧列
        self.file_area_frame.columnconfigure(1, weight=1, uniform="group1")  # 右侧列
        
        self.left_frame = ttk.LabelFrame(self.file_area_frame, text="ASR转换结果文件")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.right_frame = ttk.LabelFrame(self.file_area_frame, text="标注文件")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # ASR文件选择按钮和列表
        self.asr_btn = ttk.Button(self.left_frame, text="选择ASR文件", command=self.select_asr_files)
        self.asr_btn.pack(pady=5)
        
        # 创建一个frame来容纳canvas，以便控制高度
        self.asr_canvas_frame = ttk.Frame(self.left_frame)
        self.asr_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设置canvas的高度和宽度
        self.asr_canvas = tk.Canvas(self.asr_canvas_frame, bg="white", height=160, width=350)  # 设置固定宽度
        self.asr_canvas.pack(fill=tk.BOTH, expand=True)
        self.asr_canvas.bind("<ButtonPress-1>", self.on_press)
        self.asr_canvas.bind("<B1-Motion>", self.on_drag)
        self.asr_canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # 标注文件选择按钮和列表
        self.ref_btn = ttk.Button(self.right_frame, text="选择标注文件", command=self.select_ref_files)
        self.ref_btn.pack(pady=5)
        
        # 创建一个frame来容纳canvas，以便控制高度
        self.ref_canvas_frame = ttk.Frame(self.right_frame)
        self.ref_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设置canvas的高度和宽度，确保与左侧一致
        self.ref_canvas = tk.Canvas(self.ref_canvas_frame, bg="white", height=160, width=350)  # 设置固定宽度
        self.ref_canvas.pack(fill=tk.BOTH, expand=True)
        self.ref_canvas.bind("<ButtonPress-1>", self.on_press)
        self.ref_canvas.bind("<B1-Motion>", self.on_drag)
        self.ref_canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # 创建单一控制框架，将统计按钮和过滤勾选框放在同一行
        self.control_frame = ttk.Frame(self.top_frame)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        # 创建按钮容器框架
        self.btn_container = ttk.Frame(self.control_frame)
        self.btn_container.pack(side=tk.TOP, fill=tk.X)
        
        # 统计按钮 - 居中对齐
        self.calculate_btn = ttk.Button(self.btn_container, text="开始统计", command=self.calculate_accuracy, width=15)
        self.calculate_btn.pack(side=tk.TOP, pady=5)
        
        # 语气词过滤开关 - 调整位置到右侧，并与"开始统计"按钮垂直居中对齐
        self.filter_frame = ttk.Frame(self.control_frame)
        # 使用place布局，设置rely=0.5使其垂直居中，anchor=E使其靠右对齐
        self.filter_frame.place(relx=1.0, rely=0.5, anchor=tk.E, x=-20)
        
        self.filter_check = ttk.Checkbutton(
            self.filter_frame, 
            text="语气词过滤", 
            variable=self.filter_fillers,
            onvalue=True,
            offvalue=False
        )
        self.filter_check.pack(side=tk.LEFT)
        
        # 为语气词过滤开关添加提示信息
        filter_tooltip = tk.Label(self.filter_frame, text="?", font=("Arial", 9, "bold"), fg="blue")
        filter_tooltip.pack(side=tk.LEFT, padx=3)
        
        # 鼠标悬停显示提示信息
        def show_tooltip(event):
            # 避免多个提示框出现，如果已存在则不创建新的
            if self.tooltip_window:
                return
                
            # 创建提示框
            self.tooltip_window = tk.Toplevel(self.root)
            self.tooltip_window.wm_overrideredirect(True)  # 无边框窗口
            self.tooltip_window.geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            tooltip_text = '开启此选项后，计算字准确率时将会过滤掉"嗯"、"啊"、"呢"等语气词。\n这可以使CER计算更准确地反映实际语义内容。'
            label = tk.Label(self.tooltip_window, text=tooltip_text, justify=tk.LEFT, 
                             background="#FFFFCC", relief=tk.SOLID, borderwidth=1, padx=5, pady=5)
            label.pack()
            
            # 构建虚拟边界框（30x30像素的区域）
            # 获取问号标签的位置和尺寸
            x = filter_tooltip.winfo_rootx()
            y = filter_tooltip.winfo_rooty()
            w = filter_tooltip.winfo_width()
            h = filter_tooltip.winfo_height()
            
            # 计算中心点
            center_x = x + w/2
            center_y = y + h/2
            
            # 边界框的边界
            self.tooltip_boundary = {
                'x1': center_x - 15,  # 左边界
                'y1': center_y - 15,  # 上边界
                'x2': center_x + 15,  # 右边界
                'y2': center_y + 15   # 下边界
            }
            
            # 绑定鼠标移动事件
            self.root.bind("<Motion>", check_tooltip_boundary)
            
        def check_tooltip_boundary(event):
            """检查鼠标是否在提示框边界内"""
            if self.tooltip_window:
                # 获取鼠标当前位置
                x, y = event.x_root, event.y_root
                
                # 检查是否在30x30的边界框内
                if (x < self.tooltip_boundary['x1'] or 
                    x > self.tooltip_boundary['x2'] or 
                    y < self.tooltip_boundary['y1'] or 
                    y > self.tooltip_boundary['y2']):
                    # 如果鼠标移出边界框，销毁提示框
                    self.tooltip_window.destroy()
                    self.tooltip_window = None
                    self.root.unbind("<Motion>")
        
        filter_tooltip.bind("<Enter>", show_tooltip)
        
        # 下半部分 - 结果显示区域
        self.result_frame = ttk.LabelFrame(self.bottom_frame, text="字准确率统计结果")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建一个frame来容纳treeview，以便控制高度
        self.result_tree_frame = ttk.Frame(self.result_frame)
        self.result_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 结果展示表格，设置高度 - 增加显示行数
        columns = ("原始文件", "标注文件", "ASR字数", "标注字数", "字准确率", "过滤语气词")
        self.result_tree = ttk.Treeview(self.result_tree_frame, columns=columns, show="headings", height=8)  # 原来是12行，现在减少到8行
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120, anchor="center")
        
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        # 创建导出按钮的容器框架用于居中对齐
        self.export_frame = ttk.Frame(self.bottom_frame)
        self.export_frame.pack(fill=tk.X, pady=10)
        
        # 导出按钮 - 居中对齐
        self.export_btn = ttk.Button(self.export_frame, text="导出结果", command=self.export_results, width=15)
        self.export_btn.pack(side=tk.TOP, pady=0)
        
        # 设置拖拽变量
        self.drag_data = {"x": 0, "y": 0, "item": None, "canvas": None}
    
    def select_asr_files(self):
        files = filedialog.askopenfilenames(title="选择ASR文件", filetypes=[("文本文件", "*.txt")])
        if files:
            self.asr_files = list(files)
            self.update_canvas_items(self.asr_canvas, self.asr_files)
    
    def select_ref_files(self):
        files = filedialog.askopenfilenames(title="选择标注文件", filetypes=[("文本文件", "*.txt")])
        if files:
            self.ref_files = list(files)
            self.update_canvas_items(self.ref_canvas, self.ref_files)
    
    def update_canvas_items(self, canvas, file_list):
        canvas.delete("all")
        y_pos = 10
        canvas_width = canvas.winfo_width()
        
        # 确保canvas宽度至少有最小值，避免初始化时winfo_width返回1的问题
        if canvas_width < 10:
            canvas_width = 350  # 使用之前设置的默认宽度
            
        for i, file_path in enumerate(file_list):
            file_name = os.path.basename(file_path)
            # 使用固定宽度创建矩形，确保两边宽度一致
            item_width = canvas_width - 20  # 左右各留10像素边距
            item_id = canvas.create_rectangle(10, y_pos, 10 + item_width, y_pos+30, 
                                            fill="lightblue", tags=f"file_{i}")
            canvas.create_text(20, y_pos+15, text=file_name, anchor="w", tags=f"file_{i}")
            canvas.itemconfig(item_id, tags=(f"file_{i}", file_path))
            y_pos += 40
    
    def on_press(self, event):
        canvas = event.widget
        closest = canvas.find_closest(event.x, event.y)
        if closest:
            tags = canvas.gettags(closest)
            if tags and tags[0].startswith("file_"):
                self.drag_data["item"] = closest
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.drag_data["canvas"] = canvas
    
    def on_drag(self, event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            canvas = self.drag_data["canvas"]
            item = self.drag_data["item"]
            
            canvas.move(item, 0, dy)
            # 同时移动文本标签
            tags = canvas.gettags(item)
            for tag in tags:
                if tag.startswith("file_"):
                    text_items = canvas.find_withtag(tag)
                    for text_item in text_items:
                        if text_item != item:
                            canvas.move(text_item, 0, dy)
            
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def on_release(self, event):
        self.drag_data["item"] = None
        self.drag_data["canvas"] = None
    
    def get_file_order(self, canvas):
        items = canvas.find_all()
        file_items = {}
        
        for item in items:
            tags = canvas.gettags(item)
            if tags and tags[0].startswith("file_"):
                coords = canvas.coords(item)
                if len(coords) >= 2:  # 确保有足够的坐标信息
                    y_pos = coords[1]  # 获取y坐标
                    file_path = tags[1] if len(tags) > 1 else None
                    if file_path:
                        file_items[y_pos] = file_path
        
        # 按y坐标排序
        return [file_items[y] for y in sorted(file_items.keys())]
    
    def calculate_accuracy(self):
        # 清空结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.results = []
        
        # 获取排序后的文件列表
        sorted_asr_files = self.get_file_order(self.asr_canvas)
        sorted_ref_files = self.get_file_order(self.ref_canvas)
        
        # 检查文件数量是否匹配
        if len(sorted_asr_files) != len(sorted_ref_files):
            messagebox.showerror("错误", "ASR文件和标注文件数量不匹配！")
            return
        
        # 获取语气词过滤设置
        filter_fillers = self.filter_fillers.get()
        
        # 逐对计算字准确率
        for asr_file, ref_file in zip(sorted_asr_files, sorted_ref_files):
            try:
                # 读取文件内容
                asr_text = self.read_file_with_multiple_encodings(asr_file)
                ref_text = self.read_file_with_multiple_encodings(ref_file)
                
                # 使用ASRMetrics计算各项指标，传入语气词过滤设置
                metrics = ASRMetrics.calculate_detailed_metrics(ref_text, asr_text, filter_fillers)
                
                # 获取结果
                accuracy = metrics['accuracy']
                ref_chars = metrics['ref_length']
                asr_chars = metrics['hyp_length']
                
                result = {
                    "asr_file": os.path.basename(asr_file),
                    "ref_file": os.path.basename(ref_file),
                    "asr_chars": asr_chars,
                    "ref_chars": ref_chars,
                    "accuracy": accuracy,
                    "details": metrics,  # 保存详细指标供后续使用
                    "filter_fillers": filter_fillers  # 记录是否应用了语气词过滤
                }
                
                self.results.append(result)
                
                # 添加到结果表格
                self.result_tree.insert("", "end", values=(
                    result["asr_file"],
                    result["ref_file"],
                    result["asr_chars"],
                    result["ref_chars"],
                    f"{result['accuracy']:.4f}",
                    "是" if filter_fillers else "否"
                ))
                
            except Exception as e:
                messagebox.showerror("错误", f"处理文件时出错: {str(e)}")
    
    def read_file_with_multiple_encodings(self, file_path):
        """
        尝试使用多种编码方式读取文件内容
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            str: 文件内容
            
        Raises:
            Exception: 如果所有编码方式都失败则抛出异常
        """
        # 尝试的编码格式列表
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'ansi']
        
        # 存储可能的异常
        errors = []
        
        # 依次尝试不同的编码
        for encoding in encodings:
            try:
                # 对于 'ansi'，我们使用系统默认编码
                if encoding == 'ansi':
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                else:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                return content
            except UnicodeDecodeError as e:
                # 记录错误但继续尝试其他编码
                errors.append((encoding, str(e)))
                continue
        
        # 如果所有编码都失败，抛出异常
        error_msg = "无法解码文件，尝试了以下编码：\n"
        for encoding, error in errors:
            error_msg += f"- {encoding}: {error}\n"
        raise Exception(error_msg)
    
    def export_results(self):
        if not self.results:
            messagebox.showinfo("提示", "没有可导出的结果！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv")],
            title="导出结果"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                # 导出为CSV格式
                df = pd.DataFrame(self.results)
                # 只保留基本字段和过滤状态
                df = df[['asr_file', 'ref_file', 'asr_chars', 'ref_chars', 'accuracy', 'filter_fillers']]
                # 将过滤状态标记为更易读的文本
                df['filter_fillers'] = df['filter_fillers'].apply(lambda x: "是" if x else "否")
                # 重命名列名
                df.columns = ['ASR文件', '标注文件', 'ASR字数', '标注字数', '字准确率', '是否过滤语气词']
                df.to_csv(file_path, index=False, encoding='utf-8')
            else:
                # 导出为TXT格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("原始文件\t标注文件\tASR字数\t标注字数\t字准确率\t是否过滤语气词\n")
                    for result in self.results:
                        filter_status = "是" if result.get('filter_fillers', False) else "否"
                        f.write(f"{result['asr_file']}\t{result['ref_file']}\t"
                                f"{result['asr_chars']}\t{result['ref_chars']}\t"
                                f"{result['accuracy']:.4f}\t{filter_status}\n")
            
            messagebox.showinfo("成功", f"结果已导出到 {file_path}")
        
        except Exception as e:
            messagebox.showerror("错误", f"导出结果时出错: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASRComparisonTool(root)
    root.mainloop() 