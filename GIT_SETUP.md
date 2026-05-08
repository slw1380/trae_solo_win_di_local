# Git初始化和推送指南

## 步骤1: 安装Git（如果还没安装）

从 [https://git-scm.com/download/win](https://git-scm.com/download/win) 下载并安装Git。

## 步骤2: 打开PowerShell并执行以下命令

```powershell
# 进入项目目录
cd "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "first commit: Ollama TUI Agent with AutoGen framework"

# 重命名分支为main
git branch -M main

# 添加远程仓库
git remote add origin https://github.com/slw1380/trae_solo_win_di_local.git

# 推送到GitHub
git push -u origin main
```

## 步骤3: 如果遇到推送问题

可能需要设置GitHub认证：

```powershell
# 配置GitHub用户名和邮箱（替换为你的信息）
git config --global user.name "Your GitHub Username"
git config --global user.email "your.email@example.com"

# 如果使用HTTPS推送，可以设置凭据缓存
git config --global credential.helper manager
```

## 或者使用SSH方式（推荐）

```powershell
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 将公钥添加到GitHub Settings -> SSH Keys

# 4. 修改远程仓库URL
git remote set-url origin git@github.com:slw1380/trae_solo_win_di_local.git

# 5. 推送
git push -u origin main
```

## 已包含的文件

- ✅ README.md
- ✅ pyproject.toml
- ✅ src/ollama_tui/__init__.py
- ✅ src/ollama_tui/config.py
- ✅ src/ollama_tui/ollama_client.py
- ✅ src/ollama_tui/agent.py
- ✅ src/ollama_tui/tui.py
- ✅ src/ollama_tui/main.py
