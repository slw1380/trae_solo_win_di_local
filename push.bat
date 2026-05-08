@echo off
echo ========================================
echo  Ollama TUI Agent - Git推送脚本
echo ========================================
echo.

cd /d "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"

echo [1/5] 初始化Git仓库...
git init

echo [2/5] 添加所有文件...
git add .

echo [3/5] 提交代码...
git commit -m "first commit: Ollama TUI Agent with AutoGen framework"

echo [4/5] 重命名分支为main...
git branch -M main

echo [5/5] 添加远程仓库...
git remote add origin https://github.com/slw1380/trae_solo_win_di_local.git

echo.
echo ========================================
echo  准备推送到GitHub
echo ========================================
echo.

echo 请执行以下命令完成推送：
echo git push -u origin main
echo.
echo 或者使用SSH方式（如果已配置）：
echo git remote set-url origin git@github.com:slw1380/trae_solo_win_di_local.git
echo git push -u origin main
echo.
pause
