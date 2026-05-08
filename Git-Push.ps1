# Ollama TUI Agent - Git推送脚本 (Windows版)
# 保存编码: UTF-8 with BOM
# 运行方式: 右键点击 -> "使用PowerShell运行"

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ollama TUI Agent - Git推送脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectDir = "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"

if (-not (Test-Path $ProjectDir)) {
    Write-Host "[错误] 项目目录不存在: $ProjectDir" -ForegroundColor Red
    exit 1
}

Set-Location $ProjectDir
Write-Host "[信息] 工作目录: $ProjectDir" -ForegroundColor Gray
Write-Host ""

Write-Host "[步骤1/6] 检查Git安装..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "  [OK] Git已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  [错误] Git未安装或未配置到环境变量" -ForegroundColor Red
    Write-Host ""
    Write-Host "  请先安装Git:" -ForegroundColor Yellow
    Write-Host "  1. 下载: https://git-scm.com/download/win" -ForegroundColor Gray
    Write-Host "  2. 安装时选择: 'Use Git from Windows Command Prompt'" -ForegroundColor Gray
    Write-Host "  3. 重新打开PowerShell窗口" -ForegroundColor Gray
    Write-Host ""
    Read-Host "按Enter退出"
    exit 1
}

Write-Host ""
Write-Host "[步骤2/6] 检查SSH密钥..." -ForegroundColor Yellow
$SSHKeyPub = "$env:USERPROFILE\.ssh\id_ed25519.pub"
$SSHKeyPrivate = "$env:USERPROFILE\.ssh\id_ed25519"

if ((Test-Path $SSHKeyPub) -and (Test-Path $SSHKeyPrivate)) {
    Write-Host "  [OK] SSH密钥已存在" -ForegroundColor Green
    Write-Host ""
    Write-Host "  请确认公钥已添加到GitHub:" -ForegroundColor Cyan
    Write-Host "  https://github.com/settings/keys" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  你的公钥:" -ForegroundColor Cyan
    Get-Content $SSHKeyPub | Write-Host -ForegroundColor Gray
    Write-Host ""
    $Confirm = Read-Host "  公钥已添加到GitHub? (y/n, 默认:y)"
    if ($Confirm -eq 'n') {
        Write-Host "  请先访问GitHub添加SSH公钥, 然后重新运行脚本" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "  [提示] 未找到SSH密钥, 将为你生成" -ForegroundColor Yellow
    $Email = Read-Host "  请输入你的GitHub注册邮箱"
    if ([string]::IsNullOrWhiteSpace($Email)) {
        Write-Host "  [错误] 邮箱不能为空" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "  正在生成SSH密钥 (直接按回车使用默认位置和空密码)..." -ForegroundColor Cyan
    ssh-keygen -t ed25519 -C $Email
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [错误] SSH密钥生成失败" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  [重要] 请复制以下公钥并添加到GitHub" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"
    Write-Host ""
    Write-Host "  添加步骤:" -ForegroundColor Cyan
    Write-Host "  1. 访问: https://github.com/settings/keys" -ForegroundColor Gray
    Write-Host "  2. 点击 'New SSH key'" -ForegroundColor Gray
    Write-Host "  3. Title随意填写, 如: 'My PC'" -ForegroundColor Gray
    Write-Host "  4. 在Key框中粘贴上方的公钥" -ForegroundColor Gray
    Write-Host "  5. 点击 'Add SSH key'" -ForegroundColor Gray
    Write-Host ""
    Read-Host "添加完成后按Enter继续"
}

Write-Host ""
Write-Host "[步骤3/6] 初始化Git仓库..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "  [跳过] Git仓库已存在" -ForegroundColor Gray
} else {
    git init
    Write-Host "  [OK] Git仓库已初始化" -ForegroundColor Green
}

Write-Host ""
Write-Host "[步骤4/6] 添加所有文件到暂存区..." -ForegroundColor Yellow
git add .
$status = git status --short
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "  [跳过] 没有新文件需要添加" -ForegroundColor Gray
} else {
    Write-Host "  [OK] 已添加以下文件:" -ForegroundColor Green
    $status | Write-Host -ForegroundColor Gray
}

Write-Host ""
Write-Host "[步骤5/6] 提交代码..." -ForegroundColor Yellow
$CommitMsg = "first commit: Ollama TUI Agent with AutoGen framework"
git commit -m $CommitMsg
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] 提交成功" -ForegroundColor Green
} else {
    Write-Host "  [提示] 没有内容需要提交" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[步骤6/6] 推送到GitHub..." -ForegroundColor Yellow
git branch -M main
git remote remove origin 2>$null | Out-Null
git remote add origin git@github.com:slw1380/trae_solo_win_di_local.git

Write-Host ""
Write-Host "  正在推送 (可能需要几秒钟)..." -ForegroundColor Cyan
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  [成功] 代码已推送到GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  仓库地址: https://github.com/slw1380/trae_solo_win_di_local" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  [失败] 推送失败!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  可能原因:" -ForegroundColor Yellow
    Write-Host "  1. SSH密钥未正确配置" -ForegroundColor Gray
    Write-Host "  2. 公钥未添加到GitHub" -ForegroundColor Gray
    Write-Host "  3. 网络连接问题" -ForegroundColor Gray
    Write-Host "  4. 仓库名称错误或不存在" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  建议:" -ForegroundColor Yellow
    Write-Host "  1. 访问 https://github.com/settings/keys 确认SSH公钥" -ForegroundColor Gray
    Write-Host "  2. 访问 https://github.com/slw1380/trae_solo_win_di_local 确认仓库存在" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Read-Host "按Enter退出"
