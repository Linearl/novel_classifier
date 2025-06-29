# 日志记录工具使用指南

## 工具概述

为提高AI手动分类工作流的效率，开发了两个专门的日志记录工具：

- `append_to_file.py`: 通用文件追加工具，支持详细的格式化追加
- `quick_log.py`: 快速记录工具，简化常用的关键词和分类日志记录

## quick_log.py 快速使用

### 记录新关键词
```bash
python tools/quick_log.py 小说库 keywords "分类名" "关键词描述"
```

示例：
```bash
python tools/quick_log.py 小说库 keywords "历史类" "- 广平郡、曲梁城：三国地名，用于识别历史小说"
```

### 记录分类结果
```bash
python tools/quick_log.py 小说库 classification "文件名" "标题" "分类" "理由" ["关键词"] ["状态"]
```

示例：
```bash
python tools/quick_log.py 小说库 classification \
  "12639.txt" "三国志乱" "06-历史" \
  "三国穿越题材，有历史人物和地名" \
  "广平郡,曲梁城,阳球,王甫" "已移动到历史分类"
```

## append_to_file.py 详细使用

### 记录关键词（详细格式）
```bash
python tools/append_to_file.py 小说库/new_keywords_discovered.txt \
  --type keywords \
  --title "小说标题" \
  --category "06-历史" \
  --keywords "地名:广平郡,曲梁城;人物:阳球,王甫" \
  --reason "三国穿越题材，用于历史小说识别"
```

### 记录分类日志（详细格式）
```bash
python tools/append_to_file.py 小说库/logs/manual_classification_log.txt \
  --type log \
  --filename "12639.txt" \
  --title "三国志乱" \
  --category "06-历史" \
  --reason "详细的分析理由" \
  --keywords "相关关键词" \
  --status "处理状态"
```

### 简单文本追加
```bash
python tools/append_to_file.py 目标文件路径 \
  --type text \
  --content "要追加的文本内容"
```

## 输出格式

### 关键词文件格式
```
## 历史类关键词补充 - 2025-06-29 04:00
- 广平郡、曲梁城：三国地名，用于识别历史小说
- 阳球、王甫：东汉历史人物，用于识别历史背景小说
```

### 分类日志格式
```
### 文件：12639.txt
- **原标题**：三国志乱
- **目标分类**：06-历史
- **分析时间**：2025-06-29 04:00
- **分析理由**：三国穿越题材，有历史人物和地名
- **新关键词**：广平郡,曲梁城,阳球,王甫
- **处理状态**：已移动到历史分类
```

## 工作流集成

在AI手动分类工作流的3.3节，建议使用这些工具来替代手动编辑文件的操作：

1. **分析文件** → 使用 `read_file` 工具
2. **记录关键词** → 使用 `quick_log.py keywords`
3. **记录分类结果** → 使用 `quick_log.py classification`
4. **移动文件** → 使用 `run_in_terminal` 执行 `Move-Item` 命令

这样可以大大提高工作效率，避免每次都要输出完整的文件内容进行追加操作。

## 注意事项

1. 工具会自动创建必要的目录结构
2. 时间戳会自动添加
3. 文件编码使用UTF-8
4. **PowerShell查看文件编码问题**：在PowerShell中查看UTF-8文件时需要指定编码，否则会出现乱码：

   **方法一：手动指定编码**
   ```powershell
   # 正确的查看方式
   Get-Content "小说库\new_keywords_discovered.txt" -Encoding UTF8
   Get-Content "小说库\logs\manual_classification_log.txt" -Encoding UTF8
   
   # 查看最后几行
   Get-Content "小说库\new_keywords_discovered.txt" -Encoding UTF8 | Select-Object -Last 10
   ```

   **方法二：使用提供的PowerShell脚本（推荐）**
   ```powershell
   # 如果遇到执行策略限制，先设置执行策略（仅当前会话）
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # 加载日志查看工具
   . tools\LogViewer.ps1
   
   # 使用简化命令
   Show-Keywords 5              # 查看最后5条关键词记录
   Show-ClassificationLog 10    # 查看最后10行分类日志
   Show-AllKeywords            # 查看全部关键词
   Show-AllLogs               # 查看全部日志
   ```
5. 建议在Git管理下使用，便于跟踪变更

---
*创建时间：2025年6月29日*
*用于：AI手动分类工作流优化*
