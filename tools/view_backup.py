#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份文件查看工具

用于正确查看编码修复过程中的备份文件
因为备份文件保持原始编码，需要用对应的编码方式打开
"""

import chardet
from pathlib import Path
import sys

def detect_and_read_file(file_path):
    """检测并读取文件"""
    try:
        # 检测编码
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        encoding_result = chardet.detect(raw_data)
        encoding = encoding_result.get('encoding', 'utf-8')
        confidence = encoding_result.get('confidence', 0)
        
        print(f"文件: {file_path.name}")
        print(f"检测编码: {encoding} (置信度: {confidence:.2f})")
        
        # 尝试读取内容
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            # 如果失败，尝试其他常见编码
            for fallback_encoding in ['gbk', 'gb2312', 'utf-8', 'latin1']:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        content = f.read()
                    print(f"实际使用编码: {fallback_encoding}")
                    return content, fallback_encoding
                except UnicodeDecodeError:
                    continue
            
            # 如果都失败了，用errors='ignore'读取
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            print("警告: 使用UTF-8忽略错误方式读取")
            return content, 'utf-8-ignore'
            
    except Exception as e:
        return f"读取文件失败: {e}", None

def view_backup_file(backup_file_path):
    """查看单个备份文件"""
    file_path = Path(backup_file_path)
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    content, encoding = detect_and_read_file(file_path)
    
    print("=" * 50)
    print("文件内容预览（前500字符）:")
    print("=" * 50)
    print(content[:500])
    if len(content) > 500:
        print("...")
        print(f"（文件总长度: {len(content)} 字符）")

def view_backup_directory(backup_dir_path):
    """查看备份目录中的所有文件"""
    backup_dir = Path(backup_dir_path)
    
    if not backup_dir.exists():
        print(f"备份目录不存在: {backup_dir}")
        return
    
    txt_files = list(backup_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"备份目录中没有找到txt文件: {backup_dir}")
        return
    
    print(f"找到 {len(txt_files)} 个备份文件:")
    
    for i, file_path in enumerate(txt_files, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(txt_files)}] {file_path.name}")
        print(f"{'='*60}")
        
        content, encoding = detect_and_read_file(file_path)
        
        # 显示内容预览
        print("内容预览（前200字符）:")
        print("-" * 40)
        print(content[:200])
        if len(content) > 200:
            print("...")
        print("-" * 40)
        print()

def main():
    """主函数"""
    print("备份文件查看工具")
    print("="*50)
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        target_path = Path(target)
        
        if target_path.is_file():
            view_backup_file(target)
        elif target_path.is_dir():
            view_backup_directory(target)
        else:
            print(f"路径不存在: {target}")
    else:
        # 默认查看最新的备份目录
        default_backup_dir = Path(r"d:\3.娱乐\小说整理\小说库\00-待分类\backup\encoding_fix_20250628_141329")
        
        if default_backup_dir.exists():
            print(f"查看默认备份目录: {default_backup_dir}")
            view_backup_directory(default_backup_dir)
        else:
            print("使用方法:")
            print("  python view_backup.py <文件或目录路径>")
            print("  python view_backup.py  # 查看默认备份目录")

if __name__ == "__main__":
    main()
