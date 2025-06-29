#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
负责管理系统配置文件的加载、验证和更新
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.keywords_config_path = self.config_dir / "keywords_config.yaml"
        self.gui_config_path = self.config_dir / "gui_config.yaml"
        self.default_config_path = self.config_dir / "default_config.yaml"
        
        # 配置缓存
        self._keywords_config = None
        self._gui_config = None
        self._default_config = None
        
        # 初始化配置文件
        self._init_config_files()
    
    def _init_config_files(self):
        """初始化配置文件"""
        # 创建默认配置
        if not self.default_config_path.exists():
            self._create_default_config()
        
        # 创建GUI配置
        if not self.gui_config_path.exists():
            self._create_gui_config()
        
        # 检查关键词配置
        if not self.keywords_config_path.exists():
            self._create_keywords_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            'app': {
                'name': '小说整理系统',
                'version': '1.0.0',
                'author': 'AI Assistant'
            },
            'paths': {
                'work_dir': '',
                'backup_dir': 'backup',
                'logs_dir': 'logs'
            },
            'thresholds': {
                'direct_classification': 16,
                'secondary_check': 8,
                'score_difference': 4
            },
            'weights': {
                'high': 3,
                'medium': 2,
                'low': 1
            },
            'processing': {
                'batch_size': 50,
                'max_preview_chars': 3000,
                'create_backup': True,
                'auto_fix_encoding': True,
                'text_extraction': {
                    'begin_chars': 3000,
                    'random_fragment_count': 3,
                    'random_fragment_size': 500
                }
            },
            'encoding': {
                'target_encoding': 'utf-8',
                'min_confidence': 0.7,
                'supported_encodings': [
                    'utf-8',           # UTF-8标准编码
                    'utf-8-sig',       # UTF-8 with BOM  
                    'gbk',             # 简体中文GBK
                    'gb2312',          # 简体中文GB2312
                    'gb18030',         # 简体中文GB18030(全字符集)
                    'big5',            # 繁体中文Big5
                    'big5-hkscs',      # 香港Big5扩展
                    'cp936',           # Windows简体中文代码页(同GBK)
                    'cp950',           # Windows繁体中文代码页(同Big5)
                    'utf-16',          # UTF-16
                    'utf-16le',        # UTF-16 Little Endian
                    'utf-16be',        # UTF-16 Big Endian
                    'utf-32',          # UTF-32
                    'utf-32le',        # UTF-32 Little Endian
                    'utf-32be',        # UTF-32 Big Endian
                    'latin1',          # Latin-1 (ISO-8859-1)
                    'cp1252',          # Windows Western European
                    'ascii'            # ASCII
                ],
                'detection_encodings': [
                    'gbk',             # 简体中文GBK
                    'gb2312',          # 简体中文GB2312
                    'gb18030',         # 简体中文GB18030
                    'big5',            # 繁体中文Big5
                    'big5-hkscs',      # 香港Big5扩展
                    'cp936',           # Windows简体中文代码页
                    'cp950',           # Windows繁体中文代码页
                    'utf-8-sig',       # UTF-8 with BOM
                    'utf-16',          # UTF-16
                    'utf-16le',        # UTF-16 Little Endian
                    'utf-16be',        # UTF-16 Big Endian
                    'utf-32',          # UTF-32
                    'utf-32le',        # UTF-32 Little Endian  
                    'utf-32be',        # UTF-32 Big Endian
                    'cp1252',          # Windows Western European
                    'latin1'           # Latin-1
                ],
                'validation_encodings': [
                    'utf-8',           # UTF-8标准编码
                    'utf-8-sig',       # UTF-8 with BOM
                    'gbk',             # 简体中文GBK
                    'gb2312',          # 简体中文GB2312 
                    'gb18030',         # 简体中文GB18030(全字符集)
                    'big5',            # 繁体中文Big5
                    'big5-hkscs',      # 香港Big5扩展
                    'cp936',           # Windows简体中文代码页
                    'cp950',           # Windows繁体中文代码页
                    'utf-16',          # UTF-16
                    'utf-16le',        # UTF-16 Little Endian
                    'utf-16be',        # UTF-16 Big Endian  
                    'utf-32',          # UTF-32
                    'utf-32le',        # UTF-32 Little Endian
                    'utf-32be',        # UTF-32 Big Endian
                    'latin1',          # Latin-1 (ISO-8859-1)
                    'cp1252',          # Windows Western European
                    'ascii'            # ASCII
                ]
            }
        }
        
        self._save_yaml(self.default_config_path, default_config)
    
    def _create_gui_config(self):
        """创建GUI配置文件"""
        gui_config = {
            'window': {
                'title': '小说整理系统 v1.0',
                'width': 1000,
                'height': 800,
                'min_width': 800,
                'min_height': 700,
                'resizable': True
            },
            'theme': {
                'font_family': '微软雅黑',
                'font_size': 9,
                'bg_color': '#f0f0f0',
                'fg_color': '#333333',
                'accent_color': '#0078d4'
            },
            'layout': {
                'panel_spacing': 10,
                'button_height': 30,
                'progress_height': 20,
                'log_lines': 15
            },
            'behavior': {
                'auto_save_logs': True,
                'confirm_operations': True,
                'show_progress': True,
                'remember_window_state': True
            }
        }
        
        self._save_yaml(self.gui_config_path, gui_config)
    
    def _create_keywords_config(self):
        """创建关键词配置文件（如果不存在）"""
        keywords_config = {
            'thresholds': {
                'direct_classification': 16,
                'secondary_check': 8,
                'score_difference': 4
            },
            'weights': {
                'high': 3,
                'medium': 2,
                'low': 1
            },
            'categories': {
                '01-玄幻': {
                    'high_weight': ['玄幻', '异界', '斗气', '修炼'],
                    'medium_weight': ['魔法', '境界', '武者'],
                    'low_weight': ['强者', '等级', '战斗']
                },
                '02-奇幻': {
                    'high_weight': ['奇幻', '魔法', '精灵', '魔法师'],
                    'medium_weight': ['法师', '魔兽', '巫师'],
                    'low_weight': ['魔力', '咒语', '魔法学院']
                },
                '05-都市': {
                    'high_weight': ['都市', '重生', '系统', '签到'],
                    'medium_weight': ['现代', '都市生活', '商战'],
                    'low_weight': ['都市情感', '职场', '创业']
                },
                '10-科幻': {
                    'high_weight': ['科幻', '星际', '未来', '机甲'],
                    'medium_weight': ['太空', '科技', '星球'],
                    'low_weight': ['外星', '时空', '变异']
                }
            }
        }
        
        self._save_yaml(self.keywords_config_path, keywords_config)
    
    def _save_yaml(self, file_path: Path, data: Dict[str, Any]):
        """保存YAML文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        except Exception as e:
            raise Exception(f"保存配置文件失败: {file_path} - {e}")
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML文件"""
        try:
            if not file_path.exists():
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise Exception(f"加载配置文件失败: {file_path} - {e}")
    
    def get_keywords_config(self) -> Dict[str, Any]:
        """获取关键词配置"""
        if self._keywords_config is None:
            self._keywords_config = self._load_yaml(self.keywords_config_path)
        return self._keywords_config
    
    def get_gui_config(self) -> Dict[str, Any]:
        """获取GUI配置"""
        if self._gui_config is None:
            self._gui_config = self._load_yaml(self.gui_config_path)
        return self._gui_config
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        if self._default_config is None:
            self._default_config = self._load_yaml(self.default_config_path)
        return self._default_config
    
    def get_config(self) -> Dict[str, Any]:
        """获取默认配置（兼容性别名）"""
        return self.get_default_config()
    
    def save_keywords_config(self, config: Dict[str, Any]):
        """保存关键词配置"""
        self._save_yaml(self.keywords_config_path, config)
        self._keywords_config = config
    
    def save_gui_config(self, config: Dict[str, Any]):
        """保存GUI配置"""
        self._save_yaml(self.gui_config_path, config)
        self._gui_config = config
    
    def reload_config(self):
        """重新加载所有配置"""
        self._keywords_config = None
        self._gui_config = None
        self._default_config = None
    
    def validate_config(self, config_type: str = "all") -> bool:
        """
        验证配置文件格式
        
        Args:
            config_type: 配置类型 ("keywords", "gui", "default", "all")
        
        Returns:
            bool: 验证是否通过
        """
        try:
            if config_type in ["keywords", "all"]:
                config = self.get_keywords_config()
                if not all(key in config for key in ['categories', 'thresholds', 'weights']):
                    return False
            
            if config_type in ["gui", "all"]:
                config = self.get_gui_config()
                if not all(key in config for key in ['window', 'theme']):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_config_status(self) -> Dict[str, bool]:
        """获取配置文件状态"""
        return {
            'keywords_config': self.keywords_config_path.exists(),
            'gui_config': self.gui_config_path.exists(),
            'default_config': self.default_config_path.exists(),
            'config_dir': self.config_dir.exists()
        }
    
    def get_classification_config(self) -> Dict[str, Any]:
        """
        获取分类配置
        
        Returns:
            Dict[str, Any]: 分类配置字典，包含categories、thresholds、weights等
        """
        keywords_config = self.get_keywords_config()
        default_config = self.get_default_config()
        
        # 合并配置，关键词配置优先
        classification_config = {
            'categories': keywords_config.get('categories', {}),
            'thresholds': keywords_config.get('thresholds', default_config.get('thresholds', {})),
            'weights': keywords_config.get('weights', default_config.get('weights', {}))
        }
        
        return classification_config
    
    def get_default_work_dir(self) -> str:
        """
        获取默认工作目录路径
        
        Returns:
            str: 默认工作目录的绝对路径
        """
        default_config = self.get_default_config()
        work_dir = default_config.get('paths', {}).get('work_dir', '小说库')
        
        # 如果是相对路径，转换为绝对路径（相对于项目根目录）
        if not os.path.isabs(work_dir):
            # 获取项目根目录（配置目录的上级目录）
            project_root = self.config_dir.parent
            work_dir = project_root / work_dir
        
        return str(work_dir)
    
    def ensure_work_dir_exists(self, work_dir: Optional[str] = None) -> str:
        """
        确保工作目录存在，如果不存在则创建
        
        Args:
            work_dir: 工作目录路径，如果为None则使用默认路径
            
        Returns:
            str: 工作目录的绝对路径
        """
        if work_dir is None:
            work_dir = self.get_default_work_dir()
        
        work_path = Path(work_dir)
        
        # 创建工作目录
        work_path.mkdir(parents=True, exist_ok=True)
        
        # 创建必要的子目录
        required_dirs = [
            "00-待分类",
            "00-二次确认", 
            "01-玄幻",
            "02-奇幻",
            "03-武侠",
            "04-仙侠",
            "05-都市",
            "06-历史",
            "07-军事",
            "08-游戏",
            "09-竞技",
            "10-科幻",
            "11-灵异",
            "12-同人",
            "99-知名作者专区",
            "backup",
            "logs",
            "statistics",
            "temp"
        ]
        
        for dir_name in required_dirs:
            (work_path / dir_name).mkdir(exist_ok=True)
        
        return str(work_path)
    
    def update_work_dir_config(self, work_dir: str):
        """
        更新配置文件中的工作目录路径
        
        Args:
            work_dir: 新的工作目录路径
        """
        default_config = self.get_default_config()
        
        # 更新工作目录路径
        if 'paths' not in default_config:
            default_config['paths'] = {}
        default_config['paths']['work_dir'] = work_dir
        
        # 保存配置
        self._save_yaml(self.default_config_path, default_config)
        
        # 清除缓存，强制重新加载
        self._default_config = None
    
    def get_encoding_config(self) -> Dict[str, Any]:
        """
        获取编码配置
        
        Returns:
            Dict[str, Any]: 编码配置字典，包含支持的编码列表等
        """
        default_config = self.get_default_config()
        return default_config.get('encoding', {})
    
    def get_supported_encodings(self) -> list:
        """
        获取支持的编码列表
        
        Returns:
            list: 支持的编码列表
        """
        encoding_config = self.get_encoding_config()
        return encoding_config.get('supported_encodings', ['utf-8', 'gbk', 'gb2312'])
    
    def get_detection_encodings(self) -> list:
        """
        获取用于编码检测的编码列表
        
        Returns:
            list: 用于编码检测的编码列表
        """
        encoding_config = self.get_encoding_config()
        return encoding_config.get('detection_encodings', ['gbk', 'gb2312', 'gb18030', 'big5'])
    
    def get_validation_encodings(self) -> list:
        """
        获取用于文件验证的编码列表
        
        Returns:
            list: 用于文件验证的编码列表
        """
        encoding_config = self.get_encoding_config()
        return encoding_config.get('validation_encodings', ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5'])
    
    def get_target_encoding(self) -> str:
        """
        获取目标编码
        
        Returns:
            str: 目标编码
        """
        encoding_config = self.get_encoding_config()
        return encoding_config.get('target_encoding', 'utf-8')
    
    def get_min_confidence(self) -> float:
        """
        获取最小置信度阈值
        
        Returns:
            float: 最小置信度阈值
        """
        encoding_config = self.get_encoding_config()
        return encoding_config.get('min_confidence', 0.7)
