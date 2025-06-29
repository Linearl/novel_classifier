# 小说分类系统 (Novel Classification System)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

一个功能强大的小说文件智能分类和管理系统，通过图形界面提供完整的小说库管理解决方案，包括目录初始化、文件导入、编码修复、智能分类、统计分析等核心功能。

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

### 环境要求
- Python 3.8 或更高版本
- Windows 操作系统（推荐）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动程序
```bash
python novel_gui.py
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
- **二次确认处理**：对分类不确定的文件进行人工确认
- **AI手动分类**：使用专门的工作流进行深度分析（参考：`docs/workflows/4.小说文件AI手动分类工作流.md`）
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
categories:
  "01-玄幻":
    keywords:
      - 修仙
      - 异世界
      - 系统
    weight: 1.0
  "02-奇幻":
    keywords:
      - 魔法
      - 龙族
      - 精灵
    weight: 1.0
```

## 📁 项目结构

```
novel_classification/
├── novel_gui.py          # 主程序入口
├── requirements.txt      # 依赖包列表
├── README.md            # 项目文档
├── config/              # 配置文件
│   ├── default_config.yaml
│   ├── gui_config.yaml
│   └── keywords_config.yaml
├── core/                # 核心模块
│   ├── config_manager.py
│   └── workflow_manager.py
├── gui/                 # GUI界面
│   ├── main_window.py
│   ├── dialogs/
│   ├── panels/
│   └── widgets/
├── tools/               # 实用工具
│   ├── txt_preview.py
│   ├── batch_processor.py
│   ├── novel_statistics.py
│   └── init_novel_library.py
├── workflows/           # 工作流模块
│   ├── initialization.py
│   ├── file_import.py
│   ├── encoding_fix.py
│   └── auto_classification.py
└── docs/               # 文档
    └── workflows/      # 工作流说明文档
```

## 🛠️ 工具使用

### 独立工具脚本
项目包含多个实用工具，可以独立使用：

- **文本预览工具** (`tools/txt_preview.py`)：预览文件内容
- **统计工具** (`tools/novel_statistics.py`)：生成统计报告  
- **批量处理器** (`tools/batch_processor.py`)：批量文件操作
- **快速日志** (`tools/quick_log.py`)：记录分类日志

## � 注意事项

1. **备份重要**：在进行批量操作前，建议备份重要文件
2. **编码问题**：主要针对中文txt文件的编码问题
3. **性能考虑**：大批量文件处理时建议分批进行
4. **路径要求**：避免使用包含特殊字符的文件路径

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🔧 更新日志

### v1.0.2 (2025年6月29日)
- 集成前三个工作流到novel_gui.py主程序
- 优化图形界面，提供一站式管理体验
- 完善编码修复和统计功能
- 项目结构清理和文档更新

---

**当前版本**: 1.0.2  
**更新日期**: 2025年6月29日
