#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复破损文件名脚本
检测并修复文件名不完整的文件，特别是那些导致文件变成0字节的文件
"""

import os
import sys
import glob
import shutil
from pathlib import Path

def detect_broken_files(directory):
    """检测破损的文件"""
    broken_files = []
    
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return broken_files
    
    for file_path in glob.glob(os.path.join(directory, "*.txt")):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # 检测可能的问题
        issues = []
        
        # 1. 检查0字节文件
        if file_size == 0:
            issues.append("0字节文件")
        
        # 2. 检查文件名不完整（以【得分接近 结尾但没有完整的评分信息）
        if "【得分接近" in filename and not filename.endswith("】.txt"):
            issues.append("文件名不完整")
        
        # 3. 检查文件名以【开头但没有结尾】
        if "【" in filename and not "】" in filename:
            issues.append("缺少文件名结尾")
        
        if issues:
            broken_files.append({
                'path': file_path,
                'filename': filename,
                'size': file_size,
                'issues': issues
            })
    
    return broken_files

def suggest_filename_fix(filename):
    """建议修复的文件名"""
    if "【得分接近" in filename and not filename.endswith(】.txt"):
        # 补全评分区间标记
        if filename.endswith("【得分接近"):
            return filename + " (15分)】.txt"
        else:
            # 检查是否有部分评分信息
            return filename + "】.txt"
    
    if "【" in filename and not "】" in filename:
        return filename + "】.txt"
    
    return filename

def fix_broken_files(directory, dry_run=True):
    """修复破损文件"""
    broken_files = detect_broken_files(directory)
    
    if not broken_files:
        print("✅ 未发现破损文件")
        return True
    
    print(f"🔍 发现 {len(broken_files)} 个可能有问题的文件:")
    print("=" * 80)
    
    for i, file_info in enumerate(broken_files, 1):
        print(f"{i}. {file_info['filename']}")
        print(f"   大小: {file_info['size']} 字节")
        print(f"   问题: {', '.join(file_info['issues'])}")
        
        if "文件名不完整" in file_info['issues'] or "缺少文件名结尾" in file_info['issues']:
            suggested_name = suggest_filename_fix(file_info['filename'])
            print(f"   建议修复为: {suggested_name}")
        
        print()
    
    if dry_run:
        print("⚠️  这是预览模式，没有实际修改文件")
        print("   如需实际修复，请运行: python fix_broken_filenames.py <目录> --fix")
        return True
    
    # 实际修复
    print("🔧 开始修复文件...")
    
    for file_info in broken_files:
        try:
            if file_info['size'] == 0:
                # 0字节文件，询问是否删除
                print(f"⚠️  发现0字节文件: {file_info['filename']}")
                print("   建议删除该文件（可能是文件名损坏导致的残留文件）")
                # 在自动模式下，移动到backup目录而不是直接删除
                backup_dir = os.path.join(os.path.dirname(file_info['path']), "backup")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f"broken_{file_info['filename']}")
                shutil.move(file_info['path'], backup_path)
                print(f"   已移动到备份目录: {backup_path}")
                continue
            
            if "文件名不完整" in file_info['issues'] or "缺少文件名结尾" in file_info['issues']:
                suggested_name = suggest_filename_fix(file_info['filename'])
                new_path = os.path.join(os.path.dirname(file_info['path']), suggested_name)
                
                if os.path.exists(new_path):
                    print(f"⚠️  目标文件已存在: {suggested_name}")
                    continue
                
                shutil.move(file_info['path'], new_path)
                print(f"✅ 已修复: {file_info['filename']} -> {suggested_name}")
        
        except Exception as e:
            print(f"❌ 修复失败 {file_info['filename']}: {e}")
    
    print("🎉 文件修复完成")
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python fix_broken_filenames.py <目录> [--fix]")
        print("示例: python fix_broken_filenames.py \"d:\\3.娱乐\\novel_classification\\2\\00-二次确认\"")
        print("     python fix_broken_filenames.py \"d:\\3.娱乐\\novel_classification\\2\\00-二次确认\" --fix")
        return
    
    directory = sys.argv[1]
    fix_mode = "--fix" in sys.argv
    
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    print(f"🔍 检查目录: {directory}")
    print(f"💾 修复模式: {'启用' if fix_mode else '预览'}")
    print()
    
    fix_broken_files(directory, dry_run=not fix_mode)

if __name__ == "__main__":
    main()
