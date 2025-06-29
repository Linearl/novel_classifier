#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文件处理工作流
每批次处理10个文件，最多10个批次后暂停等待用户指令
"""

import os
import glob
import subprocess
from novel_statistics import get_classification_statistics

class BatchProcessor:
    def __init__(self, base_path="小说库/00-二次确认"):
        self.base_path = base_path
        self.analysis_path = os.path.join(base_path, "analysis")
        self.processed_files = []
        self.failed_files = []
        self.processing_start_time = None
        
    def setup_analysis_directory(self):
        """创建并准备 analysis 目录"""
        if os.path.exists(self.analysis_path):
            # 检查是否有文件，询问是否清理
            existing_files = glob.glob(os.path.join(self.analysis_path, "*.txt"))
            if existing_files:
                print(f"⚠️  发现 analysis 目录已存在且包含 {len(existing_files)} 个文件")
                response = input("是否清理旧的分析文件？(y/N): ")
                if response.lower() in ['y', 'yes']:
                    self.cleanup_analysis_directory()
                    print("✅ 已清理旧的分析文件")
        
        # 确保目录存在
        os.makedirs(self.analysis_path, exist_ok=True)
        print(f"📁 Analysis 目录已准备就绪: {self.analysis_path}")
        
    def cleanup_analysis_directory(self):
        """清理 analysis 目录"""
        if os.path.exists(self.analysis_path):
            import shutil
            try:
                shutil.rmtree(self.analysis_path)
                print(f"🗑️  已清理 analysis 目录: {self.analysis_path}")
                return True
            except Exception as e:
                print(f"❌ 清理 analysis 目录失败: {e}")
                return False
        return True
        
    def extract_all_content(self):
        """提取所有待处理文件的内容"""
        pending_files = self.get_pending_files()
        
        if not pending_files:
            print("✅ 没有待处理的文件")
            return True
            
        print(f"\n🚀 开始全量内容提取")
        print(f"📅 处理时间：{self.get_current_time()}")
        print(f"📋 待处理文件：{len(pending_files)} 个")
        print("===")
        
        self.processing_start_time = self.get_current_time()
        
        for i, file_path in enumerate(pending_files, 1):
            filename = os.path.basename(file_path)
            print(f"🔍 [{i}/{len(pending_files)}] 处理: {filename}")
            
            try:
                # 调用 txt_preview.py 提取内容
                analysis_file = os.path.join(self.analysis_path, filename)
                success = self._extract_file_content(file_path, analysis_file)
                
                if success:
                    self.processed_files.append(filename)
                    print(f"   ✅ 成功提取内容")
                else:
                    self.failed_files.append(filename)
                    print(f"   ❌ 提取失败")
                    
            except Exception as e:
                self.failed_files.append(filename)
                print(f"   ❌ 处理异常: {e}")
                
        # 生成处理报告
        self._generate_processing_report()
        return len(self.failed_files) == 0
    
    def _extract_file_content(self, source_file, analysis_file):
        """为单个文件提取内容"""
        try:
            # 构建 txt_preview.py 的调用命令
            import sys
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "txt_preview.py")
            
            # 调用 txt_preview.py
            result = subprocess.run(
                [sys.executable, script_path, source_file, "--begin", "3000", "--fragment", "10"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if result.returncode == 0:
                # 添加文件元信息
                content = self._format_analysis_content(source_file, result.stdout)
                
                # 写入分析文件
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                print(f"   ⚠️ txt_preview.py 返回错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ 处理超时")
            return False
        except Exception as e:
            print(f"   ⚠️ 提取异常: {e}")
            return False
    
    def _format_analysis_content(self, source_file, preview_content):
        """格式化分析文件内容"""
        file_size = os.path.getsize(source_file) if os.path.exists(source_file) else 0
        
        header = f"""=== 文件元信息 ===
原文件: {os.path.basename(source_file)}
原路径: {source_file}
处理时间: {self.get_current_time()}
文件大小: {file_size / 1024 / 1024:.2f} MB
提取参数: --begin 3000 --fragment 10 --fragment-size 300

=== 内容预览 ===
"""
        return header + preview_content
    
    def _generate_processing_report(self):
        """生成处理报告"""
        total_files = len(self.processed_files) + len(self.failed_files)
        success_rate = (len(self.processed_files) / total_files * 100) if total_files > 0 else 0
        
        print("\n===")
        print("📈 内容提取完成报告")
        print("===")
        print(f"开始时间: {self.processing_start_time}")
        print(f"完成时间: {self.get_current_time()}")
        print(f"总文件数: {total_files}")
        print(f"成功提取: {len(self.processed_files)} 个")
        print(f"提取失败: {len(self.failed_files)} 个")
        print(f"成功率: {success_rate:.1f}%")
        
        if self.failed_files:
            print(f"\n❌ 失败文件列表:")
            for i, filename in enumerate(self.failed_files, 1):
                print(f"  {i:2d}. {filename}")
                
        print("===")
        print("💡 下一步操作：")
        print("   1. 检查 analysis 目录下的分析文件")
        print("   2. 开始AI分析和分类决策")
        print("   3. 完成后运行清理命令清除 analysis 目录")
        print("===")
    
    def get_current_time(self):
        """获取当前时间的格式化字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_pending_files(self):
        """获取待处理文件列表"""
        pattern = os.path.join(self.base_path, "*.txt")
        files = glob.glob(pattern)
        # 按文件名排序，确保处理顺序一致
        files.sort()
        return files
    
    def analyze_file_type(self, filename):
        """分析文件类型和状态"""
        if "得分过低" in filename:
            return "小说", "待分类"
        elif "得分接近" in filename:
            return "小说", "需确认"
        elif filename.endswith('.txt'):
            return "小说", "待分析"
        else:
            return "其他", "跳过"
    
    def print_files_preview(self, files):
        """显示文件列表预览"""
        print(f"📋 待处理文件预览（{len(files)}个文件）:")
        print("=" * 80)
        print(f"{'序号':<4} {'文件名':<40} {'类型':<10} {'状态'}")
        print("=" * 80)
        
        for i, file_path in enumerate(files[:20], 1):  # 只显示前20个文件
            filename = os.path.basename(file_path)
            # 截断过长的文件名
            display_name = filename[:37] + "..." if len(filename) > 40 else filename
            file_type, status = self.analyze_file_type(filename)
            print(f"{i:<4} {display_name:<40} {file_type:<10} {status}")
        
        if len(files) > 20:
            print(f"... 还有 {len(files) - 20} 个文件未显示")
    
    def print_progress_summary(self):
        """打印进度总结"""
        stats, total_files = get_classification_statistics()
        pending_count = stats.get("00-二次确认", {}).get('count', 0)
        
        print(f"\n📊 当前进度总结:")
        print(f"   待处理文件：{pending_count} 个")
        
        if pending_count > 0:
            print(f"   预计处理时间：{pending_count * 2:.0f}-{pending_count * 5:.0f} 秒")
            
    def process_all_files(self):
        """处理所有文件的主流程"""
        # 1. 检查目录
        if not os.path.exists(self.base_path):
            print(f"❌ 工作目录不存在: {self.base_path}")
            return False
            
        # 2. 获取待处理文件
        pending_files = self.get_pending_files()
        if not pending_files:
            print("✅ 没有待处理的文件")
            return True
            
        # 3. 显示文件预览
        self.print_files_preview(pending_files)
        
        # 4. 设置 analysis 目录
        self.setup_analysis_directory()
        
        # 5. 提取所有文件内容
        success = self.extract_all_content()
        
        if success:
            print(f"\n🎉 所有文件处理完成！")
            print(f"📁 分析文件位置: {self.analysis_path}")
            print(f"📄 分析文件数量: {len(self.processed_files)}")
            return True
        else:
            print(f"\n⚠️ 处理完成，但有 {len(self.failed_files)} 个文件失败")
            return False
    
def main():
    """主函数"""
    processor = BatchProcessor()
    
    print("🔧 批量文件处理工作流")
    print("=" * 80)
    print("配置信息：")
    print(f"  目标目录：{processor.base_path}")
    print(f"  分析目录：{processor.analysis_path}")
    print(f"  处理模式：全量内容提取")
    print("=" * 80)
    
    # 显示初始统计
    processor.print_progress_summary()
    
    # 开始处理所有文件
    success = processor.process_all_files()
    
    if success:
        print("\n✨ 批量内容提取完成！")
        print("\n🚨 重要提醒：")
        print("=" * 80)
        print("📖 AI分析指南：")
        print("   1. 分析 analysis/ 目录下的所有文件")
        print("   2. 每个文件包含开头3000字符 + 10个随机片段")
        print("   3. 基于内容特征决定分类，忽略标题误导")
        print("   4. 记录新关键词和分类理由")
        print("   5. 完成后清理 analysis 目录")
        print("=" * 80)
    else:
        print("\n⚠️ 部分文件处理失败，请检查错误信息")
    
    return processor

if __name__ == "__main__":
    processor = main()