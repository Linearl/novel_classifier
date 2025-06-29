#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动分类工作流
负责基于关键词规则自动分类小说文件

功能：
1. 基于配置文件的关键词规则进行分类
2. 支持批量处理和进度回调
3. 自动处理编码问题
4. 智能分类评分系统
5. 二次确认机制
"""

import os
import sys
import shutil
import yaml
from pathlib import Path
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from core.logger_manager import get_logger

class AutoClassificationWorkflow:
    """自动分类工作流"""
    
    def __init__(self, library_path: str, config_manager=None, progress_callback: Optional[Callable] = None):
        """
        初始化分类工作流
        
        Args:
            library_path: 小说库根目录
            config_manager: 配置管理器实例
            progress_callback: 进度回调函数，接收(progress, message)参数
        """
        self.logger = get_logger("AutoClassificationWorkflow")
        self.library_path = Path(library_path)
        self.pending_dir = self.library_path / "00-待分类"
        self.secondary_check_dir = self.library_path / "00-二次确认"
        self.config_manager = config_manager
        self.progress_callback = progress_callback
        
        # 加载配置
        self._load_classification_config()
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'classified_files': 0,
            'encoding_fixed': 0,
            'skipped_files': 0,
            'error_files': 0,
            'secondary_check_files': 0
        }
        self.processing_log = []
        
        # 创建二次确认目录
        self.secondary_check_dir.mkdir(exist_ok=True)
    
    def _update_progress(self, progress: float, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def _load_classification_config(self):
        """加载分类配置"""
        try:
            if self.config_manager:
                # 从配置管理器获取配置
                config = self.config_manager.get_classification_config()
            else:
                # 直接从文件加载
                config_path = self.library_path.parent / "config" / "keywords_config.yaml"
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                else:
                    config = self._get_default_config()
            
            # 提取配置项
            self.categories = config.get('categories', {})
            self.thresholds = config.get('thresholds', {})
            self.weights = config.get('weights', {})
            
            # 设置默认阈值
            self.SCORE_THRESHOLD = self.thresholds.get('direct_classification', 16)
            self.SCORE_DIFFERENCE_THRESHOLD = self.thresholds.get('score_difference', 4)
            
        except Exception as e:
            self.logger.error(f"加载分类配置失败: {e}")
            self._load_default_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        config = self._get_default_config()
        self.categories = config['categories']
        self.thresholds = config['thresholds']
        self.weights = config['weights']
        self.SCORE_THRESHOLD = 16
        self.SCORE_DIFFERENCE_THRESHOLD = 4
    
    def _get_default_config(self):
        """获取默认分类配置"""
        return {
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
                    'medium_weight': ['魔法', '修炼', '境界'],
                    'low_weight': ['强者', '等级', '战斗']
                },
                '04-仙侠': {
                    'high_weight': ['仙侠', '修仙', '仙人', '飞升'],
                    'medium_weight': ['丹药', '法宝', '元婴'],
                    'low_weight': ['灵石', '功法', '洞府']
                },
                '05-都市': {
                    'high_weight': ['都市', '现代', '城市', '白领'],
                    'medium_weight': ['公司', '职场', '商业'],
                    'low_weight': ['手机', '汽车', '咖啡']
                }
            }
        }
    
    def scan_pending_files(self) -> List[Path]:
        """扫描待分类文件夹，返回txt文件列表"""
        try:
            if not self.pending_dir.exists():
                return []
            
            # 扫描所有可能的txt文件（包括大小写变体）
            txt_files = []
            txt_extensions = ['.txt', '.TXT', '.Txt', '.tXt', '.txT', '.TxT', '.TXt', '.tXT']
            
            for ext in txt_extensions:
                txt_files.extend(list(self.pending_dir.glob(f"*{ext}")))
            
            # 规范化文件名
            normalized_files = []
            for file_path in txt_files:
                if not file_path.name.endswith('.txt'):
                    # 重命名为小写扩展名
                    new_name = file_path.stem + '.txt'
                    new_path = file_path.parent / new_name
                    
                    counter = 1
                    while new_path.exists():
                        new_name = f"{file_path.stem}_{counter}.txt"
                        new_path = file_path.parent / new_name
                        counter += 1
                    
                    file_path.rename(new_path)
                    normalized_files.append(new_path)
                else:
                    normalized_files.append(file_path)
            
            return normalized_files
            
        except Exception as e:
            self.logger.error(f"扫描文件失败: {e}")
            return []
    
    def preview_and_fix_file(self, file_path: Path) -> tuple:
        """
        预览文件内容并自动修复编码问题
        使用txt_preview工具提取开头和随机片段
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (内容字符串, 是否修复了编码)
        """
        try:
            # 从配置获取文本提取参数
            text_config = {}
            if self.config_manager:
                processing_config = self.config_manager.get_config().get('processing', {})
                text_config = processing_config.get('text_extraction', {})
            
            # 设置默认值
            begin_chars = text_config.get('begin_chars', 3000)
            fragment_count = text_config.get('random_fragment_count', 3)
            fragment_size = text_config.get('random_fragment_size', 500)
            
            # 导入txt_preview模块
            tools_path = str(self.library_path.parent / "tools")
            if tools_path not in sys.path:
                sys.path.append(tools_path)
            from txt_preview import preview_txt_file
            
            # 使用txt_preview提取内容
            content = preview_txt_file(
                str(file_path), 
                begin_chars=begin_chars,
                fragment_count=fragment_count,
                fragment_size=fragment_size
            )
            
            # 检查是否包含编码修复的消息
            encoding_fixed = "编码修复成功" in content
            
            return content, encoding_fixed
            
        except Exception as e:
            self.logger.error(f"预览文件失败: {e}")
            # 降级到简单方法
            try:
                encodings = ['utf-8', 'gbk', 'gb2312', 'big5']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read(3000)
                        return content, False
                    except UnicodeDecodeError:
                        continue
                return "文件读取失败", False
            except Exception as fallback_e:
                return f"预览失败: {fallback_e}", False
    
    def classify_content(self, content: str, filename: str) -> tuple:
        """
        基于内容和文件名进行分类
        
        Args:
            content: 文件内容
            filename: 文件名
            
        Returns:
            tuple: (分类目录名或'secondary_check', 得分信息)
        """
        # 处理包含多个片段的文本内容
        # txt_preview返回的内容可能包含开头片段和随机片段的标记
        text_to_analyze = f"{filename} {content}".lower()
        
        # 移除片段标记，只保留实际内容
        import re
        # 移除=== [文件开头片段] ===等标记
        text_to_analyze = re.sub(r'=== \[.*?\] ===', '', text_to_analyze)
        # 移除--- 片段 X ---等标记
        text_to_analyze = re.sub(r'--- 片段 \d+ .*? ---', '', text_to_analyze)
        # 移除多余的空白字符
        text_to_analyze = ' '.join(text_to_analyze.split())
        
        # 统计每个类别的匹配度
        category_scores = {}
        for category, keyword_groups in self.categories.items():
            score = 0
            
            # 处理高权重关键词
            if 'high_weight' in keyword_groups:
                for keyword in keyword_groups['high_weight']:
                    score += text_to_analyze.count(keyword.lower()) * self.weights.get('high', 3)
            
            # 处理中权重关键词
            if 'medium_weight' in keyword_groups:
                for keyword in keyword_groups['medium_weight']:
                    score += text_to_analyze.count(keyword.lower()) * self.weights.get('medium', 2)
            
            # 处理低权重关键词
            if 'low_weight' in keyword_groups:
                for keyword in keyword_groups['low_weight']:
                    score += text_to_analyze.count(keyword.lower()) * self.weights.get('low', 1)
            
            category_scores[category] = score
        
        # 按得分排序
        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_scores or sorted_scores[0][1] == 0:
            return 'secondary_check', "无匹配关键词"
        
        best_category, best_score = sorted_scores[0]
        
        # 检查得分是否达到阈值
        if best_score < self.SCORE_THRESHOLD:
            return 'secondary_check', f"得分过低 ({best_score}分)"
        
        # 检查是否有其他分类得分接近
        close_competitors = []
        for category, score in sorted_scores[1:4]:
            if score > 0 and (best_score - score) < self.SCORE_DIFFERENCE_THRESHOLD:
                close_competitors.append(f"{category}({score})")
        
        if close_competitors:
            competitors_str = ", ".join(close_competitors)
            return 'secondary_check', f"得分接近: {best_category}({best_score}) vs {competitors_str}"
        
        return best_category, f"匹配度: {best_score}"
    
    def move_file(self, source_file: Path, target_category: str, score_info: str = "") -> bool:
        """
        移动文件到目标分类文件夹或二次确认文件夹
        
        Args:
            source_file: 源文件路径
            target_category: 目标分类或'secondary_check'
            score_info: 得分信息，用于二次确认时的说明
            
        Returns:
            bool: 是否成功移动
        """
        try:
            if target_category == 'secondary_check':
                target_dir = self.secondary_check_dir
                # 为二次确认文件添加说明后缀
                original_name = source_file.stem
                file_suffix = source_file.suffix
                new_name = f"{original_name}【{score_info}】{file_suffix}"
                target_file = target_dir / new_name
            else:
                target_dir = self.library_path / target_category
                target_dir.mkdir(exist_ok=True)
                target_file = target_dir / source_file.name
            
            # 如果目标文件已存在，生成新名称
            counter = 1
            original_target = target_file
            while target_file.exists():
                if target_category == 'secondary_check':
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_file = target_dir / f"{stem}_{counter}{suffix}"
                else:
                    stem = source_file.stem
                    suffix = source_file.suffix
                    target_file = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # 移动文件
            shutil.move(str(source_file), str(target_file))
            return True
            
        except Exception as e:
            self.logger.error(f"移动文件失败: {e}")
            return False
    
    def process_batch(self, max_files: Optional[int] = None) -> Dict:
        """
        批量处理文件
        
        Args:
            max_files: 最大处理文件数，None表示处理所有文件
            
        Returns:
            Dict: 处理结果
        """
        result = {
            "success": False,
            "message": "",
            "stats": {},
            "processing_log": [],
            "errors": []
        }
        
        try:
            self._update_progress(5, "扫描待分类文件...")
            
            # 扫描待分类文件
            pending_files = self.scan_pending_files()
            
            # 添加调试信息
            self.logger.debug(f"扫描到 {len(pending_files)} 个待分类文件")
            self.logger.debug(f"待分类目录: {self.pending_dir}")
            self.logger.debug(f"目录是否存在: {self.pending_dir.exists()}")
            
            if not pending_files:
                result["success"] = True  # 修改：没有待分类文件也视为成功
                result["stats"] = self.stats.copy()  # 修改：返回空的统计数据
                result["message"] = "没有找到待分类文件"
                self.logger.debug("没有找到待分类文件，返回空结果")
                return result
            
            # 限制处理文件数
            if max_files:
                pending_files = pending_files[:max_files]
            
            self._update_progress(10, f"开始处理 {len(pending_files)} 个文件...")
            
            # 逐个处理文件
            for i, file_path in enumerate(pending_files):
                try:
                    file_result = self._process_single_file(file_path)
                    self.processing_log.append(file_result)
                    
                    if file_result['success']:
                        if file_result['is_secondary_check']:
                            self.stats['secondary_check_files'] += 1
                        else:
                            self.stats['classified_files'] += 1
                        
                        if file_result['encoding_fixed']:
                            self.stats['encoding_fixed'] += 1
                    else:
                        self.stats['error_files'] += 1
                    
                    progress = 10 + (i + 1) / len(pending_files) * 85
                    self._update_progress(progress, f"处理文件: {file_path.name}")
                    
                except Exception as e:
                    self.stats['error_files'] += 1
                    result["errors"].append(f"处理文件 {file_path.name} 时出错: {str(e)}")
            
            self._update_progress(98, "生成处理报告...")
            
            # 生成处理报告
            self._create_classification_report(result)
            
            result["success"] = True
            result["stats"] = self.stats.copy()
            result["processing_log"] = self.processing_log.copy()
            result["message"] = f"处理完成，成功分类 {self.stats['classified_files']} 个文件"
            
            self._update_progress(100, "自动分类完成！")
            
        except Exception as e:
            result["errors"].append(f"批量处理过程发生错误: {str(e)}")
            
        return result
    
    def _process_single_file(self, file_path: Path) -> Dict:
        """处理单个文件"""
        result = {
            'filename': file_path.name,
            'success': False,
            'category': None,
            'encoding_fixed': False,
            'error': None,
            'is_secondary_check': False
        }
        
        try:
            self.stats['total_files'] += 1
            
            # 预览文件并修复编码
            content, encoding_fixed = self.preview_and_fix_file(file_path)
            result['encoding_fixed'] = encoding_fixed
            
            # 检查是否成功获取内容
            if content.startswith("读取文件时出错") or content.startswith("预览失败"):
                result['error'] = content
                return result
            
            # 基于内容进行分类
            category, score_info = self.classify_content(content, file_path.stem)
            
            if category == 'secondary_check':
                # 移动到二次确认文件夹
                if self.move_file(file_path, category, score_info):
                    result['success'] = True
                    result['category'] = '00-二次确认'
                    result['is_secondary_check'] = True
                else:
                    result['error'] = "文件移动失败"
            else:
                # 移动到分类文件夹
                if self.move_file(file_path, category):
                    result['success'] = True
                    result['category'] = category
                else:
                    result['error'] = "文件移动失败"
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _create_classification_report(self, process_result: Dict):
        """创建分类报告"""
        try:
            logs_dir = self.library_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = logs_dir / f"classification_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "classification_summary": self.stats,
                "processing_log": self.processing_log,
                "errors": process_result.get("errors", []),
                "config_info": {
                    "categories_count": len(self.categories),
                    "score_threshold": self.SCORE_THRESHOLD,
                    "score_difference_threshold": self.SCORE_DIFFERENCE_THRESHOLD
                }
            }
            
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"创建分类报告失败: {e}")
    
    def get_classification_statistics(self) -> Dict:
        """获取分类统计信息"""
        stats = {
            "pending_count": 0,
            "category_distribution": {},
            "recent_classifications": [],
            "last_classification_time": None
        }
        
        try:
            # 统计待分类文件
            if self.pending_dir.exists():
                pending_files = list(self.pending_dir.glob("*.txt"))
                stats["pending_count"] = len(pending_files)
            
            # 统计各分类目录的文件数量
            for category in self.categories.keys():
                category_dir = self.library_path / category
                if category_dir.exists():
                    txt_files = list(category_dir.glob("*.txt"))
                    stats["category_distribution"][category] = len(txt_files)
            
            # 获取最近的分类记录
            logs_dir = self.library_path / "logs"
            if logs_dir.exists():
                classification_reports = list(logs_dir.glob("classification_report_*.json"))
                if classification_reports:
                    latest_report = max(classification_reports, key=lambda x: x.stat().st_mtime)
                    stats["last_classification_time"] = datetime.fromtimestamp(latest_report.stat().st_mtime).isoformat()
                    
                    # 读取最近几次分类记录
                    classification_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    for report_file in classification_reports[:5]:
                        try:
                            import json
                            with open(report_file, 'r', encoding='utf-8') as f:
                                report_data = json.load(f)
                                stats["recent_classifications"].append({
                                    "timestamp": report_data["timestamp"],
                                    "classified_count": report_data["classification_summary"]["classified_files"],
                                    "secondary_check_count": report_data["classification_summary"]["secondary_check_files"]
                                })
                        except:
                            continue
                            
        except Exception as e:
            stats["error"] = str(e)
            
        return stats
