#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说库初始化工作流
负责创建小说库的目录结构和初始化配置

功能：
1. 创建标准的小说库目录结构
2. 生成初始化记录文件
3. 创建默认配置文件
4. 设置目录说明文件
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

class InitializationWorkflow:
    """小说库初始化工作流"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化工作流
        
        Args:
            progress_callback: 进度回调函数，接收(progress, message)参数
        """
        self.progress_callback = progress_callback
        
        # 标准目录结构
        self.standard_dirs = [
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
        
        # 类别说明
        self.category_descriptions = {
            "00-待分类": "新导入的小说文件暂存区，等待分类处理",
            "00-二次确认": "自动分类不确定的文件，需要人工确认",
            "01-玄幻": "玄幻类小说，包含修真、异能等",
            "02-奇幻": "奇幻类小说，西方魔法、异世界等",
            "03-武侠": "武侠类小说，传统武侠、新武侠等",
            "04-仙侠": "仙侠类小说，修仙、仙缘等",
            "05-都市": "都市类小说，现代都市背景",
            "06-历史": "历史类小说，历史穿越、架空历史等",
            "07-军事": "军事类小说，战争、军旅题材",
            "08-游戏": "游戏类小说，网游、电竞等",
            "09-竞技": "竞技类小说，体育竞技等",
            "10-科幻": "科幻类小说，未来科技、星际等",
            "11-灵异": "灵异类小说，恐怖、悬疑、超自然",
            "12-同人": "同人类小说，基于原作的二次创作",
            "99-知名作者专区": "知名作者作品专门存放区",
            "backup": "备份文件存放区",
            "logs": "系统日志文件存放区", 
            "statistics": "统计数据文件存放区",
            "temp": "临时文件存放区"
        }
    
    def _update_progress(self, progress: float, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def create_novel_library(self, library_path: str) -> Dict:
        """
        创建小说库目录结构
        
        Args:
            library_path: 小说库根目录路径
            
        Returns:
            Dict: 创建结果信息
        """
        result = {
            "success": False,
            "message": "",
            "created_dirs": [],
            "created_files": [],
            "errors": []
        }
        
        try:
            library_dir = Path(library_path)
            
            # 检查目录是否存在
            if library_dir.exists() and any(library_dir.iterdir()):
                result["message"] = "目标目录已存在且不为空，请选择空目录或不存在的目录"
                return result
            
            # 创建根目录
            library_dir.mkdir(parents=True, exist_ok=True)
            self._update_progress(10, "创建根目录...")
            
            # 创建子目录
            total_dirs = len(self.standard_dirs)
            for i, dir_name in enumerate(self.standard_dirs):
                dir_path = library_dir / dir_name
                dir_path.mkdir(exist_ok=True)
                result["created_dirs"].append(str(dir_path))
                
                # 为特殊目录创建说明文件
                if dir_name == "00-二次确认":
                    self._create_secondary_check_readme(dir_path)
                    result["created_files"].append(str(dir_path / "目录说明.txt"))
                
                progress = 10 + (i + 1) / total_dirs * 60
                self._update_progress(progress, f"创建目录: {dir_name}")
            
            # 创建README文件
            self._update_progress(75, "创建README文件...")
            readme_path = library_dir / "README.md"
            self._create_readme(readme_path)
            result["created_files"].append(str(readme_path))
            
            # 创建初始化记录
            self._update_progress(85, "创建初始化记录...")
            init_record_path = library_dir / "初始化记录.json"
            self._create_init_record(init_record_path, library_path)
            result["created_files"].append(str(init_record_path))
            
            # 创建新发现关键词文件
            self._update_progress(95, "创建关键词发现文件...")
            keywords_file = library_dir / "new_keywords_discovered.txt"
            keywords_file.touch()
            result["created_files"].append(str(keywords_file))
            
            self._update_progress(100, "小说库初始化完成！")
            
            result["success"] = True
            result["message"] = f"成功创建小说库，共创建 {len(result['created_dirs'])} 个目录和 {len(result['created_files'])} 个文件"
            
        except Exception as e:
            result["errors"].append(f"创建小说库时发生错误: {str(e)}")
            result["message"] = f"创建失败: {str(e)}"
            
        return result
    
    def _create_readme(self, readme_path: Path):
        """创建README文件"""
        content = f"""# 小说库使用说明

## 目录结构说明

本小说库采用标准化的目录结构，便于管理和查找：

### 核心分类目录

{self._format_category_list()}

### 系统目录

- **backup/**: 备份文件存放区，系统自动备份重要文件
- **logs/**: 系统运行日志，记录所有操作历史
- **statistics/**: 统计数据文件，包含分类统计、关键词分析等
- **temp/**: 临时文件存放区，处理过程中的临时文件

## 使用流程

1. **文件导入**: 将新小说文件放入 `00-待分类/` 目录
2. **自动分类**: 运行分类工具进行自动分类
3. **人工确认**: 检查 `00-二次确认/` 目录中需要确认的文件
4. **完成整理**: 文件自动移动到对应分类目录

## 注意事项

- 请勿直接删除系统目录（backup、logs、statistics、temp）
- 建议定期备份整个小说库
- 如有新的分类需求，请联系管理员

---
初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        readme_path.write_text(content, encoding='utf-8')
    
    def _format_category_list(self) -> str:
        """格式化分类目录列表"""
        lines = []
        for dir_name in self.standard_dirs:
            if dir_name in self.category_descriptions:
                desc = self.category_descriptions[dir_name]
                lines.append(f"- **{dir_name}/**: {desc}")
        return "\n".join(lines)
    
    def _create_secondary_check_readme(self, dir_path: Path):
        """创建二次确认目录说明"""
        content = """# 二次确认目录说明

此目录用于存放自动分类系统无法确定分类的小说文件。

## 处理方式

1. 查看文件内容，确定正确的分类
2. 手动将文件移动到对应的分类目录
3. 如果确实无法分类，可以留在此目录中

## 常见情况

- 多重题材混合的小说
- 关键词不明确的小说
- 新类型或特殊题材的小说
- 文件内容过短无法准确判断

请定期处理此目录中的文件，保持分类系统的准确性。
"""
        readme_path = dir_path / "目录说明.txt"
        readme_path.write_text(content, encoding='utf-8')
    
    def _create_init_record(self, record_path: Path, library_path: str):
        """创建初始化记录文件"""
        record = {
            "library_path": library_path,
            "initialized_at": datetime.now().isoformat(),
            "version": "1.0",
            "created_directories": self.standard_dirs,
            "total_directories": len(self.standard_dirs),
            "initialization_source": "GUI工具自动创建"
        }
        
        with open(record_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    
    def validate_library_structure(self, library_path: str) -> Dict:
        """
        验证小说库目录结构的完整性
        
        Args:
            library_path: 小说库根目录路径
            
        Returns:
            Dict: 验证结果
        """
        result = {
            "is_valid": False,
            "missing_dirs": [],
            "extra_files": [],
            "recommendations": []
        }
        
        try:
            library_dir = Path(library_path)
            
            if not library_dir.exists():
                result["recommendations"].append("目标目录不存在")
                return result
            
            # 检查必需目录
            for dir_name in self.standard_dirs:
                dir_path = library_dir / dir_name
                if not dir_path.exists():
                    result["missing_dirs"].append(dir_name)
            
            # 检查是否有初始化记录
            init_record = library_dir / "初始化记录.json"
            if not init_record.exists():
                result["recommendations"].append("缺少初始化记录文件")
            
            # 判断是否有效
            result["is_valid"] = len(result["missing_dirs"]) == 0
            
            if result["missing_dirs"]:
                result["recommendations"].append(f"缺少目录: {', '.join(result['missing_dirs'])}")
            
            if result["is_valid"]:
                result["recommendations"].append("小说库结构完整")
                
        except Exception as e:
            result["recommendations"].append(f"验证过程发生错误: {str(e)}")
            
        return result
    
    def get_library_info(self, library_path: str) -> Dict:
        """
        获取小说库基本信息
        
        Args:
            library_path: 小说库根目录路径
            
        Returns:
            Dict: 小说库信息
        """
        info = {
            "path": library_path,
            "exists": False,
            "is_initialized": False,
            "total_files": 0,
            "category_stats": {},
            "init_info": None
        }
        
        try:
            library_dir = Path(library_path)
            
            if not library_dir.exists():
                return info
                
            info["exists"] = True
            
            # 检查是否已初始化
            init_record = library_dir / "初始化记录.json"
            if init_record.exists():
                info["is_initialized"] = True
                try:
                    with open(init_record, 'r', encoding='utf-8') as f:
                        info["init_info"] = json.load(f)
                except:
                    pass
            
            # 统计各分类目录的文件数量
            for dir_name in self.standard_dirs:
                dir_path = library_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    # 只统计.txt文件
                    txt_files = list(dir_path.glob("*.txt"))
                    info["category_stats"][dir_name] = len(txt_files)
                    info["total_files"] += len(txt_files)
                else:
                    info["category_stats"][dir_name] = 0
                    
        except Exception as e:
            info["error"] = str(e)
            
        return info
