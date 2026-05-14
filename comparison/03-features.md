# Claude Code vs Codex CLI 对比分析 - 功能特性详细对比

---

## 一、核心命令对比

### 1.1 常用命令对照表

| 功能 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **初始化项目** | `/init` | `codex init`（自动检测） |
| **查看帮助** | `/help` | `codex --help` |
| **切换模型** | `/model <model-id>` | `/model` 或 `--model` |
| **查看项目结构** | `/tree` | 自动理解 |
| **项目概览** | `/overview` | `codex "explain this codebase"` |
| **代码审查** | `/review` | `codex "review this code"` |
| **继续会话** | `/continue` | 自动恢复 |
| **清除上下文** | `/clear` | 自动管理 |
| **压缩历史** | `/compact` | 自动管理 |
| **查看成本** | `/cost` | 查看使用统计 |
| **导出对话** | `/export` | 不支持 |
| **执行命令** | 直接输入 | `codex exec "prompt"` |

### 1.2 交互模式

**Claude Code 交互模式：**
```bash
# 进入交互式 REPL
claude

# 直接执行单次任务
claude "create a React component"

# 继续上次会话
claude -c
```

**Codex CLI 交互模式：**
```bash
# 进入交互式 TUI
codex

# 直接执行单次任务
codex "explain this codebase"

# 非交互式执行
codex exec "fix the CI failure"

# 带图像输入
codex -i screenshot.png "Explain this error"
```

---

## 二、代码编辑功能

### 2.1 文件操作

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **文件引用** | `@filename` 语法 | 自动检测或显式指定 |
| **多文件编辑** | ✅ 支持 | ✅ 支持 |
| **代码 diff 预览** | ✅ 交互式确认 | ✅ 交互式确认 |
| **批量重构** | ✅ 支持 | ✅ 支持 |
| **代码搜索** | ✅ 内置搜索 | ✅ 内置搜索 |

### 2.2 代码生成质量

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **代码风格遵循** | CLAUDE.md 指导 | AGENTS.md 指导 |
| **测试生成** | ✅ 支持 | ✅ 支持 |
| **文档生成** | ✅ 支持 | ✅ 支持 |
| **类型注解** | ✅ 根据项目风格 | ✅ 根据项目风格 |
| **注释语言** | 跟随用户语言 | 跟随用户语言 |

---

## 三、Git 集成

### 3.1 Git 工作流支持

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **自动提交** | ✅ "create a commit" | ✅ 支持 |
| **提交信息生成** | ✅ 规范格式 | ✅ 规范格式 |
| **PR 创建** | ✅ 支持 | ✅ GitHub 集成 |
| **代码审查** | ✅ Claude Code Review | ✅ Codex Code Review |
| **分支管理** | ✅ 支持 | ✅ 支持 |
| **合并冲突解决** | ✅ 支持 | ✅ 支持 |

### 3.2 代码审查功能

**Claude Code Review：**
- 多代理 PR 分析系统
- 安全漏洞扫描（Claude Code Security）
- 2026年3月发布

**Codex Code Review：**
- 自动 PR 审查
- GitHub 原生集成
- 可捕获关键 Bug

---

## 四、图像与多模态支持

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **截图输入** | ✅ 支持粘贴 | ✅ 支持粘贴 |
| **线框图理解** | ✅ 支持 | ✅ 支持 |
| **图表分析** | ✅ 支持 | ✅ 支持 |
| **多图像输入** | ✅ 支持 | ✅ `--image img1.png,img2.jpg` |
| **PDF 阅读** | ✅ 直接分析 | ❌ 不支持 |

---

## 五、会话与状态管理

### 5.1 会话持久化

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **会话保存** | ✅ 自动保存 | ✅ 云端同步 |
| **跨设备恢复** | ❌ 本地存储 | ✅ 通过 ChatGPT 账号 |
| **会话压缩** | `/compact` 命令 | 自动管理 |
| **会话导出** | `/export` 命令 | ❌ 不支持 |
| **会话回滚** | ✅ Checkpoint（ESC 两次） | ❌ 不支持 |

### 5.2 状态同步

**Claude Code：**
- 本地会话持久化
- Session Teleportation（2.1.0+）
- 本地状态文件

**Codex CLI：**
- 云端状态同步
- 跨设备无缝切换
- 与 ChatGPT 历史集成

---

## 六、高级功能

### 6.1 思考模式

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **思考命令** | `/think`, `/think harder`, `/ultraplan` | 推理级别调整 |
| **扩展思考** | ✅ 支持 | ✅ 支持 |
| **计划模式** | `/ultraplan`（云端规划） | 自动动态调整 |

### 6.2 自动化与脚本

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **CI/CD 集成** | ✅ 脚本化执行 | ✅ `codex exec` |
| **Hooks 系统** | ✅ 1.0.60+ | ❌ 基础支持 |
| **定时任务** | ✅ `/loop` 命令 | ❌ 不支持 |
| **后台执行** | ❌ 不支持 | ✅ Codex Cloud |

### 6.3 学习与适应

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **交互学习** | ✅ `/powerup` 系统 | ❌ 不支持 |
| **技能热重载** | ✅ 2.1.0+ | ❌ 不支持 |
| **项目记忆** | ✅ `/memory` 管理 | ✅ AGENTS.md |

---

## 七、开发者体验

### 7.1 错误处理

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **错误恢复** | ✅ Checkpoint 回滚 | ✅ 迭代修复 |
| **网络错误** | ✅ 自动重连 | ✅ 自动重连 |
| **诊断工具** | `claude doctor` | 内置诊断 |

### 7.2 自定义配置

**Claude Code 配置：**
```bash
# 主题配置
/config theme dark

# 权限配置
/permissions add "Bash(git commit:*)"

# 键盘快捷键
/config keybindings
```

**Codex CLI 配置：**
```toml
# ~/.codex/config.toml
disable_response_storage = true
preferred_auth_method = "apikey"
model = "gpt-5-codex"
```

---

## 八、功能特性评分

| 功能类别 | Claude Code | Codex CLI |
|----------|-------------|-----------|
| **代码编辑** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Git 集成** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **多模态** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **会话管理** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **云端功能** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **自动化** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **安全性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **扩展性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **移动端** | ⭐ | ⭐⭐⭐⭐⭐ |
| **开源生态** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
