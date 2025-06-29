#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI主窗口
小说整理系统的主界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import sys
import os

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import ConfigManager
from core.workflow_manager import WorkflowManager

class MainApplication:
    """主应用程序类"""
    
    def __init__(self):
        """初始化主应用"""        # 创建主窗口
        self.root = tk.Tk()
        
        # 初始化配置管理器
        try:
            self.config_manager = ConfigManager()
            self.gui_config = self.config_manager.get_gui_config()
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置失败: {e}")
            self.gui_config = self._get_default_gui_config()
        
        # 初始化工作流管理器
        try:
            self.workflow_manager = WorkflowManager(
                config_manager=self.config_manager,
                progress_callback=self._on_workflow_progress
            )
        except Exception as e:
            messagebox.showerror("初始化错误", f"工作流管理器初始化失败: {e}")
            self.workflow_manager = None
        
        # 初始化变量
        self.work_dir = tk.StringVar()
        self.status_text = tk.StringVar(value="系统就绪")
        self.progress_var = tk.DoubleVar()
        
        # 设置窗口
        self._setup_window()
        
        # 创建界面
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        
        # 初始化状态
        self._init_state()
    
    def _get_default_gui_config(self):
        """获取默认GUI配置"""
        return {
            'window': {
                'title': '小说整理系统 v1.0',
                'width': 1000,
                'height': 700,
                'min_width': 800,
                'min_height': 600
            },
            'theme': {
                'font_family': '微软雅黑',
                'font_size': 9
            }
        }
    
    def _setup_window(self):
        """设置主窗口"""
        window_config = self.gui_config.get('window', {})
        
        # 设置标题
        self.root.title(window_config.get('title', '小说整理系统'))
        
        # 设置大小
        width = window_config.get('width', 1000)
        height = window_config.get('height', 700)
        self.root.geometry(f"{width}x{height}")
        
        # 设置最小大小
        min_width = window_config.get('min_width', 800)
        min_height = window_config.get('min_height', 600)
        self.root.minsize(min_width, min_height)
        
        # 居中显示
        self._center_window()
        
        # 设置图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')  # 暂时注释，稍后可添加图标
            pass
        except:
            pass
    
    def _center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        self._create_main_frame()
        
        # 创建工作目录选择区域
        self._create_work_dir_frame()
        
        # 创建工作流面板区域
        self._create_workflow_frame()
        
        # 创建状态监控区域
        self._create_status_frame()
        
        # 创建日志输出区域
        self._create_log_frame()
        
        # 创建底部按钮区域
        self._create_bottom_frame()
    
    def _create_main_frame(self):
        """创建主框架"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)  # 日志区域可扩展
    
    def _create_work_dir_frame(self):
        """创建工作目录选择区域"""
        dir_frame = ttk.LabelFrame(self.main_frame, text="工作目录", padding="5")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # 目录标签和输入框
        ttk.Label(dir_frame, text="小说库目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.work_dir, width=50)
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_btn = ttk.Button(dir_frame, text="浏览", command=self._browse_directory)
        self.browse_btn.grid(row=0, column=2, sticky=tk.W)
    
    def _create_workflow_frame(self):
        """创建工作流面板区域"""
        workflow_frame = ttk.LabelFrame(self.main_frame, text="工作流程", padding="5")
        workflow_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 配置网格
        for i in range(4):
            workflow_frame.columnconfigure(i, weight=1)
        
        # 工作流1: 初始化
        self._create_init_panel(workflow_frame, 0)
        
        # 工作流2: 文件导入
        self._create_import_panel(workflow_frame, 1)        
        # 工作流3: 编码修复
        self._create_encoding_panel(workflow_frame, 2)
        
        # 工作流4: 自动分类
        self._create_classification_panel(workflow_frame, 3)
    
    def _create_init_panel(self, parent, column):
        """创建初始化面板"""
        frame = ttk.LabelFrame(parent, text="1. 初始化", padding="5")
        frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2)
        
        self.init_status = ttk.Label(frame, text="状态: 未初始化", foreground="orange")
        self.init_status.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.init_btn = ttk.Button(frame, text="创建目录结构", command=self._on_init_clicked)
        self.init_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.clear_library_btn = ttk.Button(frame, text="清空小说库", command=self._on_clear_library_clicked)
        self.clear_library_btn.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        frame.columnconfigure(0, weight=1)
    
    def _create_import_panel(self, parent, column):
        """创建文件导入面板"""
        frame = ttk.LabelFrame(parent, text="2. 文件导入", padding="5")
        frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2)
        
        self.import_path = tk.StringVar()
        
        self.import_entry = ttk.Entry(frame, textvariable=self.import_path, width=15)
        self.import_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        self.import_browse_btn = ttk.Button(frame, text="选择路径", command=self._browse_import_path)
        self.import_browse_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        self.import_status = ttk.Label(frame, text="发现: 0个文件")
        self.import_status.grid(row=2, column=0, sticky=tk.W, pady=(0, 2))
        
        self.import_btn = ttk.Button(frame, text="开始导入", command=self._on_import_clicked)
        self.import_btn.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        frame.columnconfigure(0, weight=1)
    
    def _create_encoding_panel(self, parent, column):
        """创建编码修复面板"""
        frame = ttk.LabelFrame(parent, text="3. 编码修复", padding="5")
        frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2)
        
        self.encoding_scan_btn = ttk.Button(frame, text="扫描编码问题", command=self._on_encoding_scan_clicked)
        self.encoding_scan_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        self.encoding_status = ttk.Label(frame, text="发现: 0个问题")
        self.encoding_status.grid(row=1, column=0, sticky=tk.W, pady=(0, 2))
        
        # 备份选项
        self.backup_var = tk.BooleanVar(value=True)
        self.backup_check = ttk.Checkbutton(frame, text="修复前备份", variable=self.backup_var)
        self.backup_check.grid(row=2, column=0, sticky=tk.W, pady=(0, 2))
        
        self.encoding_fix_btn = ttk.Button(frame, text="修复全部", command=self._on_encoding_fix_clicked)
        self.encoding_fix_btn.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        frame.columnconfigure(0, weight=1)
    
    def _create_classification_panel(self, parent, column):
        """创建自动分类面板"""
        frame = ttk.LabelFrame(parent, text="4. 自动分类", padding="5")
        frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2)
        
        # 批次大小设置
        batch_frame = ttk.Frame(frame)
        batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        ttk.Label(batch_frame, text="批次大小:").grid(row=0, column=0, sticky=tk.W)
        self.batch_size = tk.StringVar(value="50")
        batch_spinbox = ttk.Spinbox(batch_frame, from_=10, to=500, width=8, textvariable=self.batch_size)
        batch_spinbox.grid(row=0, column=1, sticky=tk.E)
        
        batch_frame.columnconfigure(1, weight=1)
        
        # 文本提取配置
        text_config_frame = ttk.LabelFrame(frame, text="文本提取配置", padding="3")
        text_config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 4))
        
        # 开头片段长度
        begin_frame = ttk.Frame(text_config_frame)
        begin_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=1)
        ttk.Label(begin_frame, text="开头片段长度:").grid(row=0, column=0, sticky=tk.W)
        self.begin_chars = tk.StringVar(value="3000")
        begin_spinbox = ttk.Spinbox(begin_frame, from_=1000, to=10000, width=8, textvariable=self.begin_chars)
        begin_spinbox.grid(row=0, column=1, sticky=tk.E)
        begin_frame.columnconfigure(1, weight=1)
        
        # 随机片段数量
        fragment_count_frame = ttk.Frame(text_config_frame)
        fragment_count_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=1)
        ttk.Label(fragment_count_frame, text="随机片段数量:").grid(row=0, column=0, sticky=tk.W)
        self.fragment_count = tk.StringVar(value="3")
        fragment_count_spinbox = ttk.Spinbox(fragment_count_frame, from_=0, to=10, width=8, textvariable=self.fragment_count)
        fragment_count_spinbox.grid(row=0, column=1, sticky=tk.E)
        fragment_count_frame.columnconfigure(1, weight=1)
        
        # 随机片段大小
        fragment_size_frame = ttk.Frame(text_config_frame)
        fragment_size_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=1)
        ttk.Label(fragment_size_frame, text="随机片段大小:").grid(row=0, column=0, sticky=tk.W)
        self.fragment_size = tk.StringVar(value="500")
        fragment_size_spinbox = ttk.Spinbox(fragment_size_frame, from_=100, to=2000, width=8, textvariable=self.fragment_size)
        fragment_size_spinbox.grid(row=0, column=1, sticky=tk.E)
        fragment_size_frame.columnconfigure(1, weight=1)
        
        text_config_frame.columnconfigure(0, weight=1)
        
        self.classification_status = ttk.Label(frame, text="配置: 已加载")
        self.classification_status.grid(row=2, column=0, sticky=tk.W, pady=(0, 2))
        
        self.classification_btn = ttk.Button(frame, text="开始分类", command=self._on_classification_clicked)
        self.classification_btn.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        self.config_btn = ttk.Button(frame, text="编辑分类配置", command=self._on_edit_config_clicked)
        self.config_btn.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        frame.columnconfigure(0, weight=1)
    
    def _create_status_frame(self):
        """创建状态监控区域"""
        status_frame = ttk.LabelFrame(self.main_frame, text="状态监控", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # 状态信息
        info_frame = ttk.Frame(status_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="状态:", font=('Microsoft YaHei UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.status_label = ttk.Label(info_frame, textvariable=self.status_text, font=('Microsoft YaHei UI', 9))
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # 进度条
        progress_frame = ttk.Frame(status_frame)
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        progress_frame.columnconfigure(1, weight=1)
        
        ttk.Label(progress_frame, text="进度:", font=('Microsoft YaHei UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style='TProgressbar')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), ipady=2)
        
        self.progress_label = ttk.Label(progress_frame, text="0%", font=('Microsoft YaHei UI', 9))
        self.progress_label.grid(row=0, column=2, sticky=tk.W)
    
    def _create_log_frame(self):
        """创建日志输出区域"""
        log_frame = ttk.LabelFrame(self.main_frame, text="日志输出", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
    def _create_bottom_frame(self):
        """创建底部按钮区域"""
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        # 左对齐按钮（统计功能）
        left_button_frame = ttk.Frame(bottom_frame)
        left_button_frame.pack(side=tk.LEFT)
        
        self.statistics_btn = ttk.Button(left_button_frame, text="📊 统计报告", command=self._show_statistics)
        self.statistics_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 右对齐按钮
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.save_log_btn = ttk.Button(button_frame, text="保存日志", command=self._save_log)
        self.save_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_log_btn = ttk.Button(button_frame, text="清空日志", command=self._clear_log)
        self.clear_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.exit_btn = ttk.Button(button_frame, text="退出", command=self._on_exit)
        self.exit_btn.pack(side=tk.LEFT)
    
    def _bind_events(self):
        """绑定事件"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        
        # 工作目录变化事件
        self.work_dir.trace('w', self._on_work_dir_changed)
        
        # 文本提取配置变化事件
        self.begin_chars.trace('w', self._on_text_config_changed)
        self.fragment_count.trace('w', self._on_text_config_changed)
        self.fragment_size.trace('w', self._on_text_config_changed)
    
    def _init_state(self):
        """初始化状态"""
        # 记录初始日志
        self.log("系统启动完成")
        self.log("配置文件加载成功")
        
        # 自动设置默认工作目录
        self._set_default_work_dir()
        
        # 加载文本提取配置
        self._load_text_extraction_config()
        
        # 检查工作目录
        self._check_work_dir()
    
    def _set_default_work_dir(self):
        """设置默认工作目录"""
        try:
            # 获取默认工作目录
            default_work_dir = self.config_manager.get_default_work_dir()
            
            # 确保工作目录存在
            actual_work_dir = self.config_manager.ensure_work_dir_exists(default_work_dir)
            
            # 设置到界面
            self.work_dir.set(actual_work_dir)
            
            self.log(f"默认工作目录已设置: {actual_work_dir}")
            
        except Exception as e:
            self.log(f"设置默认工作目录失败: {e}")
            # 如果失败，使用项目根目录下的小说库作为默认值
            fallback_dir = project_root / "小说库"
            try:
                fallback_dir.mkdir(parents=True, exist_ok=True)
                self.work_dir.set(str(fallback_dir))
                self.log(f"使用备用工作目录: {fallback_dir}")
            except Exception as e2:
                self.log(f"创建备用工作目录也失败: {e2}")
    
    # 事件处理方法
    def _browse_directory(self):
        """浏览工作目录"""
        # 设置默认路径为项目根目录
        default_path = project_root
        
        directory = filedialog.askdirectory(
            title="选择小说库目录",
            initialdir=str(default_path)
        )
        if directory:
            self.work_dir.set(directory)
    
    def _browse_import_path(self):
        """浏览导入路径"""
        # 设置默认路径为novel_gui.py所在的目录（项目根目录）
        default_path = project_root
        
        directory = filedialog.askdirectory(
            title="选择要导入的文件目录",
            initialdir=str(default_path)
        )
        if directory:
            self.import_path.set(directory)
            self._scan_import_files()
    
    def _scan_import_files(self):
        """扫描导入文件"""
        import_dir = self.import_path.get()
        if not import_dir:
            return
        
        try:
            txt_files = list(Path(import_dir).rglob("*.txt"))
            self.import_status.config(text=f"发现: {len(txt_files)}个文件")
            self.log(f"扫描导入目录: 发现 {len(txt_files)} 个txt文件")
        except Exception as e:
            self.log(f"扫描导入目录失败: {e}")
    
    def _on_work_dir_changed(self, *args):
        """工作目录变化时的处理"""
        work_dir = self.work_dir.get()
        
        # 更新工作流管理器的库路径
        if self.workflow_manager:
            self.workflow_manager.set_library_path(work_dir)
        
        self._check_work_dir()
    
    def _check_work_dir(self):
        """检查工作目录状态"""
        work_dir = self.work_dir.get()
        if not work_dir:
            self.init_status.config(text="状态: 未选择目录", foreground="gray")
            return

        work_path = Path(work_dir)
        if not work_path.exists():
            self.init_status.config(text="状态: 目录不存在", foreground="red")
            return
        
        # 检查是否已初始化
        required_dirs = ["00-待分类", "00-二次确认"]
        if all((work_path / d).exists() for d in required_dirs):
            self.init_status.config(text="状态: 已初始化", foreground="green")
            self.log(f"工作目录已就绪: {work_dir}")
        else:
            self.init_status.config(text="状态: 未初始化", foreground="orange")
            self.log(f"工作目录需要初始化: {work_dir}")
    
    def _on_edit_config_clicked(self):
        """编辑配置按钮点击，使用系统默认程序打开配置文件"""
        try:
            # 修正: 直接访问正确的属性 `keywords_config_path`
            config_path = self.config_manager.keywords_config_path
            if not config_path or not Path(config_path).exists():
                messagebox.showerror("错误", f"配置文件不存在:\n{config_path}")
                self.log(f"错误: 配置文件 'keywords_config.yaml' 未找到。")
                return
            
            # 使用os.startfile在Windows上用默认程序打开
            os.startfile(config_path)
            self.log(f"已调用系统默认编辑器打开配置文件: {config_path}")
            
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开配置文件:\n{e}")
            self.log(f"错误: 打开配置文件失败 - {e}")

    # 工作流按钮事件处理
    def _on_init_clicked(self):
        """初始化按钮点击"""
        if not self.workflow_manager:
            self.log("工作流管理器未初始化")
            return
        
        work_dir = self.work_dir.get()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择小说库目录")
            return
        
        self.log("开始初始化小说库目录...")
        self.status_text.set("正在初始化...")
        
        # 异步执行初始化工作流
        import threading
        def run_init():
            result = self.workflow_manager.execute_workflow_sync(
                'initialization', 
                library_path=work_dir
            )
            self.root.after(100, lambda: self._on_workflow_completed('initialization', result))
        
        threading.Thread(target=run_init, daemon=True).start()
    
    def _on_import_clicked(self):
        """导入按钮点击"""
        if not self.workflow_manager:
            self.log("工作流管理器未初始化")
            return
        
        source_path = self.import_path.get()
        if not source_path:
            messagebox.showwarning("警告", "请先选择要导入的文件目录")
            return
        
        work_dir = self.work_dir.get()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择小说库目录")
            return
        
        self.log("开始导入文件...")
        self.status_text.set("正在导入文件...")
        
        # 异步执行文件导入工作流
        import threading
        def run_import():
            result = self.workflow_manager.execute_workflow_sync(
                'file_import',
                source_path=source_path
            )
            self.root.after(100, lambda: self._on_workflow_completed('file_import', result))        
        threading.Thread(target=run_import, daemon=True).start()
    
    def _on_encoding_scan_clicked(self):
        """编码扫描按钮点击"""
        if not self.workflow_manager:
            self.log("工作流管理器未初始化")
            return
        
        work_dir = self.work_dir.get()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择小说库目录")
            return
        
        self.log("开始扫描编码问题...")
        self.status_text.set("正在扫描编码...")
        
        # 异步执行编码扫描
        import threading
        def run_scan():
            try:
                # 创建编码修复工作流实例进行扫描
                from workflows.encoding_fix import EncodingFixWorkflow
                encoding_workflow = EncodingFixWorkflow(
                    lambda progress, message: self.root.after(100, lambda: self._on_workflow_progress('encoding_scan', progress, message))
                )
                
                scan_result = encoding_workflow.scan_encoding_issues(
                    str(Path(work_dir) / "00-待分类"),
                    recursive=False
                )
                
                # 更新界面显示
                if scan_result["success"]:
                    problem_count = len(scan_result["problem_files"])
                    self.root.after(100, lambda: self.encoding_status.config(
                        text=f"发现: {problem_count}个问题"
                    ))
                    self.root.after(100, lambda: self.log(f"编码扫描完成，发现 {problem_count} 个问题"))
                    
                    # 显示报告文件位置
                    if "report_file" in scan_result:
                        self.root.after(100, lambda: self.log(f"扫描报告已保存: {scan_result['report_file']}"))
                        
                    # 显示问题清单保存信息
                    if problem_count > 0:
                        self.root.after(100, lambda: self.log("问题文件清单已保存，修复时将使用此清单"))
                    
                    # 更新状态，指示可以修复
                    self.root.after(100, lambda: self._update_fix_button_state(problem_count > 0))
                else:
                    error_msg = ", ".join(scan_result.get("errors", ["未知错误"]))
                    self.root.after(100, lambda: self.log(f"编码扫描失败: {error_msg}"))
                    self.root.after(100, lambda: self._update_fix_button_state(False))
                    
                # 重置状态
                self.root.after(100, lambda: self.status_text.set("系统就绪"))
                    
            except Exception as e:
                self.root.after(100, lambda: self.log(f"编码扫描异常: {str(e)}"))
                self.root.after(100, lambda: self.status_text.set("扫描失败"))
                import traceback
                traceback.print_exc()
        
        threading.Thread(target=run_scan, daemon=True).start()
    
    def _on_encoding_fix_clicked(self):
        """编码修复按钮点击"""
        if not self.workflow_manager:
            self.log("工作流管理器未初始化")
            return
        
        work_dir = self.work_dir.get()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择小说库目录")
            return
        
        # 检查是否存在问题文件清单
        from pathlib import Path
        problem_list_file = Path(work_dir) / "logs" / "encoding_problems_current.json"
        use_problem_list = problem_list_file.exists()
        
        if use_problem_list:
            self.log("发现问题文件清单，将使用清单进行修复...")
        else:
            self.log("未发现问题文件清单，将重新扫描后修复...")
        
        self.status_text.set("正在修复编码...")
        
        # 异步执行编码修复工作流
        import threading
        def run_fix():
            result = self.workflow_manager.execute_workflow_sync(
                'encoding_fix',
                create_backup=self.backup_var.get(),
                use_problem_list=use_problem_list
            )
            self.root.after(100, lambda: self._on_encoding_fix_completed(result))
        
        threading.Thread(target=run_fix, daemon=True).start()
    
    def _on_classification_clicked(self):
        """分类按钮点击"""
        if not self.workflow_manager:
            self.log("工作流管理器未初始化")
            return
        
        work_dir = self.work_dir.get()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择小说库目录")
            return
        
        try:
            batch_size = int(self.batch_size.get())
        except ValueError:
            messagebox.showerror("错误", "批次大小必须是数字")
            return
        
        self.log(f"开始自动分类 (批次大小: {batch_size})...")
        self.status_text.set("正在自动分类...")
        
        # 异步执行自动分类工作流
        import threading
        def run_classification():
            result = self.workflow_manager.execute_workflow_sync(
                'auto_classification',
                max_files=batch_size
            )
            self.root.after(100, lambda: self._on_workflow_completed('auto_classification', result))
        
        threading.Thread(target=run_classification, daemon=True).start()
    
    def _on_config_clicked(self):
        """配置按钮点击"""
        self.log("打开配置编辑器...")
        # TODO: 打开配置编辑对话框
        self.log("配置编辑功能开发中...")
    
    # 工具方法
    def log(self, message: str):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _save_log(self):
        """保存日志"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="保存日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get("1.0", tk.END))
                self.log(f"日志已保存到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存日志失败: {e}")
    
    def _clear_log(self):
        """清空日志"""
        if messagebox.askyesno("确认", "确定要清空日志吗？"):
            self.log_text.delete("1.0", tk.END)
            self.log("日志已清空")
    
    def _show_statistics(self):
        """显示小说分类统计报告"""
        # 首先检查工作目录是否已设置
        work_dir = self.work_dir.get().strip()
        if not work_dir:
            messagebox.showwarning(
                "未设置工作目录", 
                "请先选择包含'小说库'文件夹的工作目录，\n然后再运行统计功能。"
            )
            self.log("统计失败: 未设置工作目录")
            return

        # 智能检测小说库路径
        work_path = Path(work_dir)
        
        # 首先检查用户选择的目录是否本身就是小说库目录
        if self._is_novel_library_directory(work_dir):
            # 用户直接选择了小说库目录（包括"小说库"目录或其他包含分类子目录的目录）
            novel_lib_path = work_dir
            self.log(f"检测到小说库目录: {work_dir}")
        else:
            # 检查是否存在传统的"小说库"子目录
            potential_novel_lib = os.path.join(work_dir, "小说库")
            if os.path.exists(potential_novel_lib) and self._is_novel_library_directory(potential_novel_lib):
                novel_lib_path = potential_novel_lib
                self.log(f"检测到传统小说库子目录: {potential_novel_lib}")
            else:
                # 都没找到有效的小说库目录
                messagebox.showerror(
                    "小说库不存在", 
                    f"在指定的工作目录中未找到有效的小说库:\n{work_dir}\n\n"
                    f"请确保选择的目录包含小说分类子目录（如：00-待分类、01-玄幻等），\n"
                    f"或者选择包含'小说库'子目录的父目录。"
                )
                self.log(f"统计失败: 未找到有效的小说库目录 - {work_dir}")
                return
        
        try:
            import subprocess
            import threading
            
            self.log("正在生成统计报告...")
            self.statistics_btn.config(state='disabled', text='统计中...')
            
            def run_statistics():
                error_msg = None
                try:
                    # 构建命令
                    script_path = os.path.join(project_root, "tools", "novel_statistics.py")
                    if not os.path.exists(script_path):
                        error_msg = "未找到统计脚本文件"
                        raise FileNotFoundError(error_msg)                    # 运行统计脚本并捕获输出
                    # 在Windows上使用系统默认编码，避免UTF-8编码错误
                    import locale
                    system_encoding = locale.getpreferredencoding() or 'gbk'
                    
                    try:
                        # 首先尝试使用UTF-8编码
                        result = subprocess.run(
                            [sys.executable, script_path, novel_lib_path],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='strict',
                            timeout=60
                        )
                    except UnicodeDecodeError:
                        # 如果UTF-8失败，使用系统默认编码
                        result = subprocess.run(
                            [sys.executable, script_path, novel_lib_path],
                            capture_output=True,
                            text=True,
                            encoding=system_encoding,
                            errors='replace',
                            timeout=60
                        )
                    
                    # 在主线程中更新UI
                    def update_ui():
                        try:
                            if result.returncode == 0:
                                # 显示统计结果在新窗口
                                self._show_statistics_window(result.stdout)
                                self.log("统计报告生成完成")
                            else:
                                error_info = result.stderr or "统计脚本执行失败"
                                messagebox.showerror("统计失败", f"生成统计报告失败:\n{error_info}")
                                self.log(f"统计失败: {error_info}")
                        except Exception as ui_error:
                            messagebox.showerror("错误", f"处理统计结果时出错: {ui_error}")
                            self.log(f"统计处理错误: {ui_error}")
                        finally:
                            self.statistics_btn.config(state='normal', text='📊 统计报告')
                    
                    self.root.after(0, update_ui)
                    
                except Exception as thread_error:
                    error_msg = str(thread_error)
                    # 在主线程中更新UI
                    def update_error():
                        messagebox.showerror("统计失败", f"生成统计报告失败:\n{error_msg}")
                        self.log(f"统计失败: {error_msg}")
                        self.statistics_btn.config(state='normal', text='📊 统计报告')
                    
                    self.root.after(0, update_error)
            
            # 在后台线程中运行统计
            threading.Thread(target=run_statistics, daemon=True).start()
            
        except Exception as main_error:
            messagebox.showerror("错误", f"启动统计失败: {main_error}")
            self.log(f"统计启动失败: {main_error}")
            self.statistics_btn.config(state='normal', text='📊 统计报告')
    
    def _show_statistics_window(self, statistics_text):
        """在新窗口中显示统计结果"""
        # 创建新窗口
        stats_window = tk.Toplevel(self.root)
        stats_window.title("小说分类统计报告")
        stats_window.geometry("800x600")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(stats_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建文本框
        text_widget = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10), 
            bg="white", 
            fg="black"
        )
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 插入统计文本
        text_widget.insert(tk.END, statistics_text)
        text_widget.config(state=tk.DISABLED)
        
        # 创建底部按钮
        button_frame = ttk.Frame(stats_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_statistics():
            """保存统计报告"""
            try:
                filename = filedialog.asksaveasfilename(
                    title="保存统计报告",
                    defaultextension=".txt",
                    filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
                )
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(statistics_text)
                    messagebox.showinfo("保存成功", f"统计报告已保存到:\n{filename}")
            except Exception as e:
                messagebox.showerror("保存失败", f"保存统计报告失败:\n{e}")
        
        save_btn = ttk.Button(button_frame, text="保存报告", command=save_statistics)
        save_btn.pack(side=tk.LEFT)
        
        close_btn = ttk.Button(button_frame, text="关闭", command=stats_window.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # 让窗口居中显示
        stats_window.update_idletasks()
        x = (stats_window.winfo_screenwidth() // 2) - (stats_window.winfo_width() // 2)
        y = (stats_window.winfo_screenheight() // 2) - (stats_window.winfo_height() // 2)
        stats_window.geometry(f"+{x}+{y}")
        
    def _on_exit(self):
        """退出程序"""
        if messagebox.askyesno("确认", "确定要退出程序吗？"):
            try:
                # 清理工作流管理器资源
                if hasattr(self, 'workflow_manager') and self.workflow_manager:
                    self.workflow_manager.cleanup()
                
                # 停止所有定时器和回调
                self.root.quit()
                
                # 销毁窗口
                self.root.destroy()
                
            except Exception as e:
                # 如果清理过程出错，直接强制退出
                print(f"退出清理时出错: {e}")
                self.root.quit()
                
    def run(self):
        """运行GUI应用"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log("用户中断程序")
        except Exception as e:
            messagebox.showerror("运行错误", f"程序运行出错: {e}")
        finally:
            try:
                # 确保清理资源
                if hasattr(self, 'workflow_manager') and self.workflow_manager:
                    self.workflow_manager.cleanup()
            except:
                pass
    
    def _on_workflow_progress(self, workflow_id: str, progress: float, message: str):
        """工作流进度回调"""
        # 更新进度条
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")
        
        # 更新状态文本
        self.status_text.set(message)
        
        # 添加日志
        if progress == 100:
            self.log(f"工作流完成: {message}")
        elif progress % 20 == 0:  # 每20%记录一次日志
            self.log(f"进度 {progress:.0f}%: {message}")
        
        # 刷新界面
        self.root.update_idletasks()
    
    def _on_workflow_completed(self, workflow_id: str, result: dict):
        """工作流完成处理"""
        if result.get("success", False):
            self.log(f"工作流 {workflow_id} 执行成功: {result.get('message', '')}")
            
            # 根据工作流类型进行特殊处理
            if workflow_id == 'initialization':
                self._check_work_dir()  # 重新检查目录状态
            elif workflow_id == 'file_import':
                # 更新导入状态
                self.import_status.config(text="导入完成")
                
                # 显示扫描和导入统计信息
                scan_info = result.get("scan_info", {})
                if scan_info:
                    total_scanned = scan_info.get("total_scanned", 0)
                    valid_count = scan_info.get("valid_files_count", 0)
                    invalid_count = scan_info.get("invalid_files_count", 0)
                    imported_count = result.get("total_imported", 0)
                    
                    self.log(f"扫描统计: 总文件{total_scanned}个，有效{valid_count}个，无效{invalid_count}个")
                    self.log(f"导入统计: 成功导入{imported_count}个文件")
                    
                    # 显示无效文件详情
                    invalid_files = scan_info.get("invalid_files", [])
                    if invalid_files:
                        self.log(f"以下{len(invalid_files)}个文件被过滤（无效）:")
                        for invalid_file in invalid_files:
                            file_name = invalid_file.get("name", "未知文件")
                            reason = invalid_file.get("reason", "未知原因")
                            self.log(f"  - {file_name}: {reason}")
                
                # 处理失败文件信息
                failed_files = result.get("failed_files", [])
                if failed_files:
                    self.log(f"导入失败的文件数量: {len(failed_files)}")
                    for failed_file in failed_files:
                        file_name = failed_file.get("file", "未知文件")
                        error_msg = failed_file.get("error", "未知错误")
                        self.log(f"导入失败: {file_name} - {error_msg}")
                
                # 显示跳过文件信息
                skipped_files = result.get("skipped_files", [])
                if skipped_files:
                    self.log(f"跳过的文件数量: {len(skipped_files)}")
                    for skipped_file in skipped_files:
                        file_name = skipped_file.get("file", "未知文件")
                        reason = skipped_file.get("reason", "未知原因")
                        self.log(f"跳过文件: {file_name} - {reason}")
            elif workflow_id == 'encoding_fix':
                # 更新编码状态
                fixed_count = len(result.get("fixed_files", []))
                self.encoding_status.config(text=f"已修复: {fixed_count}个文件")
            elif workflow_id == 'auto_classification':
                # 更新分类状态
                stats = result.get("stats", {})
                classified = stats.get("classified_files", 0)
                secondary = stats.get("secondary_check_files", 0)
                status_text = f"已分类: {classified}, 待确认: {secondary}"
                self.classification_status.config(text=status_text)
                self.log(f"DEBUG: 更新分类状态 - {status_text}")
                self.log(f"DEBUG: 收到统计数据 - {stats}")
                # 强制刷新界面
                self.root.update_idletasks()
                self.root.update()
        else:
            error_msg = result.get("error", "未知错误")
            self.log(f"工作流 {workflow_id} 执行失败: {error_msg}")
            messagebox.showerror("执行失败", f"工作流执行失败: {error_msg}")
        
        # 重置状态
        self.status_text.set("系统就绪")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
    
    def _update_fix_button_state(self, has_problems: bool):
        """更新修复按钮状态"""
        if has_problems:
            self.encoding_fix_btn.config(state="normal")
        else:
            self.encoding_fix_btn.config(state="disabled")
    
    def _on_encoding_fix_completed(self, result: dict):
        """编码修复完成处理"""
        if result.get("success", False):
            fixed_count = len(result.get("fixed_files", []))
            failed_count = len(result.get("failed_files", []))
            
            self.log(f"编码修复完成: 成功 {fixed_count} 个，失败 {failed_count} 个")
            
            # 显示验证结果
            verification = result.get("verification", {})
            if verification:
                all_fixed = verification.get("all_fixed", False)
                if all_fixed:
                    self.log("✓ 所有问题文件已修复完成！")
                    self.encoding_status.config(text="发现: 0个问题")
                    self._update_fix_button_state(False)
                else:
                    still_problematic = verification.get("still_problematic", 0)
                    self.log(f"⚠ 仍有 {still_problematic} 个文件存在问题")
                    self.encoding_status.config(text=f"发现: {still_problematic}个问题")
            
            # 显示备份目录
            backup_dir = result.get("backup_dir")
            if backup_dir:
                self.log(f"备份文件保存在: {backup_dir}")
        else:
            error_msg = ", ".join(result.get("errors", ["未知错误"]))
            self.log(f"编码修复失败: {error_msg}")
        
        self.status_text.set("系统就绪")
    def _on_clear_library_clicked(self):
        """清空小说库按钮点击"""
        if not self.workflow_manager:
            self.log("工作流管理器未初始化")
            return
        
        work_dir = self.work_dir.get()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择小说库目录")
            return
        
        # 确认对话框
        result = messagebox.askyesno(
            "确认清空",
            f"确定要清空小说库目录吗？\n\n"
            f"目录: {work_dir}\n\n"
            f"此操作将删除该目录下的所有文件和子目录！\n"
            f"请确保已经备份重要数据。",
            icon="warning"
        )
        
        if not result:
            return
        
        # 二次确认
        confirm = messagebox.askyesno(
            "最终确认",
            "这是最后的确认！\n\n"
            "清空操作不可撤销，所有数据将永久丢失！\n"
            "确定要继续吗？",
            icon="error"
        )
        
        if not confirm:
            return
        
        self.log("开始清空小说库目录...")
        self.status_text.set("正在清空小说库...")
        
        # 异步执行清空操作
        import threading
        import shutil
        from pathlib import Path
        
        def run_clear():
            try:
                library_path = Path(work_dir)
                
                if not library_path.exists():
                    result = {
                        "success": False,
                        "error": "小说库目录不存在"
                    }
                    self.root.after(100, lambda: self._on_clear_completed(result))
                    return
                
                # 统计文件数量
                total_files = 0
                total_dirs = 0
                
                for item in library_path.iterdir():
                    if item.is_file():
                        total_files += 1
                    elif item.is_dir():
                        total_dirs += 1
                        # 统计子文件
                        for sub_item in item.rglob("*"):
                            if sub_item.is_file():
                                total_files += 1
                
                # 删除所有内容
                deleted_files = 0
                deleted_dirs = 0
                
                for item in library_path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            deleted_files += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            deleted_dirs += 1
                    except Exception as e:
                        self.log(f"删除失败: {item.name} - {e}")
                
                result = {
                    "success": True,
                    "message": f"清空完成，删除了 {deleted_files} 个文件，{deleted_dirs} 个目录",
                    "deleted_files": deleted_files,
                    "deleted_dirs": deleted_dirs,
                    "total_files": total_files,
                    "total_dirs": total_dirs
                }
                
            except Exception as e:
                result = {
                    "success": False,
                    "error": f"清空过程中发生错误: {str(e)}"
                }
            
            self.root.after(100, lambda: self._on_clear_completed(result))
        
        threading.Thread(target=run_clear, daemon=True).start()
    
    def _on_clear_completed(self, result):
        """清空操作完成处理"""
        if result.get("success", False):
            self.log(f"小说库清空成功: {result.get('message', '')}")
            
            # 更新界面状态
            self.init_status.config(text="状态: 未初始化", foreground="orange")
            self.import_status.config(text="状态: 无文件")
            self.encoding_status.config(text="状态: 无需修复")
            self.classification_status.config(text="状态: 无待分类文件")
            
            messagebox.showinfo("清空完成", result.get("message", "小说库已清空"))
        else:
            error_msg = result.get("error", "未知错误")
            self.log(f"小说库清空失败: {error_msg}")
            messagebox.showerror("清空失败", f"清空小说库失败:\n{error_msg}")
        
        # 重置状态
        self.status_text.set("系统就绪")
        self.progress_var.set(0)
        self.root.update_idletasks()
        
        # 重新检查工作目录状态
        self._check_work_dir()
    
    def _is_novel_library_directory(self, path):
        """检查指定路径是否是有效的小说库目录"""
        path_obj = Path(path)
        if not path_obj.exists():
            return False
        
        # 检查是否包含小说库的典型子目录
        required_dirs = ["00-待分类", "00-二次确认"]
        category_dirs = ["01-玄幻", "02-奇幻", "03-武侠", "04-仙侠", "05-都市"]
        
        # 至少需要有必需的目录
        has_required = all((path_obj / d).exists() for d in required_dirs)
        # 或者有一些分类目录
        has_categories = any((path_obj / d).exists() for d in category_dirs)
        
        return has_required or has_categories

    def _load_text_extraction_config(self):
        """加载文本提取配置"""
        try:
            config = self.config_manager.get_config()
            text_config = config.get('processing', {}).get('text_extraction', {})
            
            # 加载配置到界面
            self.begin_chars.set(str(text_config.get('begin_chars', 3000)))
            self.fragment_count.set(str(text_config.get('random_fragment_count', 3)))
            self.fragment_size.set(str(text_config.get('random_fragment_size', 500)))
            
            self.log("文本提取配置已加载")
            
        except Exception as e:
            self.log(f"加载文本提取配置失败: {e}")
            # 使用默认值
            self.begin_chars.set("3000")
            self.fragment_count.set("3")
            self.fragment_size.set("500")
    
    def _save_text_extraction_config(self):
        """保存文本提取配置"""
        try:
            # 获取当前配置
            config = self.config_manager.get_config()
            
            # 更新文本提取配置
            if 'processing' not in config:
                config['processing'] = {}
            if 'text_extraction' not in config['processing']:
                config['processing']['text_extraction'] = {}
            
            config['processing']['text_extraction']['begin_chars'] = int(self.begin_chars.get())
            config['processing']['text_extraction']['random_fragment_count'] = int(self.fragment_count.get())
            config['processing']['text_extraction']['random_fragment_size'] = int(self.fragment_size.get())
            
            # 保存配置
            self.config_manager._save_yaml(self.config_manager.default_config_path, config)
            self.config_manager._default_config = None  # 清除缓存
            
            self.log("文本提取配置已保存")
            return True
            
        except Exception as e:
            self.log(f"保存文本提取配置失败: {e}")
            return False

    def _on_text_config_changed(self, *args):
        """文本提取配置变更时的事件处理"""
        try:
            # 验证输入值的有效性
            begin_chars = int(self.begin_chars.get())
            fragment_count = int(self.fragment_count.get()) 
            fragment_size = int(self.fragment_size.get())
            
            # 验证范围
            if not (1000 <= begin_chars <= 10000):
                return
            if not (0 <= fragment_count <= 10):
                return  
            if not (100 <= fragment_size <= 2000):
                return
                
            # 自动保存配置
            self._save_text_extraction_config()
            
        except ValueError:
            # 输入值无效时忽略
            pass
        except Exception as e:
            self.log(f"文本配置变更处理错误: {e}")
