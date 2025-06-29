#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说文件重命名工具（临时目录版本）
检查以数字命名的txt文件，从文件内容中提取书名并重命名
"""

import os
import re
import chardet
import sys
from pathlib import Path

def detect_encoding(file_path):
    """检测文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 读取前10KB来检测编码
            result = chardet.detect(raw_data)
            return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
    except:
        return 'utf-8'

def read_file_content(file_path, max_lines=50):
    """读取文件前几行内容"""
    encoding = detect_encoding(file_path)
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.strip())
            return lines
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")
        return []

def extract_book_title(lines):
    """从文件内容中提取书名"""
    # 常见的书名模式
    patterns = [
        r'《(.+?)》',  # 《书名》
        r'书名[:：]\s*(.+)',  # 书名: 书名
        r'篇名[:：]\s*(.+)',  # 篇名: 书名
        r'作品[:：]\s*(.+)',  # 作品: 书名
        r'小说[:：]\s*(.+)',  # 小说: 书名
        r'标题[:：]\s*(.+)',  # 标题: 书名
        r'题目[:：]\s*(.+)',  # 题目: 书名
        r'^(.+?)\s*作者[:：]',  # 书名 作者:
        r'^(.+?)\s*著',  # 书名 著
        r'第一章\s*(.+)',  # 第一章 章节名（可能包含书名）
    ]
    
    # 检查前几行
    for line in lines[:20]:  # 只检查前20行
        if not line or len(line.strip()) < 2:
            continue
            
        # 移除常见的无关内容
        line = re.sub(r'^第[一二三四五六七八九十\d]+[章节]', '', line)
        line = re.sub(r'^\d+\.', '', line)
        line = line.strip()
        
        if len(line) < 2:
            continue
            
        # 尝试各种模式
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # 清理标题
                title = clean_title(title)
                if is_valid_title(title):
                    return title
    
    # 如果没有找到明确的书名，尝试使用第一行非空内容
    for line in lines[:5]:
        if line and len(line.strip()) > 2:
            title = clean_title(line.strip())
            if is_valid_title(title):
                return title
    
    return None

def clean_title(title):
    """清理书名"""
    # 移除常见的无关词汇
    unwanted_patterns = [
        r'第[一二三四五六七八九十\d]+[章节].*',
        r'^\d+\..*',
        r'正文.*',
        r'序章.*',
        r'楔子.*',
        r'前言.*',
        r'目录.*',
        r'内容简介.*',
        r'作者.*',
        r'www\..*',
        r'http.*',
        r'来源.*',
        r'转载.*',
        r'整理.*',
        r'校对.*',
        r'txt.*',
    ]
    
    for pattern in unwanted_patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # 移除特殊字符
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    # 移除多余空格
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def is_valid_title(title):
    """判断是否是有效的书名"""
    if not title or len(title) < 2:
        return False
    
    # 排除明显不是书名的内容
    invalid_patterns = [
        r'^\d+$',  # 纯数字
        r'^第\d+章',  # 第X章
        r'^chapter\s*\d+',  # chapter X
        r'^www\.',  # 网址
        r'^http',  # 网址
        r'^\s*$',  # 空白
        r'^[a-zA-Z]+$',  # 纯英文字母
        r'^[\W]+$',  # 纯特殊字符
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, title, re.IGNORECASE):
            return False
    
    # 书名长度限制
    if len(title) > 50:
        return False
        
    return True

def is_numeric_filename(filename):
    """判断文件名是否是纯数字或以数字开头"""
    name = Path(filename).stem
    # 纯数字文件名
    if name.isdigit():
        return True
    # 数字开头文件名（如 "123xxx.txt"）
    if name and name[0].isdigit():
        return True
    return False

def rename_file(old_path, new_title):
    """重命名文件"""
    old_path = Path(old_path)
    parent_dir = old_path.parent
    extension = old_path.suffix
    
    # 构造新文件名
    new_filename = f"《{new_title}》{extension}"
    new_path = parent_dir / new_filename
    
    # 如果新文件名已存在，添加序号
    counter = 1
    while new_path.exists():
        new_filename = f"《{new_title}》({counter}){extension}"
        new_path = parent_dir / new_filename
        counter += 1
    
    try:
        old_path.rename(new_path)
        return new_path
    except Exception as e:
        print(f"重命名失败: {old_path} -> {new_path}, 错误: {e}")
        return None

def main():
    """主函数"""
    # 设置要处理的目录
    target_dir = "/Volumes/980pro/待整理/temp_renaming"
    
    # 如果提供了命令行参数，使用第一个参数作为目标目录
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    
    base_dir = Path(target_dir)
    
    # 打印当前工作目录和目标目录
    print(f"当前工作目录: {os.getcwd()}")
    print(f"目标处理目录: {base_dir}")
    
    # 确认目录存在
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"错误: 目录 '{base_dir}' 不存在或不是一个有效的目录")
        return
    
    # 找出所有数字命名的txt文件
    numeric_files = []
    for file_path in base_dir.glob("*.txt"):
        # 过滤掉._开头的macOS隐藏文件
        if not file_path.name.startswith("._") and is_numeric_filename(file_path.name):
            numeric_files.append(file_path)
    
    # 也查找TXT文件（大写扩展名）
    for file_path in base_dir.glob("*.TXT"):
        if not file_path.name.startswith("._") and is_numeric_filename(file_path.name):
            numeric_files.append(file_path)
    
    # 更可靠的判断：根据文件名检查是否是数字命名
    numeric_files = [f for f in numeric_files if is_numeric_filename(f.name)]
    
    print(f"找到 {len(numeric_files)} 个数字命名的txt文件")
    if len(numeric_files) == 0:
        # 列出目录中所有文件以便调试
        print("目录中的所有文件:")
        all_files = list(base_dir.glob("*"))
        for f in all_files:
            print(f"  - {f.name}")
        return
    
    renamed_count = 0
    failed_files = []
    
    for file_path in numeric_files:
        print(f"\n处理文件: {file_path.name}")
        
        # 读取文件内容
        lines = read_file_content(file_path)
        if not lines:
            print(f"  无法读取文件内容")
            failed_files.append(file_path.name)
            continue
        
        # 提取书名
        title = extract_book_title(lines)
        if not title:
            print(f"  未能提取到有效书名")
            print(f"  文件前几行: {lines[:3]}")
            failed_files.append(file_path.name)
            continue
        
        print(f"  提取到书名: {title}")
        
        # 重命名文件
        new_path = rename_file(file_path, title)
        if new_path:
            print(f"  重命名成功: {new_path.name}")
            renamed_count += 1
        else:
            failed_files.append(file_path.name)
    
    print(f"\n\n=== 处理完成 ===")
    print(f"成功重命名: {renamed_count} 个文件")
    print(f"失败文件数: {len(failed_files)}")
    
    if failed_files:
        print("\n失败的文件:")
        for filename in failed_files:
            print(f"  - {filename}")

if __name__ == "__main__":
    main()