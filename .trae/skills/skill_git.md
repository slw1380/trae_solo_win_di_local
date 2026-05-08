# Git操作Skill

## 描述

自动化Git操作的工具，支持代码提交、推送、拉取等常用操作。

## 触发条件

当用户需要执行以下操作时触发：
- 提交代码到Git仓库
- 推送代码到GitHub
- 查看Git状态
- 拉取最新代码
- 查看提交历史

## 参数

### 必需参数

- `action`: 操作类型
  - `status` - 查看Git状态
  - `add` - 添加文件到暂存区
  - `commit` - 提交代码
  - `push` - 推送到远程仓库
  - `pull` - 拉取远程代码
  - `log` - 查看提交日志
  - `full-push` - 完整推送流程（add + commit + push）

### 可选参数

- `message`: 提交信息（commit和full-push时需要）
- `files`: 要添加的文件路径（默认为当前目录所有文件）
- `branch`: 分支名称（默认为main）
- `force`: 是否强制推送（默认为false）

## 配置

```yaml
project_dir: "e:\slw\trae_solo_cn_workspace\ollama-tui-agent"
git_path: "D:\Program Files\Git\bin\git.exe"
python_path: "C:\Users\di\AppData\Local\Python\pythoncore-3.14-64\python.exe"
```

## 使用示例

### 查看Git状态
```
帮我查看Git状态
```

### 提交并推送代码
```
提交代码，信息是"修复bug"
```

### 完整推送流程
```
推送代码到GitHub，提交信息"更新功能"
```

## 执行方式

通过调用Python脚本执行：

```bash
{python_path} {project_dir}\git_skill.py {action} [参数...]
```

## 注意事项

1. 确保Git已安装并配置正确
2. 确保有远程仓库的写入权限
3. 提交前建议先查看状态确认修改内容
4. 强制推送(--force)会覆盖远程历史，谨慎使用

## 返回值

- 成功：返回操作结果和成功提示
- 失败：返回错误信息和失败原因
