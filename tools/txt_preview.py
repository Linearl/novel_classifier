#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT文件预览工具（集成编码修复功能）
用于读取txt文件的前10000个字符，避免读取完整文件导致上下文超出限制
当遇到编码问题时，自动调用编码修复功能

功能特点：
1. 智能编码检测，支持多种中文编码（utf-8, gbk, gb2312, utf-16, big5）
2. 自动编码修复：遇到乱码时自动修复编码问题
3. 限制读取字符数，避免内存溢出和上下文超出
4. 错误处理机制，确保程序稳定运行
5. 详细的输出信息，包括编码类型和字符统计
6. 支持提取文件开头和随机片段，更全面地反映内容

使用场景：
- 快速预览大型小说文件的开头内容
- 结合随机片段，更准确地判断文件类型
- 检查文件编码和格式是否正确
- 批量处理文件时的内容识别
- 自动修复编码问题的文件

作者：AI Assistant
版本：2.1（增加随机片段提取功能）
更新日期：2025年6月28日
"""

import sys
import os
import argparse
import random
from pathlib import Path

def get_file_content(file_path, max_chars=None):
    """
    使用多种编码尝试读取整个或部分文件内容。
    
    Args:
        file_path (str): 文件路径。
        max_chars (int, optional): 最大读取字符数。如果为None，则读取整个文件。

    Returns:
        tuple: (文件内容, 使用的编码) 或 (None, None) 如果失败。
    """
    # 优先尝试中文编码
    encodings = [
        'utf-8', 'gbk', 'gb2312', 'utf-16', 'big5',
        'iso-8859-1', 'cp1252', 'latin-1', 'ascii',
        'utf-16le', 'utf-16be', 'utf-32'
    ]
    
    # 第一轮：直接文本模式读取
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read(max_chars) if max_chars else f.read()
                # 检查是否包含中文字符，如果是乱码会很少有中文
                chinese_char_count = sum(1 for char in content[:100] if '\u4e00' <= char <= '\u9fff')
                if chinese_char_count > 5 or encoding in ['utf-8', 'gbk', 'gb2312']:
                    print(f"✓ 成功使用编码: {encoding} (中文字符: {chinese_char_count}/100)")
                    return content, encoding
                else:
                    print(f"⚠ 尝试编码 {encoding} - 疑似乱码，继续尝试其他编码")
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue
    
    # 第二轮：二进制模式读取后解码
    try:
        with open(file_path, 'rb') as f:
            raw_content = f.read(max_chars * 4 if max_chars else -1)  # 中文字符可能占用2-4字节
            for encoding in encodings:
                try:
                    content = raw_content.decode(encoding, errors='ignore')
                    if content.strip():  # 确保解码后有有效内容
                        chinese_char_count = sum(1 for char in content[:100] if '\u4e00' <= char <= '\u9fff')
                        if chinese_char_count > 5:
                            print(f"✓ 成功使用编码 (二进制模式): {encoding} (中文字符: {chinese_char_count}/100)")
                            return content[:max_chars] if max_chars else content, encoding
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception:
                    continue
    except Exception:
        pass
    
    # 最后尝试：使用错误处理策略强制读取
    for encoding in ['gbk', 'gb2312', 'utf-8', 'iso-8859-1']:
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read(max_chars) if max_chars else f.read()
                print(f"✓ 成功使用编码 (容错模式): {encoding}")
                return content, encoding
        except Exception:
            continue
        
    return None, None

def preview_txt_file(file_path, begin_chars=3000, fragment_count=0, fragment_size=300):
    """
    预览txt文件的开头，并可选择性地提取随机片段。

    Args:
        file_path (str): 文件路径。
        begin_chars (int): 开头要提取的字符数。
        fragment_count (int): 要提取的随机片段数量。
        fragment_size (int): 每个随机片段的大小（字符数）。

    Returns:
        str: 包含开头和随机片段的预览文本。
    """
    output = []
    
    full_content, encoding = get_file_content(file_path)
    
    if not full_content:
        # 如果读取失败，尝试调用旧的修复逻辑（如果存在）
        print("⚠ 检测到编码问题，尝试自动修复...")
        try:
            # 尝试导入编码修复器
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from workflows.encoding_fix import EncodingFixer
            fixer = EncodingFixer()
            result = fixer.fix_file_encoding(file_path, create_backup=True)
            
            if result['success'] and result['original_encoding'] != 'utf-8':
                print(f"✓ 编码修复成功: {result['message']}")
                print(f"  备份文件: {result['backup_file']}")
                # 重新尝试读取修复后的文件
                full_content, encoding = get_file_content(file_path)
                if full_content:
                    chinese_char_count = sum(1 for char in full_content[:100] if '\u4e00' <= char <= '\u9fff')
                    print(f"✓ 修复后重新读取成功 (中文字符: {chinese_char_count}/100)")
            else:
                print(f"⚠ 编码修复结果: {result['message']}")
        except ImportError:
            print("⚠ 编码修复工具不可用")
            return f"❌ 无法读取文件: {file_path}，且编码修复工具不可用。"
        except Exception as e:
            print(f"⚠ 编码修复失败: {e}")
            return f"❌ 读取和修复文件时发生严重错误: {e}"

    if not full_content:
        return f"❌ 最终无法读取文件: {file_path}"

    print(f"✓ 成功使用编码: {encoding}")

    # 1. 提取开头部分
    if begin_chars > 0:
        output.append("=== [文件开头片段] ===")
        output.append(full_content[:begin_chars].strip())
        output.append("===")
        output.append("")

    # 2. 提取随机片段
    if fragment_count > 0:
        content_len = len(full_content)
        # 确保我们不在开头部分重复取样
        start_offset = begin_chars if content_len > begin_chars else 0
        
        if content_len > start_offset + fragment_size:
            output.append("=== [文件随机片段] ===")
            
            for i in range(fragment_count):
                # 随机选择一个起始点
                random_start = random.randint(start_offset, max(start_offset, content_len - fragment_size - 1))
                fragment = full_content[random_start : random_start + fragment_size]
                
                output.append(f"--- 片段 {i+1} (从字符 {random_start} 开始) ---")
                output.append(fragment.strip())
            
            output.append("===")

    return "\n".join(output)

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(
        description="TXT文件预览工具，支持提取开头和随机内容片段。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="要预览的TXT文件的路径。"
    )
    parser.add_argument(
        "--begin",
        type=int,
        default=2000,
        help="从文件开头提取的字符数。\n默认值: 2000"
    )
    parser.add_argument(
        "--fragment",
        type=int,
        default=5,
        help="要随机抽取的片段数量。\n默认值: 5"
    )
    parser.add_argument(
        "--fragment-size",
        type=int,
        default=400,
        help="每个随机片段的大小（字符数）。\n默认值: 400"
    )
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    # 为了兼容旧的调用方式 `python txt_preview.py "filename" 3000`
    if len(sys.argv) == 3 and sys.argv[2].isdigit():
        file_path = sys.argv[1]
        begin_chars = int(sys.argv[2])
        fragment_count = 0
        fragment_size = 0
        print("提示：检测到旧版调用方式，已兼容。建议使用新的命令行参数格式。")
        preview_content = preview_txt_file(file_path, begin_chars, fragment_count, fragment_size)
        print(preview_content)
        return

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"错误: 文件不存在 -> {args.file_path}")
        sys.exit(1)

    preview_content = preview_txt_file(
        args.file_path,
        args.begin,
        args.fragment,
        args.fragment_size
    )
    print(preview_content)

if __name__ == "__main__":
    main()