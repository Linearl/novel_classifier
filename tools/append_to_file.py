#!/usr/bin/env python3
"""
文件追加工具 - 高效追加内容到指定文件
支持关键词记录和分类日志的格式化追加
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

def append_keywords(file_path, title, category, keywords_data, analysis_reason):
    """
    追加新关键词记录到关键词发现文件
    
    Args:
        file_path: 目标文件路径
        title: 小说标题
        category: 分类目录
        keywords_data: 关键词数据字典 {权重: [关键词列表]}
        analysis_reason: 分析理由
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 格式化内容
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"\n## {category}类关键词补充 - {timestamp}\n"
    
    for weight_desc, keywords in keywords_data.items():
        if keywords:
            content += f"- {', '.join(keywords)}：{weight_desc}\n"
    
    if analysis_reason:
        content += f"- 分析理由：{analysis_reason}\n"
    
    # 追加到文件
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已追加关键词记录到: {file_path}")


def append_classification_log(file_path, filename, title, category, analysis_time, 
                             analysis_reason, keywords, status):
    """
    追加分类日志记录到分类日志文件
    
    Args:
        file_path: 目标文件路径
        filename: 原文件名
        title: 小说标题
        category: 目标分类
        analysis_time: 分析时间
        analysis_reason: 分析理由
        keywords: 新发现关键词
        status: 处理状态
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 格式化内容
    content = f"""
### 文件：{filename}
- **原标题**：{title}
- **目标分类**：{category}
- **分析时间**：{analysis_time}
- **分析理由**：
  {analysis_reason}
- **新关键词**：{keywords}
- **处理状态**：{status}

"""
    
    # 追加到文件
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已追加分类日志到: {file_path}")


def append_simple_text(file_path, content):
    """
    简单的文本追加功能
    
    Args:
        file_path: 目标文件路径
        content: 要追加的内容
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 追加到文件
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')
    
    print(f"✅ 已追加内容到: {file_path}")


def main():
    parser = argparse.ArgumentParser(description='文件追加工具')
    parser.add_argument('file_path', help='目标文件路径')
    parser.add_argument('--type', choices=['keywords', 'log', 'text'], 
                       default='text', help='追加类型')
    
    # 关键词追加参数
    parser.add_argument('--title', help='小说标题')
    parser.add_argument('--category', help='分类目录')
    parser.add_argument('--keywords', help='关键词（JSON格式）')
    parser.add_argument('--reason', help='分析理由')
    
    # 日志追加参数
    parser.add_argument('--filename', help='原文件名')
    parser.add_argument('--analysis-time', help='分析时间')
    parser.add_argument('--status', help='处理状态')
    
    # 简单文本追加
    parser.add_argument('--content', help='要追加的文本内容')
    
    args = parser.parse_args()
    
    try:
        if args.type == 'keywords':
            if not all([args.title, args.category, args.keywords, args.reason]):
                print("❌ 关键词模式需要提供 --title, --category, --keywords, --reason 参数")
                sys.exit(1)
            
            # 解析关键词数据（简单格式：权重描述:关键词1,关键词2）
            keywords_data = {}
            for item in args.keywords.split(';'):
                if ':' in item:
                    weight_desc, kw_str = item.split(':', 1)
                    keywords_data[weight_desc.strip()] = [kw.strip() for kw in kw_str.split(',')]
            
            append_keywords(args.file_path, args.title, args.category, 
                          keywords_data, args.reason)
                          
        elif args.type == 'log':
            if not all([args.filename, args.title, args.category, args.reason]):
                print("❌ 日志模式需要提供 --filename, --title, --category, --reason 参数")
                sys.exit(1)
            
            analysis_time = args.analysis_time or datetime.now().strftime("%Y-%m-%d %H:%M")
            append_classification_log(args.file_path, args.filename, args.title, 
                                    args.category, analysis_time, args.reason,
                                    args.keywords or "", args.status or "已处理")
                                    
        elif args.type == 'text':
            if not args.content:
                print("❌ 文本模式需要提供 --content 参数")
                sys.exit(1)
            
            append_simple_text(args.file_path, args.content)
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
