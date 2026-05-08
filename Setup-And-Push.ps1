# Ollama TUI Agent - 完整设置和推送脚本
# 运行方式: 右键点击此文件 -> "使用PowerShell运行"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ollama TUI Agent - Git推送脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置项目目录
$ProjectDir = "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"
Set-Location $ProjectDir

# 检查Git是否安装
Write-Host "[检查] 验证Git安装状态..." -ForegroundColor Yellow
$gitVersion = git --version 2>$null

if ($gitVersion) {
    Write-Host "[OK] Git已安装: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "[错误] Git未安装!" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装Git:" -ForegroundColor Yellow
    Write-Host "1. 访问 https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. 下载并安装Git for Windows" -ForegroundColor White
    Write-Host "3. 重新打开PowerShell" -ForegroundColor White
    Write-Host ""
    Write-Host "或者在安装向导中选择:'Use Git from Windows Command Prompt'" -ForegroundColor Gray
    Write-Host ""
    Read-Host "按Enter键退出"
    exit 1
}

# 检查SSH密钥
Write-Host ""
Write-Host "[检查] 验证SSH密钥..." -ForegroundColor Yellow
$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519.pub"

if (Test-Path $sshKeyPath) {
    Write-Host "[OK] SSH密钥已存在" -ForegroundColor Green
    Write-Host ""
    Write-Host "请确认公钥已添加到GitHub:" -ForegroundColor Yellow
    Write-Host "1. 访问 https://github.com/settings/keys" -ForegroundColor White
    Write-Host "2. 点击 'New SSH key'" -ForegroundColor White
    Write-Host "3. 复制以下公钥内容:" -ForegroundColor White
    Write-Host ""
    Get-Content $sshKeyPath
    Write-Host ""
    $confirm = Read-Host "公钥已添加到GitHub了吗? (y/n)"
    if ($confirm -ne 'y') {
        Write-Host "请先添加SSH密钥到GitHub，然后重新运行脚本" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "[警告] 未找到SSH密钥" -ForegroundColor Red
    Write-Host ""
    Write-Host "生成新SSH密钥..." -ForegroundColor Yellow
    $email = Read-Host "请输入你的GitHub注册邮箱"
    ssh-keygen -t ed25519 -C $email
    Write-Host ""
    Write-Host "[重要] 请将以下公钥添加到GitHub:" -ForegroundColor Yellow
    Write-Host ""
    Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"
    Write-Host ""
    Write-Host "1. 访问 https://github.com/settings/keys" -ForegroundColor White
    Write-Host "2. 点击 'New SSH key'" -ForegroundColor White
    Write-Host "3. 粘贴上面的公钥" -ForegroundColor White
    Write-Host "4. 点击 'Add SSH key'" -ForegroundColor White
    Write-Host ""
    Read-Host "添加完成后按Enter继续"
}

# Git操作
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  执行Git操作" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 初始化仓库
Write-Host "[1/5] 初始化Git仓库..." -ForegroundColor Yellow
git init
Write-Host "[OK] Git仓库已初始化" -ForegroundColor Green

# 添加文件
Write-Host ""
Write-Host "[2/5] 添加所有文件..." -ForegroundColor Yellow
git add .
Write-Host "[OK] 文件已添加到暂存区" -ForegroundColor Green

# 提交
Write-Host ""
Write-Host "[3/5] 提交代码..." -ForegroundColor Yellow
git commit -m "first commit: Ollama TUI Agent with AutoGen framework"
Write-Host "[OK] 代码已提交" -ForegroundColor Green

# 重命名分支
Write-Host ""
Write-Host "[4/5] 重命名分支为main..." -ForegroundColor Yellow
git branch -M main
Write-Host "[OK] 分支已重命名为main" -ForegroundColor Green

# 添加远程仓库
Write-Host ""
Write-Host "[5/5] 添加远程仓库..." -ForegroundColor Yellow
git remote add origin git@github.com:slw1380/trae_solo_win_di_local.git
Write-Host "[OK] 远程仓库已添加" -ForegroundColor Green

# 推送
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  推送到GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  成功! 代码已推送到GitHub" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "仓库地址: https://github.com/slw1380/trae_solo_win_di_local" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[错误] 推送失败!" -ForegroundColor Red
    Write-Host "请检查SSH连接和仓库权限" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "按Enter键退出"
