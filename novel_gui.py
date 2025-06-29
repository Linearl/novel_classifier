16#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说分类系统GUI - 主程序入口
作者：AI Assistant
版本：1.0
更新日期：2025年6月28日
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入日志管理器
from core.logger_manager import LoggerManager, get_logger

def check_dependencies():
    """检查依赖包是否安装"""
    missing_deps = []
    
    try:
        import yaml
    except ImportError:
        missing_deps.append("PyYAML")
    
    try:
        import chardet
    except ImportError:
        missing_deps.append("chardet")
    
    if missing_deps:
        error_msg = (
            f"缺少必要的依赖包: {', '.join(missing_deps)}\n\n"
            f"请运行以下命令安装:\n"
            f"pip install {' '.join(missing_deps)}"
        )
        
        # 尝试记录到日志
        try:
            logger = get_logger("NovelGUI")
            logger.error(f"依赖检查失败: {missing_deps}")
        except:
            pass
        
        messagebox.showerror("依赖缺失", error_msg)
        return False
    
    return True

def main():
    """主函数"""
    try:
        # 初始化日志系统
        LoggerManager.initialize()
        logger = get_logger("NovelGUI")
        logger.info("=== 小说分类系统启动 ===")
        
        # 检查依赖
        if not check_dependencies():
            logger.error("依赖检查失败，程序退出")
            return 1
        
        logger.info("依赖检查通过")
        
        # 导入GUI主窗口类
        from gui.main_window import MainApplication
        
        # 创建并运行GUI应用
        logger.info("正在启动GUI应用...")
        app = MainApplication()
        app.run()
        
        logger.info("GUI应用正常关闭")
        return 0
        
    except Exception as e:
        # 尝试记录错误到日志
        try:
            logger = get_logger("NovelGUI")
            logger.critical(f"程序启动失败: {e}", exc_info=True)
        except:
            pass
        
        messagebox.showerror(
            "启动错误",
            f"程序启动失败:\n{str(e)}\n\n"
            f"请检查配置文件和工作目录是否正确。"
        )
        return 1

if __name__ == "__main__":
    exit_code = main()
    # 关闭日志系统
    LoggerManager.shutdown()
    sys.exit(exit_code)
