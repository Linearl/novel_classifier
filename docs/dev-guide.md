# 开发指南 (Development Guide)

## 1. 概述

本指南旨在为本项目的所有开发者提供一个标准的开发流程和规范，确保代码质量、协作效率和项目的长期可维护性。所有贡献者都应遵循本指南。

## 2. 环境搭建

### 2.1. 源码获取

通过Git克隆项目到本地：

```bash
git clone <repository-url>
cd novel-organizer
```

### 2.2. Python环境

本项目使用Python 3.10+。建议使用虚拟环境（如 `venv`）来管理项目依赖，避免与全局环境冲突。

**创建并激活虚拟环境 (Windows):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**创建并激活虚拟环境 (macOS/Linux):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3. 安装依赖

项目的所有依赖都记录在 `requirements.txt` 文件中。激活虚拟环境后，运行以下命令进行安装：

```bash
pip install -r requirements.txt
```

## 3. 代码风格

本项目遵循 **PEP 8** 代码风格指南。为了保证代码风格的统一，我们使用 `black` 进行代码格式化，使用 `flake8` 进行代码质量检查。

### 3.1. 自动格式化

在提交代码前，请务必对修改过的文件使用 `black` 进行格式化：

```bash
black .
```

### 3.2. 代码检查

运行 `flake8` 检查代码中是否存在不符合规范或潜在的问题：

```bash
flake8 .
```

请在提交前解决所有 `flake8` 报告的错误。

## 4. 工作流程

### 4.1. 分支策略

- **`main`**: 主分支，始终保持稳定和可发布状态。
- **`develop`**: 开发分支，所有新功能的起点，从此分支创建特性分支。
- **`feature/<feature-name>`**: 特性分支，用于开发新功能（例如 `feature/statistics-panel`）。
- **`fix/<issue-name>`**: Bug修复分支，用于修复非紧急的Bug（例如 `fix/encoding-error`）。

### 4.2. Git提交规范

本项目的Git提交信息遵循特定格式，以提高日志的可读性和自动化处理能力。详细规范请参考 `docs/workflows/git-commit-workflow.md`。

**核心格式:**

```text
<类型>(<范围>): <主题>

[可选的正文]

[可选的页脚]
```

- **示例**: `feat(gui): 添加自动分类编辑按钮`

### 4.3. 开发步骤

1. **从 `develop` 分支创建新分支**: `git checkout -b feature/your-feature-name develop`
2. **编码与开发**: 完成你的代码修改。
3. **本地测试**: 确保你的修改没有引入新的Bug，并按需编写或更新测试用例。
4. **代码格式化与检查**: `black .` 和 `flake8 .`。
5. **提交代码**: `git commit -m "feat(scope): your detailed message"`
6. **推送分支**: `git push origin feature/your-feature-name`
7. **创建合并请求 (Pull Request)**: 在代码托管平台（如GitHub）上，创建一个从你的特性分支到 `develop` 分支的合并请求。

## 5. 测试

### 5.1. 运行单元测试

项目在 `tests/` 目录下包含了一系列单元测试和集成测试。你可以使用 `pytest` 来运行它们：

```bash
pytest
```

### 5.2. 编写新测试

- 新增的功能模块必须附带相应的单元测试。
- Bug修复应首先编写一个能够复现该Bug的测试用例，然后再进行修复。
- 测试文件应以 `test_` 开头，存放于 `tests/` 目录下。

## 6. 文档

- **代码注释**: 重要的函数、类和模块应有清晰的Docstring注释。
- **工作流文档**: 核心的业务流程（如文件导入、编码修复）应在 `docs/workflows/` 目录下有对应的Markdown文档说明。
- **项目文档**: 对项目架构、重要决策的说明，应记录在 `docs/` 目录下的相关文档中。

---

*本指南旨在持续更新，以反映项目开发的最佳实践。*
