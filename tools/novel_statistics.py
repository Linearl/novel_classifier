#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说分类统计脚本
统计各分类文件夹中的文件数量和百分比
"""

import os
import sys
import glob
from collections import defaultdict

# 设置标准输出编码，避免在Windows上的编码问题
if sys.platform.startswith('win'):
    import locale
    # 尝试设置控制台编码为UTF-8
    try:
        # 在Windows上设置环境变量以支持UTF-8输出
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # 重新配置stdout的编码
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        # 如果重新配置失败，使用系统默认编码
        pass

def count_files_in_directory(directory_path):
    """统计目录中的txt文件数量"""
    if not os.path.exists(directory_path):
        return 0
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    return len(txt_files)

def detect_novel_library_root(potential_path):
    """智能检测小说库根目录"""
    potential_path = os.path.normpath(potential_path)
    
    # 定义分类目录标识
    category_indicators = ["00-待分类", "00-二次确认", "01-玄幻", "02-奇幻", "03-武侠"]
    
    # 检查当前路径是否直接包含分类目录
    found_categories = 0
    for indicator in category_indicators:
        if os.path.exists(os.path.join(potential_path, indicator)):
            found_categories += 1
    
    # 如果当前路径包含多个分类目录，则认为这是小说库根目录
    if found_categories >= 2:
        return potential_path
    
    # 否则检查是否存在"小说库"子目录
    traditional_path = os.path.join(potential_path, "小说库")
    if os.path.exists(traditional_path):
        # 检查传统路径下是否有分类目录
        traditional_found = 0
        for indicator in category_indicators:
            if os.path.exists(os.path.join(traditional_path, indicator)):
                traditional_found += 1
        
        if traditional_found >= 2:
            return traditional_path
    
    # 如果都没找到，返回原路径
    return potential_path

def get_classification_statistics(base_path="/Volumes/980pro/待整理/小说库"):
    """获取各分类的统计信息"""
    # 智能检测小说库根目录
    base_path = detect_novel_library_root(base_path)
    print(f"🔍 检测到小说库根目录: {base_path}")
    
    categories = {
        "00-待分类": "待分类",
        "00-二次确认": "二次确认", 
        "01-玄幻": "玄幻",
        "02-奇幻": "奇幻",
        "03-武侠": "武侠",
        "04-仙侠": "仙侠",
        "05-都市": "都市",
        "06-历史": "历史",
        "07-军事": "军事",
        "08-游戏": "游戏",
        "09-竞技": "竞技",
        "10-科幻": "科幻",
        "11-灵异": "灵异",
        "12-同人": "同人",
        "99-知名作者专区": "知名作者"
    }
    
    stats = {}
    total_files = 0
    
    print("📊 小说分类统计报告")
    print("=" * 50)
    
    # 统计各分类文件数量
    for folder_name, display_name in categories.items():
        folder_path = os.path.join(base_path, folder_name)
        file_count = count_files_in_directory(folder_path)
        stats[folder_name] = {
            'name': display_name,
            'count': file_count,
            'path': folder_path
        }
        total_files += file_count
    
    # 计算百分比
    for folder_name in stats:
        if total_files > 0:
            stats[folder_name]['percentage'] = (stats[folder_name]['count'] / total_files) * 100
        else:
            stats[folder_name]['percentage'] = 0
    
    return stats, total_files

def print_statistics_report(stats, total_files):
    """打印统计报告"""
    print(f"📈 总文件数：{total_files:,} 个")
    print()
    
    # 按文件数量排序
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    print("🏆 分类排名（按文件数量）:")
    print("-" * 60)
    print(f"{'排名':<4} {'分类':<12} {'文件数':<8} {'百分比':<8} {'状态'}")
    print("-" * 60)
    
    for rank, (folder_name, data) in enumerate(sorted_stats, 1):
        status = ""
        if folder_name == "00-二次确认":
            status = "⚠️ 需处理"
        elif folder_name == "00-待分类":
            status = "📥 待分类"
        elif data['count'] == 0:
            status = "📭 空"
        else:
            status = "✅ 已分类"
            
        print(f"{rank:<4} {data['name']:<12} {data['count']:<8,} {data['percentage']:<7.1f}% {status}")
    
    print("-" * 60)
    
    # 计算处理进度
    pending_files = stats.get("00-二次确认", {}).get('count', 0)
    unclassified_files = stats.get("00-待分类", {}).get('count', 0)
    classified_files = total_files - pending_files - unclassified_files
    
    if total_files > 0:
        progress_percentage = (classified_files / total_files) * 100
        print(f"\n📋 处理进度统计:")
        print(f"   已分类文件：{classified_files:,} 个 ({progress_percentage:.1f}%)")
        print(f"   二次确认：{pending_files:,} 个 ({(pending_files/total_files)*100:.1f}%)")
        print(f"   待分类：{unclassified_files:,} 个 ({(unclassified_files/total_files)*100:.1f}%)")
    
    print("\n" + "=" * 50)

def print_detailed_analysis(stats):
    """打印详细分析"""
    print("\n📝 详细分析:")
    
    # 主要分类统计（排除特殊文件夹）
    main_categories = {}
    for folder_name, data in stats.items():
        if not folder_name.startswith("00-") and not folder_name.startswith("99-"):
            main_categories[folder_name] = data
    
    if main_categories:
        main_total = sum(data['count'] for data in main_categories.values())
        print(f"   主要分类总计：{main_total:,} 个文件")
        
        # 找出最大和最小的分类
        max_category = max(main_categories.items(), key=lambda x: x[1]['count'])
        min_category = min(main_categories.items(), key=lambda x: x[1]['count'])
        
        print(f"   最大分类：{max_category[1]['name']} ({max_category[1]['count']:,} 个)")
        print(f"   最小分类：{min_category[1]['name']} ({min_category[1]['count']:,} 个)")
        
        # 热门分类（超过平均值的分类）
        if main_total > 0:
            average = main_total / len(main_categories)
            popular_categories = [data['name'] for data in main_categories.values() if data['count'] > average]
            if popular_categories:
                print(f"   热门分类：{', '.join(popular_categories)}")

def main():
    """主函数"""
    import sys
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            base_path = sys.argv[1]
            # 确保路径使用正确的分隔符
            base_path = os.path.normpath(base_path)
        else:
            base_path = "小说库"  # 默认路径
        
        # 检查路径是否存在
        if not os.path.exists(base_path):
            print(f"❌ 错误：指定的路径不存在: {base_path}")
            return None, 0
            
        print(f"📁 正在分析路径: {base_path}")
        
        stats, total_files = get_classification_statistics(base_path)
        print_statistics_report(stats, total_files)
        print_detailed_analysis(stats)
        
        # 返回统计数据供其他脚本使用
        return stats, total_files
        
    except Exception as e:
        print(f"❌ 统计过程中出现错误：{e}")
        import traceback
        traceback.print_exc()
        return None, 0

if __name__ == "__main__":
    main()