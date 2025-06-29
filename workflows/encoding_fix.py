#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编码修复工作流 - 修复版本
负责检测和修复小说文件的编码问题

功能：
1. 扫描指定目录中的文件编码问题
2. 自动检测文件的实际编码
3. 统一转换为UTF-8编码
4. 修复前创建备份
5. 生成修复报告
6. 保存问题文件清单
7. 从清单修复文件
"""

import os
import chardet
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from core.logger_manager import get_logger
from core.config_manager import ConfigManager

class EncodingFixWorkflow:
    """编码修复工作流"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化编码修复工作流
        
        Args:
            progress_callback: 进度回调函数，接收(progress, message)参数
        """
        self.logger = get_logger("EncodingFixWorkflow")
        self.progress_callback = progress_callback
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 从配置获取编码设置
        self.target_encoding = self.config_manager.get_target_encoding()
        self.supported_encodings = self.config_manager.get_supported_encodings()
        self.min_confidence = self.config_manager.get_min_confidence()
    
    def _update_progress(self, progress: float, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def scan_encoding_issues(self, directory_path: str, recursive: bool = True) -> Dict:
        """
        扫描目录中的编码问题
        
        Args:
            directory_path: 要扫描的目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            Dict: 扫描结果
        """
        result = {
            "success": False,
            "total_files": 0,
            "problem_files": [],
            "valid_files": [],
            "errors": [],
            "scan_time": datetime.now().isoformat(),
            "scan_dir": directory_path
        }
        
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                result["errors"].append("扫描目录不存在")
                return result
            
            self._update_progress(5, "开始扫描编码问题...")
              # 获取所有txt文件（去重处理）
            if recursive:
                txt_files = list(directory.rglob("*.txt")) + list(directory.rglob("*.TXT"))
            else:
                txt_files = list(directory.glob("*.txt")) + list(directory.glob("*.TXT"))
            
            # 去重：在Windows系统中，文件路径可能重复
            txt_files = list(set(txt_files))
            
            result["total_files"] = len(txt_files)
            
            if not txt_files:
                result["errors"].append("目录中没有找到txt文件")
                return result
            
            # 逐个检查文件编码
            for i, file_path in enumerate(txt_files):
                try:
                    file_info = self._analyze_file_encoding(file_path)
                    
                    if file_info["has_problem"]:
                        result["problem_files"].append(file_info)
                    else:
                        result["valid_files"].append(file_info)
                    
                    progress = 5 + (i + 1) / len(txt_files) * 90
                    self._update_progress(progress, f"检查文件: {file_path.name}")
                    
                except Exception as e:
                    result["errors"].append(f"检查文件 {file_path.name} 时出错: {str(e)}")
            
            self._update_progress(98, "生成扫描报告...")
            
            result["success"] = True
            result["message"] = f"扫描完成，发现 {len(result['problem_files'])} 个编码问题"
            # 保存扫描报告到日志文件
            report_path = self._save_scan_report(directory.parent, result)
            if report_path:
                result["report_file"] = report_path
            
            self._update_progress(100, "编码扫描完成！")
        
        except Exception as e:
            result["errors"].append(f"扫描过程发生错误: {str(e)}")
            
        return result
    
    def _analyze_file_encoding(self, file_path: Path) -> Dict:
        """
        分析单个文件的编码情况
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 文件编码分析结果
        """
        info = {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "detected_encoding": None,
            "confidence": 0.0,
            "has_problem": False,
            "problem_type": "",
            "can_fix": False,
            "needs_verification": False,  # 新增：是否需要人工确认
            "content_preview": ""  # 新增：内容预览
        }
        
        try:
            # 读取文件的一部分内容进行编码检测
            sample_size = min(info["size"], 10240)  # 最多读取10KB
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
            
            # 使用chardet检测编码
            detection_result = chardet.detect(raw_data)
            
            if detection_result and detection_result.get('encoding'):
                detected_encoding = detection_result.get('encoding', '')
                info["detected_encoding"] = detected_encoding.lower() if detected_encoding else None
                info["confidence"] = detection_result.get('confidence', 0.0)
            else:
                info["detected_encoding"] = None
                info["confidence"] = 0.0
            
            # 为ASCII文件添加内容预览
            if info["detected_encoding"] == 'ascii':
                try:
                    with open(file_path, 'r', encoding='ascii') as f:
                        content = f.read(200)  # 读取前200字符作为预览
                        info["content_preview"] = content.replace('\n', '\\n')[:100] + "..."
                except:
                    info["content_preview"] = "无法读取内容预览"
            
            # 判断是否有编码问题
            if not info["detected_encoding"]:
                # chardet无法检测编码，尝试常见编码
                info["has_problem"] = True
                info["problem_type"] = "无法检测编码，需要尝试常见编码"
                
                # 从配置获取用于检测的编码列表
                common_encodings = self.config_manager.get_detection_encodings()
                can_read_with_common = False
                working_encoding = None
                
                for encoding in common_encodings:
                    try:
                        # 尝试读取文件
                        with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                            content = f.read(1000)
                        
                        # 检查内容是否合理（包含中文字符或可打印字符）
                        if any('\u4e00' <= char <= '\u9fff' for char in content) or \
                           (len(content) > 0 and content.isprintable()):
                            working_encoding = encoding
                            can_read_with_common = True
                            break
                            
                    except UnicodeDecodeError:
                        # 严格模式失败，尝试容错模式
                        try:
                            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                                content = f.read(1000)
                            
                            # 容错模式下，检查是否包含合理内容（不全是替换字符）
                            non_replacement_chars = [c for c in content if c != '�']
                            if len(non_replacement_chars) > len(content) * 0.5:  # 至少一半字符是正常的
                                working_encoding = encoding
                                can_read_with_common = True
                                break
                                
                        except Exception:
                            continue
                    except Exception:
                        continue
                
                # 更新编码信息
                if working_encoding:
                    info["detected_encoding"] = working_encoding
                    info["confidence"] = 0.8  # 给一个合理的置信度
                    info["problem_type"] = f"检测失败但可用{working_encoding}读取"
                
                info["can_fix"] = can_read_with_common
            elif info["confidence"] < self.min_confidence:
                info["has_problem"] = True
                info["problem_type"] = f"编码检测置信度过低 ({info['confidence']:.2f})"
                info["can_fix"] = info["detected_encoding"] in self.supported_encodings
            elif info["detected_encoding"] not in [self.target_encoding]:
                # 包括ASCII在内的所有非UTF-8编码都需要转换
                info["has_problem"] = True
                if info["detected_encoding"] == 'ascii':
                    info["problem_type"] = f"ASCII编码文件 (建议转换为UTF-8)"
                else:
                    info["problem_type"] = f"非目标编码 ({info['detected_encoding']})"
                info["can_fix"] = info["detected_encoding"] in self.supported_encodings or info["detected_encoding"] == 'ascii'
            
            # 额外验证：尝试读取文件内容
            if not info["has_problem"] and not info["needs_verification"]:
                try:
                    with open(file_path, 'r', encoding=self.target_encoding) as f:
                        f.read(1000)  # 尝试读取前1000字符
                except UnicodeDecodeError:
                    info["has_problem"] = True
                    info["problem_type"] = "UTF-8解码失败"
                    info["can_fix"] = info["detected_encoding"] in self.supported_encodings
            
        except Exception as e:
            info["has_problem"] = True
            info["problem_type"] = f"分析失败: {str(e)}"
            info["can_fix"] = False
            
        return info
    
    def _save_scan_report(self, library_dir: Path, scan_result: Dict) -> Optional[str]:
        """保存扫描报告到日志文件"""
        try:
            logs_dir = library_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = logs_dir / f"encoding_scan_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(scan_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"扫描报告已保存到: {report_file}")
            
            # 额外保存问题文件清单，供修复使用
            problem_list_file = logs_dir / "encoding_problems_current.json"
            problem_list = {
                "timestamp": timestamp,
                "scan_dir": scan_result.get("scan_dir", ""),
                "problem_files": scan_result.get("problem_files", []),
                "total_problems": len(scan_result.get("problem_files", [])),
                "scan_report_file": str(report_file)
            }
            
            with open(problem_list_file, 'w', encoding='utf-8') as f:
                json.dump(problem_list, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"问题文件清单已保存到: {problem_list_file}")
            
            # 额外保存简化的问题文件列表（仅包含文件路径）
            simple_problem_list_file = logs_dir / f"problem_files_{timestamp}.txt"
            problem_files = scan_result.get("problem_files", [])
            if problem_files:
                with open(simple_problem_list_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 编码问题文件清单\n")
                    f.write(f"# 扫描时间: {timestamp}\n")
                    f.write(f"# 总计问题文件: {len(problem_files)}\n")
                    f.write(f"# 扫描目录: {scan_result.get('scan_dir', '')}\n\n")
                    
                    for file_info in problem_files:
                        f.write(f"{file_info['path']}\n")
                
                self.logger.info(f"简化问题文件清单已保存到: {simple_problem_list_file}")
            
            return str(report_file)
                
        except Exception as e:
            self.logger.error(f"保存扫描报告失败: {e}")
            return None
    
    def load_problem_files_list(self, library_dir: Path) -> Optional[Dict]:
        """加载当前的问题文件清单"""
        try:
            logs_dir = library_dir / "logs"
            problem_list_file = logs_dir / "encoding_problems_current.json"
            
            if not problem_list_file.exists():
                return None
                
            with open(problem_list_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"加载问题文件清单失败: {e}")
            return None
    
    def fix_from_problem_list(self, library_path: str, create_backup: bool = True) -> Dict:
        """
        从问题文件清单修复编码问题
        
        Args:
            library_path: 小说库路径
            create_backup: 是否创建备份
            
        Returns:
            Dict: 修复结果
        """
        result = {
            "success": False,
            "fixed_files": [],
            "failed_files": [],
            "skipped_files": [],
            "backup_dir": None,
            "errors": [],
            "fix_time": datetime.now().isoformat(),
            "message": ""
        }
        
        try:
            library_dir = Path(library_path)
              # 加载问题文件清单
            problem_list = self.load_problem_files_list(library_dir)
            if not problem_list:
                result["errors"].append("没有找到问题文件清单，请先运行编码扫描")
                return result
            
            problem_files = problem_list.get("problem_files", [])
            if not problem_files:
                result["errors"].append("问题文件清单为空")
                return result
            
            self._update_progress(5, f"从清单加载到 {len(problem_files)} 个问题文件")
            # 过滤仍然存在且可修复的文件
            valid_problem_files = []
            total_files = len(problem_files)
            
            for i, file_info in enumerate(problem_files):
                file_path = Path(file_info["path"])
                file_exists = file_path.exists()
                can_fix = file_info.get("can_fix", False)
                
                if file_exists and can_fix:
                    valid_problem_files.append(file_info)
                    # 只显示消息，不更新进度，避免与后续修复进度冲突
                    if i % 10 == 0 or i == len(problem_files) - 1:  # 每10个文件或最后一个文件显示一次
                        self._update_progress(5, f"准备修复: {file_info['name']} ({i+1}/{total_files})")
                else:
                    skip_reason = []
                    if not file_exists:
                        skip_reason.append("文件不存在")
                    if not can_fix:
                        skip_reason.append("不可修复")
                    
                    result["skipped_files"].append({
                        "file": file_info["name"],
                        "reason": " + ".join(skip_reason),
                        "encoding": file_info.get("detected_encoding", "unknown")
                    })
                    self.logger.debug(f"跳过文件: {file_info['name']} - {', '.join(skip_reason)} (编码: {file_info.get('detected_encoding', 'unknown')})")
            
            self.logger.info(f"过滤结果: 总计{len(problem_files)}个问题文件，可修复{len(valid_problem_files)}个，跳过{len(result['skipped_files'])}个")
            if not valid_problem_files:
                result["errors"].append("没有可修复的问题文件")
                return result
            
            self._update_progress(10, f"准备修复 {len(valid_problem_files)} 个文件")
            
            # 执行修复
            fix_result = self.fix_encoding_issues(valid_problem_files, create_backup)
            
            # 合并结果（保留原有的errors和其他信息）
            result["success"] = fix_result["success"]
            result["fixed_files"] = fix_result["fixed_files"]
            result["failed_files"] = fix_result["failed_files"]
            result["backup_dir"] = fix_result["backup_dir"]
            if fix_result.get("errors"):
                result["errors"].extend(fix_result["errors"])
            result["message"] = fix_result.get("message", "")
            
            # 修复完成后，验证并更新清单
            if result["success"]:
                self._update_progress(95, "验证修复结果...")
                verified_result = self._verify_fix_results(valid_problem_files)
                result["verification"] = verified_result
                
                # 如果所有文件都修复成功，删除问题清单
                if verified_result["all_fixed"]:
                    try:
                        problem_list_file = library_dir / "logs" / "encoding_problems_current.json"
                        if problem_list_file.exists():
                            problem_list_file.unlink()
                            self.logger.info("所有问题已修复，清单文件已删除")
                    except Exception as e:
                        self.logger.warning(f"删除清单文件失败: {e}")
                
                self._update_progress(100, "修复验证完成！")
            
        except Exception as e:
            result["errors"].append(f"修复过程发生错误: {str(e)}")
            
        return result
    
    def _verify_fix_results(self, problem_files: List[Dict]) -> Dict:
        """验证修复结果"""
        verification = {
            "total_files": len(problem_files),
            "fixed_files": 0,
            "still_problematic": 0,
            "all_fixed": False,
            "details": []
        }
        
        for file_info in problem_files:
            file_path = Path(file_info["path"])
            detail = {
                "file": file_info["name"],
                "path": str(file_path),
                "fixed": False,
                "error": ""
            }
            
            try:
                if file_path.exists():
                    # 尝试用UTF-8读取文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(100)  # 只读取前100字符验证
                    
                    # 检查是否还有编码问题
                    current_info = self._analyze_file_encoding(file_path)
                    if not current_info.get("has_problem", True):
                        detail["fixed"] = True
                        verification["fixed_files"] += 1
                    else:
                        detail["error"] = current_info.get("problem_type", "仍有编码问题")
                        verification["still_problematic"] += 1
                else:
                    detail["error"] = "文件不存在"
                    verification["still_problematic"] += 1
                    
            except Exception as e:
                detail["error"] = f"验证失败: {str(e)}"
                verification["still_problematic"] += 1
            
            verification["details"].append(detail)
        
        verification["all_fixed"] = verification["still_problematic"] == 0
        return verification
    
    def fix_encoding_issues(self, problem_files: List[Dict], 
                          create_backup: bool = True,
                          backup_dir: Optional[str] = None) -> Dict:
        """
        修复编码问题
        
        Args:
            problem_files: 有问题的文件列表
            create_backup: 是否创建备份
            backup_dir: 备份目录，如果为None则在原目录创建backup子目录

        Returns:
            Dict: 修复结果
        """
        result = {
            "success": False,
            "fixed_files": [],
            "failed_files": [],
            "skipped_files": [],
            "backup_dir": None,
            "errors": [],
            "fix_time": datetime.now().isoformat()
        }
        
        try:
            # 筛选可修复的文件
            fixable_files = [f for f in problem_files if f.get("can_fix", False)]
            
            if not fixable_files:
                result["errors"].append("没有可修复的文件")
                return result
            
            # 创建备份目录
            if create_backup:
                if backup_dir:
                    backup_path = Path(backup_dir)
                else:
                    # 使用第一个文件的目录作为基准
                    first_file_dir = Path(fixable_files[0]["path"]).parent
                    backup_path = first_file_dir / "backup" / f"encoding_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                backup_path.mkdir(parents=True, exist_ok=True)
                result["backup_dir"] = str(backup_path)
                self._update_progress(5, f"创建备份目录: {backup_path}")
            
            # 逐个修复文件
            total_files = len(fixable_files)
            
            for i, file_info in enumerate(fixable_files):
                try:
                    file_path = Path(file_info["path"])
                    
                    # 创建备份
                    if create_backup:
                        backup_file = backup_path / file_path.name
                        # 如果备份文件已存在，添加序号
                        counter = 1
                        original_backup = backup_file
                        while backup_file.exists():
                            stem = original_backup.stem
                            suffix = original_backup.suffix
                            backup_file = backup_path / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        shutil.copy2(file_path, backup_file)
                    
                    # 执行编码转换
                    fix_result = self._fix_single_file(file_path, file_info["detected_encoding"])
                    
                    # 添加详细的调试信息
                    self.logger.debug(f"处理文件 {file_info['name']} (第{i+1}/{total_files}个)")
                    self.logger.debug(f"修复结果: {'成功' if fix_result['success'] else '失败'}")
                    
                    if fix_result["success"]:
                        result["fixed_files"].append({
                            "file": file_info["name"],
                            "original_encoding": file_info["detected_encoding"],
                            "target_encoding": self.target_encoding,
                            "backup_file": str(backup_file) if create_backup else None,
                            "method": fix_result.get("method", "未知")
                        })
                        self.logger.debug("文件已添加到修复成功列表")
                    else:
                        result["failed_files"].append({
                            "file": file_info["name"],
                            "error": fix_result["error"]
                        })
                        self.logger.debug(f"文件已添加到修复失败列表，原因: {fix_result['error']}")
                    
                    progress = 10 + (i + 1) / total_files * 85  # 从10%到95%
                    self._update_progress(progress, f"修复文件: {file_info['name']} ({i+1}/{total_files})")
                    
                except Exception as e:
                    result["failed_files"].append({
                        "file": file_info["name"],
                        "error": str(e)
                    })
            
            # 跳过的文件
            skipped_count = len(problem_files) - len(fixable_files)
            if skipped_count > 0:
                result["skipped_files"] = [
                    {"file": f["name"], "reason": f["problem_type"]} 
                    for f in problem_files if not f.get("can_fix", False)
                ]
            
            self._update_progress(98, "生成修复报告...")
            
            result["success"] = True
            result["message"] = f"修复完成，成功 {len(result['fixed_files'])} 个，失败 {len(result['failed_files'])} 个"
            
            # 保存修复报告到日志文件
            self.create_fix_report(Path(fixable_files[0]["path"]).parent, result)
            
            self._update_progress(100, "编码修复完成！")
            
        except Exception as e:
            result["errors"].append(f"修复过程发生错误: {str(e)}")
            
        return result
    
    def _fix_single_file(self, file_path: Path, source_encoding: str) -> Dict:
        """
        修复单个文件的编码
        
        Args:
            file_path: 文件路径
            source_encoding: 源编码
            
        Returns:
            Dict: 修复结果
        """
        result = {"success": False, "error": "", "method": "", "debug_info": []}
        
        # 添加调试信息
        result["debug_info"].append(f"开始修复文件: {file_path}")
        result["debug_info"].append(f"检测到的编码: {source_encoding}")
        self.logger.debug(f"开始修复文件: {file_path.name}")
        self.logger.debug(f"检测到的编码: {source_encoding}")
        
        # 检查文件是否存在
        if not file_path.exists():
            result["error"] = f"文件不存在: {file_path}"
            result["debug_info"].append(f"错误: 文件不存在")
            self.logger.debug(f"错误 - 文件不存在: {file_path}")
            return result
            
        # 检查文件大小
        file_size = file_path.stat().st_size
        result["debug_info"].append(f"文件大小: {file_size} 字节")
        self.logger.debug(f"文件大小: {file_size} 字节")
        
        if file_size == 0:
            result["error"] = "文件大小为0字节"
            result["debug_info"].append("错误: 文件大小为0字节")
            self.logger.debug("错误 - 文件大小为0字节")
            return result

        # 定义多种编码修复策略
        strategies = [
            # 策略1: 使用检测到的编码直接读取
            {"encoding": source_encoding, "errors": "strict", "name": f"直接使用{source_encoding}"},
            # 策略2: 使用检测到的编码，错误字符替换为空格
            {"encoding": source_encoding, "errors": "replace", "name": f"使用{source_encoding}并替换错误字符"},
            # 策略3: UTF-8 BOM
            {"encoding": "utf-8-sig", "errors": "replace", "name": "使用UTF-8-BOM编码并替换错误字符"},
            # 策略4: GBK编码（中文常用）
            {"encoding": "gbk", "errors": "replace", "name": "使用GBK编码并替换错误字符"},
            # 策略5: GB18030编码（更全面的中文编码）
            {"encoding": "gb18030", "errors": "replace", "name": "使用GB18030编码并替换错误字符"},
            # 策略6: Big5编码（繁体中文）
            {"encoding": "big5", "errors": "replace", "name": "使用Big5编码并替换错误字符"},
            # 策略7: Big5-HKSCS编码（香港繁体中文）
            {"encoding": "big5-hkscs", "errors": "replace", "name": "使用Big5-HKSCS编码并替换错误字符"},
            # 策略8: UTF-16编码
            {"encoding": "utf-16", "errors": "replace", "name": "使用UTF-16编码并替换错误字符"},
            # 策略9: UTF-32编码
            {"encoding": "utf-32", "errors": "replace", "name": "使用UTF-32编码并替换错误字符"},
            # 策略10: Windows Western European (CP1252)
            {"encoding": "cp1252", "errors": "replace", "name": "使用CP1252编码并替换错误字符"},
            # 策略11: Latin1编码（几乎不会失败）
            {"encoding": "latin1", "errors": "replace", "name": "使用Latin1编码并替换错误字符"},
            # 策略12: 直接以二进制方式读取，解码时替换错误
            {"encoding": "utf-8", "errors": "replace", "name": "二进制读取后UTF-8解码"}
        ]
        
        content = None
        successful_strategy = None
        
        # 尝试各种策略
        for i, strategy in enumerate(strategies):
            try:
                result["debug_info"].append(f"尝试策略{i+1}: {strategy['name']}")
                self.logger.debug(f"尝试策略{i+1}: {strategy['name']}")
                
                if strategy["name"] == "二进制读取后UTF-8解码":
                    # 特殊策略：二进制读取
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                    content = raw_data.decode('utf-8', errors='replace')
                else:
                    # 常规策略
                    with open(file_path, 'r', encoding=strategy["encoding"], errors=strategy["errors"]) as f:
                        content = f.read()
                
                successful_strategy = strategy
                result["debug_info"].append(f"策略成功: {strategy['name']}")
                result["debug_info"].append(f"读取到内容长度: {len(content) if content else 0} 字符")
                self.logger.debug(f"策略{i+1}成功: {strategy['name']}")
                self.logger.debug(f"读取到内容长度: {len(content) if content else 0} 字符")
                break
                
            except Exception as e:
                # 当前策略失败，尝试下一个
                result["debug_info"].append(f"策略失败: {strategy['name']} - {str(e)}")
                self.logger.debug(f"策略{i+1}失败: {strategy['name']} - {str(e)}")
                continue
        
        if content is not None:
            try:
                # 清理内容：将替换字符(�)替换为空格
                original_length = len(content)
                content = content.replace('�', ' ')
                cleaned_length = len(content)
                result["debug_info"].append(f"内容清理: 原始长度 {original_length}, 清理后长度 {cleaned_length}")
                self.logger.debug(f"内容清理 - 原始长度: {original_length}, 清理后长度: {cleaned_length}")
                
                # 创建临时备份以防写入失败
                temp_file = file_path.with_suffix('.tmp')
                result["debug_info"].append(f"创建临时文件: {temp_file}")
                self.logger.debug(f"创建临时文件: {temp_file}")
                
                # 写入临时文件
                with open(temp_file, 'w', encoding=self.target_encoding) as f:
                    f.write(content)
                self.logger.debug("内容已写入临时文件")
                
                # 验证临时文件
                with open(temp_file, 'r', encoding=self.target_encoding) as f:
                    verify_content = f.read()
                
                if len(verify_content) == len(content):
                    # 替换原文件
                    temp_file.replace(file_path)
                    result["debug_info"].append("文件写入验证成功，已替换原文件")
                    self.logger.debug("文件写入验证成功，已替换原文件")
                    
                    result["success"] = True
                    result["method"] = successful_strategy["name"]
                else:
                    result["error"] = f"文件验证失败: 原内容长度 {len(content)}, 验证长度 {len(verify_content)}"
                    result["debug_info"].append(f"错误: 文件验证失败")
                    self.logger.debug(f"错误 - 文件验证失败: 原内容长度 {len(content)}, 验证长度 {len(verify_content)}")
                    # 清理临时文件
                    if temp_file.exists():
                        temp_file.unlink()
                
            except Exception as e:
                result["error"] = f"写入文件失败: {str(e)}"
                result["debug_info"].append(f"错误: 写入文件失败 - {str(e)}")
                self.logger.debug(f"错误 - 写入文件失败: {str(e)}")
                # 清理临时文件
                temp_file = file_path.with_suffix('.tmp')
                if temp_file.exists():
                    temp_file.unlink()
        else:
            result["error"] = "所有编码策略都失败"
            result["debug_info"].append("错误: 所有编码策略都失败")
            self.logger.debug("错误 - 所有编码策略都失败")
        
        self.logger.debug(f"文件 {file_path.name} 修复结果: {'成功' if result['success'] else '失败'}")
        if not result["success"]:
            self.logger.debug(f"失败原因: {result['error']}")
            
        return result
    
    def create_fix_report(self, library_dir: Path, fix_result: Dict):
        """创建修复报告"""
        try:
            logs_dir = library_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = logs_dir / f"encoding_fix_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(fix_result, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"创建修复报告失败: {e}")
    
    def get_encoding_statistics(self, library_path: str) -> Dict:
        """
        获取编码统计信息
        
        Args:
            library_path: 小说库路径
            
        Returns:
            Dict: 统计信息
        """
        stats = {
            "total_files": 0,
            "utf8_files": 0,
            "problem_files": 0,
            "encoding_distribution": {},
            "last_fix_time": None
        }
        
        try:
            library_dir = Path(library_path)
            
            # 扫描所有txt文件
            txt_files = list(library_dir.rglob("*.txt"))
            stats["total_files"] = len(txt_files)
            
            # 快速检查前100个文件的编码分布（避免全扫描太慢）
            sample_files = txt_files[:100] if len(txt_files) > 100 else txt_files
            
            for file_path in sample_files:
                try:
                    with open(file_path, 'rb') as f:
                        raw_data = f.read(1024)  # 读取1KB样本
                    
                    detection = chardet.detect(raw_data)
                    if detection and detection['encoding']:
                        encoding = detection['encoding'].lower()
                        stats["encoding_distribution"][encoding] = stats["encoding_distribution"].get(encoding, 0) + 1
                        
                        if encoding == 'utf-8':
                            stats["utf8_files"] += 1
                        elif detection['confidence'] < self.min_confidence:
                            stats["problem_files"] += 1
                except:
                    stats["problem_files"] += 1
            
            # 获取最近的修复记录
            logs_dir = library_dir / "logs"
            if logs_dir.exists():
                fix_reports = list(logs_dir.glob("encoding_fix_report_*.json"))
                if fix_reports:
                    latest_report = max(fix_reports, key=lambda x: x.stat().st_mtime)
                    stats["last_fix_time"] = datetime.fromtimestamp(latest_report.stat().st_mtime).isoformat()
                    
        except Exception as e:
            stats["error"] = str(e)
            
        return stats
