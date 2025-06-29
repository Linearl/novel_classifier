#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件导入工作流
负责将选定目录中的小说文件导入到小说库的待分类目录

功能：
1. 扫描指定目录中的txt文件
2. 筛选有效的小说文件
3. 复制或移动文件到待分类目录
4. 处理文件名冲突
5. 生成导入报告
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Set
from core.logger_manager import get_logger
from core.config_manager import ConfigManager

class FileImportWorkflow:
    """文件导入工作流"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化导入工作流
        
        Args:
            progress_callback: 进度回调函数，接收(progress, message)参数
        """
        self.logger = get_logger("FileImportWorkflow")
        self.progress_callback = progress_callback
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 支持的文件扩展名
        self.supported_extensions = {'.txt', '.TXT'}
        
        # 最小文件大小（字节），过滤掉过小的文件
        self.min_file_size = 1024  # 1KB
        
        # 最大文件大小（字节），避免处理过大的文件
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    def _update_progress(self, progress: float, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def scan_source_directory(self, source_path: str, recursive: bool = True) -> Dict:
        """
        扫描源目录，查找所有可导入的小说文件
        
        Args:
            source_path: 源目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            Dict: 扫描结果
        """
        result = {
            "success": False,
            "total_files": 0,
            "valid_files": [],
            "invalid_files": [],
            "errors": [],
            "total_size": 0
        }
        
        try:
            source_dir = Path(source_path)
            
            if not source_dir.exists():
                result["errors"].append("源目录不存在")
                return result
            
            if not source_dir.is_dir():
                result["errors"].append("指定路径不是目录")
                return result
            
            self._update_progress(10, "开始扫描文件...")
            
            # 获取所有文件
            if recursive:
                all_files = list(source_dir.rglob("*"))
            else:
                all_files = list(source_dir.glob("*"))
            
            # 筛选文件
            files_to_check = [f for f in all_files if f.is_file()]
            result["total_files"] = len(files_to_check)
            
            if not files_to_check:
                result["errors"].append("源目录中没有找到任何文件")
                return result
            
            # 检查每个文件
            for i, file_path in enumerate(files_to_check):
                try:
                    file_info = self._analyze_file(file_path)
                    
                    if file_info["is_valid"]:
                        result["valid_files"].append(file_info)
                        result["total_size"] += file_info["size"]
                    else:
                        result["invalid_files"].append(file_info)
                    
                    progress = 10 + (i + 1) / len(files_to_check) * 80
                    self._update_progress(progress, f"分析文件: {file_path.name}")
                    
                except Exception as e:
                    result["invalid_files"].append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "error": str(e),
                        "is_valid": False
                    })
            
            self._update_progress(95, "扫描完成，正在生成报告...")
            
            result["success"] = True
            result["message"] = f"扫描完成，找到 {len(result['valid_files'])} 个有效文件"
            
            self._update_progress(100, "文件扫描完成！")
            
        except Exception as e:
            result["errors"].append(f"扫描过程发生错误: {str(e)}")
            
        return result
    
    def _analyze_file(self, file_path: Path) -> Dict:
        """
        分析单个文件是否为有效的小说文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 文件分析结果
        """
        info = {
            "path": str(file_path),
            "name": file_path.name,
            "size": 0,
            "extension": file_path.suffix,
            "is_valid": False,
            "reason": "",
            "md5": "",
            "relative_path": ""
        }
        
        try:
            # 检查文件大小
            info["size"] = file_path.stat().st_size
            
            # 检查扩展名
            if info["extension"].lower() not in {ext.lower() for ext in self.supported_extensions}:
                info["reason"] = f"不支持的文件类型: {info['extension']}"
                return info
            
            # 检查文件大小范围
            if info["size"] < self.min_file_size:
                info["reason"] = f"文件过小: {info['size']} 字节"
                return info
                
            if info["size"] > self.max_file_size:
                info["reason"] = f"文件过大: {info['size']} 字节"
                return info
            
            # 计算MD5校验和
            info["md5"] = self._calculate_md5(file_path)
            
            # 尝试读取文件内容进行基本验证
            if not self._validate_text_content(file_path):
                info["reason"] = "文件内容无效或编码问题"
                return info
            
            info["is_valid"] = True
            info["reason"] = "有效的小说文件"
            
        except Exception as e:
            info["reason"] = f"分析失败: {str(e)}"
            
        return info
    
    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件MD5校验和"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def _validate_text_content(self, file_path: Path) -> bool:
        """验证文本文件内容的有效性"""
        try:
            # 从配置管理器获取用于验证的编码列表
            encodings = self.config_manager.get_validation_encodings()
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        # 读取前1000字符进行验证
                        content = f.read(1000)
                        
                        # 检查是否包含基本的文本内容
                        if len(content.strip()) > 10:
                            # 检查是否包含可读的字符（不全是乱码）
                            readable_chars = sum(1 for c in content if c.isprintable() or c in '\n\r\t　')
                            if readable_chars > len(content) * 0.5:  # 至少50%是可读字符
                                return True
                except UnicodeDecodeError:
                    continue
                except Exception:
                    # 其他异常也继续尝试下一个编码，不要break
                    continue
            
            return False
            
        except Exception:
            return False
    
    def import_files(self, valid_files: List[Dict], target_library: str, 
                    import_mode: str = "copy") -> Dict:
        """
        导入文件到小说库
        
        Args:
            valid_files: 有效文件列表
            target_library: 目标小说库路径
            import_mode: 导入模式，"copy"复制或"move"移动
            
        Returns:
            Dict: 导入结果
        """
        result = {
            "success": False,
            "imported_files": [],
            "failed_files": [],
            "skipped_files": [],
            "errors": [],
            "total_imported": 0,
            "import_mode": import_mode
        }
        
        try:
            library_dir = Path(target_library)
            pending_dir = library_dir / "00-待分类"
            
            # 检查目标目录
            if not pending_dir.exists():
                result["errors"].append("目标小说库的待分类目录不存在")
                return result
            
            # 获取已存在文件的MD5集合，用于去重
            existing_md5s = self._get_existing_file_md5s(pending_dir)
            
            total_files = len(valid_files)
            
            for i, file_info in enumerate(valid_files):
                try:
                    source_path = Path(file_info["path"])
                    
                    # 检查是否重复（通过MD5）
                    if file_info["md5"] in existing_md5s:
                        result["skipped_files"].append({
                            "file": file_info["name"],
                            "reason": "文件已存在（MD5重复）"
                        })
                        continue
                    
                    # 生成目标文件名（处理冲突）
                    target_name = self._generate_unique_filename(pending_dir, source_path.name)
                    target_path = pending_dir / target_name
                    
                    # 执行文件操作
                    if import_mode == "move":
                        shutil.move(str(source_path), str(target_path))
                        operation = "移动"
                    else:
                        shutil.copy2(str(source_path), str(target_path))
                        operation = "复制"
                    
                    result["imported_files"].append({
                        "original_name": file_info["name"],
                        "target_name": target_name,
                        "size": file_info["size"],
                        "operation": operation,
                        "md5": file_info["md5"]
                    })
                    
                    result["total_imported"] += 1
                    existing_md5s.add(file_info["md5"])
                    
                    progress = (i + 1) / total_files * 100
                    self._update_progress(progress, f"{operation}文件: {target_name}")
                    
                except Exception as e:
                    result["failed_files"].append({
                        "file": file_info["name"],
                        "error": str(e)
                    })
            
            result["success"] = True
            result["message"] = f"成功导入 {result['total_imported']} 个文件"
              # 生成导入报告
            self._create_import_report(library_dir, result)
            
        except Exception as e:
            result["errors"].append(f"导入过程发生错误: {str(e)}")
            
        return result
    
    def _get_existing_file_md5s(self, directory: Path) -> Set[str]:
        """获取目录中已存在文件的MD5集合"""
        md5_set = set()
        
        try:
            for file_path in directory.glob("*.txt"):
                if file_path.is_file():
                    md5 = self._calculate_md5(file_path)
                    if md5:
                        md5_set.add(md5)
        except:
            pass
            
        return md5_set
    
    def _generate_unique_filename(self, directory: Path, original_name: str) -> str:
        """生成唯一且标准化的文件名，避免冲突"""
        # 1. 先进行文件名标准化
        standardized_name = self._standardize_filename(original_name)
        
        # 2. 检查标准化后的文件名是否存在冲突
        target_path = directory / standardized_name
        if not target_path.exists():
            return standardized_name
        
        # 3. 如果有冲突，生成带编号的文件名
        base_name = Path(standardized_name).stem
        extension = Path(standardized_name).suffix
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = directory / new_name
            if not new_path.exists():
                return new_name
            counter += 1
            
            # 防止无限循环
            if counter > 1000:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return f"{base_name}_{timestamp}{extension}"
    
    def _standardize_filename(self, filename: str) -> str:
        """标准化文件名"""
        path_obj = Path(filename)
        stem = path_obj.stem
        suffix = path_obj.suffix
        
        # 标准化扩展名：统一转换为小写
        if suffix.upper() in ['.TXT']:
            suffix = '.txt'
        elif suffix.upper() in ['.MD']:
            suffix = '.md'
        else:
            suffix = suffix.lower()
        
        # 清理文件名中的问题字符（可选，目前保持简单）
        # 移除文件名首尾空格
        stem = stem.strip()
        
        # 处理连续空格
        import re
        stem = re.sub(r'\s+', ' ', stem)
        
        # 移除Windows文件系统不支持的字符
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            stem = stem.replace(char, '')
        
        return f"{stem}{suffix}"
    
    def _create_import_report(self, library_dir: Path, import_result: Dict):
        """创建导入报告"""
        try:
            logs_dir = library_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = logs_dir / f"import_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "import_summary": {
                    "total_imported": import_result["total_imported"],
                    "failed_count": len(import_result["failed_files"]),
                    "skipped_count": len(import_result["skipped_files"]),
                    "import_mode": import_result["import_mode"]
                },
                "imported_files": import_result["imported_files"],
                "failed_files": import_result["failed_files"],
                "skipped_files": import_result["skipped_files"],
                "errors": import_result["errors"]
            }
            
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"创建导入报告失败: {e}")
    
    def get_import_statistics(self, library_path: str) -> Dict:
        """
        获取导入统计信息
        
        Args:
            library_path: 小说库路径
            
        Returns:
            Dict: 统计信息
        """
        stats = {
            "pending_count": 0,
            "pending_total_size": 0,
            "recent_imports": [],
            "last_import_time": None
        }
        
        try:
            library_dir = Path(library_path)
            pending_dir = library_dir / "00-待分类"
            logs_dir = library_dir / "logs"
            
            # 统计待分类文件
            if pending_dir.exists():
                txt_files = list(pending_dir.glob("*.txt"))
                stats["pending_count"] = len(txt_files)
                stats["pending_total_size"] = sum(f.stat().st_size for f in txt_files)
            
            # 获取最近的导入记录
            if logs_dir.exists():
                import_reports = list(logs_dir.glob("import_report_*.json"))
                import_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                for report_file in import_reports[:5]:  # 最近5次导入
                    try:
                        import json
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                            stats["recent_imports"].append({
                                "timestamp": report_data["timestamp"],
                                "imported_count": report_data["import_summary"]["total_imported"],
                                "failed_count": report_data["import_summary"]["failed_count"]
                            })
                    except:
                        continue
                
                if stats["recent_imports"]:
                    stats["last_import_time"] = stats["recent_imports"][0]["timestamp"]
                    
        except Exception as e:
            stats["error"] = str(e)
            
        return stats
