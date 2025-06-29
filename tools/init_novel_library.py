#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说库目录初始化工具
自动创建完整的小说库目录结构，为文件分类工作流做准备

功能特点：
1. 自动创建标准的分类目录结构
2. 生成必要的配置文件和说明文档
3. 检查目录权限和可用空间
4. 提供详细的初始化状态报告
5. 支持自定义目录路径和分类设置

作者：AI Assistant
版本：1.0
创建日期：2025年6月17日
"""

import os
import sys
import shutil
from pathlib import Path
import json
from datetime import datetime

class NovelLibraryInitializer:
    """小说库初始化器"""
    
    def __init__(self, base_path=None):
        """
        初始化器构造函数
        
        Args:
            base_path (str, optional): 小说库根目录路径，默认为当前目录下的"小说库"
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.cwd() / "小说库"
        
        # 标准分类目录结构
        self.categories = {
            "00-待分类": "新下载或未分类的小说文件",
            "00-二次确认": "自动分类需要人工确认的文件",
            "01-玄幻": "异界大陆、修炼升级、玄幻世界观",
            "02-奇幻": "魔法世界、精灵矮人、西方奇幻",
            "03-武侠": "江湖门派、武功内力、侠客故事",
            "04-仙侠": "修真仙道、丹药飞升、古典仙侠",
            "05-都市": "现代都市、商战职场、都市生活",
            "06-历史": "古代历史、穿越架空、宫廷官场",
            "07-军事": "战争军事、军队生活、战略战术",
            "08-游戏": "虚拟游戏、网游世界、游戏系统",
            "09-竞技": "体育竞技、电子竞技、比赛运动",
            "10-科幻": "未来科技、星际文明、科幻设定",
            "11-灵异": "鬼怪灵异、超自然、悬疑恐怖",
            "12-同人": "二次创作、动漫游戏改编",
            "99-知名作者专区": "知名作者的精品作品集合"
        }
        
        # 辅助目录
        self.aux_directories = {
            "backup": "文件备份目录",
            "logs": "处理日志目录",
            "temp": "临时文件目录",
            "statistics": "统计报告目录"
        }
        
        self.init_status = {
            "directories_created": [],
            "files_created": [],
            "errors": [],
            "warnings": []
        }
    
    def check_prerequisites(self):
        """检查初始化前提条件"""
        print("🔍 检查初始化前提条件...")
        
        # 检查父目录是否存在和可写
        parent_dir = self.base_path.parent
        if not parent_dir.exists():
            self.init_status["errors"].append(f"父目录不存在: {parent_dir}")
            return False
        
        if not os.access(parent_dir, os.W_OK):
            self.init_status["errors"].append(f"父目录无写入权限: {parent_dir}")
            return False
        
        # 检查磁盘空间（至少需要100MB）
        try:
            statvfs = os.statvfs(parent_dir)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            required_space = 100 * 1024 * 1024  # 100MB
            
            if free_space < required_space:
                self.init_status["warnings"].append(
                    f"磁盘可用空间较少: {free_space / (1024*1024):.1f}MB"
                )
        except:
            self.init_status["warnings"].append("无法检查磁盘空间")
        
        # 检查是否已存在小说库目录
        if self.base_path.exists():
            self.init_status["warnings"].append(f"目标目录已存在: {self.base_path}")
            return "exists"
        
        print("✅ 前提条件检查通过")
        return True
    
    def create_directory_structure(self):
        """创建目录结构"""
        print(f"📁 创建目录结构: {self.base_path}")
        
        try:
            # 创建根目录
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.init_status["directories_created"].append(str(self.base_path))
            
            # 创建分类目录
            print("   创建分类目录...")
            for category, description in self.categories.items():
                category_path = self.base_path / category
                category_path.mkdir(exist_ok=True)
                self.init_status["directories_created"].append(str(category_path))
                print(f"     ✓ {category}")
            
            # 创建辅助目录
            print("   创建辅助目录...")
            for aux_dir, description in self.aux_directories.items():
                aux_path = self.base_path / aux_dir
                aux_path.mkdir(exist_ok=True)
                self.init_status["directories_created"].append(str(aux_path))
                print(f"     ✓ {aux_dir}")
            
            print("✅ 目录结构创建完成")
            return True
            
        except Exception as e:
            self.init_status["errors"].append(f"创建目录失败: {e}")
            return False
    
    def create_readme_files(self):
        """创建说明文件"""
        print("📝 创建说明文件...")
        
        try:
            # 创建主README
            main_readme = self.base_path / "README.md"
            readme_content = f"""# 小说库目录说明

## 目录结构

本小说库采用标准化的分类目录结构，便于管理和查找小说文件。

### 📚 分类目录

| 目录名称 | 分类说明 | 适用作品特征 |
|---------|----------|-------------|
"""
            
            for category, description in self.categories.items():
                readme_content += f"| `{category}` | {description} | - |\n"
            
            readme_content += f"""
### 🛠️ 辅助目录

| 目录名称 | 用途说明 |
|---------|----------|
"""
            
            for aux_dir, description in self.aux_directories.items():
                readme_content += f"| `{aux_dir}` | {description} |\n"
            
            readme_content += f"""
## 📋 使用说明

### 初始化完成后的步骤

1. **添加待分类文件**
   ```bash
   # 将需要分类的小说文件复制到待分类目录
   cp /path/to/novels/*.txt "小说库/00-待分类/"
   ```

2. **运行分类工具**
   ```bash
   # 自动分类（推荐用于大批量文件）
   python main.py "小说库"
   
   # 手动分类（推荐用于精确分类）
   python batch_processor.py
   ```

3. **查看统计报告**
   ```bash
   # 生成分类统计
   python novel_statistics.py
   ```

### 🔧 工具推荐使用顺序

1. 异常文件名修复工作流 → 规范化文件名
2. 小说文件自动快速分类工作流 → 批量自动分类
3. 小说文件AI手动分类工作流 → 精确处理

### ⚠️ 注意事项

- 请将待分类文件放入 `00-待分类` 目录
- 分类前建议备份重要文件
- 定期清理 `temp` 和 `logs` 目录
- 保持目录结构不要随意修改

---

*目录创建时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}*
*初始化工具版本：v1.0*
"""
            
            with open(main_readme, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            self.init_status["files_created"].append(str(main_readme))
            
            # 为重要目录创建说明文件
            important_dirs = ["00-待分类", "00-二次确认"]
            for dir_name in important_dirs:
                dir_path = self.base_path / dir_name
                info_file = dir_path / "目录说明.txt"
                
                if dir_name == "00-待分类":
                    content = """此目录用于存放待分类的小说文件

使用说明：
1. 将需要分类的txt文件复制到此目录
2. 运行自动分类工具处理文件
3. 文件将被移动到对应的分类目录中

注意事项：
- 支持 .txt 和 .TXT 扩展名
- 建议先使用异常文件名修复工具处理数字文件名
- 大量文件建议分批处理

最后更新：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                elif dir_name == "00-二次确认":
                    content = """此目录用于存放需要人工确认的文件

文件来源：
- 自动分类得分过低的文件
- 多个分类得分接近的文件
- 无法匹配关键词的文件

处理建议：
1. 使用 batch_processor.py 工具批量处理
2. 仔细阅读文件内容再做分类决策
3. 记录新发现的关键词

最后更新：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.init_status["files_created"].append(str(info_file))
            
            print("✅ 说明文件创建完成")
            return True
            
        except Exception as e:
            self.init_status["errors"].append(f"创建说明文件失败: {e}")
            return False
    
    def create_config_files(self):
        """创建配置文件"""
        print("⚙️  创建配置文件...")
        
        try:
            # 创建关键词发现记录文件
            keywords_file = self.base_path / "new_keywords_discovered.txt"
            keywords_content = f"""# 手动分类过程中发现的新关键词记录
# 
# 用途：记录在手动分类过程中发现的新关键词，用于优化自动分类系统
# 格式：文件名 → 分类 → 关键词(权重) → 内容要点
# 
# 创建时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
# 
---

"""
            with open(keywords_file, 'w', encoding='utf-8') as f:
                f.write(keywords_content)
            self.init_status["files_created"].append(str(keywords_file))
            
            # 创建初始化状态记录文件
            init_record = self.base_path / "初始化记录.json"
            init_data = {
                "初始化时间": datetime.now().isoformat(),
                "初始化工具版本": "v1.0",
                "目录结构版本": "标准v1.0",
                "创建的目录数量": len(self.categories) + len(self.aux_directories) + 1,
                "分类目录": list(self.categories.keys()),
                "辅助目录": list(self.aux_directories.keys()),
                "配置说明": "标准小说分类库初始化完成"
            }
            
            with open(init_record, 'w', encoding='utf-8') as f:
                json.dump(init_data, f, ensure_ascii=False, indent=2)
            self.init_status["files_created"].append(str(init_record))
            
            print("✅ 配置文件创建完成")
            return True
            
        except Exception as e:
            self.init_status["errors"].append(f"创建配置文件失败: {e}")
            return False
    
    def generate_status_report(self):
        """生成初始化状态报告"""
        print("\n" + "="*60)
        print("📊 小说库初始化状态报告")
        print("="*60)
        print(f"📅 初始化时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print(f"📂 目标路径: {self.base_path}")
        print(f"📁 创建目录数: {len(self.init_status['directories_created'])}")
        print(f"📄 创建文件数: {len(self.init_status['files_created'])}")
        
        if self.init_status["errors"]:
            print(f"❌ 错误数量: {len(self.init_status['errors'])}")
            for error in self.init_status["errors"]:
                print(f"   • {error}")
        
        if self.init_status["warnings"]:
            print(f"⚠️  警告数量: {len(self.init_status['warnings'])}")
            for warning in self.init_status["warnings"]:
                print(f"   • {warning}")
        
        print("\n📋 创建的目录列表:")
        for category, description in self.categories.items():
            status = "✅" if str(self.base_path / category) in self.init_status["directories_created"] else "❌"
            print(f"   {status} {category} - {description}")
        
        print("\n🛠️ 辅助目录:")
        for aux_dir, description in self.aux_directories.items():
            status = "✅" if str(self.base_path / aux_dir) in self.init_status["directories_created"] else "❌"
            print(f"   {status} {aux_dir} - {description}")
        
        print("\n📄 生成的文件:")
        for file_path in self.init_status["files_created"]:
            print(f"   ✅ {Path(file_path).name}")
        
        # 提供后续操作建议
        print("\n" + "="*60)
        print("🎯 后续操作建议")
        print("="*60)
        print("1. 📥 添加待分类文件：")
        print(f'   cp /path/to/novels/*.txt "{self.base_path}/00-待分类/"')
        print()
        print("2. 🔧 准备分类工具：")
        print("   确保以下工具在当前目录或tools目录中：")
        tools_needed = [
            "txt_preview.py", "encoding_fixer.py", "novel_renamer.py",
            "main.py", "batch_processor.py", "novel_statistics.py",
            "keywords_config.yaml"
        ]
        for tool in tools_needed:
            tool_path = Path(tool)
            tools_path = Path("tools") / tool
            if tool_path.exists() or tools_path.exists():
                print(f"   ✅ {tool}")
            else:
                print(f"   ❌ {tool} (需要获取)")
        
        print()
        print("3. 🚀 开始处理流程：")
        print("   a) 异常文件名修复：python novel_renamer.py")
        print("   b) 自动批量分类：python main.py \"小说库\"")
        print("   c) 手动精确分类：python batch_processor.py")
        print("   d) 查看统计报告：python novel_statistics.py")
        
        print("\n💡 提示：")
        print("• 建议先备份重要文件")
        print("• 大量文件建议分批处理")
        print("• 可参考工作流文档获取详细操作指南")
        print("="*60)
    
    def initialize(self, force=False):
        """执行完整的初始化流程"""
        print("🚀 开始小说库初始化...")
        print(f"📂 目标路径: {self.base_path}")
        
        # 检查前提条件
        prereq_result = self.check_prerequisites()
        
        if prereq_result is False:
            print("❌ 前提条件检查失败")
            return False
        
        if prereq_result == "exists" and not force:
            print("⚠️  目标目录已存在")
            response = input("是否继续初始化？(y/n): ")
            if response.lower() != 'y':
                print("❌ 用户取消初始化")
                return False
        
        # 执行初始化步骤
        steps = [
            ("创建目录结构", self.create_directory_structure),
            ("创建说明文件", self.create_readme_files),
            ("创建配置文件", self.create_config_files)
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\n🔄 执行步骤: {step_name}")
            if not step_func():
                print(f"❌ 步骤失败: {step_name}")
                success = False
                break
        
        # 生成状态报告
        self.generate_status_report()
        
        if success and not self.init_status["errors"]:
            print(f"\n🎉 小说库初始化成功完成！")
            print(f"📂 目录位置: {self.base_path}")
            return True
        else:
            print(f"\n❌ 小说库初始化完成，但存在错误")
            return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("小说库目录初始化工具 v1.0")
        print()
        print("用途：自动创建完整的小说库目录结构")
        print()
        print("使用方法:")
        print("  python init_novel_library.py <目标路径> [选项]")
        print()
        print("参数说明:")
        print("  目标路径     : 小说库根目录的路径（将创建完整的目录结构）")
        print()
        print("选项:")
        print("  --force     : 强制初始化（即使目录已存在）")
        print()
        print("使用示例:")
        print('  python init_novel_library.py "小说库"')
        print('  python init_novel_library.py "/path/to/novels" --force')
        print('  python init_novel_library.py "."   # 在当前目录创建小说库')
        print()
        print("功能说明:")
        print("- 创建标准的分类目录结构（14个分类目录）")
        print("- 生成配置文件和说明文档")
        print("- 检查系统权限和磁盘空间")
        print("- 提供详细的初始化状态报告")
        print("- 给出后续操作建议")
        return 1
    
    # 解析参数
    target_path = sys.argv[1]
    force = "--force" in sys.argv
    
    # 处理特殊路径
    if target_path == ".":
        target_path = Path.cwd() / "小说库"
    else:
        target_path = Path(target_path)
    
    print(f"小说库目录初始化工具 v1.0")
    print(f"目标路径: {target_path}")
    if force:
        print("模式: 强制初始化")
    print()
    
    try:
        # 创建初始化器
        initializer = NovelLibraryInitializer(target_path)
        
        # 执行初始化
        success = initializer.initialize(force=force)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        return 1
    except Exception as e:
        print(f"\n❌ 初始化过程发生错误: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)