# SSH密钥和GitHub设置指南

## 检查现有SSH密钥

在PowerShell或Git Bash中运行：

```powershell
# 查看.ssh目录内容
dir ~/.ssh

# 或者Linux/Mac:
ls -la ~/.ssh
```

如果看到以下文件，说明已经存在SSH密钥：
- `id_ed25519` - 私钥
- `id_ed25519.pub` - 公钥

## 查看现有公钥

```powershell
cat ~/.ssh/id_ed25519.pub
```

如果这个公钥已经在GitHub上使用，直接跳到"推送代码"部分。

## 如果想创建新的SSH密钥

```powershell
# 1. 生成新密钥（指定文件名避免覆盖旧的）
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/github_key

# 2. 查看新公钥
cat ~/.ssh/github_key.pub

# 3. 复制公钥内容，添加到GitHub

# 4. 配置SSH使用新密钥
# 创建或编辑 ~/.ssh/config 文件，添加：
```

创建 `~/.ssh/config` 文件：
```
# GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_key
```

## 推送代码到GitHub

### 方法1: HTTPS方式（需要每次输入用户名密码）

```powershell
cd "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/slw1380/trae_solo_win_di_local.git
git push -u origin main
```

### 方法2: SSH方式（推荐，一次配置永久使用）

```powershell
cd "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:slw1380/trae_solo_win_di_local.git
git push -u origin main
```

## 验证SSH连接

```powershell
ssh -T git@github.com
```

如果看到 "Hi [username]! You've successfully authenticated" 就表示成功了。

## 常见问题

### Q: git命令找不到？
A: 需要安装Git for Windows：https://git-scm.com/download/win

### Q: 推送时提示权限拒绝？
A: 检查SSH公钥是否添加到GitHub，或使用HTTPS方式

### Q: 想修改现有密钥名称？
A: 直接重命名文件即可：
```powershell
mv ~/.ssh/id_ed25519 ~/.ssh/your_new_name
mv ~/.ssh/id_ed25519.pub ~/.ssh/your_new_name.pub
```
