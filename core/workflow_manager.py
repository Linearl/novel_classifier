#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流管理器
统一管理和协调各个工作流的执行

功能：
1. 工作流注册和管理
2. 工作流状态监控
3. 工作流间的数据传递
4. 错误处理和恢复
5. 进度统一回调
"""

import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

# 导入各个工作流
from workflows.initialization import InitializationWorkflow
from workflows.file_import import FileImportWorkflow
from workflows.encoding_fix import EncodingFixWorkflow
from workflows.auto_classification import AutoClassificationWorkflow

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    IDLE = "idle"           # 空闲
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 暂停
    COMPLETED = "completed" # 完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled" # 取消

class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, config_manager=None, progress_callback: Optional[Callable] = None):
        """
        初始化工作流管理器
        
        Args:
            config_manager: 配置管理器实例
            progress_callback: 进度回调函数，接收(workflow_name, progress, message)参数
        """
        self.config_manager = config_manager
        self.progress_callback = progress_callback
        
        # 工作流实例存储
        self.workflows = {}
        
        # 工作流状态
        self.workflow_status = {}
        
        # 当前工作目录
        self.current_library_path = None
        
        # 线程管理
        self.workflow_threads = {}
        self.stop_flags = {}
        
        # 执行历史
        self.execution_history = []
        
        # 注册工作流
        self._register_workflows()
    
    def _register_workflows(self):
        """注册所有可用的工作流"""
        workflow_definitions = {
            'initialization': {
                'name': '小说库初始化',
                'class': InitializationWorkflow,
                'requires_library': False,  # 不需要已存在的小说库
                'description': '创建小说库目录结构和初始化配置'
            },
            'file_import': {
                'name': '文件导入',
                'class': FileImportWorkflow,
                'requires_library': True,
                'description': '将外部文件导入到小说库待分类目录'
            },
            'encoding_fix': {
                'name': '编码修复',
                'class': EncodingFixWorkflow,
                'requires_library': True,
                'description': '检测和修复文件编码问题'
            },
            'auto_classification': {
                'name': '自动分类',
                'class': AutoClassificationWorkflow,
                'requires_library': True,
                'description': '基于关键词规则自动分类小说文件'
            }
        }
        
        for workflow_id, definition in workflow_definitions.items():
            self.workflows[workflow_id] = definition
            self.workflow_status[workflow_id] = WorkflowStatus.IDLE
    
    def set_library_path(self, library_path: str):
        """设置当前工作的小说库路径"""
        self.current_library_path = Path(library_path) if library_path else None
    
    def get_available_workflows(self) -> List[Dict]:
        """获取可用的工作流列表"""
        available = []
        
        for workflow_id, definition in self.workflows.items():
            # 检查是否满足前置条件
            can_execute = True
            if definition['requires_library']:
                can_execute = self._validate_library_path()
            
            available.append({
                'id': workflow_id,
                'name': definition['name'],
                'description': definition['description'],
                'status': self.workflow_status[workflow_id].value,
                'can_execute': can_execute,
                'requires_library': definition['requires_library']
            })
        
        return available
    
    def _validate_library_path(self) -> bool:
        """验证小说库路径是否有效"""
        if not self.current_library_path:
            return False
        
        return self.current_library_path.exists()
    
    def execute_workflow(self, workflow_id: str, **kwargs) -> Dict:
        """
        执行指定的工作流
        
        Args:
            workflow_id: 工作流ID
            **kwargs: 工作流特定的参数
            
        Returns:
            Dict: 执行结果
        """
        if workflow_id not in self.workflows:
            return {"success": False, "error": f"未知的工作流: {workflow_id}"}
        
        if self.workflow_status[workflow_id] == WorkflowStatus.RUNNING:
            return {"success": False, "error": "工作流正在运行中"}
        
        # 检查前置条件
        definition = self.workflows[workflow_id]
        if definition['requires_library'] and not self._validate_library_path():
            return {"success": False, "error": "小说库路径无效或不存在"}
        
        try:
            # 创建工作流实例
            workflow_instance = self._create_workflow_instance(workflow_id)
            
            # 异步执行工作流
            self._execute_workflow_async(workflow_id, workflow_instance, kwargs)
            
            return {"success": True, "message": f"工作流 {definition['name']} 已开始执行"}
            
        except Exception as e:
            return {"success": False, "error": f"启动工作流失败: {str(e)}"}
    
    def _create_workflow_instance(self, workflow_id: str):
        """创建工作流实例"""
        definition = self.workflows[workflow_id]
        workflow_class = definition['class']
        
        # 创建进度回调函数
        def workflow_progress_callback(progress: float, message: str):
            if self.progress_callback:
                self.progress_callback(workflow_id, progress, message)
        
        # 根据工作流类型创建实例
        if workflow_id == 'initialization':
            return workflow_class(progress_callback=workflow_progress_callback)
        elif workflow_id == 'file_import':
            return workflow_class(progress_callback=workflow_progress_callback)
        elif workflow_id == 'encoding_fix':
            return workflow_class(progress_callback=workflow_progress_callback)
        elif workflow_id == 'auto_classification':
            return workflow_class(
                library_path=str(self.current_library_path),
                config_manager=self.config_manager,
                progress_callback=workflow_progress_callback
            )
        else:
            raise ValueError(f"不支持的工作流类型: {workflow_id}")
    
    def _execute_workflow_async(self, workflow_id: str, workflow_instance, kwargs: Dict):
        """异步执行工作流"""
        # 创建停止标志
        self.stop_flags[workflow_id] = threading.Event()
        
        def workflow_runner():
            try:
                self.workflow_status[workflow_id] = WorkflowStatus.RUNNING
                self._log_execution_start(workflow_id)
                
                # 根据工作流类型调用相应方法
                result = self._call_workflow_method(workflow_id, workflow_instance, kwargs)
                
                # 记录执行结果
                self._log_execution_end(workflow_id, result)
                
                if result.get("success", False):
                    self.workflow_status[workflow_id] = WorkflowStatus.COMPLETED
                else:
                    self.workflow_status[workflow_id] = WorkflowStatus.FAILED
                    
            except Exception as e:
                self.workflow_status[workflow_id] = WorkflowStatus.FAILED
                self._log_execution_error(workflow_id, str(e))
            
            finally:
                # 清理线程信息
                if workflow_id in self.workflow_threads:
                    del self.workflow_threads[workflow_id]
                if workflow_id in self.stop_flags:
                    del self.stop_flags[workflow_id]
        
        # 启动线程
        thread = threading.Thread(target=workflow_runner, daemon=True)
        self.workflow_threads[workflow_id] = thread
        thread.start()
    
    def _call_workflow_method(self, workflow_id: str, workflow_instance, kwargs: Dict) -> Dict:
        """调用工作流的相应方法"""
        if workflow_id == 'initialization':
            library_path = kwargs.get('library_path', str(self.current_library_path))
            return workflow_instance.create_novel_library(library_path)
            
        elif workflow_id == 'file_import':
            source_path = kwargs.get('source_path')
            if not source_path:
                return {"success": False, "error": "缺少源路径参数"}
            
            # 先扫描文件
            scan_result = workflow_instance.scan_source_directory(
                source_path, 
                kwargs.get('recursive', True)
            )
            
            if not scan_result["success"]:
                return scan_result
            
            # 执行导入
            import_result = workflow_instance.import_files(
                scan_result["valid_files"],
                str(self.current_library_path),
                kwargs.get('import_mode', 'copy')
            )
            
            # 合并扫描结果和导入结果，包含被过滤的文件信息
            if import_result.get("success", False):
                import_result["scan_info"] = {
                    "total_scanned": scan_result["total_files"],
                    "valid_files_count": len(scan_result["valid_files"]),
                    "invalid_files_count": len(scan_result["invalid_files"]),
                    "invalid_files": scan_result["invalid_files"]
                }
                
                # 更新消息，包含扫描信息
                original_msg = import_result.get("message", "")
                import_result["message"] = f"{original_msg}（扫描了{scan_result['total_files']}个文件，{len(scan_result['invalid_files'])}个无效）"
            
            return import_result
            
        elif workflow_id == 'encoding_fix':
            # 检查是否使用问题清单修复
            if kwargs.get('use_problem_list', False):
                # 从问题清单修复
                return workflow_instance.fix_from_problem_list(
                    str(self.current_library_path),
                    kwargs.get('create_backup', True)
                )
            else:
                # 传统方式：先扫描再修复
                scan_dir = kwargs.get('scan_directory', str(self.current_library_path / "00-待分类"))
                
                # 先扫描编码问题
                scan_result = workflow_instance.scan_encoding_issues(
                    scan_dir, 
                    kwargs.get('recursive', True)
                )
                
                if not scan_result["success"] or not scan_result["problem_files"]:
                    return scan_result
                
                # 执行修复
                return workflow_instance.fix_encoding_issues(
                    scan_result["problem_files"],
                    kwargs.get('create_backup', True),
                    kwargs.get('backup_dir')
                )
            
        elif workflow_id == 'auto_classification':
            return workflow_instance.process_batch(
                kwargs.get('max_files')
            )
            
        else:
            return {"success": False, "error": f"未实现的工作流: {workflow_id}"}
    
    def stop_workflow(self, workflow_id: str) -> bool:
        """停止指定的工作流"""
        if workflow_id not in self.stop_flags:
            return False
        
        # 设置停止标志
        self.stop_flags[workflow_id].set()
        self.workflow_status[workflow_id] = WorkflowStatus.CANCELLED
        
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """获取工作流状态"""
        return self.workflow_status.get(workflow_id)
    
    def is_any_workflow_running(self) -> bool:
        """检查是否有任何工作流正在运行"""
        return any(status == WorkflowStatus.RUNNING for status in self.workflow_status.values())
    
    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """获取执行历史记录"""
        return self.execution_history[-limit:]
    
    def _log_execution_start(self, workflow_id: str):
        """记录工作流开始执行"""
        definition = self.workflows[workflow_id]
        
        log_entry = {
            "workflow_id": workflow_id,
            "workflow_name": definition["name"],
            "action": "start",
            "timestamp": datetime.now().isoformat(),
            "library_path": str(self.current_library_path) if self.current_library_path else None
        }
        
        self.execution_history.append(log_entry)
    
    def _log_execution_end(self, workflow_id: str, result: Dict):
        """记录工作流执行结束"""
        definition = self.workflows[workflow_id]
        
        log_entry = {
            "workflow_id": workflow_id,
            "workflow_name": definition["name"],
            "action": "end",
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "result": result
        }
        
        self.execution_history.append(log_entry)
    
    def _log_execution_error(self, workflow_id: str, error_message: str):
        """记录工作流执行错误"""
        definition = self.workflows[workflow_id]
        
        log_entry = {
            "workflow_id": workflow_id,
            "workflow_name": definition["name"],
            "action": "error",
            "timestamp": datetime.now().isoformat(),
            "error": error_message
        }
        
        self.execution_history.append(log_entry)
    
    def get_library_overview(self) -> Dict:
        """获取小说库概览信息"""
        overview = {
            "library_path": str(self.current_library_path) if self.current_library_path else None,
            "is_valid": False,
            "statistics": {}
        }
        
        if not self.current_library_path or not self.current_library_path.exists():
            return overview
        
        try:
            overview["is_valid"] = True
            
            # 统计各目录文件数量
            categories = [
                "00-待分类", "00-二次确认", "01-玄幻", "02-奇幻", "03-武侠", 
                "04-仙侠", "05-都市", "06-历史", "07-军事", "08-游戏", 
                "09-竞技", "10-科幻", "11-灵异", "12-同人", "99-知名作者专区"
            ]
            
            total_files = 0
            for category in categories:
                category_dir = self.current_library_path / category
                if category_dir.exists():
                    txt_files = list(category_dir.glob("*.txt"))
                    file_count = len(txt_files)
                    overview["statistics"][category] = file_count
                    total_files += file_count
                else:
                    overview["statistics"][category] = 0
            
            overview["statistics"]["total_files"] = total_files
            
        except Exception as e:
            overview["error"] = str(e)
        
        return overview
    
    def reset_workflow_status(self, workflow_id: str):
        """重置工作流状态"""
        if workflow_id in self.workflow_status:
            self.workflow_status[workflow_id] = WorkflowStatus.IDLE
    
    def cleanup(self):
        """清理资源"""
        # 停止所有运行中的工作流
        for workflow_id in list(self.workflow_threads.keys()):
            self.stop_workflow(workflow_id)
        
        # 等待所有线程结束
        for thread in self.workflow_threads.values():
            if thread.is_alive():
                thread.join(timeout=5)  # 最多等待5秒
        
        # 清空状态
        self.workflow_threads.clear()
        self.stop_flags.clear()
    
    def execute_workflow_sync(self, workflow_id: str, **kwargs) -> Dict:
        """
        同步执行工作流（阻塞直到完成）
        
        Args:
            workflow_id: 工作流ID
            **kwargs: 工作流参数
            
        Returns:
            Dict: 执行结果
        """
        if workflow_id not in self.workflows:
            return {"success": False, "error": f"未知的工作流: {workflow_id}"}
        
        # 检查是否有工作流正在运行
        if self.is_any_workflow_running():
            return {"success": False, "error": "工作流正在运行中"}
        
        # 检查前置条件
        definition = self.workflows[workflow_id]
        if definition['requires_library'] and not self._validate_library_path():
            return {"success": False, "error": "小说库路径无效或不存在"}
        
        try:
            # 创建工作流实例
            workflow_instance = self._create_workflow_instance(workflow_id)
            
            # 同步执行工作流
            self.workflow_status[workflow_id] = WorkflowStatus.RUNNING
            self._log_execution_start(workflow_id)
            
            result = self._call_workflow_method(workflow_id, workflow_instance, kwargs)
            
            # 记录执行结果
            self._log_execution_end(workflow_id, result)
            
            if result.get("success", False):
                self.workflow_status[workflow_id] = WorkflowStatus.COMPLETED
            else:
                self.workflow_status[workflow_id] = WorkflowStatus.FAILED
                
            return result
            
        except Exception as e:
            self.workflow_status[workflow_id] = WorkflowStatus.FAILED
            self._log_execution_error(workflow_id, str(e))
            return {"success": False, "error": f"执行工作流失败: {str(e)}"}
