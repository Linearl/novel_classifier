#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理器
负责统一管理系统日志配置和初始化
"""

import os
import logging
import logging.config
from pathlib import Path
from typing import Optional

class LoggerManager:
    """日志管理器"""
    
    _initialized = False
    _loggers = {}
    
    @classmethod
    def initialize(cls, config_file: Optional[str] = None, work_dir: Optional[str] = None):
        """
        初始化日志系统
        
        Args:
            config_file: 日志配置文件路径
            work_dir: 工作目录，用于确定日志文件输出位置
        """
        if cls._initialized:
            return
        
        try:
            # 确定配置文件路径
            if config_file is None:
                project_root = Path(__file__).parent.parent
                config_file = project_root / "config" / "log_config.ini"
            
            # 确保日志目录存在
            if work_dir:
                log_dir = Path(work_dir) / "logs"
            else:
                project_root = Path(__file__).parent.parent
                log_dir = project_root / "小说库" / "logs"
            
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 检查是否安装了colorlog
            try:
                import colorlog
                has_colorlog = True
            except ImportError:
                has_colorlog = False
            
            if has_colorlog and config_file.exists():
                # 使用配置文件初始化
                try:
                    logging.config.fileConfig(str(config_file), encoding='utf-8')
                except UnicodeDecodeError:
                    # 如果UTF-8失败，尝试使用gbk
                    logging.config.fileConfig(str(config_file), encoding='gbk')
            else:
                # 使用基本配置
                cls._setup_basic_logging(log_dir)
            
            cls._initialized = True
            
            # 记录初始化完成
            logger = cls.get_logger("LoggerManager")
            logger.info("日志系统初始化完成")
            if not has_colorlog:
                logger.warning("colorlog包未安装，使用基本日志配置")
            
        except Exception as e:
            # 如果初始化失败，至少设置基本logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler(log_dir / "app.log", encoding='utf-8')
                ]
            )
            logger = logging.getLogger("LoggerManager")
            logger.error(f"日志系统初始化失败，使用基本配置: {e}")
            cls._initialized = True
    
    @classmethod
    def _setup_basic_logging(cls, log_dir: Path):
        """设置基本日志配置"""
        log_file = log_dir / "app.log"
        
        # 创建根logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的logger
        
        Args:
            name: logger名称
            
        Returns:
            logging.Logger: logger实例
        """
        if not cls._initialized:
            cls.initialize()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        numeric_level = getattr(logging, level.upper(), None)
        if numeric_level is None:
            raise ValueError(f'无效的日志级别: {level}')
        
        logging.getLogger().setLevel(numeric_level)
    
    @classmethod
    def is_initialized(cls) -> bool:
        """检查日志系统是否已初始化"""
        return cls._initialized
    
    @classmethod
    def shutdown(cls):
        """关闭日志系统"""
        logging.shutdown()
        cls._initialized = False
        cls._loggers.clear()

# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取logger的便捷函数"""
    return LoggerManager.get_logger(name)

def init_logging(config_file: Optional[str] = None, work_dir: Optional[str] = None):
    """初始化日志系统的便捷函数"""
    LoggerManager.initialize(config_file, work_dir)
