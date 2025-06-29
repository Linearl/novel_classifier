# PowerShell 辅助脚本 - 正确查看UTF-8日志文件
# 解决PowerShell默认编码导致的中文乱码问题

function Show-Keywords {
    <#
    .SYNOPSIS
    查看关键词发现文件的内容
    
    .PARAMETER Last
    显示最后N行，默认为10行
    #>
    param(
        [int]$Last = 10
    )
    
    $file = "小说库\new_keywords_discovered.txt"
    if (Test-Path $file) {
        Get-Content $file -Encoding UTF8 | Select-Object -Last $Last
    } else {
        Write-Host "❌ 文件不存在: $file" -ForegroundColor Red
    }
}

function Show-ClassificationLog {
    <#
    .SYNOPSIS
    查看分类日志文件的内容
    
    .PARAMETER Last
    显示最后N行，默认为15行
    #>
    param(
        [int]$Last = 15
    )
    
    $file = "小说库\logs\manual_classification_log.txt"
    if (Test-Path $file) {
        Get-Content $file -Encoding UTF8 | Select-Object -Last $Last
    } else {
        Write-Host "❌ 文件不存在: $file" -ForegroundColor Red
    }
}

function Show-AllKeywords {
    <#
    .SYNOPSIS
    查看关键词发现文件的全部内容
    #>
    $file = "小说库\new_keywords_discovered.txt"
    if (Test-Path $file) {
        Get-Content $file -Encoding UTF8
    } else {
        Write-Host "❌ 文件不存在: $file" -ForegroundColor Red
    }
}

function Show-AllLogs {
    <#
    .SYNOPSIS
    查看分类日志文件的全部内容
    #>
    $file = "小说库\logs\manual_classification_log.txt"
    if (Test-Path $file) {
        Get-Content $file -Encoding UTF8
    } else {
        Write-Host "❌ 文件不存在: $file" -ForegroundColor Red
    }
}

# 导出函数，使其在模块加载后可用
Export-ModuleMember -Function Show-Keywords, Show-ClassificationLog, Show-AllKeywords, Show-AllLogs

# 使用说明
Write-Host "
=== 日志查看工具已加载 ===

可用命令：
  Show-Keywords [行数]           # 查看最近的关键词记录
  Show-ClassificationLog [行数]  # 查看最近的分类日志  
  Show-AllKeywords              # 查看全部关键词记录
  Show-AllLogs                  # 查看全部分类日志

示例：
  Show-Keywords 5               # 查看最后5条关键词记录
  Show-ClassificationLog 10     # 查看最后10行分类日志

注意：这些命令已经内置UTF-8编码设置，可以正确显示中文内容。
" -ForegroundColor Green
