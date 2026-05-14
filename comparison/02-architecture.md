# Claude Code vs Codex CLI 对比分析 - 架构与技术实现

---

## 一、系统架构对比

### 1.1 Claude Code 架构

```
┌─────────────────────────────────────────┐
│           Claude Code CLI                │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │ Terminal│ │ VS Code │ │ JetBrains│  │
│  │  REPL   │ │ Extension│ │  Plugin  │  │
│  └────┬────┘ └────┬────┘ └────┬─────┘  │
│       └─────────────┴───────────┘        │
│                   │                      │
│       ┌───────────▼───────────┐          │
│       │   Claude Code Core    │          │
│       │  (Native Binary)      │          │
│       └───────────┬───────────┘          │
│                   │                      │
│       ┌───────────▼───────────┐          │
│       │    Tool Orchestrator   │          │
│       │  - File Operations     │          │
│       │  - Bash Execution      │          │
│       │  - Git Integration     │          │
│       │  - MCP Client          │          │
│       └───────────┬───────────┘          │
│                   │                      │
│       ┌───────────▼───────────┐          │
│       │   Claude API Layer    │          │
│       │  - Anthropic API      │          │
│       │  - AWS Bedrock        │          │
│       │  - Google Vertex      │          │
│       └───────────────────────┘          │
└─────────────────────────────────────────┘
```

**架构特点：**
- **原生二进制**：高性能终端渲染引擎（NO_FLICKER）
- **Unix 哲学**：标准输入输出，可与其他工具组合
- **模块化设计**：核心 + 工具编排器 + API 层

### 1.2 Codex CLI 架构

```
┌─────────────────────────────────────────┐
│           Codex Ecosystem                │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │   CLI   │ │   IDE   │ │  Cloud   │  │
│  │ Terminal│ │Extension│ │  Agent   │  │
│  └────┬────┘ └────┬────┘ └────┬─────┘  │
│       └─────────────┴───────────┘        │
│                   │                      │
│       ┌───────────▼───────────┐          │
│       │   Codex Agent Core    │          │
│       │    (Rust/Open Source) │          │
│       └───────────┬───────────┘          │
│                   │                      │
│       ┌───────────▼───────────┐          │
│       │    Sandbox Layer       │          │
│       │  - macOS Seatbelt      │          │
│       │  - Linux Docker        │          │
│       │  - Network Isolation   │          │
│       └───────────┬───────────┘          │
│                   │                      │
│       ┌───────────▼───────────┐          │
│       │   OpenAI API Layer    │          │
│       │  - GPT-5 / GPT-5-Codex│          │
│       │  - Responses API      │          │
│       └───────────────────────┘          │
└─────────────────────────────────────────┘
```

**架构特点：**
- **开源 Rust 实现**：高性能、社区驱动
- **统一体验**：CLI/IDE/Cloud 共享同一 Agent 核心
- **沙盒优先**：默认隔离执行环境

---

## 二、技术实现细节

### 2.1 终端渲染引擎

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **渲染引擎** | NO_FLICKER（自定义） | 标准 TUI |
| **界面风格** | Focus View、命名主题 | 简洁终端 UI |
| **Vim 支持** | 完整 Vim 视觉模式 | 基础支持 |
| **多主题** | 支持命名主题切换 | 默认主题 |

### 2.2 编程语言与运行时

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **实现语言** | 原生二进制（推测 Rust/Go） | Rust（开源） |
| **安装包大小** | 轻量级原生包 | Rust 编译产物 |
| **启动速度** | 极快（原生） | 快（Rust） |
| **内存占用** | 优化良好 | 沙盒机制增加开销 |

### 2.3 网络与 API 通信

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **传输协议** | HTTP/2 + SSE | HTTP/2 + SSE |
| **认证方式** | OAuth / API Key | ChatGPT 账号 / API Key |
| **多区域支持** | Anthropic / AWS / Google | OpenAI 全球 |
| **离线支持** | 否 | 否 |

---

## 三、上下文管理

### 3.1 上下文窗口

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **最大上下文** | 100万 token | 标准 GPT-5 上下文 |
| **代码库索引** | 实时文件读取 | 实时文件读取 |
| **持久化记忆** | `/memory` 命令 | AGENTS.md 文件 |
| **会话压缩** | `/compact` 命令 | 自动管理 |

### 3.2 代码理解机制

**Claude Code：**
- 通过 `@` 语法引用文件
- `/tree` 展示项目结构
- `/overview` 获取高层概览
- `/structure` 分析架构模式
- CLAUDE.md 项目特定指导

**Codex CLI：**
- 自动代码库导航
- AGENTS.md 项目指令
- 图像输入理解（截图、线框图）
- 多轮对话式需求调整

---

## 四、扩展机制

### 4.1 MCP（Model Context Protocol）

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **MCP 版本** | 完整支持 | 支持 |
| **传输方式** | SSE / HTTP / OAuth 2.0 | SSE / HTTP |
| **自定义服务器** | 支持 | 支持 |
| **社区生态** | 丰富 |  growing |

### 4.2 自定义命令

**Claude Code：**
```bash
# Markdown 自定义 Slash 命令
.claude/commands/frontend/component.md → /frontend:component
```

**Codex CLI：**
```bash
# AGENTS.md 项目级指令
# 位于项目根目录，定义编码规范和工作流
```

---

## 五、性能对比

| 指标 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **启动时间** | < 1s | < 1s |
| **大文件处理** | 优秀（100万上下文） | 良好 |
| **多文件编辑** | 高效 | 高效 |
| **长时间任务** | 支持（Checkpoint 回滚） | 支持（云端后台） |
| **内存使用** | 较低 | 中等（沙盒开销） |
