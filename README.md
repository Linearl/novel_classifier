# 小说分类系统 (Novel Classification System)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

一个功能强大的小说文件智能分类和管理系统，通过图形界面提供完整的小说库管理解决方案，包括目录初始化、文件导入、编码修复、智能分类、统计分析等核心功能。

## 🌟 特性亮点

- 🎯 **智能分类**：基于关键词的自动分类算法，支持12大小说类别
- 🔧 **编码修复**：自动检测和修复中文编码问题（GB2312、GBK、UTF-8等）
- 🖥️ **图形界面**：友好的Tkinter GUI，一站式操作体验
- ⚙️ **高度配置化**：支持自定义分类规则、权重和阈值
- 📊 **实时统计**：动态显示分类进度和统计分析
- 🛠️ **实用工具集**：包含多种文件处理和分析工具
- 📝 **详细日志**：完整的操作记录和调试信息
- 💾 **安全可靠**：自动备份，多重确认机制

## 📸 界面预览

> 注：实际界面截图将在后续版本中添加

![主界面](docs/images/main-interface.png)
*主界面：集成化的小说分类管理界面*

![统计界面](docs/images/statistics.png)
*统计界面：实时显示分类结果和分析报告*

## 📋 目录

- [🌟 特性亮点](#-特性亮点)
- [📸 界面预览](#-界面预览)
- [🖥️ 主程序介绍](#️-主程序介绍)
- [✨ 主要功能](#-主要功能)
- [🚀 快速开始](#-快速开始)
- [📖 使用指南](#-使用指南)
- [🔧 配置说明](#-配置说明)
- [📁 项目结构](#-项目结构)
- [🛠️ 工具使用](#️-工具使用)
- [⚠️ 注意事项](#️-注意事项)
- [❓ 常见问题](#-常见问题)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)
- [🙏 致谢](#-致谢)

## 🖥️ 主程序介绍

### novel_gui.py - 图形界面主程序

`novel_gui.py` 是整个小说分类系统的主入口程序，提供了直观的图形用户界面，集成了所有核心功能：

- **集成化设计**：将原本分散的工作流整合到统一的图形界面中
- **实时反馈**：所有操作都提供实时进度显示和状态更新
- **一站式管理**：从初始化到分类完成的完整流程管理
- **配置化支持**：支持通过配置文件自定义分类规则和系统参数
- **错误处理**：完善的异常处理和用户友好的错误提示

#### 主要界面功能模块

1. **小说库管理**：创建和初始化标准目录结构
2. **文件导入**：批量导入txt文件到待分类目录
3. **编码修复**：检测和修复文件编码问题
4. **智能分类**：基于关键词的自动分类处理
5. **统计分析**：实时查看分类统计和分析报告

## ✨ 主要功能

### 🏗️ 小说库管理

- 自动创建标准的小说库目录结构
- 支持多级分类目录（玄幻、奇幻、武侠、仙侠、都市、历史、军事、游戏、竞技、科幻、灵异、同人等）
- 一键清空和重新初始化功能

### 📁 文件导入处理

- 支持从任意目录批量导入txt文件
- 自动扫描和统计待导入文件数量
- 智能文件归类和去重处理

### 🔧 编码检测与修复

- 自动检测文件编码问题（支持GB2312、GBK、UTF-8等）
- 多策略编码修复：从严格模式到容错模式的递进修复
- 自动备份原始文件
- 详细的调试信息和修复日志

### 🤖 智能自动分类

- 基于关键词的智能文件分类
- 支持自定义分类规则和权重
- 二次确认机制确保分类准确性
- 可配置的批处理大小

### 📊 统计分析

- 实时统计各分类文件数量和占比
- 详细的分类排名和热门分析
- 处理进度监控
- 支持导出统计报告

### 🛠️ 实用工具集

- **文本预览工具**：支持开头+随机片段采样
- **批量处理器**：批量文件操作和分析
- **统计工具**：生成详细统计报告
- **日志工具**：高效记录处理日志

## 🚀 快速开始

### 系统要求

- **操作系统**：Windows 7/8/10/11 （推荐）
- **Python版本**：Python 3.8 或更高版本
- **内存**：建议4GB以上RAM
- **存储空间**：至少100MB可用空间

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/your-username/novel-classifier.git
cd novel-classifier
```

2. **安装Python依赖**

```bash
pip install -r requirements.txt
```

或者使用国内镜像加速：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

3. **启动程序**

```bash
python novel_gui.py
```

### Docker支持（可选）

如果你熟悉Docker，也可以使用容器化部署：

```bash
# 构建镜像
docker build -t novel-classifier .

# 运行容器
docker run -it --rm -v $(pwd)/novels:/app/novels novel-classifier
```

## 📖 使用指南

### 程序启动

1. 确保已安装Python 3.8+和相关依赖
2. 运行 `python novel_gui.py` 启动图形界面
3. 系统将自动加载配置文件和初始化界面

### 基本操作流程

1. **设置工作目录**：选择或创建小说库根目录
2. **初始化目录结构**：点击创建标准分类目录
3. **导入文件**：从指定目录批量导入txt文件
4. **修复编码**：检测和修复文件编码问题
5. **自动分类**：基于关键词进行智能分类
6. **查看统计**：实时查看分类结果和统计报告

### 高级功能

- **AI手动分类**：对分类不确定的文件，可借助工作流，让copilot使用专门的工作流进行深度分析（参考：`docs/workflows/4.小说文件AI手动分类工作流.md`）
- **批量工具**：使用tools目录下的各种实用工具
- **自定义配置**：修改config目录下的配置文件调整分类规则

## 🔧 开发与测试

### 开发指南

详细的开发指南请参考 `docs/dev-guide.md`。

### 测试指南

详细的测试指南请参考 `docs/testing-guide.md`。

## 🔧 配置说明

### 主要配置文件

- `config/default_config.yaml`：系统默认配置
- `config/gui_config.yaml`：GUI界面配置
- `config/keywords_config.yaml`：分类关键词配置

### 关键词配置

编辑 `config/keywords_config.yaml` 文件可以自定义分类规则：

```yaml
# 分类阈值设置
thresholds:
  direct_classification: 16  # 直接分类阈值（≥16分自动分类）
  secondary_check: 8        # 二次确认下限（8-15分需要人工确认）
  score_difference: 4       # 竞争检测阈值

# 关键词权重设置
weights:
  high: 3      # 高权重关键词得分
  medium: 2    # 中权重关键词得分
  low: 1       # 低权重关键词得分

# 分类关键词库示例
categories:
  "01-玄幻":
    high_weight: ["玄幻", "异界", "修炼", "系统", "境界"]
    medium_weight: ["魔法", "魔兽", "突破", "传承"]
    low_weight: ["天才", "强者", "实力", "进化"]
  "02-奇幻":
    high_weight: ["奇幻", "精灵", "矮人", "龙族", "魔法师"]
    medium_weight: ["骑士", "法师", "公主", "王国"]
    low_weight: ["城堡", "森林", "冒险", "村庄"]
```

## 📁 项目结构

```
novel_classification/
├── novel_gui.py          # 主程序入口
├── requirements.txt      # 依赖包列表
├── README.md            # 项目文档
├── LICENSE              # 开源许可证
├── config/              # 配置文件
│   ├── default_config.yaml
│   ├── gui_config.yaml
│   ├── keywords_config.yaml
│   └── log_config.ini
├── core/                # 核心模块
│   ├── __init__.py
│   ├── config_manager.py
│   ├── logger_manager.py
│   └── workflow_manager.py
├── gui/                 # GUI界面模块
│   ├── __init__.py
│   ├── main_window.py
│   ├── dialogs/         # 对话框组件
│   ├── panels/          # 面板组件
│   └── widgets/         # 小部件组件
├── tools/               # 实用工具
│   ├── append_to_file.py
│   ├── batch_processor.py
│   ├── fix_broken_filenames.py
│   ├── init_novel_library.py
│   ├── LogViewer.ps1
│   ├── novel_statistics.py
│   ├── quick_log.py
│   ├── temp_renamer.py
│   ├── txt_preview.py
│   └── view_backup.py
├── workflows/           # 工作流模块
│   ├── __init__.py
│   ├── initialization.py
│   ├── file_import.py
│   ├── encoding_fix.py
│   └── auto_classification.py
└── docs/               # 文档
    ├── dev-guide.md
    ├── testing-guide.md
    ├── logging-tools-guide.md
    └── workflows/      # 工作流说明文档
        ├── 1.小说库初始化工作流.md
        ├── 2.异常文件修复工作流.md
        ├── 3.小说文件自动快速分类工作流.md
        ├── 4.小说文件AI手动分类工作流.md
        └── git-commit-workflow.md
```

## 🛠️ 工具使用

### 独立工具脚本

项目包含多个实用工具，可以独立使用：

- **文本预览工具** (`tools/txt_preview.py`)：预览文件内容
- **统计工具** (`tools/novel_statistics.py`)：生成统计报告
- **批量处理器** (`tools/batch_processor.py`)：批量文件操作
- **快速日志** (`tools/quick_log.py`)：记录分类日志

## ⚠️ 注意事项

1. **备份重要**：在进行批量操作前，建议备份重要文件
2. **编码问题**：主要针对中文txt文件的编码问题
3. **性能考虑**：大批量文件处理时建议分批进行
4. **路径要求**：避免使用包含特殊字符的文件路径

## ❓ 常见问题

### Q: 程序无法启动怎么办？

A: 请检查：

- Python版本是否为3.8+
- 是否安装了所有依赖包
- 查看终端错误信息

### Q: 文件分类不准确怎么办？

A: 可以：

- 调整 `config/keywords_config.yaml` 中的关键词
- 修改分类阈值设置

### Q: 支持哪些文件格式？

A: 目前只支持：

- .txt 文件（各种中文编码）

### Q: 可以在Linux/Mac上使用吗？

A: 理论上可以，但主要在Windows上测试。可能需要调整部分文件路径处理代码。

## 🤝 贡献指南

欢迎参与改进这个项目！以下是贡献方式：

### 如何贡献

1. **Fork** 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 **Pull Request**

### 问题反馈

- 发现Bug？请创建一个 [Issue](../../issues)
- 有功能建议？也请创建一个 [Issue](../../issues)
- 有使用问题？可以在 [Discussions](../../discussions) 中讨论

### 开发规范

- 请遵循项目现有的代码风格
- 添加新功能时请更新相应的文档
- 确保代码通过基本测试

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看 LICENSE 文件了解详细信息。

这意味着你可以自由地：

- ✅ 商业使用
- ✅ 修改代码
- ✅ 分发代码
- ✅ 私人使用

只需要：

- 📝 包含原始许可证和版权声明

## 🙏 致谢

感谢所有为这个项目贡献代码、提出建议或报告问题的朋友们！

特别感谢：

- Python社区提供的优秀开源库
- 所有测试用户的反馈和建议
- GitHub提供的开源平台

## 🔧 更新日志

### v1.0.0 (2025年6月29日)

- 集成前三个工作流到novel_gui.py主程序
- 优化图形界面，提供一站式管理体验
- 完善编码修复和统计功能
- 项目结构清理和文档更新

---

**当前版本**: 1.0.0
**更新日期**: 2025年6月29日
