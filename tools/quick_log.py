#!/usr/bin/env python3
"""
简化的分类记录工具 - 专门用于AI手动分类工作流
提供快速追加关键词和分类日志的功能
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def log_keywords(base_path, category, keywords_text, description=""):
    """
    快速记录新关键词
    
    Args:
        base_path: 小说库根目录路径
        category: 分类名称（如"历史类"、"游戏类"）
        keywords_text: 关键词描述文本
        description: 额外描述
    """
    file_path = os.path.join(base_path, "new_keywords_discovered.txt")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"\n## {category}关键词补充 - {timestamp}\n{keywords_text}\n"
    if description:
        content += f"# {description}\n"
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已记录{category}关键词")


def log_classification(base_path, filename, title, category, reason, keywords="", status="已处理"):
    """
    快速记录分类结果
    
    Args:
        base_path: 小说库根目录路径
        filename: 原文件名
        title: 小说标题
        category: 目标分类
        reason: 分析理由
        keywords: 新发现关键词
        status: 处理状态
    """
    file_path = os.path.join(base_path, "logs", "manual_classification_log.txt")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""
### 文件：{filename}
- **原标题**：{title}
- **目标分类**：{category}
- **分析时间**：{timestamp}
- **分析理由**：{reason}
- **新关键词**：{keywords}
- **处理状态**：{status}

"""
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已记录分类日志：{title} → {category}")


def main():
    """命令行接口"""
    if len(sys.argv) < 4:
        print("使用方法:")
        print("  记录关键词: python quick_log.py 小说库路径 keywords 分类名 关键词描述")
        print("  记录分类: python quick_log.py 小说库路径 classification 文件名 标题 分类 理由 [关键词] [状态]")
        sys.exit(1)
    
    base_path = sys.argv[1]
    action = sys.argv[2]
    
    try:
        if action == "keywords":
            if len(sys.argv) < 5:
                print("❌ 关键词模式需要: 分类名 关键词描述")
                sys.exit(1)
            log_keywords(base_path, sys.argv[3], sys.argv[4], 
                        sys.argv[5] if len(sys.argv) > 5 else "")
                        
        elif action == "classification":
            if len(sys.argv) < 7:
                print("❌ 分类模式需要: 文件名 标题 分类 理由")
                sys.exit(1)
            log_classification(base_path, sys.argv[3], sys.argv[4], sys.argv[5], 
                             sys.argv[6], 
                             sys.argv[7] if len(sys.argv) > 7 else "",
                             sys.argv[8] if len(sys.argv) > 8 else "已处理")
        else:
            print(f"❌ 未知操作: {action}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
